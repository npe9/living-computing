#pragma once

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

void     host_init(uint32_t dummy);
void     host_shutdown(uint32_t dummy);
uint64_t host_max_cycles(void);
uint32_t host_trace(void);
void     host_log(uint64_t cyc, uint32_t taskn, uint32_t mpc,
                  uint32_t pc, uint32_t ir, uint32_t waitn, uint32_t fields,
                  uint32_t ac0, uint32_t ac1, uint32_t ac2, uint32_t ac3);
void     host_task_tick(uint32_t taskn);
void     host_dump_mem(uint32_t addr, uint32_t data);

uint32_t host_ucode(uint32_t bank, uint32_t addr);
uint16_t host_constant(uint32_t addr);
uint8_t  host_acs(uint32_t addr);
uint32_t host_cram_word(uint32_t addr);
uint16_t host_cram_half(uint32_t addr);
void     host_cram_write(uint32_t addr, uint32_t data);

uint32_t host_disk_loaded(void);
uint16_t host_disk_cylinders(void);
uint16_t host_disk_read_word(uint32_t idx);
void     host_disk_write_word(uint32_t idx, uint16_t data);
void     host_disk_select(uint32_t cyl, uint32_t head, uint32_t sec);
void     host_disk_commit(void);

void     host_draw_word(uint32_t line, uint32_t wordn, uint16_t data, uint32_t lowres);
void     host_draw_cursor(uint32_t line, uint32_t x, uint32_t wob, uint16_t csr);
void     host_render_field(uint32_t fieldn);

uint16_t host_kb_read(uint16_t addr);
uint16_t host_mouse_bits(void);
void     host_poll_input(void);

void     host_ether_tx_word(uint16_t w);
void     host_ether_tx_end(void);
uint32_t host_ether_rx_count(void);
uint16_t host_ether_rx_word(void);
void     host_ether_reset(void);
void     host_ether_rx_rewind(void);
void     host_ether_rx_release(void);
void     host_ether_post(uint16_t status);
void     host_ether_look(uint16_t peek, uint16_t bus);
void     host_ether_ebfct(uint32_t cmd, uint32_t done, uint32_t late, uint32_t coll);
void     host_ether_pkt(uint16_t ebloc, uint16_t eip,
                        uint16_t w0, uint16_t w1, uint16_t w2, uint16_t w3);

#ifdef __cplusplus
}
#endif
