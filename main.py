# main.py
import sys
import threading
import plot_manager
import asyncio
from device_data import SensorData
from bleak import BleakScanner
from data_buffer import update_buffers
from device_model import DeviceModel

def start_ble_device(mac_address: str):
    async def _runner():
        print(f"正在连接设备（最长20s响应时间）: {mac_address}")
        ble_device = await BleakScanner.find_device_by_address(mac_address, timeout=20)
        if ble_device is None:
            print(f"没有找到设备：{mac_address}")
            return
        device = DeviceModel("蓝牙传感器", ble_device, on_data_received)
        await device.openDevice()
    def _thread_entry():
        asyncio.run(_runner())

    thread = threading.Thread(target=_thread_entry, daemon=True)
    thread.start()

    print("等待传感器数据接入...")
    if not device_ready.wait(timeout=30):
        print("设备数据未接入，程序终止。")
        sys.exit(1)  # 终止整个程序
    
def on_data_received(device):
    update_callback(device)
    update_buffers(latest_sensor_data)
    if not device_ready.is_set():
        device_ready.set()

def update_callback(device: DeviceModel):
    global latest_sensor_data
    latest_sensor_data = SensorData(
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


## 线程启动 ##
device_ready = threading.Event()
start_ble_device("D9:7C:FB:58:D8:C2") # 启动蓝牙设备，启动后会自动启动数据采集线程（填入你的传感器 MAC 地址）
plot_manager.run_plot() # 启动绘图窗口

# main.py 开始运行
#    ↓
# 创建 device_ready = threading.Event()
#    ↓
# start_ble_device(...) 启动异步连接线程
#    ↓
# 主线程执行 device_ready.wait(timeout=30) → 阻塞等待
#    ↓
# BLE 设备连接成功，开始接收数据
#    ↓
# on_data_received(...) 被调用
#    ↓
# device_ready.set() → 主线程继续运行
#    ↓
# 启动 plot_manager.run_plot()