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
    返回包含时间戳、加速度、角速度、姿态角的数据对象。
    加速度每3秒波动一次，然后静止3秒，循环往复。
    """
    time.sleep(0.01)
    timestamp = time.time()
    base_time = timestamp - start_time

    # 波动状态判断（每6秒一个周期）
    cycle = 6.0
    within_cycle = base_time % cycle
    is_vibrating = within_cycle < 3.0  # 前3秒波动，后3秒静止

    # 加速度
    acc_base = [0.0, 0.0, 0.0]
    if is_vibrating:
        vibration = np.random.normal(0, 1, size=3)
        acc = np.array(acc_base) + vibration
    else:
        acc = np.array(acc_base)

    # 角速度
    base_gyro = [0.0, 0.0, 0.0]
    gyro_noise = np.random.normal(0, 0.0, size=3)
    gyro = np.array(base_gyro) + gyro_noise

    # 姿态角
    roll = 0.0
    pitch = 0.0
    yaw = 0.0

    return SensorData(
        timestamp=timestamp,
        acc_x=acc[0], acc_y=acc[1], acc_z=acc[2],
        gyro_x=gyro[0], gyro_y=gyro[1], gyro_z=gyro[2],
        roll=roll, pitch=pitch, yaw=yaw
    )
