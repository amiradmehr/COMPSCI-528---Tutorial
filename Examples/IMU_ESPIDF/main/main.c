#include "driver/i2c.h"
#include "esp_log.h"
#include "mpu6050.h"
#include <stdio.h>

#define I2C_MASTER_SCL_IO 19      /*!< GPIO number for I2C master clock */
#define I2C_MASTER_SDA_IO 18      /*!< GPIO number for I2C master data  */
#define I2C_MASTER_NUM I2C_NUM_0  /*!< I2C port number for master dev   */
#define I2C_MASTER_FREQ_HZ 100000 /*!< I2C master clock frequency        */

static const char *TAG = "mpu6050 test";
static mpu6050_handle_t mpu6050 = NULL;

/**
 * @brief Initialize the I2C bus as master.
 */
static void i2c_bus_init(void) {
  i2c_config_t conf;
  conf.mode = I2C_MODE_MASTER;
  conf.sda_io_num = (gpio_num_t)I2C_MASTER_SDA_IO;
  conf.sda_pullup_en = GPIO_PULLUP_ENABLE;
  conf.scl_io_num = (gpio_num_t)I2C_MASTER_SCL_IO;
  conf.scl_pullup_en = GPIO_PULLUP_ENABLE;
  conf.master.clk_speed = I2C_MASTER_FREQ_HZ;
  conf.clk_flags = I2C_SCLK_SRC_FLAG_FOR_NOMAL;

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

/**
 * @brief Initialize the MPU6050 sensor over I2C.
 */
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
  ESP_LOGI(TAG, "acce_x:%.2f, acce_y:%.2f, acce_z:%.2f", acce.acce_x,
           acce.acce_y, acce.acce_z);

  /* --- Gyroscope --- */
  ret = mpu6050_get_gyro(mpu6050, &gyro);
  if (ret != ESP_OK) {
    ESP_LOGE(TAG, "Failed to get gyroscope data");
  }
  ESP_LOGI(TAG, "gyro_x:%.2f, gyro_y:%.2f, gyro_z:%.2f", gyro.gyro_x,
           gyro.gyro_y, gyro.gyro_z);

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
