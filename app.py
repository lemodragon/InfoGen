#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfoGen-信息生成器 - 应用程序入口
Python桌面版姓名生成器主程序
"""

import sys
import os

# 确保程序可以找到模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from main_window import main
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装 PyQt5")
    print("安装命令: pip install PyQt5")
    sys.exit(1)


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"程序运行错误: {e}")
        sys.exit(1) 