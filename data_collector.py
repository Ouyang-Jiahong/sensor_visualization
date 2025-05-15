# data_collector.py
import threading

import device_data

device_data.start_ble_device("D9:7C:FB:58:D8:C2")  # 填入你的传感器 MAC 地址
collector_thread = threading.Thread(target=device_data.on_data_received, daemon=True)