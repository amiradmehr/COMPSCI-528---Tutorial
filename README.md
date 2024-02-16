# COMPSCI-528---Tutorial


This is a tutorial for COMPSCI 528.

## Useful Links
These are useful links for the tutorial:

# ESP-IDF Setup



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

