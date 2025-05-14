# data_collector.py
import threading
import queue
import sensor_data

data_queue = queue.Queue()

def data_collector():
    while True:
        data = sensor_data.GetDeviceData()
        data_queue.put(data)

collector_thread = threading.Thread(target=data_collector, daemon=True)