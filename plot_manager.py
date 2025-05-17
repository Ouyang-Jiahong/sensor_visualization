import sys
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore

# 导入数据缓冲区（必须保证 data_buffer.py 在同一目录下）
from data_buffer import (
    acc_x_data, acc_y_data, acc_z_data,
    gyro_x_data, gyro_y_data, gyro_z_data,
    roll_data, pitch_data, yaw_data,
    velocity_x_data, velocity_y_data, velocity_z_data,
    displacement_x_data, displacement_y_data, displacement_z_data,
)

# 设置刷新频率（毫秒）
UPDATE_INTERVAL = 5

def run_plot():
    app = QtWidgets.QApplication(sys.argv)

    # 创建主窗口
    win = pg.GraphicsLayoutWidget(show=True, title="IMU 实时绘图 - 极简模式")
    win.resize(1200, 800)

    # 创建多个子图
    p_acc = win.addPlot(row=0, col=0, title="Acceleration (m/s²)")
    p_vel = win.addPlot(row=2, col=0, title="Velocity (m/s)")
    p_disp = win.addPlot(row=3, col=0, title="Displacement (m)")

    # 曲线对象
    curve_acc_x = p_acc.plot(pen='r', name="X")
    curve_acc_y = p_acc.plot(pen='g', name="Y")
    curve_acc_z = p_acc.plot(pen='b', name="Z")

    curve_vel_x = p_vel.plot(pen='r')
    curve_vel_y = p_vel.plot(pen='g')
    curve_vel_z = p_vel.plot(pen='b')

    curve_disp_x = p_disp.plot(pen='r')
    curve_disp_y = p_disp.plot(pen='g')
    curve_disp_z = p_disp.plot(pen='b')

    # 定时更新函数
    def update():
        # 加速度
        curve_acc_x.setData(acc_x_data[-600:])
        curve_acc_y.setData(acc_y_data[-600:])
        curve_acc_z.setData(acc_z_data[-600:])

        # 速度
        curve_vel_x.setData(velocity_x_data[-600:])
        curve_vel_y.setData(velocity_y_data[-600:])
        curve_vel_z.setData(velocity_z_data[-600:])

        # 位移
        curve_disp_x.setData(displacement_x_data[-600:])
        curve_disp_y.setData(displacement_y_data[-600:])
        curve_disp_z.setData(displacement_z_data[-600:])

    # 启动定时器
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(UPDATE_INTERVAL)

    # 运行主循环
    sys.exit(app.exec_())