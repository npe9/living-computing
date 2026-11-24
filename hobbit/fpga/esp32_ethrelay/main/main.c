/*
 * ULX3S ESP32 Ethernet relay (hobbit/docs/ulx3s_ethernet.md).
 *
 * The FPGA's SONIC-subset engine sends and receives raw Ethernet frames
 * over a UART to this ESP32 (link protocol: relay.h).  The ESP32 carries
 * each frame as one UDP datagram to tools/qemu1e/hub.py on the host,
 * exactly the framing of QEMU's dgram netdev: no header, no FCS.
 *
 * Written for ESP-IDF v5.3 (target esp32, ESP32-WROOM-32 on the ULX3S).
 * NOT YET COMPILED FOR THE TARGET: no ESP-IDF is installed where it was
 * written.  The protocol code (relay.c) is compiled and tested on the
 * host by hobbit/tests/test_ethrelay.py; this file is only the glue.
 *
 * Pins (ULX3S v3.x, emard/ulx3s ulx3s_v20.lpf): UART2 TX = GPIO17 (FPGA
 * N3, "wifi_gpio17"), RX = GPIO16 (FPGA L1, "wifi_gpio16"), optional
 * RTS = GPIO4 (FPGA H1, sd_d1).  None of them is a boot strap.
 *
 * Two tasks:
 *   link_rx_task: UART bytes -> relay_feed -> sendto(hub)
 *   net_rx_task:  recvfrom(hub) -> relay_encode -> uart_write_bytes
 * The UART driver's TX ring (CONFIG_RELAY_UART_TX_BUF) is the queue
 * towards the FPGA; when it is full net_rx_task blocks and lwIP's UDP
 * mailbox (CONFIG_LWIP_UDP_RECVMBOX_SIZE in sdkconfig.defaults) absorbs
 * the rest of a burst, then drops.
 */
#include <string.h>

#include "driver/uart.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/task.h"
#include "lwip/inet.h"
#include "lwip/sockets.h"
#include "nvs_flash.h"

#include "relay.h"

#define UART_PORT UART_NUM_2
#define GOT_IP    BIT0

static const char *TAG = "ethrelay";
static EventGroupHandle_t wifi_events;
static int sock = -1;
static struct sockaddr_in hub_addr;

static void wifi_event(void *arg, esp_event_base_t base, int32_t id,
                       void *data)
{
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        xEventGroupClearBits(wifi_events, GOT_IP);
        ESP_LOGW(TAG, "WiFi disconnected, reconnecting");
        esp_wifi_connect();
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t *e = data;
        ESP_LOGI(TAG, "got ip " IPSTR, IP2STR(&e->ip_info.ip));
        xEventGroupSetBits(wifi_events, GOT_IP);
    }
}

static void wifi_start(void)
{
    wifi_events = xEventGroupCreate();
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(
        WIFI_EVENT, ESP_EVENT_ANY_ID, wifi_event, NULL, NULL));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(
        IP_EVENT, IP_EVENT_STA_GOT_IP, wifi_event, NULL, NULL));
    wifi_config_t wc = { 0 };
    strncpy((char *)wc.sta.ssid, CONFIG_RELAY_WIFI_SSID, sizeof wc.sta.ssid);
    strncpy((char *)wc.sta.password, CONFIG_RELAY_WIFI_PASSWORD,
            sizeof wc.sta.password);
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wc));
    ESP_ERROR_CHECK(esp_wifi_start());
    /* Modem sleep would add up to a beacon interval (~100 ms) to every
     * inbound frame: as long as IL's whole timer tick (stil.c Iltickms). */
    ESP_ERROR_CHECK(esp_wifi_set_ps(WIFI_PS_NONE));
    xEventGroupWaitBits(wifi_events, GOT_IP, pdFALSE, pdTRUE, portMAX_DELAY);
}

