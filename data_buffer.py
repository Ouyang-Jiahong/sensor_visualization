# data_buffer.py
import numpy as np

MAX_POINTS = 600

# 初始化数据缓冲区
acc_x_data = []
acc_y_data = []
acc_z_data = []

gyro_x_data = []
gyro_y_data = []
gyro_z_data = []

roll_data = []
pitch_data = []
yaw_data = []

velocity_x_data = []
velocity_y_data = []
velocity_z_data = []

displacement_x_data = []
displacement_y_data = []
displacement_z_data = []

timestamps = []

def update_buffers(data):
    """更新原始IMU数据到缓冲区"""
    timestamps.append(data.timestamp)

    acc_x_data.append(data.acc_x)
    acc_y_data.append(data.acc_y)
    acc_z_data.append(data.acc_z)

    gyro_x_data.append(data.gyro_x)
    gyro_y_data.append(data.gyro_y)
    gyro_z_data.append(data.gyro_z)

    roll_data.append(data.roll)
    pitch_data.append(data.pitch)
    yaw_data.append(data.yaw)

    # 得到去除重力影响的加速度，用于积分计算
    pure_acc = remove_gravity(
        data.acc_x, data.acc_y, data.acc_z,
        data.roll, data.pitch, data.yaw
    )
    print(pure_acc)
    # 首先将零速区间的判断所需条件计算出来
    # 计算模长用于零速判断
    acc_norm = np.linalg.norm(pure_acc)
    gyro_norm = np.linalg.norm([
        gyro_x_data[-1],
        gyro_y_data[-1],
        gyro_z_data[-1]
    ])

    if is_zero_velocity(acc_norm, gyro_norm):
        vx, vy, vz = 0, 0, 0  # 零速修正
        dx, dy, dz = 0, 0, 0

    else:
        # 如果不是处于零速状态，则处理最后一个数据点，然后积分得到最新的速度
        vx, dx = compute_velocity_displacement(timestamps, acc_x_data)
        vy, dy = compute_velocity_displacement(timestamps, acc_y_data)
        vz, dz = compute_velocity_displacement(timestamps, acc_z_data)

    velocity_x_data.append(vx)
    velocity_y_data.append(vy)
    velocity_z_data.append(vz)

    displacement_x_data.append(dx)
    displacement_y_data.append(dy)
    displacement_z_data.append(dz)

    # 控制缓存长度
    if len(acc_x_data) > MAX_POINTS:
        timestamps.pop(0)

        acc_x_data.pop(0)
        acc_y_data.pop(0)
        acc_z_data.pop(0)

        gyro_x_data.pop(0)
        gyro_y_data.pop(0)
        gyro_z_data.pop(0)

        roll_data.pop(0)
        pitch_data.pop(0)
        yaw_data.pop(0)

        velocity_x_data.pop(0)
        velocity_y_data.pop(0)
        velocity_z_data.pop(0)

        displacement_x_data.pop(0)
        displacement_y_data.pop(0)
        displacement_z_data.pop(0)

def compute_velocity_displacement(timestamps, acc_data):
    """
    单轴速度和位移计算
    """
    if len(timestamps) < 2:
        return 0, 0

    dt = np.diff(timestamps)
    corrected_acc = np.array(acc_data)
    velocity = np.sum(corrected_acc[:-1] * dt)
    displacement = np.sum(velocity * dt)

    return velocity, displacement


def is_zero_velocity(acc_norm, gyro_norm, acc_thresh=0.3, gyro_thresh=0.1):
    """
    综合加速度和角速度判断是否为零速
    """
    return acc_norm < acc_thresh and gyro_norm < gyro_thresh

def remove_gravity(acc_x, acc_y, acc_z, roll_deg, pitch_deg, yaw_deg):
    # 姿态角结算时所使用的坐标系为东北天坐标系，定义为为 Z-Y-X,即先绕 Z 轴转，再绕 Y 轴转，再绕 X 轴转。
    g = 0.98
    roll = np.radians(roll_deg)
    pitch = np.radians(pitch_deg)
    yaw = np.radians(yaw_deg)
    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw),  np.cos(yaw), 0],
        [0,            0,           1]
    ])
    Ry = np.array([
        [ np.cos(pitch), 0, np.sin(pitch)],
        [ 0,             1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])
    Rx = np.array([
        [1, 0,           0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll),  np.cos(roll)]
    ])

    R = Rz @ Ry @ Rx
    g_world = np.array([0, 0, g])
    g_sensor = R.T @ g_world
    acc = np.array([acc_x, acc_y, acc_z])
    pure_acc = acc - g_sensor

    return pure_acc