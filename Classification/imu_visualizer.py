import serial
import time
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import threading
import queue

# Setup serial connection
ser = serial.Serial('COM4', 115200, timeout=0)
data_queue = queue.Queue()

def read_from_port(q):
    """ Thread for reading the serial data and storing it in a queue. """
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            q.put(line)

# Start thread for reading serial data
thread = threading.Thread(target=read_from_port, args=(data_queue,))
thread.start()

# Initialize the 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-2, 2])
ax.set_ylim([-2, 2])
ax.set_zlim([-2, 2])

# Initial vertices of a cube
vertices = np.array([
    [1, 1, 1], [1, -1, 1], [-1, -1, 1], [-1, 1, 1],
    [1, 1, -1], [1, -1, -1], [-1, -1, -1], [-1, 1, -1]
])

# Function to update the cube orientation
def update_orientation(R, vertices):
    """ Rotate vertices by the rotation matrix R """
    return np.dot(vertices, R.T)

def update(frame):
    while not data_queue.empty():
        line = data_queue.get()
        try:
            acc_str, gyro_str, temp_str = line.split('|')
            gyro = eval(gyro_str)

            # Integrate gyro data to estimate rotation (simplified, not accurate for long term)
            angle = np.linalg.norm(gyro) * 0.01  # Assuming data rate is 100 Hz
            axis = gyro / np.linalg.norm(gyro) if np.linalg.norm(gyro) != 0 else np.array([0, 0, 1])
            cos_angle = np.cos(angle)
            sin_angle = np.sin(angle)
            one_minus_cos = 1.0 - cos_angle

            # Rotation matrix from axis-angle (Rodrigues' rotation formula)
            R = np.array([
                [cos_angle + axis[0]**2 * one_minus_cos,
                 axis[0] * axis[1] * one_minus_cos - axis[2] * sin_angle,
                 axis[0] * axis[2] * one_minus_cos + axis[1] * sin_angle],
                [axis[1] * axis[0] * one_minus_cos + axis[2] * sin_angle,
                 cos_angle + axis[1]**2 * one_minus_cos,
                 axis[1] * axis[2] * one_minus_cos - axis[0] * sin_angle],
                [axis[2] * axis[0] * one_minus_cos - axis[1] * sin_angle,
                 axis[2] * axis[1] * one_minus_cos + axis[0] * sin_angle,
                 cos_angle + axis[2]**2 * one_minus_cos]
            ])

            # Apply rotation
            rotated_vertices = update_orientation(R, vertices)

            # Clear and plot new orientation
            ax.cla()
            ax.scatter(rotated_vertices[:, 0], rotated_vertices[:, 1], rotated_vertices[:, 2])
            ax.set_xlim([-2, 2])
            ax.set_ylim([-2, 2])
            ax.set_zlim([-2, 2])
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')

        except Exception as e:
            print(f"Error parsing data: {e}")
            plt.close()
            ser.close()

# Create animation
ani = FuncAnimation(fig, update, interval=10)

plt.show()
