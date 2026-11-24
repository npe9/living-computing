idf_component_register(SRCS "main.c" "relay.c"
                       INCLUDE_DIRS "."
                       PRIV_REQUIRES esp_wifi esp_netif esp_event nvs_flash
                                     esp_driver_uart lwip)
