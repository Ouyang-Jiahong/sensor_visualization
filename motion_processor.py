# motion_processor.py
import time
from data_buffer import timestamps
from data_buffer import (
    acc_x_data, acc_y_data, acc_z_data,
    velocity_x_data, velocity_y_data, velocity_z_data,
    displacement_x_data, displacement_y_data, displacement_z_data
)
import numpy as np

# 参数设置
ZERO_SPEED_THRESHOLD = 0.15     # 静止判断阈值 (m/s²)
MAX_POINTS = 200                # 最大数据长度（用于初始化 drift_estimators）

# 初始化漂移估计器（用于X/Y/Z轴）
drift_estimators = {
    'x': [],
    'y': [],
    'z': []
}

def is_zero_velocity(acc):
    """简单判断是否处于静止状态"""
    return abs(acc) < ZERO_SPEED_THRESHOLD

def update_drift_estimator(axis, acc):
    """根据静止阶段的数据估计漂移量"""
    drift_list = drift_estimators[axis]
    drift_list.append(acc)

    # 只保留最近 N 个静止点用于漂移估计
    MAX_DRIFT_SAMPLES = 30
    if len(drift_list) > MAX_DRIFT_SAMPLES:
        drift_list.pop(0)

    return np.mean(drift_list) if drift_list else 0.0

def compute_velocity_and_displacement(timestamps, accelerations, axis='x'):
    """
    输入：时间戳列表、加速度列表
    输出：速度列表、位移列表
    """
    velocities = []
    displacements = []

    last_time = timestamps[0]
    velocity = 0.0
    displacement = 0.0

    for t, a in zip(timestamps, accelerations):
        dt = t - last_time

        if is_zero_velocity(a):
            drift = update_drift_estimator(axis, a)
            velocity = 0.0  # 零速修正
        else:
            drift = update_drift_estimator(axis, a)
            corrected_a = a - drift
            velocity += corrected_a * dt  # 简单矩形积分（可升级 cumtrapz）

        displacement += velocity * dt

        velocities.append(velocity)
        displacements.append(displacement)

        last_time = t

    return velocities, displacements

def process_motion_data():
    """主处理函数：根据当前加速度数据更新速度和位移"""

    # 处理 X 轴
    vx, dx = compute_velocity_and_displacement(acc_x_data, timestamps, axis='x')
    velocity_x_data.extend(vx)
    displacement_x_data.extend(dx)

    # 处理 Y 轴
    vy, dy = compute_velocity_and_displacement(acc_y_data, timestamps, axis='y')
    velocity_y_data.extend(vy)
    displacement_y_data.extend(dy)

    # 处理 Z 轴
    vz, dz = compute_velocity_and_displacement(acc_z_data, timestamps, axis='z')
    velocity_z_data.extend(vz)
    displacement_z_data.extend(dz)

    # 控制缓存长度
    for lst in [
        velocity_x_data, velocity_y_data, velocity_z_data,
        displacement_x_data, displacement_y_data, displacement_z_data
    ]:
        while len(lst) > MAX_POINTS:
            lst.pop(0)