# main.py
from data_collector import collector_thread
import plot_manager

# 启动采集线程
collector_thread.start()

plot_manager.run_plot()