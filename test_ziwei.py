#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from py_iztro import Astro
    
    print("正在初始化 Astro...")
    astro = Astro()
    print("✓ Astro 初始化成功")
    
    print("\n正在测试紫微排盘...")
    result = astro.by_solar("2000-8-16", 2, "女", language="zh-TW")
    print("✓ 排盘成功")
    
    print(f"\n基本信息:")
    print(f"  性别: {result.gender}")
    print(f"  公历: {result.solar_date}")
    print(f"  农历: {result.lunar_date}")
    print(f"  干支: {result.chinese_date}")
    print(f"  命宫: {result.soul}")
    print(f"  身宫: {result.body}")
    
except Exception as e:
    import traceback
    print(f"✗ 错误: {str(e)}")
    traceback.print_exc()


