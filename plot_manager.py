# plot_manager.py
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
from data_buffer import MAX_POINTS, acc_x_data, acc_y_data, acc_z_data
from data_buffer import gyro_x_data, gyro_y_data, gyro_z_data
from data_buffer import roll_data, pitch_data, yaw_data

fig, axs = plt.subplots(3, 1, figsize=(10, 8))
lines = {}

def setup_plot():
    for ax in axs:
        ax.set_xlim(0, MAX_POINTS / 100)
        ax.set_ylim(-4, 4)

    lines['acc_x'] = Line2D([], [], color='r', label='Acc X')
    lines['acc_y'] = Line2D([], [], color='g', label='Acc Y')
    lines['acc_z'] = Line2D([], [], color='b', label='Acc Z')
    axs[0].add_line(lines['acc_x'])
    axs[0].add_line(lines['acc_y'])
    axs[0].add_line(lines['acc_z'])
    axs[0].legend()
    axs[0].set_title("Acceleration (m/s²)")

    lines['gyro_x'] = Line2D([], [], color='r', label='Gyro X')
    lines['gyro_y'] = Line2D([], [], color='g', label='Gyro Y')
    lines['gyro_z'] = Line2D([], [], color='b', label='Gyro Z')
    axs[1].add_line(lines['gyro_x'])
    axs[1].add_line(lines['gyro_y'])
    axs[1].add_line(lines['gyro_z'])
    axs[1].legend()
    axs[1].set_title("Angular Velocity (rad/s)")

    lines['roll'] = Line2D([], [], color='r', label='Roll')
    lines['pitch'] = Line2D([], [], color='g', label='Pitch')
    lines['yaw'] = Line2D([], [], color='b', label='Yaw')
    axs[2].add_line(lines['roll'])
    axs[2].add_line(lines['pitch'])
    axs[2].add_line(lines['yaw'])
    axs[2].legend()
    axs[2].set_title("Orientation (rad)")

    fig.tight_layout()

setup_plot()

def init_plot():
    for line in lines.values():
        line.set_data([], [])
    return lines.values()

def update(frame):
    from data_collector import data_queue
    from data_buffer import update_buffers

    while not data_queue.empty():
        data = data_queue.get()
        update_buffers(data)

    x = range(len(acc_x_data))

    lines['acc_x'].set_data(x, acc_x_data)
    lines['acc_y'].set_data(x, acc_y_data)
    lines['acc_z'].set_data(x, acc_z_data)

    lines['gyro_x'].set_data(x, gyro_x_data)
    lines['gyro_y'].set_data(x, gyro_y_data)
    lines['gyro_z'].set_data(x, gyro_z_data)

    lines['roll'].set_data(x, roll_data)
    lines['pitch'].set_data(x, pitch_data)
    lines['yaw'].set_data(x, yaw_data)

    for ax in axs:
        ax.set_xlim(0, len(x))

    return lines.values()