import serial
import time
import numpy as np

# Set up the serial connection (adjust the COM port and baud rate as needed)
ser = serial.Serial('COM4', 115200, timeout=1)
freq = 20  # Frequency of data collection in Hz

try:
    # check if serial is available
    if ser.is_open:
        while True:
            # Read a line from the serial port
            line = ser.readline().decode('utf-8').strip()
            if line:  # Only print if there's something to read
                acc_str, gyro_str, temp_str = line.split('|')
                acc = eval(acc_str)
                gyro = eval(gyro_str)
                temp = float(temp_str)
                print(f"{acc[0]},{acc[1]},{acc[2]}")
            time.sleep(1/freq) # Match the sleep time of the CircuitPython script
    else:
        raise Exception("Serial port is not open")
except KeyboardInterrupt:
    print("Program interrupted by user")
finally:
    ser.close()  # Ensure the serial connection is closed on exit