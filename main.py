# main.py
import sys
import threading
import time
from data_collector import collector_thread
import plot_manager

USE_REAL_SENSOR = True

def init_ble():
    import device_data as sensor_interface
    sensor_interface.start_ble_device("D9:7C:FB:58:D8:C2")

    print("等待传感器数据接入...")
    if not sensor_interface.device_ready.wait(timeout=30):
        print("设备数据未接入，程序终止。")
        sys.exit(1)  # 终止整个程序

if USE_REAL_SENSOR:
    ble_thread = threading.Thread(target=init_ble, daemon=True)
    ble_thread.start()
else:
    import sensor_data as sensor_interface

# 启动数据采集线程（从 device_data 或 sensor_data 中收数据）
collector_thread.start()

# 启动绘图窗口（非阻塞主线程）
plot_manager.run_plot()
