import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
import sys
import time

# 从 data_buffer 导入数据和配置
from data_buffer import (
    acc_x_data, acc_y_data, acc_z_data,
    gyro_x_data, gyro_y_data, gyro_z_data,
    roll_data, pitch_data, yaw_data,
    velocity_x_data, velocity_y_data, velocity_z_data,
    displacement_x_data, displacement_y_data, displacement_z_data,
    timestamps, MAX_POINTS
)

class RealTimePlotWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMU Real-time Plot (Last 6s)")
        self.resize(1000, 800)
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        self.plots = []
        self.curves = {}

        plot_titles = [
            ("Acceleration (m/s²)", ['acc_x', 'acc_y', 'acc_z']),
            ("Orientation (rad)", ['roll', 'pitch', 'yaw']),
            ("Velocity (m/s)", ['vel_x', 'vel_y', 'vel_z']),
            ("Displacement (m)", ['disp_x', 'disp_y', 'disp_z']),
        ]

        y_ranges = {
            "Acceleration (m/s²)": [-3, 3],
            "Orientation (degree)": [-180, 180],
            "Velocity (m/s)": [-5, 5],
            "Displacement (m)": [-5, 5]
        }

        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

        for title, keys in plot_titles:
            plot = pg.PlotWidget(title=title)
            plot.setLabel('left', 'Value')
            plot.setLabel('bottom', 'Time (s)')
            plot.addLegend()
            plot.setXRange(-6, 0)  # 显示最近6秒
            if title in y_ranges:
                plot.setYRange(*y_ranges[title])
            layout.addWidget(plot)
            self.plots.append(plot)
            for key, color in zip(keys, colors):
                pen = pg.mkPen(color=color, width=2)
                curve = plot.plot(pen=pen, name=key.upper())
                self.curves[key] = curve

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(50)  # 每50ms刷新一次

    def update_data(self):
        now = time.time()
        indices = [i for i, t in enumerate(timestamps) if now - t <= 6]

        if not indices:
            return

        time_axis = [t - now for t in timestamps if now - t <= 6]

        def get_data(data_list):
            return [data_list[i] for i in indices]

        # 更新加速度
        self.curves['acc_x'].setData(time_axis, get_data(acc_x_data))
        self.curves['acc_y'].setData(time_axis, get_data(acc_y_data))
        self.curves['acc_z'].setData(time_axis, get_data(acc_z_data))

        # 更新姿态角
        self.curves['roll'].setData(time_axis, get_data(roll_data))
        self.curves['pitch'].setData(time_axis, get_data(pitch_data))
        self.curves['yaw'].setData(time_axis, get_data(yaw_data))

        # 更新速度
        self.curves['vel_x'].setData(time_axis, get_data(velocity_x_data))
        self.curves['vel_y'].setData(time_axis, get_data(velocity_y_data))
        self.curves['vel_z'].setData(time_axis, get_data(velocity_z_data))

        # 更新位移
        self.curves['disp_x'].setData(time_axis, get_data(displacement_x_data))
        self.curves['disp_y'].setData(time_axis, get_data(displacement_y_data))
        self.curves['disp_z'].setData(time_axis, get_data(displacement_z_data))


def run_plot():
    app = QtWidgets.QApplication(sys.argv)
    window = RealTimePlotWindow()
    window.show()
    sys.exit(app.exec_())