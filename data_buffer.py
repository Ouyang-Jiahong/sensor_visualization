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
    """
    利用姿态角（roll, pitch, yaw）将重力投影到传感器坐标系，剔除加速度中的重力分量。

    参数:
        acc_x: x轴加速度
        acc_y: y轴加速度
        acc_z: z轴加速度
        roll_deg: 绕x轴的旋转角度（单位：度）
        pitch_deg: 绕y轴的旋转角度（单位：度）
        yaw_deg: 绕z轴的旋转角度（单位：度）

    返回:
        剔除了重力分量的加速度 [acc_x_corrected, acc_y_corrected, acc_z_corrected]
    """

    # 传感器协议：
    #  1. 姿态角结算时所使用的坐标系为东北天坐标系，正方向放置模块,如“4 引脚说明”
    #  所示向左为 X 轴，向前为 Y 轴，向上为 Z 轴。欧拉角表示姿态时的坐标系旋转顺序
    #  定义为为 Z-Y-X,即先绕 Z 轴转，再绕 Y 轴转，再绕 X 轴转。
    #  2. 滚转角的范围虽然是±180 度，但实际上由于坐标旋转顺序是 Z-Y-X，在表示姿态
    #  的时候，俯仰角(Y 轴)的范围只有±90 度，超过 90 度后会变换到小于 90 度，同时
    #  让X轴的角度大于180度。详细原理请大家自行百度欧拉角及姿态表示的相关信息。
    #  3. 由于三轴是耦合的，只有在小角度的时候会表现出独立变化，在大角度的时候姿态
    #  角度会耦合变化，比如当 Y 轴接近 90 度时，即使姿态只绕 Y 轴转动，X 轴的角度

    g = 0.98  # 重力加速度常数
    # 将角度从度转换为弧度
    roll = np.radians(roll_deg)
    pitch = np.radians(pitch_deg)
    yaw = np.radians(yaw_deg)

    # 构建重力矢量在世界坐标系下
    gravity_world = np.array([0, 0, g])

    # 构造旋转矩阵（Z-Y-X顺序）
    R_x = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])

    R_y = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])

    R_z = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])

    # 总旋转矩阵
    R = R_x @ R_y @ R_z

    # 将重力从世界坐标系转换到传感器坐标系
    gravity_sensor = R.T @ gravity_world

    # 构建加速度向量
    acc = np.array([acc_x, acc_y, acc_z])

    # 减去重力得到纯加速度
    return acc - gravity_sensor