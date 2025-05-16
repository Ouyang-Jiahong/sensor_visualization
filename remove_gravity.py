# remove_gravity.py
import numpy as np

# 传感器协议：
#  1. 姿态角结算时所使用的坐标系为东北天坐标系，正方向放置模块,如“4 引脚说明” 
#  所示向左为 X 轴，向前为 Y 轴，向上为 Z 轴。欧拉角表示姿态时的坐标系旋转顺序 
#  定义为为 Z-Y-X,即先绕 Z 轴转，再绕 Y 轴转，再绕 X 轴转。 
#  2. 滚转角的范围虽然是±180 度，但实际上由于坐标旋转顺序是 Z-Y-X，在表示姿态 
#  的时候，俯仰角(Y 轴)的范围只有±90 度，超过 90 度后会变换到小于 90 度，同时 
#  让X轴的角度大于180度。详细原理请大家自行百度欧拉角及姿态表示的相关信息。 
#  3. 由于三轴是耦合的，只有在小角度的时候会表现出独立变化，在大角度的时候姿态 
#  角度会耦合变化，比如当 Y 轴接近 90 度时，即使姿态只绕 Y 轴转动，X 轴的角度 

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