# main.py
import matplotlib
matplotlib.use('TkAgg')

from data_collector import collector_thread
from plot_manager import fig, update, init_plot
import matplotlib.animation as animation
import matplotlib.pyplot as plt

# 启动采集线程
collector_thread.start()

# 启动动画
ani = animation.FuncAnimation(
    fig, update,
    init_func=init_plot,
    interval=10,
    blit=True,
    save_count=200
)

plt.show()