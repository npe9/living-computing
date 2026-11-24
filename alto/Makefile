# Xerox Alto II Bluesim build.  Imported from alto-bluespec (see README.md).
#
# The control PROM image rom/rom_arrays.h is NOT in git (rom/MANIFEST.md);
# put it there before building.  Bluesim's wrapper script needs bluetcl on
# PATH at run time, so this Makefile prepends the bsc bin directory.

BSC_HOME ?= /opt/homebrew/Cellar/bsc/2026.01
BSC      ?= $(BSC_HOME)/bin/bsc
export BLUESPECDIR ?= $(BSC_HOME)/libexec/lib
export PATH := $(dir $(BSC)):$(PATH)

BUILD    := build
SRC      := bsv
SIM      := sim
ROM      := rom

BSCFLAGS := -u -sim -bdir $(BUILD) -simdir $(BUILD) -info-dir $(BUILD) \
            -p $(SRC):$(SIM):+ -keep-fires -aggressive-conditions -no-show-timestamps

TOP      := mkSimTop
TOPMOD   := SimTop.bsv

.PHONY: all sim clean run smoke

all: sim

sim: $(BUILD)/alto-sim

$(ROM)/rom_arrays.h:
	@echo "missing $@: the Alto II control PROMs are held locally, not in git."
	@echo "see rom/MANIFEST.md for the file and its SHA-256."
	@exit 1

$(BUILD)/alto-sim: $(SIM)/SimTop.bsv $(SRC)/*.bsv $(SIM)/host.c $(SIM)/host.h $(ROM)/rom_arrays.h
	mkdir -p $(BUILD)
	$(BSC) $(BSCFLAGS) -g $(TOP) -u $(SIM)/$(TOPMOD)
	$(BSC) -sim -e $(TOP) -bdir $(BUILD) -simdir $(BUILD) \
		-o $(BUILD)/alto-sim -Xc -I$(ROM) -Xc -I$(SIM) \
		$(BUILD)/$(TOP).ba $(SIM)/host.c

run: sim
	@test -n "$(DISK)" || (echo "set DISK=path/to/parc.dsk"; exit 1)
	ALTO_DISK=$(DISK) ALTO_CYCLES=$(or $(CYCLES),5000000) \
		ALTO_TRACE=$(or $(TRACE),0) ALTO_FRAME=$(or $(FRAME),$(BUILD)/alto_frame.pbm) \
		$(BUILD)/alto-sim

smoke: sim
	sh tests/run_smoke.sh

clean:
	rm -rf $(BUILD)
