# 传感器运动数据处理系统

## 功能概述
本系统专注于处理传感器采集的运动数据。借助对加速度数据开展积分运算，系统能够精确计算出速度和位移。同时，系统会对加速度漂移进行估计，并实施零速修正，以此提高计算的精度。此外，系统还具备数据缓存管理功能，防止数据量过大导致内存问题。

## 项目结构
```plaintext
sensor_visualization/
├── data_buffer.py     # 定义数据缓存和相关更新函数，包含时间戳、加速度、速度和位移数据列表
├── motion_processor.py # 核心运动数据处理模块，负责漂移估计、积分计算和数据更新
├── ...                # 其他可能存在的文件
```

## 代码详细说明

### `motion_processor.py`
此文件涵盖了运动数据处理的核心逻辑，下面是各部分的详细阐释：

#### 导入模块
```python:d:\Code\sensor_visualization\motion_processor.py
import time
from data_buffer import timestamps, MAX_POINTS, update_velocity, update_displacement
from data_buffer import (
    acc_x_data, acc_y_data, acc_z_data,
    velocity_x_data, velocity_y_data, velocity_z_data,
    displacement_x_data, displacement_y_data, displacement_z_data
)
import numpy as np
```
- `time`：用于处理与时间相关的操作。
- `data_buffer`：自定义模块，提供数据缓存和更新函数。
- `numpy`：用于高效的数值计算。

#### 参数设置
```python:d:\Code\sensor_visualization\motion_processor.py
ZERO_SPEED_THRESHOLD = 0.15     # 静止判断阈值 (m/s²)
```
该阈值用于判定物体是否处于静止状态。

#### 漂移估计初始化
```python:d:\Code\sensor_visualization\motion_processor.py
drift_x = 0
drift_y = 0
drift_z = 0
```
对三个方向的加速度漂移量进行初始化。

#### 辅助函数
- `is_zero_velocity(acc)`：判断物体是否处于静止状态。
```python:d:\Code\sensor_visualization\motion_processor.py
def is_zero_velocity(acc):
    """简单判断是否处于静止状态"""
    return abs(acc) < ZERO_SPEED_THRESHOLD
```
- `update_drift(drift, acc)`：依据静止阶段的数据来估计漂移量，采用简单的指数加权平均方法。
```python:d:\Code\sensor_visualization\motion_processor.py
def update_drift(drift, acc):
    """根据静止阶段的数据估计漂移量"""
    if is_zero_velocity(acc):
        drift = 0.9 * drift + 0.1 * acc  # 简单的指数加权平均
    return drift
```
- `compute_integration(timestamps, accelerations, drift)`：输入时间戳、加速度列表和漂移量，输出速度和位移。通过修正加速度、计算时间间隔并进行积分运算得到结果，同时进行零速修正。
```python:d:\Code\sensor_visualization\motion_processor.py
def compute_integration(timestamps, accelerations, drift):
    """
    输入：时间戳列表、加速度列表、漂移量
    输出：速度、位移
    """
    if len(timestamps) < 2:        
        return 0, 0

    # 修正加速度
    corrected_acc = np.array(accelerations) - drift

    # 计算时间间隔
    dt = np.diff(timestamps)

    # 积分计算速度
    velocity = np.sum(corrected_acc[:-1] * dt)

    # 零速修正
    if is_zero_velocity(np.mean(accelerations)):
        velocity = 0

    # 积分计算位移
    displacement = np.sum(velocity * dt)

    return velocity, displacement
```

#### 主处理函数
```python:d:\Code\sensor_visualization\motion_processor.py
def process_motion_data():
    """主处理函数：根据当前加速度数据更新速度和位移"""
    global drift_x, drift_y, drift_z

    # 更新漂移估计
    drift_x = update_drift(drift_x, acc_x_data[-1])
    drift_y = update_drift(drift_y, acc_y_data[-1])
    drift_z = update_drift(drift_z, acc_z_data[-1])

    # 计算积分
    vx, dx = compute_integration(timestamps, acc_x_data, drift_x)
    vy, dy = compute_integration(timestamps, acc_y_data, drift_y)
    vz, dz = compute_integration(timestamps, acc_z_data, drift_z)

    update_velocity(vx, vy, vz)
    update_displacement(dx, dy, dz)

    # 控制缓存长度
    for lst in [
        velocity_x_data, velocity_y_data, velocity_z_data,
        displacement_x_data, displacement_y_data, displacement_z_data
    ]:
        while len(lst) > MAX_POINTS:
            lst.pop(0)
```
该函数是主处理函数，负责更新漂移估计、计算速度和位移，并更新数据缓存。

## 所需库
- `numpy`：用于数值计算。确保在运行代码前已经安装，可以使用以下命令安装：
```bash
pip install numpy
```

## 运行方式
1. 保证 `data_buffer.py` 文件存在，并且定义了所需的变量和函数。
2. 在终端中运行包含调用 `process_motion_data()` 函数的脚本，例如：
```python
from motion_processor import process_motion_data

if __name__ == "__main__":
    process_motion_data()
    print("运动数据处理完成")
```
将上述代码保存为一个新的 Python 文件（如 `run.py`），然后在终端中运行：
```bash
python run.py
```