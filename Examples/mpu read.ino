#include <Wire.h>

#define MPU_ADDR 0x68 // MPU6050 I2C address

// Define custom SDA and SCL pins
#define SDA_PIN 0
#define SCL_PIN 1

void setup() {
  Wire.begin(SDA_PIN, SCL_PIN); // Initialize I2C communication with custom pins
  Serial.begin(9600);           // Initialize serial communication
  while (!Serial);              // Wait for serial monitor to open

  // Wake up the MPU6050
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B); // PWR_MGMT_1 register
  Wire.write(0);    // Clear sleep mode bit (Bit 6)
  Wire.endTransmission();
}

void loop() {
  // Read accelerometer and gyroscope data
  int16_t accelerometer_data[3];
  int16_t gyroscope_data[3];
  
  readData(MPU_ADDR, 0x3B, accelerometer_data, 6); // Read 6 bytes starting from 0x3B (ACCEL_XOUT_H)
  readData(MPU_ADDR, 0x43, gyroscope_data, 6);     // Read 6 bytes starting from 0x43 (GYRO_XOUT_H)

  // Print the data
  Serial.print("Accelerometer: ");
  Serial.print("X = "); Serial.print(accelerometer_data[0]);
  Serial.print(", Y = "); Serial.print(accelerometer_data[1]);
  Serial.print(", Z = "); Serial.println(accelerometer_data[2]);

  Serial.print("Gyroscope: ");
  Serial.print("X = "); Serial.print(gyroscope_data[0]);
  Serial.print(", Y = "); Serial.print(gyroscope_data[1]);
  Serial.print(", Z = "); Serial.println(gyroscope_data[2]);

  delay(1000); // Wait for 1 second
}

void readData(int deviceAddress, byte address, int16_t* data, int length) {
  Wire.beginTransmission(deviceAddress);
  Wire.write(address);
  Wire.endTransmission(false); // Keep the connection alive for a repeated start

  Wire.requestFrom(deviceAddress, length); // Request bytes from the MPU6050

  int i = 0;
  while (Wire.available()) {
    byte highByte = Wire.read();
    byte lowByte = Wire.read();
    data[i] = (highByte << 8) | lowByte; // Combine high and low bytes
    i++;
  }
}
