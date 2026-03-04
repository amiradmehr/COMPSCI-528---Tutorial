# ESP-IDF Tutorial: From Blink to IMU Sensing

A hands-on introduction to embedded development with ESP-IDF — starting with the classic **Blink** example and progressing to real sensor data acquisition with the **MPU6050 IMU** over I²C.

---

## Part 1 — What is ESP-IDF?

**ESP-IDF** (Espressif IoT Development Framework) is the official SDK for programming ESP32-series microcontrollers made by Espressif Systems.

### Why ESP-IDF?

| Feature                  | Description                                                                         |
| ------------------------ | ----------------------------------------------------------------------------------- |
| Real-time OS             | Built on top of**FreeRTOS** — supports multitasking, queues, semaphores      |
| Rich driver library      | GPIO, SPI, I2C, UART, ADC, PWM, Wi-Fi, Bluetooth, and more                          |
| Component system         | Reusable components from the[ESP Component Registry](https://components.espressif.com) |
| Cross-platform toolchain | Works on Windows, macOS, and Linux                                                  |
| Active maintenance       | Maintained by Espressif with frequent releases and LTS branches                     |

### The ESP32 Family

This example supports all major ESP32 variants:

```
ESP32 · ESP32-S2 · ESP32-S3 · ESP32-C3 · ESP32-C6 · ESP32-H2 · ESP32-P4 · ...
```

Each chip has different GPIO counts, peripherals, and wireless capabilities, but ESP-IDF provides a **unified API** across all of them.

### Key ESP-IDF Concepts

| Concept        | What it means                                                                             |
| -------------- | ----------------------------------------------------------------------------------------- |
| `app_main()` | Entry point of your application (like `main()` in plain C, but runs as a FreeRTOS task) |
| Components     | Modular libraries (drivers, protocols, utilities) that you include in your build          |
| `sdkconfig`  | A generated file that stores all compile-time configuration options for your project      |
| `menuconfig` | An interactive terminal UI to configure your project (`idf.py menuconfig`)              |
| `idf.py`     | The command-line tool to build, flash, monitor, and manage ESP-IDF projects               |

### Typical Workflow

```
1. Write code  →  2. Configure (menuconfig)  →  3. Build (idf.py build)
                                                          ↓
                                            4. Flash  (idf.py flash)
                                                          ↓
                                            5. Monitor (idf.py monitor)
```

---

# Example 1 — Blink

---

## Part 2 — Blink: Project Structure

```
blink/
├── CMakeLists.txt              ← Top-level build file (project definition)
├── sdkconfig                   ← Auto-generated config (do NOT edit by hand)
├── sdkconfig.defaults          ← Default config applied before chip-specific defaults
├── sdkconfig.defaults.esp32s3  ← Chip-specific config overrides (one per target)
├── README.md                   ← Official example documentation
├── main/
│   ├── CMakeLists.txt          ← Registers source files for the main component
│   ├── blink_example_main.c    ← Application source code  ← THE MAIN FILE
│   ├── Kconfig.projbuild       ← Adds project options to menuconfig
│   └── idf_component.yml       ← Declares external component dependencies
└── managed_components/
    └── espressif__led_strip/   ← Auto-downloaded LED strip driver library
```

---

## Part 3 — Blink: File-by-File Breakdown

### `CMakeLists.txt` (top level)

```cmake
cmake_minimum_required(VERSION 3.16)

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
idf_build_set_property(MINIMAL_BUILD ON)
project(blink)
```

- **Purpose:** Defines this folder as an ESP-IDF project named `blink`.
- `include(...)` pulls in the entire ESP-IDF build system.
- `MINIMAL_BUILD ON` tells the build system to only compile components that are actually needed, keeping compile time short.
- Every ESP-IDF project must have exactly this structure in its top-level `CMakeLists.txt`.

---

### `main/CMakeLists.txt`

```cmake
idf_component_register(SRCS "blink_example_main.c"
                       INCLUDE_DIRS ".")
```

- **Purpose:** Registers the `main` component with the build system.
- `SRCS` lists every `.c` file in this component.
- `INCLUDE_DIRS` tells the compiler where to find local header files.
- In ESP-IDF, **everything is a component** — even your own `main/` folder.

---

### `main/idf_component.yml`

```yaml
dependencies:
  espressif/led_strip: "^3.0.0"
```

- **Purpose:** Declares external library dependencies, similar to `package.json` in Node.js or `requirements.txt` in Python.
- When you run `idf.py build` for the first time, the **Component Manager** automatically downloads `espressif/led_strip` (version ≥ 3.0.0) from the [ESP Component Registry](https://components.espressif.com).
- The downloaded component ends up in `managed_components/espressif__led_strip/`.

---

### `main/Kconfig.projbuild`

```kconfig
menu "Example Configuration"
    choice BLINK_LED
        prompt "Blink LED type"
        default BLINK_LED_GPIO
        config BLINK_LED_GPIO   bool "GPIO"
        config BLINK_LED_STRIP  bool "LED strip"
    endchoice

    config BLINK_GPIO
        int "Blink GPIO number"
        default 8
    ...
endmenu
```

- **Purpose:** Adds a custom configuration menu ("Example Configuration") to `idf.py menuconfig`.
- Defines three user-configurable options:
  - `CONFIG_BLINK_LED_GPIO` or `CONFIG_BLINK_LED_STRIP` — which LED type to use
  - `CONFIG_BLINK_LED_STRIP_BACKEND_RMT` or `_SPI` — how to drive the LED strip
  - `CONFIG_BLINK_GPIO` — which GPIO number the LED is on
- These options get compiled into `build/config/sdkconfig.h` as C `#define` macros, which the source code reads at compile time using `#ifdef`.

---

### `sdkconfig.defaults.esp32s3`

```
CONFIG_BLINK_LED_STRIP=y
# ESP32-S3-DevKitC v1.1 uses GPIO38 for the on-board LED
CONFIG_BLINK_GPIO=38
```

- **Purpose:** Pre-fills configuration values for a specific chip target so you don't have to run `menuconfig` every time.
- For the ESP32-S3-DevKitC, the on-board addressable LED (WS2812) sits on **GPIO 38**.
- There is one `sdkconfig.defaults.<target>` file per supported chip in this project.

---

### `sdkconfig` (auto-generated)

- **Do not edit this file manually.**
- It is created/updated by `idf.py menuconfig` or `idf.py build`.
- Contains the full resolved configuration for the current build.
- Should be committed to version control so team members share the same settings.

---

### `managed_components/espressif__led_strip/`

- Auto-downloaded by the Component Manager.
- Contains the full source code of the `led_strip` driver.
- You should **not** edit files here — treat them as a dependency.

---

## Part 4 — Blink: Source Code Walkthrough

File: `main/blink_example_main.c`

### 1. Includes

```c
#include <stdio.h>
#include "freertos/FreeRTOS.h"   // FreeRTOS core
#include "freertos/task.h"       // vTaskDelay()
#include "driver/gpio.h"         // GPIO driver
#include "esp_log.h"             // Logging (ESP_LOGI, ESP_LOGE, ...)
#include "led_strip.h"           // Addressable LED strip driver
#include "sdkconfig.h"           // Generated config macros (CONFIG_*)
```

- `FreeRTOS.h` and `task.h` give access to the RTOS — specifically `vTaskDelay()` which pauses execution without blocking the CPU entirely.
- `driver/gpio.h` provides functions to control GPIO pins.
- `esp_log.h` provides structured logging with timestamps and log levels.
- `sdkconfig.h` brings in all `CONFIG_*` macros defined via `menuconfig` / `Kconfig`.

---

### 2. Tag and GPIO Definition

```c
static const char *TAG = "example";

#define BLINK_GPIO CONFIG_BLINK_GPIO
```

- `TAG` is used as a prefix in log messages so you know which part of the code produced a log line.
- `BLINK_GPIO` is resolved at compile time from `sdkconfig.h`. For the ESP32-S3-DevKitC it will be `38`.

---

### 3. LED State Variable

```c
static uint8_t s_led_state = 0;
```

- Tracks whether the LED is currently ON (`1`) or OFF (`0`).
- `static` means this variable is local to this file (file-scope).

---

### 4. LED Strip Path (`#ifdef CONFIG_BLINK_LED_STRIP`)

This block is compiled **only** when the LED type is set to "LED strip" in menuconfig.

#### `blink_led()` — Strip version

```c
static void blink_led(void)
{
    if (s_led_state) {
        led_strip_set_pixel(led_strip, 0, 16, 16, 16); // pixel 0, R=16 G=16 B=16
        led_strip_refresh(led_strip);                  // send data over RMT/SPI
    } else {
        led_strip_clear(led_strip);                    // turn all pixels off
    }
}
```

- `led_strip_set_pixel(handle, pixel_index, R, G, B)` — sets color of a specific pixel.
- Values range from `0` (off) to `255` (maximum brightness). Using `16` for each channel gives a dim white.
- **Important:** `led_strip_refresh()` must be called after setting pixels — the data is only transmitted to the LED hardware at that point (double-buffer pattern).

#### `configure_led()` — Strip version

```c
static void configure_led(void)
{
    led_strip_config_t strip_config = {
        .strip_gpio_num = BLINK_GPIO,
        .max_leds = 1,
    };
#if CONFIG_BLINK_LED_STRIP_BACKEND_RMT
    led_strip_rmt_config_t rmt_config = {
        .resolution_hz = 10 * 1000 * 1000, // 10 MHz
    };
    ESP_ERROR_CHECK(led_strip_new_rmt_device(&strip_config, &rmt_config, &led_strip));
#elif CONFIG_BLINK_LED_STRIP_BACKEND_SPI
    led_strip_spi_config_t spi_config = {
        .spi_bus = SPI2_HOST,
        .flags.with_dma = true,
    };
    ESP_ERROR_CHECK(led_strip_new_spi_device(&strip_config, &spi_config, &led_strip));
#endif
    led_strip_clear(led_strip);
}
```

- Two backends are supported:
  - **RMT (Remote Control Transceiver):** A dedicated hardware peripheral for precise timing signals. Preferred when available because it runs independently of the CPU.
  - **SPI:** A general-purpose serial bus. Used as a fallback on chips without RMT.
- `ESP_ERROR_CHECK(expr)` is a macro that checks the return code and **aborts with a log message** if the call failed. This is the standard ESP-IDF error handling pattern.

---

### 5. Simple GPIO Path (`#elif CONFIG_BLINK_LED_GPIO`)

This block is compiled when the LED type is set to plain "GPIO".

```c
static void blink_led(void)
{
    gpio_set_level(BLINK_GPIO, s_led_state); // drive pin HIGH or LOW
}

static void configure_led(void)
{
    gpio_reset_pin(BLINK_GPIO);
    gpio_set_direction(BLINK_GPIO, GPIO_MODE_OUTPUT);
}
```

- `gpio_reset_pin()` returns the GPIO to its default state (input, no pull).
- `gpio_set_direction()` configures it as a push-pull output.
- `gpio_set_level()` drives the pin HIGH (`1`) or LOW (`0`).

---

### 6. `app_main()` — The Entry Point

```c
void app_main(void)
{
    configure_led();          // one-time hardware setup

    while (1) {
        ESP_LOGI(TAG, "Turning the LED %s!", s_led_state ? "ON" : "OFF");
        blink_led();                              // update hardware
        s_led_state = !s_led_state;              // toggle state
        vTaskDelay(CONFIG_BLINK_PERIOD / portTICK_PERIOD_MS); // wait
    }
}
```

- `app_main()` is called by ESP-IDF's startup code after the system is initialized.
- The `while(1)` loop runs forever — this is standard for embedded firmware.
- **`ESP_LOGI(TAG, format, ...)`** logs an info-level message. Output looks like:
  ```
  I (1325) example: Turning the LED ON!
  ```

  The `I` is the log level, `1325` is milliseconds since boot.
- **`vTaskDelay(ticks)`** yields the CPU to other FreeRTOS tasks during the delay. **Never use `for` loops or `sleep()` for delays in FreeRTOS** — use `vTaskDelay` instead.
- `portTICK_PERIOD_MS` converts milliseconds to FreeRTOS ticks (usually `1 tick = 1 ms`).

---

## Part 5 — Build, Flash, Monitor

```bash
# 1. Set the target chip (only needed once per project)
idf.py set-target esp32s3

# 2. (Optional) Open the interactive configuration menu
idf.py menuconfig

# 3. Build the firmware
idf.py build

# 4. Flash to the device (replace PORT with your serial port, e.g. /dev/ttyUSB0)
idf.py -p PORT flash

# 5. Open the serial monitor to see log output
idf.py -p PORT monitor

# Steps 4 and 5 combined:
idf.py -p PORT flash monitor
```

Exit the monitor with `Ctrl + ]`.

---

## Part 6 — Expected Output

Once flashed, you should see the LED blinking and the following on the serial monitor:

```
I (315) example: Example configured to blink addressable LED!
I (325) example: Turning the LED OFF!
I (1325) example: Turning the LED ON!
I (2325) example: Turning the LED OFF!
I (3325) example: Turning the LED ON!
```

---

## Blink Summary

| What we learned     | How it maps to ESP-IDF                                      |
| ------------------- | ----------------------------------------------------------- |
| Project entry point | `app_main()` in `main/blink_example_main.c`             |
| Hardware setup      | `configure_led()` — GPIO or LED strip init               |
| Main loop           | `while(1)` with `vTaskDelay()` for non-blocking delays  |
| Compile-time config | `Kconfig.projbuild` + `sdkconfig` + `#ifdef CONFIG_*` |
| External libraries  | `idf_component.yml` + Component Manager                   |
| Build system        | CMake +`idf.py` wrapper                                   |
| Logging             | `ESP_LOGI()` / `ESP_LOGE()` with level and tag          |
| Error handling      | `ESP_ERROR_CHECK()` macro                                 |

---

---

# Example 2 — IMU Sensing (MPU6050 over I²C)

---

## Part 7 — What is an IMU?

An **IMU (Inertial Measurement Unit)** is a sensor that measures motion and orientation. The **MPU6050** is one of the most widely used IMUs, combining:

| Sensor        | Measurements                        | Units              |
| ------------- | ----------------------------------- | ------------------ |
| Accelerometer | Linear acceleration on X, Y, Z axes | g (gravitational)  |
| Gyroscope     | Angular rate on X, Y, Z axes        | °/s (degrees/sec) |
| Thermometer   | On-chip temperature                 | °C                |

The MPU6050 communicates with the host microcontroller via **I²C** (Inter-Integrated Circuit), a two-wire serial protocol that supports multiple devices on the same bus.

### What is I²C?

I²C uses just two wires:

| Signal  | Name         | Purpose                                                     |
| ------- | ------------ | ----------------------------------------------------------- |
| `SCL` | Serial Clock | Generated by the **master** to synchronize data bits |
| `SDA` | Serial Data  | Bidirectional data line shared by all devices               |

Key properties:

- **Master/Slave** architecture — the ESP32 is the master, MPU6050 is the slave.
- Every device on the bus has a unique **7-bit address**. The MPU6050 default address is `0x68`.
- Maximum speed is typically **100 kHz** (Standard Mode) or **400 kHz** (Fast Mode).
- Both lines need **pull-up resistors** to VCC (usually 4.7 kΩ).

### Wiring the MPU6050 to ESP32

```
MPU6050 Pin   →   ESP32 Pin
───────────────────────────
VCC           →   3.3V
GND           →   GND
SDA           →   GPIO 18  (I2C_MASTER_SDA_IO)
SCL           →   GPIO 19  (I2C_MASTER_SCL_IO)
AD0           →   GND      (sets I²C address to 0x68)
```

> **Note:** GPIO 18 and 19 are used in this example, but I²C can be assigned to almost any GPIO on ESP32. The pins are configured entirely in software.

---

## Part 8 — IMU Project Structure

```
IMU_ESPIDF/
├── CMakeLists.txt              ← Top-level build file (includes a compatibility patch)
├── sdkconfig                   ← Auto-generated config
├── dependencies.lock           ← Locked component versions (like a lockfile)
├── main/
│   ├── CMakeLists.txt          ← Registers main.c and declares component dependencies
│   ├── idf_component.yml       ← Declares espressif/mpu6050 as a dependency
│   └── main.c                  ← Application source code  ← THE MAIN FILE
└── managed_components/
    └── espressif__mpu6050/     ← Auto-downloaded MPU6050 driver library
```

---

## Part 9 — IMU: File-by-File Breakdown

### `CMakeLists.txt` (top level)

```cmake
cmake_minimum_required(VERSION 3.16)

# ── Patch espressif/mpu6050 v1.2.1 for ESP-IDF 5.x ──────────────────────────
set(_MPU_CMAKE
    "${CMAKE_CURRENT_SOURCE_DIR}/managed_components/espressif__mpu6050/CMakeLists.txt")
if(EXISTS "${_MPU_CMAKE}")
    file(READ "${_MPU_CMAKE}" _content)
    string(REPLACE
        "set(REQ esp_driver_gpio esp_driver_i2c)"
        "set(REQ esp_driver_gpio esp_driver_i2c driver)"
        _content_fixed "${_content}")
    if(NOT "${_content_fixed}" STREQUAL "${_content}")
        file(WRITE "${_MPU_CMAKE}" "${_content_fixed}")
        message(STATUS "mpu6050: applied IDF-5.x legacy-driver patch")
    endif()
endif()

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(IMU)
```

This is more advanced than the Blink `CMakeLists.txt`. In addition to the standard boilerplate, it contains a **CMake patch** applied before the build system initializes.

**Why is the patch needed?**

The `espressif/mpu6050` v1.2.1 component was written for an older ESP-IDF API. In ESP-IDF ≥ 5.3, the legacy `driver/i2c.h` moved to a separate umbrella component called `driver`. The mpu6050 component's own `CMakeLists.txt` declares only `esp_driver_i2c` as a dependency but its C source still `#include`s `driver/i2c.h`. The patch adds `driver` to the component's `REQUIRES` so the compiler can find the header.

The `string(REPLACE ...)` call:

- **Finds** the old dependency line in the mpu6050 component's CMakeLists.
- **Replaces** it with an expanded version that adds `driver`.
- Writes the change back **only if** it was needed (idempotent — safe to run multiple times).

> **Key lesson:** When using third-party components, you may need to patch them for compatibility with newer ESP-IDF versions. Doing it via CMake (rather than modifying the downloaded files by hand) keeps the fix reproducible.

---

### `main/CMakeLists.txt`

```cmake
idf_component_register(SRCS "main.c"
                       INCLUDE_DIRS "."
                       REQUIRES mpu6050 driver)
```

Compared to the Blink version, this adds the `REQUIRES` field:

- `mpu6050` — links the MPU6050 component so its headers and compiled library are available.
- `driver` — links the legacy I²C driver umbrella component, required for `driver/i2c.h`.

---

### `main/idf_component.yml`

```yaml
dependencies:
  espressif/mpu6050:
    version: "1.2.1"
```

- Pins the MPU6050 component to exactly version `1.2.1`.
- On first build, the Component Manager downloads this from the ESP Component Registry into `managed_components/espressif__mpu6050/`.
- `dependencies.lock` is generated alongside this and records the exact resolved versions of all transitive dependencies — similar to `package-lock.json`.

---

## Part 10 — IMU: Source Code Walkthrough

File: `main/main.c`

### 1. Includes and Pin Definitions

```c
#include "driver/i2c.h"           // Legacy I²C driver (master init, param config)
#include "esp_log.h"              // ESP_LOGI / ESP_LOGE
#include "mpu6050.h"              // MPU6050 component API
#include <stdio.h>

#define I2C_MASTER_SCL_IO 19      /*!< GPIO number for I2C master clock */
#define I2C_MASTER_SDA_IO 18      /*!< GPIO number for I2C master data  */
#define I2C_MASTER_NUM I2C_NUM_0  /*!< I2C port number (0 or 1)         */
#define I2C_MASTER_FREQ_HZ 100000 /*!< 100 kHz — standard I²C speed     */
```

- `driver/i2c.h` is the **legacy I²C API** that provides `i2c_param_config()` and `i2c_driver_install()`. ESP-IDF 5.x introduced a new "I²C master" API, but this example uses the legacy one because the `mpu6050` component relies on it internally.
- `mpu6050.h` exposes the high-level sensor API: `mpu6050_create()`, `mpu6050_get_acce()`, etc.
- `I2C_NUM_0` selects the first I²C hardware peripheral on the chip. The ESP32 typically has two (`I2C_NUM_0` and `I2C_NUM_1`).

---

### 2. Global Handles

```c
static const char *TAG = "mpu6050 test";
static mpu6050_handle_t mpu6050 = NULL;
```

- `mpu6050_handle_t` is an **opaque handle** — a pointer to an internal driver structure. You never access the structure directly; you pass the handle to every API function.
- Initializing it to `NULL` is a safety convention — a `NULL` handle means "not yet created."

---

### 3. `i2c_bus_init()` — Bringing the I²C Bus Up

```c
static void i2c_bus_init(void) {
    i2c_config_t conf;
    conf.mode           = I2C_MODE_MASTER;
    conf.sda_io_num     = (gpio_num_t)I2C_MASTER_SDA_IO;
    conf.sda_pullup_en  = GPIO_PULLUP_ENABLE;
    conf.scl_io_num     = (gpio_num_t)I2C_MASTER_SCL_IO;
    conf.scl_pullup_en  = GPIO_PULLUP_ENABLE;
    conf.master.clk_speed = I2C_MASTER_FREQ_HZ;
    conf.clk_flags      = I2C_SCLK_SRC_FLAG_FOR_NOMAL;

    esp_err_t ret = i2c_param_config(I2C_MASTER_NUM, &conf);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "I2C config returned error");
        return;
    }

    ret = i2c_driver_install(I2C_MASTER_NUM, conf.mode, 0, 0, 0);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "I2C install returned error");
        return;
    }
}
```

This function configures and installs the I²C driver. Let's break it down field by field:

| Field                | Value                           | Why                                          |
| -------------------- | ------------------------------- | -------------------------------------------- |
| `mode`             | `I2C_MODE_MASTER`             | ESP32 drives the clock; MPU6050 is the slave |
| `sda_io_num`       | GPIO 18                         | Data wire                                    |
| `sda_pullup_en`    | `GPIO_PULLUP_ENABLE`          | I²C lines are open-drain and need pull-ups  |
| `scl_io_num`       | GPIO 19                         | Clock wire                                   |
| `scl_pullup_en`    | `GPIO_PULLUP_ENABLE`          | Same as SDA                                  |
| `master.clk_speed` | 100,000 Hz                      | Standard I²C 100 kHz mode                   |
| `clk_flags`        | `I2C_SCLK_SRC_FLAG_FOR_NOMAL` | Use the default APB clock source             |

- **`i2c_param_config()`** applies the configuration struct to the selected I²C port.
- **`i2c_driver_install()`** allocates driver resources (DMA buffers, interrupt handlers). The last three zeros are: receive buffer size (0 for master), transmit buffer size (0 for master), interrupt flags (0 for default).

---

### 4. `i2c_sensor_mpu6050_init()` — Creating and Configuring the Sensor

```c
static void i2c_sensor_mpu6050_init(void) {
    i2c_bus_init();

    mpu6050 = mpu6050_create(I2C_MASTER_NUM, MPU6050_I2C_ADDRESS);
    if (mpu6050 == NULL) {
        ESP_LOGE(TAG, "MPU6050 create returned NULL");
        return;
    }

    esp_err_t ret = mpu6050_config(mpu6050, ACCE_FS_4G, GYRO_FS_500DPS);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "MPU6050 config error");
        return;
    }

    ret = mpu6050_wake_up(mpu6050);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "MPU6050 wake up error");
        return;
    }
}
```

Step by step:

1. **`mpu6050_create(port, address)`**

   - Allocates and returns a handle for the sensor on `I2C_NUM_0` at address `0x68` (`MPU6050_I2C_ADDRESS`).
   - If the device is not found or allocation fails, returns `NULL`.
2. **`mpu6050_config(handle, accel_range, gyro_range)`**

   - Programs the sensor's internal registers to select measurement ranges:

   | Constant        | Accelerometer Full Scale | Smallest measurable change |
   | --------------- | ------------------------ | -------------------------- |
   | `ACCE_FS_2G`  | ±2 g                    | Most sensitive             |
   | `ACCE_FS_4G`  | ±4 g                    | ← Used here               |
   | `ACCE_FS_8G`  | ±8 g                    |                            |
   | `ACCE_FS_16G` | ±16 g                   | Least sensitive            |

   | Constant            | Gyroscope Full Scale | Smallest measurable change |
   | ------------------- | -------------------- | -------------------------- |
   | `GYRO_FS_250DPS`  | ±250 °/s           | Most sensitive             |
   | `GYRO_FS_500DPS`  | ±500 °/s           | ← Used here               |
   | `GYRO_FS_1000DPS` | ±1000 °/s          |                            |
   | `GYRO_FS_2000DPS` | ±2000 °/s          | Least sensitive            |


   > **Tip:** A smaller range gives higher resolution (more bits per unit of measurement). A larger range avoids saturation during fast/violent motion.
   >
3. **`mpu6050_wake_up(handle)`**

   - The MPU6050 powers up in **sleep mode** to save energy. This call writes to the Power Management register to wake the sensor before reading data.

---

### 5. `app_main()` — Reading Sensor Data

```c
void app_main(void) {
    esp_err_t ret;
    uint8_t mpu6050_deviceid;
    mpu6050_acce_value_t acce;
    mpu6050_gyro_value_t gyro;
    mpu6050_temp_value_t temp;

    i2c_sensor_mpu6050_init();

    /* --- Device ID --- */
    ret = mpu6050_get_deviceid(mpu6050, &mpu6050_deviceid);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to get MPU6050 device ID");
    } else {
        ESP_LOGI(TAG, "MPU6050 device ID: 0x%02X", mpu6050_deviceid);
    }

    /* --- Accelerometer --- */
    ret = mpu6050_get_acce(mpu6050, &acce);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to get accelerometer data");
    }
    ESP_LOGI(TAG, "acce_x:%.2f, acce_y:%.2f, acce_z:%.2f",
             acce.acce_x, acce.acce_y, acce.acce_z);

    /* --- Gyroscope --- */
    ret = mpu6050_get_gyro(mpu6050, &gyro);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to get gyroscope data");
    }
    ESP_LOGI(TAG, "gyro_x:%.2f, gyro_y:%.2f, gyro_z:%.2f",
             gyro.gyro_x, gyro.gyro_y, gyro.gyro_z);

    /* --- Temperature --- */
    ret = mpu6050_get_temp(mpu6050, &temp);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to get temperature data");
    }
    ESP_LOGI(TAG, "temp:%.2f C", temp.temp);

    /* --- Cleanup --- */
    mpu6050_delete(mpu6050);
    ret = i2c_driver_delete(I2C_MASTER_NUM);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to delete I2C driver");
    }
}
```

#### Data types

The component defines structs to hold the sensor readings:

```c
typedef struct {
    float acce_x;   // acceleration in g
    float acce_y;
    float acce_z;
} mpu6050_acce_value_t;

typedef struct {
    float gyro_x;   // angular rate in °/s
    float gyro_y;
    float gyro_z;
} mpu6050_gyro_value_t;

typedef struct {
    float temp;     // temperature in °C
} mpu6050_temp_value_t;
```

#### Reading Device ID

- `mpu6050_get_deviceid()` reads register `0x75` (WHO_AM_I) from the sensor.
- The MPU6050 always responds with `0x68`.
- This is a quick sanity check — if the returned ID is wrong, the wiring or address is incorrect.

#### Reading Accelerometer

- `mpu6050_get_acce()` reads 6 bytes (2 bytes per axis × 3 axes) from registers `0x3B`–`0x40`.
- The raw ADC values are converted to `float` in units of **g** based on the configured full-scale range.
- With the sensor lying flat, you should see approximately: `acce_x ≈ 0.0, acce_y ≈ 0.0, acce_z ≈ 1.0` (gravity pointing down the Z axis).

#### Reading Gyroscope

- `mpu6050_get_gyro()` reads 6 bytes from registers `0x43`–`0x48`.
- Values are in **°/s**. A motionless sensor should read approximately `0.0` on all axes (with a small offset due to sensor noise).

#### Reading Temperature

- `mpu6050_get_temp()` reads the internal die temperature — useful for calibration, not ambient temperature.
- Formula applied internally: `temp_C = raw / 340.0 + 36.53`

#### Cleanup

- `mpu6050_delete(handle)` frees the memory allocated for the sensor handle.
- `i2c_driver_delete(port)` uninstalls the I²C driver and releases hardware resources.
- In this example the program ends after reading once, so cleanup is good practice. In a real application you would read in a loop and only clean up on shutdown.

---

## Part 11 — Build and Run the IMU Project

```bash
# Navigate to the IMU project directory
cd Examples/IMU_ESPIDF

# Set the target (ESP32, ESP32-S3, etc.)
idf.py set-target esp32

# Build (component manager downloads mpu6050 automatically)
idf.py build

# Flash and monitor
idf.py -p PORT flash monitor
```

---

## Part 12 — Expected IMU Output

```
I (342) mpu6050 test: MPU6050 device ID: 0x68
I (352) mpu6050 test: acce_x:0.03, acce_y:-0.01, acce_z:0.99
I (362) mpu6050 test: gyro_x:0.12, gyro_y:-0.05, gyro_z:0.02
I (372) mpu6050 test: temp:28.41 C
```

- Device ID `0x68` confirms the sensor is correctly wired and responding.
- `acce_z ≈ 1.0 g` confirms the sensor is lying flat (gravity along Z).
- Gyro values near `0.0` confirm the sensor is stationary.
- Temperature reflects the on-chip temperature (typically a few degrees above ambient).

---

## Part 13 — Extending to a Continuous Loop

The example reads data once and exits. In a real wearable or motion-sensing application, you would wrap the reads in a FreeRTOS loop:

```c
void app_main(void) {
    mpu6050_acce_value_t acce;
    mpu6050_gyro_value_t gyro;

    i2c_sensor_mpu6050_init();

    while (1) {
        mpu6050_get_acce(mpu6050, &acce);
        mpu6050_get_gyro(mpu6050, &gyro);

        ESP_LOGI(TAG, "ax=%.2f ay=%.2f az=%.2f | gx=%.2f gy=%.2f gz=%.2f",
                 acce.acce_x, acce.acce_y, acce.acce_z,
                 gyro.gyro_x, gyro.gyro_y, gyro.gyro_z);

        vTaskDelay(pdMS_TO_TICKS(100)); // 10 Hz sampling rate
    }
}
```

- `pdMS_TO_TICKS(100)` converts 100 ms to FreeRTOS ticks — equivalent to `100 / portTICK_PERIOD_MS`.
- At 10 Hz, you get 10 samples per second — adequate for many gesture and activity recognition tasks.
- You could increase to 100 Hz or more depending on your application requirements.

---

## IMU Summary

| What we learned         | How it maps to ESP-IDF / MPU6050                          |
| ----------------------- | --------------------------------------------------------- |
| I²C bus initialization | `i2c_param_config()` + `i2c_driver_install()`         |
| Sensor handle creation  | `mpu6050_create(port, address)` → opaque handle        |
| Sensor configuration    | `mpu6050_config(handle, accel_fs, gyro_fs)`             |
| Waking up the sensor    | `mpu6050_wake_up()` — MPU6050 starts in sleep mode     |
| Reading accelerometer   | `mpu6050_get_acce()` → `mpu6050_acce_value_t` struct |
| Reading gyroscope       | `mpu6050_get_gyro()` → `mpu6050_gyro_value_t` struct |
| Reading temperature     | `mpu6050_get_temp()` → `mpu6050_temp_value_t` struct |
| Verifying connectivity  | `mpu6050_get_deviceid()` → expect `0x68`             |
| Proper cleanup          | `mpu6050_delete()` + `i2c_driver_delete()`            |
| CMake patching          | `string(REPLACE ...)` to fix component compatibility    |
| Continuous sampling     | `while(1)` + `vTaskDelay(pdMS_TO_TICKS(N))`           |

---

## Comparing the Two Examples

| Aspect           | Blink                         | IMU (MPU6050)                           |
| ---------------- | ----------------------------- | --------------------------------------- |
| Peripheral       | GPIO / RMT / SPI              | I²C                                    |
| Dependency       | `espressif/led_strip`       | `espressif/mpu6050`                   |
| Data direction   | Output only (drive a pin)     | Input (read sensor registers)           |
| Configuration    | Kconfig / menuconfig          | Hardcoded pins + sensor register config |
| Runtime behavior | Infinite loop with LED toggle | One-shot read (extendable to loop)      |
| Error handling   | `ESP_ERROR_CHECK()` macro   | Manual `if (ret != ESP_OK)` checks    |
| CMake complexity | Minimal boilerplate           | Includes a compatibility patch          |
| Output           | Blinking LED + serial log     | Sensor values on serial monitor         |
