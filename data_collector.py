# data_collector.py
import threading
import queue
from sensor_data import GetDeviceData

data_queue = queue.Queue()

def data_collector():
    while True:
        data = GetDeviceData()
        data_queue.put(data)

collector_thread = threading.Thread(target=data_collector, daemon=True)