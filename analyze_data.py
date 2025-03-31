#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os

# 读取Excel文件
file_path = '郑远元经营评分及星级数据.xlsx'
try:
    data = pd.read_excel(file_path)
    
    # 打印列名以了解数据结构
    print("列名:", data.columns.tolist())
    
    # 显示数据的前几行以了解数据格式
    print("\n数据前5行:")
    print(data.head())
    
    # 检查是否有品牌和省份/城市列
    # 由于我们不确定确切的列名，我们需要检查几种可能性
    brand_columns = [col for col in data.columns if '品牌' in col or '商户' in col]
    location_columns = [col for col in data.columns if '省份' in col or '城市' in col]
    
    print("\n品牌相关列:", brand_columns)
    print("地区相关列:", location_columns)
    
    # 检查是否有金牌/银牌/铜牌相关列
    medal_columns = [col for col in data.columns if '金牌' in col or '银牌' in col or '铜牌' in col or '等级' in col]
    print("等级相关列:", medal_columns)
    
    # 打印唯一的品牌值以确保我们可以过滤郑远元
    if brand_columns:
        for col in brand_columns:
            print(f"\n{col}的唯一值:", data[col].unique())
    
    # 打印唯一的地区值
    if location_columns:
        for col in location_columns:
            print(f"\n{col}的唯一值:", data[col].unique())
    
except Exception as e:
    print(f"读取Excel文件时出错: {e}")
