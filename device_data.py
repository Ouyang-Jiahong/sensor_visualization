# device_data.py
# 声明数据结构变量、中间变量
from dataclasses import dataclass

@dataclass
class SensorData:
    acc_x: float
    acc_y: float
    acc_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    roll: float
    pitch: float
    yaw: float

# 全局变量
latest_sensor_data = None