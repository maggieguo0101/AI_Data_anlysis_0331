#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统启动入口文件
"""

import os
import sys
import argparse

# 确保能够导入system模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from system.app import MultiAgentSystem


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="多Agent协同系统")
    parser.add_argument("--config", type=str, default="agent_config.json", help="配置文件路径")
    args = parser.parse_args()
    
    system = MultiAgentSystem(args.config)
    system.run_cli()


if __name__ == "__main__":
    main()
