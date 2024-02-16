# COMPSCI-528: Mobile and Ubiquitous Computing

This is a tutorial for COMPSCI 528 assignments.

## Useful Links

These are useful links for the tutorial:

- [ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/index.html)
- [Circuitpy online editor](https://code.circuitpython.org)
- [EDC22 Day 1 Talk 15: CircuitPython for ESP32](https://www.youtube.com/watch?v=1eZQzn0PX-A)

# ESP-IDF Setup (Ubuntu)

## Install Prerequisites

Make sure you have the following dependencies installed:

```bash
sudo apt-get install git wget flex bison gperf python3 python3-pip python3-venv cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0
```

## Get ESP-IDF

```bash
mkdir -p ~/esp
cd ~/esp
git clone -b v5.2 --recursive https://github.com/espressif/esp-idf.git
```

## Set up the Tools

```bash
cd ~/esp/esp-idf
./install.sh esp32 all
```

## Set up the Environment

```bash
Adding User to dialout or uucp on Linux
sudo usermod -a -G dialout $USER
```

# ESP-IDF Setup (Windows)

1. Download [ESP-IDF Tools Online Installer](https://dl.espressif.com/dl/idf-installer/esp-idf-tools-setup-online-2.24.exe?)
2. 

# Circuit Python Setup

## Install Prerequisites

1. Go to the [Circuitpy website](https://circuitpython.org/board/espressif_esp32s3_devkitc_1_n32r8/) and click on ***OPEN INSTALLER***
2. Click on ***Full CircuitPython 8.2.10 Install***
3. Connect the ESP32 to the computer via USB port
4. Press and hold the ***BOOT*** button on the ESP32
5. Press and release the ***RESET*** button on the ESP32
6. Release the ***BOOT*** button on the ESP32
7. Now select the com port and click ***Install***
8. After the installation is complete, press the ***RESET*** button again
9. There should be a new drive called ***CIRCUITPY*** in the file explorer
10. Copy and paste the [.UF2 file](https://downloads.circuitpython.org/bin/espressif_esp32s3_devkitc_1_n32r8/en_US/adafruit-circuitpython-espressif_esp32s3_devkitc_1_n32r8-en_US-8.2.10.uf2) file into the ***CIRCUITPY*** drive
11. Install additional libraries by copying the [lib folder](../main/lib/)
 or from the Circuitpy website [here](https://circuitpython.org/libraries#:~:text=Bundles-,Bundle%20for%20Version%208.x,-This%20bundle%20is)