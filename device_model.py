# device_model.py
import threading
import time
import struct
import bleak
import asyncio

dt = 0.005

# 设备实例 Device instance
class DeviceModel:
    # region 属性 attribute
    # 设备名称 deviceName
    deviceName = "我的设备"

    # 设备数据字典 Device Data Dictionary
    deviceData = {}

    # 设备是否开启
    isOpen = False

    # 临时数组 Temporary array
    TempBytes = []

    # endregion

    def __init__(self, deviceName, BLEDevice, callback_method):
        # 设备名称（自定义） Device Name
        self.deviceName = deviceName
        self.BLEDevice = BLEDevice
        self.client = None
        self.writer_characteristic = None
        self.isOpen = False
        self.callback_method = callback_method
        self.deviceData = {}

    # region 获取设备数据 Obtain device data
    # 设置设备数据 Set device data
    def set(self, key, value):
        # 将设备数据存到键值 Saving device data to key values
        self.deviceData[key] = value

    # 获得设备数据 Obtain device data
    def get(self, key):
        # 从键值中获取数据，没有则返回None Obtaining data from key values
        if key in self.deviceData:
            return self.deviceData[key]
        else:
            return None

    # 删除设备数据 Delete device data
    def remove(self, key):
        # 删除设备键值
        del self.deviceData[key]

    # endregion

    # 打开设备 open Device
    async def openDevice(self):
        print("正在打开设备...")
        # 获取设备的服务和特征 Obtain the services and characteristic of the device
        async with bleak.BleakClient(self.BLEDevice, timeout=15) as client:
            self.client = client
            self.isOpen = True
            # 设备UUID常量 Device UUID constant
            target_service_uuid = "0000ffe5-0000-1000-8000-00805f9a34fb"
            target_characteristic_uuid_read = "0000ffe4-0000-1000-8000-00805f9a34fb"
            target_characteristic_uuid_write = "0000ffe9-0000-1000-8000-00805f9a34fb"
            notify_characteristic = None

            # print("Matching services......")
            for service in client.services:
                if service.uuid == target_service_uuid:
                    # print(f"Service: {service}")
                    # print("Matching characteristic......")
                    for characteristic in service.characteristics:
                        if characteristic.uuid == target_characteristic_uuid_read:
                            notify_characteristic = characteristic
                        if characteristic.uuid == target_characteristic_uuid_write:
                            self.writer_characteristic = characteristic
                    if notify_characteristic:
                        break

            if self.writer_characteristic:
                print("传感器初始化开始...")
                # self.set_algorithm_6axis()  # 设置为6轴算法
                self.set_algorithm_9axis()  # 设置为9轴算法
                # 设置传输速率
                if dt == 0.005:
                    self.set_transmission_rate200()  # 设置传输速率为200Hz
                    print("数据回传频率设置为 200 Hz")
                if dt == 0.01:
                    self.set_transmission_rate100()  # 设置传输速率为100Hz
                    print("数据回传频率设置为 100 Hz")
                # 可以继续添加其他配置
                print("传感器初始化完成！")
                # 开始定时读取数据
                print("设备打开完成！开始定时读取数据...")
                asyncio.create_task(self.sendDataTh())

            if notify_characteristic:
                # print("启动通知机制，当设备有新数据时会触发回调函数 onDataReceived")
                # print(f"Characteristic: {notify_characteristic}")
                # 设置通知以接收数据 Set up notifications to receive data
                await client.start_notify(notify_characteristic.uuid, self.onDataReceived)

                # 保持连接打开 Keep connected and open
                try:
                    while self.isOpen:
                        await asyncio.sleep(1)
                except asyncio.CancelledError:
                    pass
                finally:
                    # 在退出时停止通知 Stop notification on exit
                    await client.stop_notify(notify_characteristic.uuid)
            # else:
            #     print("No matching services or characteristic found")

    # 关闭设备  close Device
    def closeDevice(self):
        self.isOpen = False
        print("设备关闭！")

    async def sendDataTh(self):
        while self.isOpen:
            await self.readReg(0x3A)
            time.sleep(0.1)
            await self.readReg(0x51)
            time.sleep(0.1)

    # region 数据解析 data analysis
    # 串口数据处理  Serial port data processing
    def onDataReceived(self, sender, data):
        tempdata = bytes.fromhex(data.hex())
        for var in tempdata:
            self.TempBytes.append(var)
            if len(self.TempBytes) == 1 and self.TempBytes[0] != 0x55:
                del self.TempBytes[0]
                continue
            if len(self.TempBytes) == 2 and (self.TempBytes[1] != 0x61 and self.TempBytes[1] != 0x71):
                del self.TempBytes[0]
                continue
            if len(self.TempBytes) == 20:
                self.processData(self.TempBytes)
                self.TempBytes.clear()

    # 数据解析 data analysis
    def processData(self, Bytes):
        if Bytes[1] == 0x61:
            Ax = self.getSignInt16(Bytes[3] << 8 | Bytes[2]) / 32768 * 16
            Ay = self.getSignInt16(Bytes[5] << 8 | Bytes[4]) / 32768 * 16
            Az = self.getSignInt16(Bytes[7] << 8 | Bytes[6]) / 32768 * 16
            Gx = self.getSignInt16(Bytes[9] << 8 | Bytes[8]) / 32768 * 2000
            Gy = self.getSignInt16(Bytes[11] << 8 | Bytes[10]) / 32768 * 2000
            Gz = self.getSignInt16(Bytes[13] << 8 | Bytes[12]) / 32768 * 2000
            AngX = self.getSignInt16(Bytes[15] << 8 | Bytes[14]) / 32768 * 180
            AngY = self.getSignInt16(Bytes[17] << 8 | Bytes[16]) / 32768 * 180
            AngZ = self.getSignInt16(Bytes[19] << 8 | Bytes[18]) / 32768 * 180
            self.set("AccX", round(Ax, 9))
            self.set("AccY", round(Ay, 9))
            self.set("AccZ", round(Az, 9))
            self.set("AsX", round(Gx, 9))
            self.set("AsY", round(Gy, 9))
            self.set("AsZ", round(Gz, 9))
            self.set("AngX", round(AngX, 9))
            self.set("AngY", round(AngY, 9))
            self.set("AngZ", round(AngZ, 9))
            self.callback_method(self)
        else:
            # 磁场 magnetic field
            if Bytes[2] == 0x3A:
                Hx = self.getSignInt16(Bytes[5] << 8 | Bytes[4]) / 120
                Hy = self.getSignInt16(Bytes[7] << 8 | Bytes[6]) / 120
                Hz = self.getSignInt16(Bytes[9] << 8 | Bytes[8]) / 120
                self.set("HX", round(Hx, 9))
                self.set("HY", round(Hy, 9))
                self.set("HZ", round(Hz, 9))
            # 四元数 Quaternion
            elif Bytes[2] == 0x51:
                Q0 = self.getSignInt16(Bytes[5] << 8 | Bytes[4]) / 32768
                Q1 = self.getSignInt16(Bytes[7] << 8 | Bytes[6]) / 32768
                Q2 = self.getSignInt16(Bytes[9] << 8 | Bytes[8]) / 32768
                Q3 = self.getSignInt16(Bytes[11] << 8 | Bytes[10]) / 32768
                self.set("Q0", round(Q0, 9))
                self.set("Q1", round(Q1, 9))
                self.set("Q2", round(Q2, 9))
                self.set("Q3", round(Q3, 9))
            else:
                pass

    # 获得int16有符号数 Obtain int16 signed number
    @staticmethod
    def getSignInt16(num):
        if num >= pow(2, 15):
            num -= pow(2, 16)
        return num

    # endregion

    # 发送串口数据 Sending serial port data
    async def sendData(self, data):
        try:
            if self.client.is_connected and self.writer_characteristic is not None:
                await self.client.write_gatt_char(self.writer_characteristic.uuid, bytes(data))
        except Exception as ex:
            print(ex)

    # 读取寄存器 read register
    async def readReg(self, regAddr):
        # 封装读取指令并向串口发送数据 Encapsulate read instructions and send data to the serial port
        await self.sendData(self.get_readBytes(regAddr))

    # 写入寄存器 Write Register
    async def writeReg(self, regAddr, sValue):
        # 解锁 unlock
        self.unlock()
        # 封装写入指令并向串口发送数据
        await self.sendData(self.get_writeBytes(regAddr, sValue))
        # 延迟100ms Delay 100ms
        time.sleep(0.1)
        # 保存 save
        self.save()

    # 读取指令封装 Read instruction encapsulation
    @staticmethod
    def get_readBytes(regAddr):
        # 初始化
        tempBytes = [None] * 5
        tempBytes[0] = 0xff
        tempBytes[1] = 0xaa
        tempBytes[2] = 0x27
        tempBytes[3] = regAddr
        tempBytes[4] = 0
        return tempBytes

    # 写入指令封装 Write instruction encapsulation
    @staticmethod
    def get_writeBytes(regAddr, rValue):
        # 初始化
        tempBytes = [None] * 5
        tempBytes[0] = 0xff
        tempBytes[1] = 0xaa
        tempBytes[2] = regAddr
        tempBytes[3] = rValue & 0xff
        tempBytes[4] = rValue >> 8
        return tempBytes

    # 解锁 unlock
    def unlock(self):
        cmd = self.get_writeBytes(0x69, 0xb588)
        asyncio.create_task(self.sendData(cmd))

    # 保存 save
    def save(self):
        cmd = self.get_writeBytes(0x00, 0x0000)
        asyncio.create_task(self.sendData(cmd))

    # 设置回传速率为200Hz
    def set_transmission_rate200(self):
        cmd = self.get_writeBytes(0x03, 0x000B)
        asyncio.create_task(self.sendData(cmd))

    # 设置回传速率为100Hz
    def set_transmission_rate100(self):
        cmd = self.get_writeBytes(0x03, 0x0009)
        asyncio.create_task(self.sendData(cmd))

    # 设置姿态解算算法为 9轴（磁场解算航向角）
    def set_algorithm_9axis(self):
        cmd = self.get_writeBytes(0x24, 0x0000)
        asyncio.create_task(self.sendData(cmd))

    # 设置姿态解算算法为 6轴（积分解算航向角）
    def set_algorithm_6axis(self):
        cmd = self.get_writeBytes(0x24, 0x0001)
        asyncio.create_task(self.sendData(cmd))