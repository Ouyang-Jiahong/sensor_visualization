import sys
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
import pyqtgraph.opengl as gl  # 用于 3D 绘图

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

    # === 创建一个 OpenGL 的 3D 窗口 ===
    win_3d = gl.GLViewWidget()
    win_3d.setWindowTitle('3D Trajectory')
    win_3d.setGeometry(100, 100, 800, 600)
    win_3d.show()

    # 设置坐标系网格
    grid = gl.GLGridItem()
    grid.scale(0.5, 0.5, 0.5)  # 可调整缩放比例
    win_3d.addItem(grid)

    # 初始化轨迹线对象
    path_data = np.zeros((1, 3))
    trajectory = gl.GLLinePlotItem(pos=path_data, color=(1, 0, 0, 1), width=2, antialias=True)
    win_3d.addItem(trajectory)

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

        # 获取最新的 x, y, z 值
        latest_x = displacement_x_data[-1]
        latest_y = displacement_y_data[-1]
        latest_z = displacement_z_data[-1]

        # 判断最新点是否是“异常接近于 0”的情况
        threshold = 1e-5  # 可根据实际数据调整这个阈值
        if abs(latest_x) < threshold and abs(latest_y) < threshold and abs(latest_z) < threshold:
            print("Skipping update: latest point is close to (0, 0, 0)")
        else:
            # 合并成 Nx3 数组
            path = np.column_stack((
                displacement_x_data,
                displacement_y_data,
                displacement_z_data
            )).astype(np.float32)

            # 检查 NaN/Inf 并替换为 0
            if np.isnan(path).any() or np.isinf(path).any():
                path = np.nan_to_num(path, nan=0.0, posinf=0.0, neginf=0.0)

            # 检查整个路径是否全是 0
            if np.allclose(path, 0):
                print("Warning: All zeros in path data, skipping update.")
            else:
                print("Updating trajectory with shape:", path.shape)
                try:
                    # 注意：GLLinePlotItem 接受 (N, 3)，通常不需要 .T
                    trajectory.setData(pos=path)
                except Exception as e:
                    print("Error setting trajectory data:", str(e))


        # trajectory.setData(pos=path.T)

    # 启动定时器
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(UPDATE_INTERVAL)

    # 运行主循环
    sys.exit(app.exec_())