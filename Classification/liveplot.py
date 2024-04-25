import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import queue
import numpy as np
from scipy.interpolate import CubicSpline  # Import the CubicSpline function

# Setup serial connection (adjust COM port and baud rate as needed)
ser = serial.Serial('COM4', baudrate=115200, timeout=1)
data_queue = queue.Queue()

def read_from_port(q) -> None:
    """ A thread for reading the serial data and storing it in a queue. """
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            q.put(line)

# Start thread for reading serial data
thread = threading.Thread(target=read_from_port, args=(data_queue,))
thread.start()

# Initialize lists to store the data for plotting
times = []
acc_x = []
acc_y = []
acc_z = []
gyro_x = []
gyro_y = []
gyro_z = []
temp_data = []

# Initialize EMA variables
ema_acc_x = ema_acc_y = ema_acc_z = 0
ema_gyro_x = ema_gyro_y = ema_gyro_z = 0
ema_temp = 0
alpha = 0.5  # Smoothing factor

# Setup the plotting framework
fig, ax = plt.subplots(3, 1, figsize=(10, 10))


def update(frame):
    while not data_queue.empty():
        line = data_queue.get()
        try:

            acc_str, gyro_str, temp_str = line.split('|')
            acc = eval(acc_str)
            gyro = eval(gyro_str)
            temp = float(temp_str)

            # Calculate EMA for smoothing
            global ema_acc_x, ema_acc_y, ema_acc_z, ema_gyro_x, ema_gyro_y, ema_gyro_z, ema_temp
            ema_acc_x = alpha * acc[0] + (1 - alpha) * ema_acc_x
            ema_acc_y = alpha * acc[1] + (1 - alpha) * ema_acc_y
            ema_acc_z = alpha * acc[2] + (1 - alpha) * ema_acc_z
            ema_gyro_x = alpha * gyro[0] + (1 - alpha) * ema_gyro_x
            ema_gyro_y = alpha * gyro[1] + (1 - alpha) * ema_gyro_y
            ema_gyro_z = alpha * gyro[2] + (1 - alpha) * ema_gyro_z
            ema_temp = alpha * temp + (1 - alpha) * ema_temp

            # Append new data for plotting
            current_time = time.time()
            times.append(current_time)
            acc_x.append(ema_acc_x)
            acc_y.append(ema_acc_y)
            acc_z.append(ema_acc_z)
            gyro_x.append(ema_gyro_x)
            gyro_y.append(ema_gyro_y)
            gyro_z.append(ema_gyro_z)
            temp_data.append(ema_temp)

            # Maintain data lists length
            if len(times) > 300:
                times.pop(0)
                acc_x.pop(0)
                acc_y.pop(0)
                acc_z.pop(0)
                gyro_x.pop(0)
                gyro_y.pop(0)
                gyro_z.pop(0)
                temp_data.pop(0)

        except Exception as e:
            print(f"Error parsing data: {e}")

    if times:
        # Update plots dynamically with smoothed data
        ax[0].clear()
        ax[0].plot(times, acc_x, label='Acc X', color='r')
        ax[0].plot(times, acc_y, label='Acc Y', color='g')
        ax[0].plot(times, acc_z, label='Acc Z', color='b')
        ax[0].legend(loc='upper left')
        ax[0].set_title('Acceleration (m/s^2)')

        ax[1].clear()
        ax[1].plot(times, gyro_x, label='Gyro X', color='r')
        ax[1].plot(times, gyro_y, label='Gyro Y', color='g')
        ax[1].plot(times, gyro_z, label='Gyro Z', color='b')
        ax[1].legend(loc='upper left')
        ax[1].set_title('Gyro (degrees/s)')

        ax[2].clear()
        ax[2].plot(times, temp_data, label='Temperature', color='r')
        ax[2].legend(loc='upper left')
        ax[2].set_title('Temperature (°C)')

        # Ensure plots do not overlap
        plt.tight_layout()

# Animation setup
ani = FuncAnimation(fig, update, interval=100)

plt.show()