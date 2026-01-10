#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
格式檢查與修復腳本
檢查 personality_matrix 的格式完整性
"""

import ast
import json
import re

def check_python_syntax(code_str):
    """檢查Python語法是否正確"""
    try:
        ast.parse(code_str)
        return True, None
    except SyntaxError as e:
        return False, str(e)

def find_missing_commas(code_str):
    """查找缺少逗號的地方"""
    issues = []
    lines = code_str.split('\n')
    
    # 查找可能的問題模式
    for i, line in enumerate(lines):
        # 檢查是否在字典值後缺少逗號
        if re.search(r'"[^"]*":\s*"[^"]*"$', line.strip()):
            # 如果下一行不是空行且不是註釋，且不是以 } 或 ] 開頭
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith('#') and not next_line.startswith('}') and not next_line.startswith(']'):
                    if not line.rstrip().endswith(',') and not line.rstrip().endswith('{') and not line.rstrip().endswith('['):
                        issues.append(f"第 {i+1} 行可能缺少逗號: {line[:80]}")
    
    return issues

def check_structure(code_str):
    """檢查結構完整性"""
    issues = []
    
    # 檢查括號匹配
    open_braces = code_str.count('{')
    close_braces = code_str.count('}')
    if open_braces != close_braces:
        issues.append(f"大括號不匹配: 開 {open_braces} 個，閉 {close_braces} 個")
    
    open_brackets = code_str.count('[')
    close_brackets = code_str.count(']')
    if open_brackets != close_brackets:
        issues.append(f"方括號不匹配: 開 {open_brackets} 個，閉 {close_brackets} 個")
    
    # 檢查引號匹配（簡單檢查）
    single_quotes = code_str.count("'")
    double_quotes = code_str.count('"')
    if single_quotes % 2 != 0:
        issues.append("單引號可能不匹配")
    if double_quotes % 2 != 0:
        issues.append("雙引號可能不匹配")
    
    return issues

def main():
    print("=" * 60)
    print("格式檢查報告")
    print("=" * 60)
    
    # 讀取用戶提供的代碼（這裡需要用戶提供文件路徑）
    print("\n請將您的代碼保存為 'personality_matrix_raw.py' 文件")
    print("然後運行此腳本進行檢查")
    
    try:
        with open('personality_matrix_raw.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        print("\n1. 語法檢查...")
        is_valid, error = check_python_syntax(code)
        if is_valid:
            print("   ✓ Python語法正確")
        else:
            print(f"   ✗ 語法錯誤: {error}")
        
        print("\n2. 結構檢查...")
        structure_issues = check_structure(code)
        if structure_issues:
            print("   ✗ 發現結構問題:")
            for issue in structure_issues:
                print(f"     - {issue}")
        else:
            print("   ✓ 結構完整")
        
        print("\n3. 逗號檢查...")
        comma_issues = find_missing_commas(code)
        if comma_issues:
            print(f"   ✗ 發現 {len(comma_issues)} 個可能的逗號問題:")
            for issue in comma_issues[:10]:  # 只顯示前10個
                print(f"     - {issue}")
            if len(comma_issues) > 10:
                print(f"     ... 還有 {len(comma_issues) - 10} 個問題")
        else:
            print("   ✓ 未發現明顯的逗號問題")
        
        print("\n" + "=" * 60)
        print("檢查完成")
        print("=" * 60)
        
    except FileNotFoundError:
        print("\n錯誤: 找不到 'personality_matrix_raw.py' 文件")
        print("請先創建該文件並將您的代碼保存進去")

if __name__ == '__main__':
    main()