static void uart_start(void)
{
    uart_config_t uc = {
        .baud_rate = CONFIG_RELAY_UART_BAUD,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
#if CONFIG_RELAY_UART_RTS_GPIO >= 0
        .flow_ctrl = UART_HW_FLOWCTRL_RTS,
        .rx_flow_ctrl_thresh = 100,     /* of the 128-byte RX FIFO */
#else
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
#endif
        .source_clk = UART_SCLK_DEFAULT,
    };
    ESP_ERROR_CHECK(uart_driver_install(UART_PORT, CONFIG_RELAY_UART_RX_BUF,
                                        CONFIG_RELAY_UART_TX_BUF, 0, NULL, 0));
    ESP_ERROR_CHECK(uart_param_config(UART_PORT, &uc));
    ESP_ERROR_CHECK(uart_set_pin(UART_PORT, CONFIG_RELAY_UART_TX_GPIO,
                                 CONFIG_RELAY_UART_RX_GPIO,
                                 CONFIG_RELAY_UART_RTS_GPIO >= 0
                                     ? CONFIG_RELAY_UART_RTS_GPIO
                                     : UART_PIN_NO_CHANGE,
                                 UART_PIN_NO_CHANGE));
}

static void send_status(const char *text)
{
    static uint8_t wire[RELAY_MAX_WIRE];
    size_t n = relay_encode(RELAY_T_STATUS, (const uint8_t *)text,
                            strlen(text), wire);
    uart_write_bytes(UART_PORT, wire, n);
}

static void link_rx_task(void *arg)
{
    static relay_dec dec;
    uint8_t buf[256];
    unsigned long sent = 0, err = 0;

    relay_dec_init(&dec);
    for (;;) {
        int k = uart_read_bytes(UART_PORT, buf, sizeof buf,
                                pdMS_TO_TICKS(10));
        for (int i = 0; i < k; i++) {
            const uint8_t *p;
            size_t n;
            if (relay_feed(&dec, buf[i], &p, &n) == RELAY_T_ETH) {
                if (sendto(sock, p, n, 0, (struct sockaddr *)&hub_addr,
                           sizeof hub_addr) < 0)
                    err++;
                else
                    sent++;
            }
        }
        if (k == 0 && (dec.bad_crc | dec.bad_cobs | dec.bad_len) &&
            (sent & 0x3FF) == 0)
            ESP_LOGW(TAG, "link: good %u crc %u cobs %u len %u ovf %u",
                     (unsigned)dec.good, (unsigned)dec.bad_crc,
                     (unsigned)dec.bad_cobs, (unsigned)dec.bad_len,
                     (unsigned)dec.overflows);
    }
}

static void net_rx_task(void *arg)
{
    static uint8_t frame[RELAY_MAX_FRAME + 64];
    static uint8_t wire[RELAY_MAX_WIRE];

    for (;;) {
        int n = recv(sock, frame, sizeof frame, 0);
        if (n < RELAY_MIN_FRAME || n > RELAY_MAX_FRAME)
            continue;
        size_t w = relay_encode(RELAY_T_ETH, frame, (size_t)n, wire);
        uart_write_bytes(UART_PORT, wire, w);       /* blocks when full */
    }
}

void app_main(void)
{
    esp_err_t e = nvs_flash_init();
    if (e == ESP_ERR_NVS_NO_FREE_PAGES ||
        e == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        e = nvs_flash_init();
    }
    ESP_ERROR_CHECK(e);
    uart_start();
    send_status("ethrelay: wifi connecting");
    wifi_start();

    sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    struct sockaddr_in me = {
        .sin_family = AF_INET,
        .sin_port = htons(CONFIG_RELAY_LOCAL_PORT),
        .sin_addr.s_addr = htonl(INADDR_ANY),
    };
    ESP_ERROR_CHECK(sock < 0 ? ESP_FAIL : ESP_OK);
    ESP_ERROR_CHECK(bind(sock, (struct sockaddr *)&me, sizeof me) < 0
                        ? ESP_FAIL : ESP_OK);
    memset(&hub_addr, 0, sizeof hub_addr);
    hub_addr.sin_family = AF_INET;
    hub_addr.sin_port = htons(CONFIG_RELAY_HUB_PORT);
    hub_addr.sin_addr.s_addr = inet_addr(CONFIG_RELAY_HUB_HOST);
    ESP_LOGI(TAG, "relaying UART%d @ %d baud <-> %s:%d (local %d)",
             UART_PORT, CONFIG_RELAY_UART_BAUD, CONFIG_RELAY_HUB_HOST,
             CONFIG_RELAY_HUB_PORT, CONFIG_RELAY_LOCAL_PORT);
    send_status("ethrelay: up");

    xTaskCreatePinnedToCore(link_rx_task, "link_rx", 4096, NULL, 10, NULL, 1);
    xTaskCreatePinnedToCore(net_rx_task, "net_rx", 4096, NULL, 10, NULL, 1);
}
