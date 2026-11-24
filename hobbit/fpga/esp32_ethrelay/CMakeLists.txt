# ULX3S ESP32 Ethernet relay: ESP-IDF v5.3 project (hobbit/docs/ulx3s_ethernet.md).
#   idf.py set-target esp32 && idf.py menuconfig   (menu "Ethernet relay")
#   idf.py build
# Not yet built for the target (no ESP-IDF where it was written); the
# protocol code is tested on the host by hobbit/tests/test_ethrelay.py.
cmake_minimum_required(VERSION 3.16)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(esp32_ethrelay)
