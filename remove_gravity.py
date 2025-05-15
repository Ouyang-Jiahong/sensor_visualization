# remove_gravity.py
import numpy as np

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
    g = 0.981  # 重力加速度常数
    # 将角度从度转换为弧度
    roll = np.radians(roll_deg)
    pitch = np.radians(pitch_deg)
    yaw = np.radians(yaw_deg)

    # 构建重力矢量在世界坐标系下
    gravity_world = np.array([0, 0, g])

    # 构造旋转矩阵（ZXY顺序）
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

    # 总旋转矩阵（从世界坐标系到传感器坐标系）
    R = R_z @ R_y @ R_x

    # 将重力从世界坐标系转换到传感器坐标系
    gravity_sensor = R.T @ gravity_world

    # 构建加速度向量
    acc = np.array([acc_x, acc_y, acc_z])

    # 减去重力得到纯加速度
    return acc - gravity_sensor