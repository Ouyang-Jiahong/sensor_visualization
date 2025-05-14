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

def GetDeviceData():
    """
    模拟绑定在杠铃上的IMU传感器数据。
    返回包含时间戳、加速度、角速度、姿态角的数据对象。
    """
    time.sleep(0.01)
    timestamp = time.time()

    # 加速度
    acc_base = [0.0, 0.0, 9.8]
    vibration = np.random.normal(0, 0.1, size=3)
    acc = np.array(acc_base) + vibration

    # 角速度
    base_gyro = [0.0, 2.0 * math.sin(timestamp), 0.0]
    gyro_noise = np.random.normal(0, 0.1, size=3)
    gyro = np.array(base_gyro) + gyro_noise

    # 姿态角
    roll = 0.0
    pitch = -1.0 * math.cos(timestamp)
    yaw = 0.0

    return SensorData(
        timestamp=timestamp,
        acc_x=acc[0], acc_y=acc[1], acc_z=acc[2],
        gyro_x=gyro[0], gyro_y=gyro[1], gyro_z=gyro[2],
        roll=roll, pitch=pitch, yaw=yaw
    )