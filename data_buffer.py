# data_buffer.py
import numpy as np
from device_model import dt

MAX_POINTS = 600
# 初始化数据缓冲区
acc_x_data = []; acc_y_data = []; acc_z_data = []
gyro_x_data = []; gyro_y_data = []; gyro_z_data = []
roll_data = []; pitch_data = []; yaw_data = []
velocity_x_data = []; velocity_y_data = []; velocity_z_data = []
displacement_x_data = []; displacement_y_data = []; displacement_z_data = []

def is_zero_velocity(acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z):
    # 角速度阈值（degree/s）: 判断是否旋转
    GYRO_THRESHOLD = 5

    # 加速度扰动阈值：判断是否受运动干扰
    ACC_VARIANCE_THRESHOLD = 0.05  # 小幅抖动视为静止

    # 计算角速度模长
    gyro_magnitude = np.sqrt(gyro_x**2 + gyro_y**2 + gyro_z**2)

    # 计算加速度与重力方向的偏差（即去重后的加速度大小）
    # pure_acc = a - g_sensor 已经在 update_buffers 中计算过了
    # 所以这里简化为使用原始加速度向量模长判断（也可以更精确地用纯加速度）

    acc = np.sqrt(acc_x**2 + acc_y**2 + acc_z**2)

    # 判断逻辑
    if gyro_magnitude < GYRO_THRESHOLD and acc < ACC_VARIANCE_THRESHOLD:
        return True  # 零速状态
    else:
        return False

### 更新原始IMU数据到缓冲区 ###
def update_buffers(data):
    absolute_acc = remove_gravity(data.acc_x, data.acc_y, data.acc_z, data.roll, data.pitch, data.yaw) # 将视加速度转化为传感器质心在地惯系下的绝对加速度
    acc_x_data.append(absolute_acc[0]); acc_y_data.append(absolute_acc[1]); acc_z_data.append(absolute_acc[2])
    gyro_x_data.append(data.gyro_x); gyro_y_data.append(data.gyro_y); gyro_z_data.append(data.gyro_z)
    zero_vel = is_zero_velocity(acc_x_data[-1], acc_y_data[-1], acc_z_data[-1], gyro_x_data[-1], gyro_y_data[-1], gyro_z_data[-1])
    # 梯形积分计算速度
    if len(velocity_x_data) == 0:
        vx, vy, vz = 0.0, 0.0, 0.0
    else:
        dvx = (acc_x_data[-1] + acc_x_data[-2]) * dt / 2; dvy = (acc_y_data[-1] + acc_y_data[-2]) * dt / 2; dvz = (acc_z_data[-1] + acc_z_data[-2]) * dt /2 # 梯形积分
        vx = velocity_x_data[-1] + dvx; vy = velocity_y_data[-1] + dvy; vz = velocity_z_data[-1] + dvz # 速度累加
    if zero_vel:
        velocity_x_data.append(0); velocity_y_data.append(0); velocity_z_data.append(0)
    else:
        velocity_x_data.append(vx); velocity_y_data.append(vy); velocity_z_data.append(vz)

    # 再次积分计算位移
    if len(displacement_x_data) == 0:
        x, y, z = 0.0, 0.0, 0.0
    else:
        dx = (velocity_x_data[-2] + velocity_x_data[-1]) * dt / 2; dy = (velocity_y_data[-2] + velocity_y_data[-1]) * dt / 2; dz = (velocity_z_data[-2] + velocity_z_data[-1]) * dt / 2
        x = displacement_x_data[-1] + dx; y = displacement_y_data[-1] + dy; z = displacement_z_data[-1] + dz
    displacement_x_data.append(x); displacement_y_data.append(y); displacement_z_data.append(z)

    
def remove_gravity(acc_x, acc_y, acc_z, roll_deg, pitch_deg, yaw_deg):
    # 姿态角结算时所使用的坐标系为东北天坐标系，定义为为 Z-Y-X,即先绕 Z 轴转，再绕 Y 轴转，再绕 X 轴转。
    g = 1
    roll = np.radians(roll_deg); pitch = np.radians(pitch_deg); yaw = np.radians(yaw_deg)
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
    absolute_acc = R @ pure_acc
    return absolute_acc