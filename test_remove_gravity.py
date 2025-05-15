# test_remove_gravity.py
import numpy as np
from remove_gravity import remove_gravity

def test_remove_gravity_case():
    print("测试案例1：设备平放在桌面")
    acc_x = 0.0
    acc_y = 0.0
    acc_z = 9.81
    roll = 0.0
    pitch = 0.0
    yaw = 0.0
    corrected_acc = remove_gravity(acc_x, acc_y, acc_z, roll, pitch, yaw)
    print("期望值: [0.0, 0.0, 0.0]")
    print("实际值: ", corrected_acc)
    assert np.allclose(corrected_acc, [0.0, 0.0, 0.0], atol=1e-6), "测试失败！"

    print("\n测试案例2：设备倒置（翻转180度）")
    acc_x = 0.0
    acc_y = 0.0
    acc_z = -9.81
    roll = 180.0   # 设备完全倒置
    pitch = 0.0
    yaw = 0.0
    corrected_acc = remove_gravity(acc_x, acc_y, acc_z, roll, pitch, yaw)
    print("期望值: [0.0, 0.0, 0.0]")
    print("实际值: ", corrected_acc)
    assert np.allclose(corrected_acc, [0.0, 0.0, 0.0], atol=1e-6), "测试失败！"

    print("\n测试案例3：设备侧放，绕Y轴倾斜90度")
    acc_x = -9.81
    acc_y = 0.0
    acc_z = 0.0
    roll = 0.0
    pitch = 90.0   # 绕Y轴倾斜90度
    yaw = 0.0
    corrected_acc = remove_gravity(acc_x, acc_y, acc_z, roll, pitch, yaw)
    expected_gravity = [9.81, 0.0, 0.0]  # 重力应沿X轴方向
    # corrected = acc - gravity_sensor ≈ [-9.81, 0, 0]
    print(f"期望值: {[-x for x in expected_gravity]}")
    print("实际值: ", corrected_acc)
    assert np.allclose(corrected_acc, [-9.81, 0.0, 0.0], atol=1e-2), "测试失败！"

test_remove_gravity_case()