# sensor_data.py
import math
import time
from dataclasses import dataclass
import numpy as np

@dataclass
class SensorData:
    timestamp: float
    acc_x: float
    acc_y: float
    acc_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    roll: float
    pitch: float
    yaw: float

start_time = time.time()

def GetDeviceData():
    """
    模拟绑定在杠铃上的IMU传感器数据。
    acc_z 分阶段模拟深蹲的竖直加速度变化，不使用正弦波。
    """
    time.sleep(0.01)
    timestamp = time.time()
    base_time = timestamp - start_time

    g = 0  # 重力加速度
    cycle = 6.0
    t = base_time % cycle

    # 模拟 acc_z（竖直加速度）的变化
    if t < 0.5:
        acc_z = g + np.random.normal(0, 0.02)  # 静止准备
    elif t < 2.0:
        acc_z = g - np.random.uniform(0.5, 1.8) + np.random.normal(0, 0.05)  # 下蹲加速
    elif t < 3.0:
        acc_z = g + np.random.normal(0, 0.02)  # 底部静止
    elif t < 4.5:
        acc_z = g + np.random.uniform(0.5, 1.5) + np.random.normal(0, 0.05)  # 起身加速
    else:
        acc_z = g + np.random.normal(0, 0.02)  # 回到静止

    # 水平方向加速度：小幅扰动
    acc_x = np.random.normal(0, 0.02)
    acc_y = np.random.normal(0, 0.02)

    # 角速度：微小扰动
    gyro = np.random.normal(0, 0.01, size=3)

    # 姿态角：暂时设为静止
    roll = pitch = yaw = 0.0

    return SensorData(
        timestamp=timestamp,
        acc_x=acc_x, acc_y=acc_y, acc_z=acc_z,
        gyro_x=gyro[0], gyro_y=gyro[1], gyro_z=gyro[2],
        roll=roll, pitch=pitch, yaw=yaw
    )

