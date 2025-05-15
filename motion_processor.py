import numpy as np
import remove_gravity
from data_buffer import (
    timestamps, MAX_POINTS, update_velocity, update_displacement,
    acc_x_data, acc_y_data, acc_z_data,
    gyro_x_data, gyro_y_data, gyro_z_data,
    velocity_x_data, velocity_y_data, velocity_z_data,
    displacement_x_data, displacement_y_data, displacement_z_data,
    roll_data, yaw_data, pitch_data,
)

def process_motion_data():
    
    # 得到去除重力影响的加速度，用于积分计算
    pure_acc = remove_gravity.remove_gravity(
        acc_x_data[-1], acc_y_data[-1], acc_z_data[-1],
        roll_data[-1], pitch_data[-1], yaw_data[-1]
    )
    # print(pure_acc)
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

    update_velocity(vx, vy, vz)
    update_displacement(dx, dy, dz)

    # 控制缓存长度
    for lst in [
        velocity_x_data, velocity_y_data, velocity_z_data,
        displacement_x_data, displacement_y_data, displacement_z_data
    ]:
        while len(lst) > MAX_POINTS:
            lst.pop(0)

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
