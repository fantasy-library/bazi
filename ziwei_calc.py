#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立脚本：用于在子进程中执行紫微排盘计算，避免 pythonmonkey 导致 Streamlit 崩溃
"""
import sys
import json
from py_iztro import Astro

def main():
    if len(sys.argv) < 5:
        print(json.dumps({"error": f"参数不足，需要至少4个参数，但只收到{len(sys.argv)-1}个"}, ensure_ascii=False))
        sys.exit(1)
    
    try:
        date_str = sys.argv[1]  # 日期字符串，如 "2000-8-16"
        time_index = int(sys.argv[2])  # 时辰索引，0-12
        gender = sys.argv[3]  # 性别，"男" 或 "女"
        use_gregorian = sys.argv[4].lower() == "true"  # 是否使用公历
        language = sys.argv[5] if len(sys.argv) > 5 else "zh-TW"  # 语言
        
        # 初始化 Astro 对象
        astro = Astro()
        
        # 执行排盘
        if use_gregorian:
            result = astro.by_solar(date_str, time_index, gender, language=language)
        else:
            result = astro.by_lunar(date_str, time_index, gender, language=language)
        
        # 转换为 JSON
        result_dict = result.model_dump(by_alias=True)
        print(json.dumps(result_dict, ensure_ascii=False))
        
    except Exception as e:
        error_info = {
            "error": str(e),
            "type": type(e).__name__
        }
        print(json.dumps(error_info, ensure_ascii=False))
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

