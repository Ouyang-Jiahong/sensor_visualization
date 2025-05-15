import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets
import sys

from data_buffer import (
    acc_x_data, acc_y_data, acc_z_data,
    gyro_x_data, gyro_y_data, gyro_z_data,
    roll_data, pitch_data, yaw_data,
    velocity_x_data, velocity_y_data, velocity_z_data,
    displacement_x_data, displacement_y_data, displacement_z_data, update_buffers, MAX_POINTS
)
from motion_processor import process_motion_data

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
            ("Angular Velocity (rad/s)", ['gyro_x', 'gyro_y', 'gyro_z']),
            ("Orientation (rad)", ['roll', 'pitch', 'yaw']),
            ("Velocity (m/s)", ['vel_x', 'vel_y', 'vel_z']),
            ("Displacement (m)", ['disp_x', 'disp_y', 'disp_z']),
        ]

        y_ranges = {
            "Acceleration (m/s²)": [-3, 3],
            "Angular Velocity (rad/s)": [-1, 1],
            "Orientation (rad)": [-np.pi, np.pi],
            "Velocity (m/s)": [-2, 2],
            "Displacement (m)": [-2, 2]
        }

        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

        for title, keys in plot_titles:
            plot = pg.PlotWidget(title=title)
            plot.setLabel('left', 'Value')
            plot.setLabel('bottom', 'Time (s)')  # 修改标签为时间
            plot.addLegend()
            plot.setXRange(0, 6)  # 设置 x 轴范围为 0 - 6
            plot.setYRange(*y_ranges[title])
            layout.addWidget(plot)
            self.plots.append(plot)

            for key, color in zip(keys, colors):
                pen = pg.mkPen(color=color, width=2)
                curve = plot.plot(pen=pen, name=key.upper())
                self.curves[key] = curve

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(50)

    def update_data(self):
        self.curves['acc_x'].setData(acc_x_data)
        self.curves['acc_y'].setData(acc_y_data)
        self.curves['acc_z'].setData(acc_z_data)

        self.curves['gyro_x'].setData(gyro_x_data)
        self.curves['gyro_y'].setData(gyro_y_data)
        self.curves['gyro_z'].setData(gyro_z_data)

        self.curves['roll'].setData(roll_data)
        self.curves['pitch'].setData(pitch_data)
        self.curves['yaw'].setData(yaw_data)

        self.curves['vel_x'].setData(velocity_x_data)
        self.curves['vel_y'].setData(velocity_y_data)
        self.curves['vel_z'].setData(velocity_z_data)

        self.curves['disp_x'].setData(displacement_x_data)
        self.curves['disp_y'].setData(displacement_y_data)
        self.curves['disp_z'].setData(displacement_z_data)

def run_plot():
    app = QtWidgets.QApplication(sys.argv)
    window = RealTimePlotWindow()
    window.show()
    sys.exit(app.exec_())