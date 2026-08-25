# Build/run the IBM 7030 "Stretch" Bluespec model and its testbench.
# Delegates to build.sh, which pins the Homebrew bsc toolchain --
# see bsv/README.md "Toolchain" for why that matters.
#
#   make sim   # compile the Bluesim executable
#   make run   # compile (if needed) and run it
#   make clean

.PHONY: sim run clean

sim:
	./build.sh

run:
	./build.sh run

clean:
	rm -rf build simbuild stretch_sim stretch_sim.so *.bo *.ba
