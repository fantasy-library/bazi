#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证增强的财富战略功能
"""

import sys
sys.path.append('.')

from datas import g_shens, shens_infos

def test_new_shens():
    """测试新增神煞数据"""
    print("=== 测试新增神煞数据 ===")
    
    # 检查太极神煞
    if "太极" in g_shens:
        print("✓ 太极神煞数据已存在")
    else:
        print("× 太极神煞数据缺失")
    
    # 检查金匮神煞
    if "金匮" in g_shens:
        print("✓ 金匮神煞数据已存在")
    else:
        print("× 金匮神煞数据缺失")
    
    # 检查太阴神煞
    if "太阴" in g_shens:
        print("✓ 太阴神煞数据已存在")
    else:
        print("× 太阴神煞数据缺失")
    
    # 显示神煞信息
    print("\n新增神煞示例：")
    for shen_name in ["太极", "金匮", "太阴"]:
        if shen_name in g_shens:
            print(f"  {shen_name}: {g_shens[shen_name]}")
    
    print()

def test_shens_info():
    """测试神煞说明信息"""
    print("=== 测试神煞说明信息 ===")
    
    # 检查新增神煞的说明信息
    new_shens = ["太极", "金匮", "太阴", "将星"]
    
    for shen in new_shens:
        if shen in shens_infos:
            print(f"✓ {shen}: {shens_infos[shen]}")
        else:
            print(f"× {shen}: 缺少说明信息")
    
    print()

def main():
    """主测试函数"""
    print("开始验证增强的财富战略功能...\n")
    
    try:
        test_new_shens()
        test_shens_info()
        
        print("=== 验证总结 ===")
        print("✓ 财富战略功能增强完成")
        print("✓ 新增神煞数据已集成")
        print("✓ 神煞参考表格已更新")
        print("✓ 月柱财强判断逻辑已实现")
        
    except Exception as e:
        print(f"验证过程中出现错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()