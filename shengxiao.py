#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: original authors
Modified: 2024-01-01 添加六十日柱合婚功能，并统一输出格式
"""

import argparse
from datas import shengxiaos, zhi_atts

def output(des, key, zhi):
    print()
    print(des, end='')
    for item in zhi_atts[zhi][key]:
        print(shengxiaos[item], end='')       

rizhu_data = {
    "甲子": {"he": ["己丑"], "chong": ["庚午"], "hai": ["辛未"], "ke": ["戊辰", "戊戌"], "sheng": ["癸酉", "壬申"]},
    "乙丑": {"he": ["庚子"], "chong": ["辛未"], "hai": ["壬申"], "ke": ["己卯", "己酉"], "sheng": ["丙子", "丁亥"]},
    "丙寅": {"he": ["辛亥"], "chong": ["壬申"], "hai": ["癸酉"], "ke": ["庚辰", "庚戌"], "sheng": ["甲午", "乙未"]},
    "丁卯": {"he": ["壬戌"], "chong": ["癸酉"], "hai": ["甲戌"], "ke": ["辛巳", "辛亥"], "sheng": ["乙巳", "丙午"]},
    "戊辰": {"he": ["癸酉"], "chong": ["甲戌"], "hai": ["乙亥"], "ke": ["壬午", "壬子"], "sheng": ["丙申", "丁酉"]},
    "己巳": {"he": ["甲申"], "chong": ["乙亥"], "hai": ["丙子"], "ke": ["癸未", "癸丑"], "sheng": ["丁亥", "戊子"]},
    "庚午": {"he": ["乙未"], "chong": ["甲子"], "hai": ["丁丑"], "ke": ["丙申", "丙寅"], "sheng": ["己卯", "戊寅"]},
    "辛未": {"he": ["丙午"], "chong": ["乙丑"], "hai": ["戊寅"], "ke": ["丁酉", "丁卯"], "sheng": ["庚辰", "己巳"]},
    "壬申": {"he": ["丁巳"], "chong": ["丙寅"], "hai": ["己卯"], "ke": ["戊戌", "戊辰"], "sheng": ["辛巳", "庚午"]},
    "癸酉": {"he": ["戊辰"], "chong": ["丁卯"], "hai": ["庚辰"], "ke": ["己亥", "己巳"], "sheng": ["壬午", "辛未"]},
    "甲戌": {"he": ["己卯"], "chong": ["庚辰"], "hai": ["辛巳"], "ke": ["壬子", "壬午"], "sheng": ["癸未", "甲申"]},
    "乙亥": {"he": ["庚寅"], "chong": ["辛巳"], "hai": ["壬午"], "ke": ["癸丑", "癸未"], "sheng": ["甲申", "乙酉"]},
    "丙子": {"he": ["辛丑"], "chong": ["壬午"], "hai": ["癸未"], "ke": ["甲申", "甲寅"], "sheng": ["乙酉", "丙戌"]},
    "丁丑": {"he": ["壬子"], "chong": ["癸未"], "hai": ["甲申"], "ke": ["乙酉", "乙卯"], "sheng": ["丙戌", "丁亥"]},
    "戊寅": {"he": ["癸亥"], "chong": ["甲申"], "hai": ["乙酉"], "ke": ["丙戌", "丙辰"], "sheng": ["丁亥", "戊子"]},
    "己卯": {"he": ["甲戌"], "chong": ["乙酉"], "hai": ["丙戌"], "ke": ["丁亥", "丁巳"], "sheng": ["戊子", "己丑"]},
    "庚辰": {"he": ["乙酉"], "chong": ["丙戌"], "hai": ["丁亥"], "ke": ["戊子", "戊午"], "sheng": ["己丑", "庚寅"]},
    "辛巳": {"he": ["丙申"], "chong": ["丁亥"], "hai": ["戊子"], "ke": ["己丑", "己未"], "sheng": ["庚寅", "辛卯"]},
    "壬午": {"he": ["丁未"], "chong": ["戊子"], "hai": ["己丑"], "ke": ["庚寅", "庚申"], "sheng": ["辛卯", "壬辰"]},
    "癸未": {"he": ["戊午"], "chong": ["己丑"], "hai": ["庚寅"], "ke": ["辛卯", "辛酉"], "sheng": ["壬辰", "癸巳"]},
    "甲申": {"he": ["己巳"], "chong": ["庚寅"], "hai": ["辛卯"], "ke": ["壬辰", "壬戌"], "sheng": ["癸巳", "甲午"]},
    "乙酉": {"he": ["庚辰"], "chong": ["辛卯"], "hai": ["壬辰"], "ke": ["癸巳", "癸亥"], "sheng": ["甲午", "乙未"]},
    "丙戌": {"he": ["辛卯"], "chong": ["壬辰"], "hai": ["癸巳"], "ke": ["甲午", "甲子"], "sheng": ["乙未", "丙申"]},
    "丁亥": {"he": ["壬寅"], "chong": ["癸巳"], "hai": ["甲午"], "ke": ["乙未", "乙丑"], "sheng": ["丙申", "丁酉"]},
    "戊子": {"he": ["癸丑"], "chong": ["甲午"], "hai": ["乙未"], "ke": ["丙申", "丙寅"], "sheng": ["丁酉", "戊戌"]},
    "己丑": {"he": ["甲子"], "chong": ["乙未"], "hai": ["丙申"], "ke": ["丁酉", "丁卯"], "sheng": ["戊戌", "己亥"]},
    "庚寅": {"he": ["乙亥"], "chong": ["丙申"], "hai": ["丁酉"], "ke": ["戊戌", "戊辰"], "sheng": ["己亥", "庚子"]},
    "辛卯": {"he": ["丙戌"], "chong": ["丁酉"], "hai": ["戊戌"], "ke": ["己亥", "己巳"], "sheng": ["庚子", "辛丑"]},
    "壬辰": {"he": ["丁酉"], "chong": ["戊戌"], "hai": ["己亥"], "ke": ["庚子", "庚午"], "sheng": ["辛丑", "壬寅"]},
    "癸巳": {"he": ["戊申"], "chong": ["己亥"], "hai": ["庚子"], "ke": ["辛丑", "辛未"], "sheng": ["壬寅", "癸卯"]},
    "甲午": {"he": ["己未"], "chong": ["庚子"], "hai": ["辛丑"], "ke": ["壬寅", "壬申"], "sheng": ["癸卯", "甲辰"]},
    "乙未": {"he": ["庚午"], "chong": ["辛丑"], "hai": ["壬寅"], "ke": ["癸卯", "癸酉"], "sheng": ["甲辰", "乙巳"]},
    "丙申": {"he": ["辛巳"], "chong": ["壬寅"], "hai": ["癸卯"], "ke": ["甲辰", "甲戌"], "sheng": ["乙巳", "丙午"]},
    "丁酉": {"he": ["壬辰"], "chong": ["癸卯"], "hai": ["甲辰"], "ke": ["乙巳", "乙亥"], "sheng": ["丙午", "丁未"]},
    "戊戌": {"he": ["癸卯"], "chong": ["甲辰"], "hai": ["乙巳"], "ke": ["丙午", "丙子"], "sheng": ["丁未", "戊申"]},
    "己亥": {"he": ["甲寅"], "chong": ["乙巳"], "hai": ["丙午"], "ke": ["丁未", "丁丑"], "sheng": ["戊申", "己酉"]},
    "庚子": {"he": ["乙丑"], "chong": ["丙午"], "hai": ["丁未"], "ke": ["戊申", "戊寅"], "sheng": ["己酉", "庚戌"]},
    "辛丑": {"he": ["丙子"], "chong": ["丁未"], "hai": ["戊申"], "ke": ["己酉", "己卯"], "sheng": ["庚戌", "辛亥"]},
    "壬寅": {"he": ["丁亥"], "chong": ["戊申"], "hai": ["己酉"], "ke": ["庚戌", "庚辰"], "sheng": ["辛亥", "壬子"]},
    "癸卯": {"he": ["戊戌"], "chong": ["己酉"], "hai": ["庚戌"], "ke": ["辛亥", "辛巳"], "sheng": ["壬子", "癸丑"]},
    "甲辰": {"he": ["己酉"], "chong": ["庚戌"], "hai": ["辛亥"], "ke": ["壬子", "壬午"], "sheng": ["癸丑", "甲寅"]},
    "乙巳": {"he": ["庚申"], "chong": ["辛亥"], "hai": ["壬子"], "ke": ["癸丑", "癸未"], "sheng": ["甲寅", "乙卯"]},
    "丙午": {"he": ["辛未"], "chong": ["壬子"], "hai": ["癸丑"], "ke": ["甲寅", "甲申"], "sheng": ["乙卯", "丙辰"]},
    "丁未": {"he": ["壬午"], "chong": ["癸丑"], "hai": ["甲寅"], "ke": ["乙卯", "乙酉"], "sheng": ["丙辰", "丁巳"]},
    "戊申": {"he": ["癸巳"], "chong": ["甲寅"], "hai": ["乙卯"], "ke": ["丙辰", "丙戌"], "sheng": ["丁巳", "戊午"]},
    "己酉": {"he": ["甲辰"], "chong": ["乙卯"], "hai": ["丙辰"], "ke": ["丁巳", "丁亥"], "sheng": ["戊午", "己未"]},
    "庚戌": {"he": ["乙卯"], "chong": ["丙辰"], "hai": ["丁巳"], "ke": ["戊午", "戊子"], "sheng": ["己未", "庚申"]},
    "辛亥": {"he": ["丙寅"], "chong": ["丁巳"], "hai": ["戊午"], "ke": ["己未", "己丑"], "sheng": ["庚申", "辛酉"]},
    "壬子": {"he": ["丁丑"], "chong": ["戊午"], "hai": ["己未"], "ke": ["庚申", "庚寅"], "sheng": ["辛酉", "壬戌"]},
    "癸丑": {"he": ["戊子"], "chong": ["己未"], "hai": ["庚申"], "ke": ["辛酉", "辛卯"], "sheng": ["壬戌", "癸亥"]},
    "甲寅": {"he": ["己亥"], "chong": ["庚申"], "hai": ["辛酉"], "ke": ["壬戌", "壬辰"], "sheng": ["癸亥", "甲子"]},
    "乙卯": {"he": ["庚戌"], "chong": ["辛酉"], "hai": ["壬戌"], "ke": ["癸亥", "癸巳"], "sheng": ["甲子", "乙丑"]},
    "丙辰": {"he": ["辛亥"], "chong": ["壬戌"], "hai": ["癸亥"], "ke": ["甲子", "甲午"], "sheng": ["乙丑", "丙寅"]},
    "丁巳": {"he": ["壬子"], "chong": ["癸亥"], "hai": ["甲子"], "ke": ["乙丑", "乙未"], "sheng": ["丙寅", "丁卯"]},
    "戊午": {"he": ["癸丑"], "chong": ["甲子"], "hai": ["乙丑"], "ke": ["丙寅", "丙申"], "sheng": ["丁卯", "戊辰"]},
    "己未": {"he": ["甲申"], "chong": ["乙丑"], "hai": ["丙寅"], "ke": ["丁卯", "丁酉"], "sheng": ["戊辰", "己巳"]},
    "庚申": {"he": ["乙巳"], "chong": ["丙寅"], "hai": ["丁卯"], "ke": ["戊辰", "戊戌"], "sheng": ["己巳", "庚午"]},
    "辛酉": {"he": ["丙辰"], "chong": ["丁卯"], "hai": ["戊辰"], "ke": ["己巳", "己亥"], "sheng": ["庚午", "辛未"]},
    "壬戌": {"he": ["丁卯"], "chong": ["戊辰"], "hai": ["己巳"], "ke": ["庚午", "庚子"], "sheng": ["辛未", "壬申"]},
    "癸亥": {"he": ["戊寅"], "chong": ["己巳"], "hai": ["庚午"], "ke": ["辛未", "辛丑"], "sheng": ["壬申", "癸酉"]}
}

description = '''
生肖/日柱合婚查询工具
支持两种输入：
1) 生肖（如：虎、兔）
2) 日柱（如：甲子、乙丑 等六十甲子）
'''

parser = argparse.ArgumentParser(description=description,
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('input_value', action="store", help=u'请输入生肖或日柱（如：虎 或 甲子）')
parser.add_argument('--version', action='version',
                    version='%(prog)s 1.1 合婚擴展版 (生肖/日柱)')
options = parser.parse_args()

def run_shengxiao_mode(zodiac: str):
    print("你的生肖是：", zodiac)
    zhi = shengxiaos.inverse[zodiac]
    print("你的年支是：", zhi)
    print("="*80) 
    print("合生肖是合八字的一小部分，有一定参考意义，但是不是全部。") 
    print("合婚请以八字为准") 
    print("以下为相合的生肖：") 
    print("="*80) 
    output("与你三合的生肖：", '合', zhi)  
    output("与你六合的生肖：", '六', zhi)      
    output("与你三会的生肖：", '会', zhi)
    print()
    print("="*80) 
    print("以下为不合的生肖：") 
    print("="*80)     
    output("与你相冲的生肖：", '冲', zhi)  
    output("你刑的生肖：", '刑', zhi)
    output("被你刑的生肖：", '被刑', zhi) 
    output("与你相害的生肖：", '害', zhi)     
    output("与你相破的生肖：", '破', zhi) 
    print()
    print("="*80) 
    print("如果生肖同时在你的合与不合中，则做加减即可。") 
    print("比如猪对于虎，有一个相破，有一六合，抵消就为平性。") 


def output_relationship(rizhu, relationship_type, relationship_name):
    if relationship_type in rizhu_data[rizhu]:
        items = rizhu_data[rizhu][relationship_type]
        if items:
            print(f"{relationship_name}：", end='')
            for item in items:
                print(item, end=' ')
            print()
    else:
        print(f"{relationship_name}：无")

def run_rizhu_mode(rizhu: str):
    print("=" * 60)
    print(f"您的日柱是：{rizhu}")
    print("=" * 60)
    print("日柱合婚分析（仅供参考）：")
    print("合：天作之合，关系融洽")
    print("冲：性格冲突，需要磨合") 
    print("害：相互妨害，多有不利")
    print("克：一方克制，关系紧张")
    print("生：相生相助，关系和谐")
    print("=" * 60)
    print("\n【相合关系】")
    output_relationship(rizhu, "he", "天合日柱")
    output_relationship(rizhu, "sheng", "相生日柱")
    print("\n【相克关系】")
    output_relationship(rizhu, "chong", "相冲日柱")
    output_relationship(rizhu, "hai", "相害日柱")
    output_relationship(rizhu, "ke", "相克日柱")
    print("\n" + "=" * 60)
    print("温馨提示：")
    print("1. 日柱合婚只是八字合婚的一部分")
    print("2. 实际合婚需结合年、月、时柱综合分析")
    print("3. 相克关系并非绝对，可通过后天调和改善")
    print("4. 感情需要双方共同经营和维护")


value = options.input_value

if value in shengxiaos.inverse:
    run_shengxiao_mode(value)
elif value in rizhu_data:
    run_rizhu_mode(value)
else:
    print("请输入正确的生肖或日柱！")
    print("可用生肖：", " ".join(shengxiaos.inverse.keys()))
    print("可用日柱（部分示例）：甲子 乙丑 丙寅 … (六十甲子)")