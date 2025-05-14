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
from data_collector import data_queue
from motion_processor import process_motion_data

def safe_slice(data_list):
    return data_list[-MAX_POINTS:]

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
            plot.setLabel('bottom', 'Samples (Last 6s)')
            plot.addLegend()
            plot.setXRange(0, MAX_POINTS)
            plot.setYRange(*y_ranges[title])
            layout.addWidget(plot)
            self.plots.append(plot)

            for key, color in zip(keys, colors):
                pen = pg.mkPen(color=color, width=2)
                curve = plot.plot(pen=pen, name=key.upper())
                self.curves[key] = curve

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(10)

    def update_data(self):
        while not data_queue.empty():
            data = data_queue.get()
            update_buffers(data)
            process_motion_data()

        self.curves['acc_x'].setData(safe_slice(acc_x_data))
        self.curves['acc_y'].setData(safe_slice(acc_y_data))
        self.curves['acc_z'].setData(safe_slice(acc_z_data))

        self.curves['gyro_x'].setData(safe_slice(gyro_x_data))
        self.curves['gyro_y'].setData(safe_slice(gyro_y_data))
        self.curves['gyro_z'].setData(safe_slice(gyro_z_data))

        self.curves['roll'].setData(safe_slice(roll_data))
        self.curves['pitch'].setData(safe_slice(pitch_data))
        self.curves['yaw'].setData(safe_slice(yaw_data))

        self.curves['vel_x'].setData(safe_slice(velocity_x_data))
        self.curves['vel_y'].setData(safe_slice(velocity_y_data))
        self.curves['vel_z'].setData(safe_slice(velocity_z_data))

        self.curves['disp_x'].setData(safe_slice(displacement_x_data))
        self.curves['disp_y'].setData(safe_slice(displacement_y_data))
        self.curves['disp_z'].setData(safe_slice(displacement_z_data))

def run_plot():
    app = QtWidgets.QApplication(sys.argv)
    window = RealTimePlotWindow()
    window.show()
    sys.exit(app.exec_())
