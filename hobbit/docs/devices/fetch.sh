#!/bin/sh
# Fetch the device data sheets listed in MANIFEST.md into this directory
# and check them against SHA256SUMS.  The PDFs stay out of git (.gitignore):
# none of their sources shows redistribution terms.
#
#   cd hobbit/docs/devices && sh fetch.sh          # fetch what is missing, check all
#   sh fetch.sh --check                            # check only
set -eu
cd "$(dirname "$0")"

fetch_pdf() {
    url=$1
    output=$2
    if [ -f "$output" ]; then
        return 0
    fi
    temporary="${output}.part"
    curl --fail --location --proto '=https' --retry 3 --output "$temporary" "$url"
    test "$(head -c 5 "$temporary")" = '%PDF-'
    mv "$temporary" "$output"
}

if [ "${1:-}" != "--check" ]; then
    B=https://bitsavers.trailing-edge.com/components
    # National DP83932B SONIC data sheet (book pp. 1-288..1-383), AN-745, AN-746
    fetch_pdf "$B/national/_dataBooks/1992_National_Local_Area_Network_Databook.pdf" \
      1992_National_Local_Area_Network_Databook.pdf
    # AN-746, Software Driver Programmer's Guide for the DP83932 SONIC (Mar 1991)
    fetch_pdf "$B/national/_appNotes/AN-0746.pdf" AN-0746.pdf
    # SC26C94/SC68C94 QUART preliminary specification, 12 Nov 1990
    fetch_pdf "$B/signetics/_dataBooks/1991_Signetics_IC019_Data_Communication_Products.pdf" \
      1991_Signetics_IC019_Data_Communication_Products.pdf
    # SC68C94 QUART product specification, 27 Apr 1994
    fetch_pdf "$B/signetics/_dataBooks/1994_Signetics_Data_Communications.pdf" \
      1994_Signetics_Data_Communications.pdf
    # WD33C93A data sheet and application notes, Nov 1990
    fetch_pdf "$B/westernDigital/WD33C93A_Data_Sheet_and_Application_Notes_Nov1990.pdf" \
      WD33C93A_Data_Sheet_and_Application_Notes_Nov1990.pdf
    # PCF8584, PCF8582C-2, PCF8574 (Philips I2C peripherals data book, 1997)
    fetch_pdf "$B/philips/_dataBooks/1997_IC12_Philips_I2C_Peripherals.pdf" \
      1997_IC12_Philips_I2C_Peripherals.pdf
    # MK48T02 TIMEKEEPER data sheet, Feb 1992
    fetch_pdf "$B/sgs/_dataBooks/1992_SGS-THOMSON_Memory_Products_2nd_Ed.pdf" \
      1992_SGS-THOMSON_Memory_Products_2nd_Ed.pdf
    # Hobbit BeBox board (docs/bebox_hardware.md):
    # VLSI VL82C106 combo I/O (book pp. 6-185..6-220) and VL16C452 (6-51..)
    fetch_pdf "$B/vti/databook/1990_VTI_Computer_Products.pdf" \
      1990_VTI_Computer_Products.pdf
    # Motorola MCS3201 floppy disk controller data sheet, 1991
    fetch_pdf "$B/motorola/_dataSheets/MCS3201_IBM_PC_XT_AT_Floppy_Disk_Controller_1991.pdf" \
      MCS3201_IBM_PC_XT_AT_Floppy_Disk_Controller_1991.pdf
    # AMD Am53C94/Am53C96, Publication 16506 Rev. C, 1993 (not on bitsavers)
    fetch_pdf "https://stuff.mit.edu/afs/sipb/contrib/doc/specs/ic/scsi/am53c94.pdf" \
      am53c94.pdf
    # NCR 53C94/95/96 data sheet, February 1990 (image-only scan; not on bitsavers)
    fetch_pdf "https://cdn.hackaday.io/files/18974811783616/NCR_53C94_53C95_53C96_Data_Sheet_Feb90.pdf" \
      NCR_53C94_53C95_53C96_Data_Sheet_Feb90.pdf
    # VGADOC 4b, Trident chapter (plain text; the display card, 2026-11-24)
    if [ ! -f VGADOC_TRIDENT.TXT ]; then
        curl --fail --location --proto '=https' --retry 3 --output VGADOC_TRIDENT.TXT.part \
          "https://pdos.csail.mit.edu/6.1810/2017/readings/hardware/vgadoc/TRIDENT.TXT"
        mv VGADOC_TRIDENT.TXT.part VGADOC_TRIDENT.TXT
    fi
fi

shasum -a 256 -c SHA256SUMS
