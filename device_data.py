# device_data.py
import time
from dataclasses import dataclass

from data_buffer import update_buffers
from device_model import DeviceModel
import asyncio
import threading
from threading import Event

device_ready = Event()

def on_data_received(device):
    update_callback(device)
    update_buffers(latest_sensor_data)
    print(latest_sensor_data)
    if not device_ready.is_set():
        device_ready.set()

@dataclass
class SensorData:
    timestamp: float
    acc_x: float
    acc_y: float
    acc_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    roll: float
    pitch: float
    yaw: float

# 全局变量
# 初始化 latest_sensor_data 为 None
latest_sensor_data = None

def update_sensor_data(new_data):
    global latest_sensor_data
    latest_sensor_data = new_data

device_ready = threading.Event()

def update_callback(device: DeviceModel):
    timestamp = time.time()
    global latest_sensor_data
    latest_sensor_data = SensorData(
        timestamp=timestamp,
        acc_x=device.get("AccX") or 0.0,
        acc_y=device.get("AccY") or 0.0,
        acc_z=device.get("AccZ") or 0.0,
        gyro_x=device.get("AsX") or 0.0,
        gyro_y=device.get("AsY") or 0.0,
        gyro_z=device.get("AsZ") or 0.0,
        roll=device.get("AngX") or 0.0,
        pitch=device.get("AngY") or 0.0,
        yaw=device.get("AngZ") or 0.0
    )
    device_ready.set()

# device_data.py
def start_ble_device(mac_address: str):
    async def _runner():
        from bleak import BleakScanner
        print(f"Connecting to device: {mac_address}")
        ble_device = await BleakScanner.find_device_by_address(mac_address, timeout=20)
        if ble_device is None:
            print("Device not found")
            return

        device = DeviceModel("RealIMU", ble_device, on_data_received)

        await device.openDevice()

    def _thread_entry():
        asyncio.run(_runner())

    thread = threading.Thread(target=_thread_entry, daemon=True)
    thread.start()


def GetDeviceData() -> SensorData:
    """
    与 sensor_data.py 同接口：获取最新真实传感器数据。
    """
    if device_ready.wait(timeout=5.0):
        return latest_sensor_data
    else:
        print("No sensor data received yet.")
        return None
