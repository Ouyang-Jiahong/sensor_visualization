import time
from data_buffer import timestamps, MAX_POINTS, update_velocity, update_displacement
from data_buffer import (
    acc_x_data, acc_y_data, acc_z_data,
    velocity_x_data, velocity_y_data, velocity_z_data,
    displacement_x_data, displacement_y_data, displacement_z_data
)
import numpy as np

# 参数设置
ZERO_SPEED_THRESHOLD = 0.15     # 静止判断阈值 (m/s²)

# 初始化漂移估计
drift_x = 0
drift_y = 0
drift_z = 0

def is_zero_velocity(acc):
    """简单判断是否处于静止状态"""
    return abs(acc) < ZERO_SPEED_THRESHOLD

def update_drift(drift, acc):
    """根据静止阶段的数据估计漂移量"""
    if is_zero_velocity(acc):
        drift = 0.9 * drift + 0.1 * acc  # 简单的指数加权平均
    return drift

def compute_integration(timestamps, accelerations, drift):
    """
    输入：时间戳列表、加速度列表、漂移量
    输出：速度、位移
    """
    if len(timestamps) < 2:        
        return 0, 0

    # 修正加速度
    corrected_acc = np.array(accelerations) - drift

    # 计算时间间隔
    dt = np.diff(timestamps)

    # 积分计算速度
    velocity = np.sum(corrected_acc[:-1] * dt)

    # 零速修正
    if is_zero_velocity(np.mean(accelerations)):
        velocity = 0

    # 积分计算位移
    displacement = np.sum(velocity * dt)

    return velocity, displacement

def process_motion_data():
    """主处理函数：根据当前加速度数据更新速度和位移"""
    global drift_x, drift_y, drift_z

    # 更新漂移估计
    drift_x = update_drift(drift_x, acc_x_data[-1])
    drift_y = update_drift(drift_y, acc_y_data[-1])
    drift_z = update_drift(drift_z, acc_z_data[-1])

    # 计算积分
    vx, dx = compute_integration(timestamps, acc_x_data, drift_x)
    vy, dy = compute_integration(timestamps, acc_y_data, drift_y)
    vz, dz = compute_integration(timestamps, acc_z_data, drift_z)

    update_velocity(vx, vy, vz)
    update_displacement(dx, dy, dz)

    # 控制缓存长度
    for lst in [
        velocity_x_data, velocity_y_data, velocity_z_data,
        displacement_x_data, displacement_y_data, displacement_z_data
    ]:
        while len(lst) > MAX_POINTS:
            lst.pop(0)