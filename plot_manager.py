# plot_manager.py
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
from data_buffer import MAX_POINTS, acc_x_data, acc_y_data, acc_z_data, velocity_x_data, velocity_y_data, \
    velocity_z_data, displacement_x_data, displacement_y_data, displacement_z_data
from data_buffer import gyro_x_data, gyro_y_data, gyro_z_data
from data_buffer import roll_data, pitch_data, yaw_data
from data_buffer import acc_x_data as acc_data
from data_collector import data_queue
from sensor_data import GetDeviceData
from motion_processor import process_motion_data

fig, axs = plt.subplots(5, 1, figsize=(10, 12))
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

    lines['vel_x'] = Line2D([], [], color='r', label='Vel X')
    lines['vel_y'] = Line2D([], [], color='g', label='Vel Y')
    lines['vel_z'] = Line2D([], [], color='b', label='Vel Z')
    axs[3].add_line(lines['vel_x'])
    axs[3].add_line(lines['vel_y'])
    axs[3].add_line(lines['vel_z'])
    axs[3].legend()
    axs[3].set_title("Velocity (m/s)")

    lines['disp_x'] = Line2D([], [], color='r', label='Disp X')
    lines['disp_y'] = Line2D([], [], color='g', label='Disp Y')
    lines['disp_z'] = Line2D([], [], color='b', label='Disp Z')
    axs[4].add_line(lines['disp_x'])
    axs[4].add_line(lines['disp_y'])
    axs[4].add_line(lines['disp_z'])
    axs[4].legend()
    axs[4].set_title("Displacement (m)")

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
        process_motion_data()

    # 确保 x 的长度和数据缓冲区长度一致
    max_len = max(len(acc_x_data), len(gyro_x_data), len(roll_data), len(velocity_x_data), len(displacement_x_data))
    x = range(max_len)

    def set_line_data(line_key, data):
        if len(data) < max_len:
            padded_data = data + [0] * (max_len - len(data))
        else:
            padded_data = data
        lines[line_key].set_data(x, padded_data)

    set_line_data('acc_x', acc_x_data)
    set_line_data('acc_y', acc_y_data)
    set_line_data('acc_z', acc_z_data)

    set_line_data('gyro_x', gyro_x_data)
    set_line_data('gyro_y', gyro_y_data)
    set_line_data('gyro_z', gyro_z_data)

    set_line_data('roll', roll_data)
    set_line_data('pitch', pitch_data)
    set_line_data('yaw', yaw_data)

    set_line_data('vel_x', velocity_x_data)
    set_line_data('vel_y', velocity_y_data)
    set_line_data('vel_z', velocity_z_data)
    set_line_data('disp_x', displacement_x_data)
    set_line_data('disp_y', displacement_y_data)
    set_line_data('disp_z', displacement_z_data)

    for ax in axs:
        ax.set_xlim(0, max_len)

    return lines.values()