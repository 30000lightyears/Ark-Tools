#!/usr/bin/env python3
"""
Ark-Tools GUI启动脚本
"""

import sys
from src.gui import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已退出")
        sys.exit(0)
    except Exception as e:
        print(f"启动GUI时发生错误: {e}")
        sys.exit(1)
