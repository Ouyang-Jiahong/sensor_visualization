# data_buffer.py

MAX_POINTS = 200

# 初始化数据缓冲区
acc_x_data = []
acc_y_data = []
acc_z_data = []

gyro_x_data = []
gyro_y_data = []
gyro_z_data = []

roll_data = []
pitch_data = []
yaw_data = []

velocity_x_data = []
velocity_y_data = []
velocity_z_data = []

displacement_x_data = []
displacement_y_data = []
displacement_z_data = []

timestamps = []

def update_buffers(data):
    """更新缓冲区"""
    timestamps.append(data.timestamp)
    
    acc_x_data.append(data.acc_x)
    acc_y_data.append(data.acc_y)
    acc_z_data.append(data.acc_z)

    gyro_x_data.append(data.gyro_x)
    gyro_y_data.append(data.gyro_y)
    gyro_z_data.append(data.gyro_z)

    roll_data.append(data.roll)
    pitch_data.append(data.pitch)
    yaw_data.append(data.yaw)

    # 控制缓存长度
    if len(acc_x_data) > MAX_POINTS:
        timestamps.pop(0)
        acc_x_data.pop(0)
        acc_y_data.pop(0)
        acc_z_data.pop(0)
        gyro_x_data.pop(0)
        gyro_y_data.pop(0)
        gyro_z_data.pop(0)
        roll_data.pop(0)
        pitch_data.pop(0)
        yaw_data.pop(0)
        velocity_x_data.pop(0)
        velocity_y_data.pop(0)
        velocity_z_data.pop(0)
        displacement_x_data.pop(0)
        displacement_y_data.pop()
        displacement_z_data.pop(0)