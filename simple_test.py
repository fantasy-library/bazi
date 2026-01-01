#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')
from datas import ten_deities, g_shens

def test_month_cai():
    print("=== Test Month Cai Strong ===")
    
    # Test case 1: Jia wood day master, Zi month
    print("\nTest case 1: Jia wood day master, Zi month")
    me = '甲'
    month_zhi = '子'
    
    # Calculate month stem and branch ten gods
    month_gan = '己'  # Month stem for Zi month
    month_gan_shen = ten_deities[me][month_gan]
    month_zhi_shen = ten_deities[me][month_zhi]
    
    print(f"Day master: {me}")
    print(f"Month stem: {month_gan}, Ten god: {month_gan_shen}")
    print(f"Month branch: {month_zhi}, Ten god: {month_zhi_shen}")
    
    # Check if both are wealth stars
    if month_gan_shen in ('财', '才') and month_zhi_shen in ('财', '才'):
        print("OK: Month pillar wealth strong!")
    else:
        print("NO: Not wealth strong")

def test_gods():
    print("\n=== Test New Gods Data ===")
    
    # Test Tianji (太极)
    print("\nTest Tianji:")
    try:
        tianji = g_shens['tianji']
        print(f"Tianji contains: {list(tianji.keys())}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_month_cai()
    test_gods()
    print("\nTest completed")