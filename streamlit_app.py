#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import re
import json
from pathlib import Path

import streamlit as st
try:
    from opencc import OpenCC
except Exception:
    OpenCC = None  # graceful fallback if not installed


def run_script(args):
    """Run a CLI python script and return combined stdout/stderr as text."""
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        result = subprocess.run(
            [sys.executable, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(Path(__file__).parent),
            env=env,
        )
        return result.stdout
    except Exception as e:
        return f"执行失败: {e}"


_ansi_re = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(text: str) -> str:
    if not text:
        return text
    return _ansi_re.sub("", text)

_cite_re = re.compile(r"\b\S*P\d{1,3}-\d{1,3}\S*", re.IGNORECASE)
_nm_range_re = re.compile(r"\b\d{1,3}-\d{1,3}\b")
_pd_re = re.compile(r"\bpd\s*\d{1,3}\b", re.IGNORECASE)
_ji_base_re = re.compile(r"(?:基礎|基础|基)\s*\d{1,3}")

def sanitize_citations(text: str) -> str:
    if not text:
        return text
    # remove tokens like 母法P24-41, P79-4, 母法總則P55-5 等，及 1-157 這類編碼
    t = _cite_re.sub("", text)
    t = _nm_range_re.sub("", t)
    t = _pd_re.sub("", t)
    t = _ji_base_re.sub("", t)
    # 清理多餘雙空白
    t = re.sub(r"[ \t]{2,}", " ", t)
    return t

def collapse_duplicates(text: str) -> str:
    if not text:
        return text
    lines = text.splitlines()
    result = []
    prev = None
    for line in lines:
        key = line.strip()
        if key == prev:
            continue
        result.append(line)
        prev = key
    return "\n".join(result)


st.set_page_config(page_title="八字排盤，僅作參考", layout="wide")

# Simplified -> Traditional converter with custom rule: keep 丑 (not 醜)
_cc = OpenCC('s2t') if OpenCC else None

_manual_tr_map = {
    '罗': '羅', '时': '時', '后': '後', '历': '曆', '历': '曆', '农': '農', '闰': '閏',
    '计': '計', '算': '算', '显': '顯', '预': '預', '览': '覽', '页': '頁', '复': '複',
    '体': '體', '术': '術', '学': '學', '网': '網', '读': '讀', '开': '開', '关': '關',
    '龙': '龍', '鸡': '雞', '马': '馬', '后': '後', '壶': '壺', '冲': '沖',
}

def to_tr(text: str) -> str:
    if not text:
        return text
    if _cc is None:
        t = text
        for k, v in _manual_tr_map.items():
            t = t.replace(k, v)
        return t.replace('醜', '丑').replace('衝', '沖')
    t = _cc.convert(text)
    t = t.replace('醜', '丑')
    t = t.replace('幹', '干')
    t = t.replace('衝', '沖')
    return t

use_tr = True  # 強制繁體顯示

def T(s: str) -> str:
    return to_tr(s) if use_tr else s

st.title(T("八字论命，仅作参考"))

# 左侧参考资料栏
with st.sidebar:
    st.header(T("参考资料"))
    with st.expander(T("八字命理分析提示詞"), expanded=False):
        reference_text = T("""
**你是精通八字命理，深研《淵海子平》《三命通會》《滴天髓》等經典，兼具哲學思辨與人文關懷的專業命理分析師。**
請依據以下提供的命盤資訊，撰寫一份全面、深入且中肯的八字分析報告。

## 核心要求

**口吻與立場**：以專業、客觀、富洞見且飽含人文關懷的語氣表述，避免絕對化斷語，改用「有… 的傾向」「… 的可能性較高」等委婉說法。分析如智慧哲友，既點明命局核心，亦給予人生啟示與鼓勵。

**分析基石**：所有論斷須以五行強弱、生克制化、喜用神解析為絕對核心，十神、神煞、納音僅作輔助參考，不得作為主要論斷依據。

**結構清晰**：嚴格依照以下邏輯架構組織報告內容。

## 命盤資訊
- 性別：
- 公曆：
- 農曆：
- 八字：

## 報告結構指引

### 第一部分：命局核心深度剖析

#### 五行強弱與喜用神解析
- 詳析日主於出生月的旺衰狀態。
- 系統解析八字中金、木、水、火、土五行的分佈、力量強弱及相互作用關係。
- 明確判定命局屬身旺、身弱、從強或從弱格局。
- 據此確定喜神、用神（對命主最有利的五行）與忌神（對命主最不利的五行）。

#### 命格性質與格局
- 基於喜用神與五行組合，總結命主核心性情特質。
- 點明命局核心矛盾（如官殺混雜、傷官見官、財多身弱等）及其對人生的具體體現。

#### 性格心理畫像
- 結合十神與五行，描繪立體性格形象，包含優勢（如正財的務實、傷官的聰慧）與潛在挑戰（如七殺的壓力、偏財的散漫等）。
- 說明內在心理與外在表現可能存在的差異。

### 第二部分：人生各領域專項分析

#### 事業方向與財運解析
- 對應喜用神五行屬性，指出最適合發展的行業領域（如喜水利流動、資訊業；喜木利文教、出版業等）。
- 分析財運模式（以穩定正財為主或波動偏財為佳）、財庫狀況，並給出具體理財建議。

#### 婚姻與感情走勢
- 女命分析官殺（夫星）、男命分析財星在命局中的狀態、位置及強弱。
- 解讀日支夫妻宮的五行、十神及其相互作用。
- 描述感情觀、理想伴侶特質，以及人生可能經歷的感情階段與需注意的年份。

#### 健康與注意事項
- 依據五行過旺、過弱或受沖克的情況，指出需長期關注的身體薄弱系統（如金弱注意肺部、水弱注意腎臟等）。

### 第三部分：運勢解讀與人生指導

#### 大運流年精析
- **當前大運**：分析正在行進的大運整體影響，以及大運與命盤的關鍵作用。
- **未來展望**：重點解析即將到來的流年運勢，包含機遇、挑戰及注意事項。
- **後續大運**：簡要展望下一階段大運的趨勢與核心主題。

#### 人生哲學與行動指南
- 基於前述所有分析，提煉核心人生發展策略。
- 在修行、心態調整、人際經營、重大決策等方面，給予具體指導性建議。

生成一篇五千字左右的詳細白話文報告, 要情理兼備, 通暢易懂, 繁體中文。
""")
        st.markdown(reference_text)
        
        # 复制到剪贴板按钮 - 将纯文本存储在session state中
        # 提取纯文本内容（去除Markdown格式标记）
        # 使用正则表达式更安全地移除Markdown标记
        reference_text_plain = re.sub(r'\*\*([^*]+)\*\*', r'\1', reference_text)  # 移除粗体标记但保留内容
        reference_text_plain = re.sub(r'^#{1,4}\s+', '', reference_text_plain, flags=re.MULTILINE)  # 移除标题标记
        reference_text_plain = reference_text_plain.strip()
        # 转义HTML特殊字符并转换为JSON字符串以便在JavaScript中使用
        reference_text_escaped = json.dumps(reference_text_plain)
        
        copy_html = f"""
        <div>
        <button id="copyBtn" style="width:100%; padding:8px; margin-top:10px; background-color:#4CAF50; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">
            📋 {T("複製到剪貼板")}
        </button>
        </div>
        <script>
        const copyText = {reference_text_escaped};
        document.getElementById('copyBtn').addEventListener('click', function() {{
            navigator.clipboard.writeText(copyText).then(function() {{
                const btn = document.getElementById('copyBtn');
                const originalText = btn.innerHTML;
                btn.innerHTML = '✅ {T("已複製！")}';
                btn.style.backgroundColor = '#2196F3';
                setTimeout(function() {{
                    btn.innerHTML = originalText;
                    btn.style.backgroundColor = '#4CAF50';
                }}, 2000);
            }}, function(err) {{
                alert('{T("複製失敗，請手動選擇文字複製")}');
            }});
        }});
        </script>
        """
        st.components.v1.html(copy_html, height=60)

# Global typography
st.markdown(
    """
    <style>
    html, body, [class^="css"], .stMarkdown, .stText, .stCaption, .stButton button {
        font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", "Noto Sans CJK TC", sans-serif !important;
        font-size: 16px;
    }
    pre, code, .stCode, .stMarkdown pre code {
        font-family: "JetBrains Mono", "Cascadia Code", Consolas, monospace !important;
        font-size: 14px !important;
        white-space: pre-wrap !important;
        word-break: break-word !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

tabs = st.tabs([T("八字排盘"), T("合婚查询")]) 


with tabs[0]:
    st.subheader(T("八字排盘"))
    col1, col2 = st.columns(2)
    with col1:
        use_gregorian = st.toggle(T("使用公历输入"), value=True)
        year = st.number_input(T("年"), value=1990, min_value=1850, max_value=2100, step=1)
        month = st.number_input(T("月"), value=1, min_value=1, max_value=12, step=1)
        day = st.number_input(T("日"), value=1, min_value=1, max_value=31, step=1)
        hour = st.number_input(T("时 (0-23)"), value=12, min_value=0, max_value=23, step=1)
    with col2:
        is_leap = st.checkbox(T("闰月 (农历专用)"), value=False)
        gender_choice = st.radio(T("出生性别"), [T("男 ♂"), T("女 ♀")], horizontal=True, index=0)
        advanced_bazi = st.checkbox(T("高级: 直接输入八字(年干支/月干支/日干支/时干支)"))

        if advanced_bazi:
            st.info(T("按照 README 用法，四项分别输入天干、地支。如不熟悉请勿勾选该项。"))
            gan_year = st.text_input(T("年干"), value="甲")
            gan_month = st.text_input(T("月干"), value="子")
            gan_day = st.text_input(T("日干"), value="甲")
            gan_time = st.text_input(T("时干"), value="子")
            zhi_year = st.text_input(T("年支"), value="子")
            zhi_month = st.text_input(T("月支"), value="子")
            zhi_day = st.text_input(T("日支"), value="子")
            zhi_time = st.text_input(T("时支"), value="子")

    if st.button(T("计算八字"), type="primary"):
        if advanced_bazi:
            # python bazi.py -b year month day time  (each is pair of gan/zhi)
            args = [
                "bazi.py",
                "-b",
                gan_year + zhi_year,
                gan_month + zhi_month,
                gan_day + zhi_day,
                gan_time + zhi_time,
            ]
        else:
            args = [
                "bazi.py",
                str(int(year)),
                str(int(month)),
                str(int(day)),
                str(int(hour)),
            ]
            if use_gregorian:
                args.append("-g")
            if is_leap:
                args.append("-r")
            # female flag
            if gender_choice.endswith('♀'):
                args.append("-n")

        output = strip_ansi(run_script(args))
        output = sanitize_citations(output)
        if use_tr:
            output = to_tr(output)
        output = collapse_duplicates(output)
        st.code(output, language="text")


with tabs[1]:
    st.subheader(T("合婚查询"))
    mode = st.radio(T("合婚类型"), [T("生肖"), T("日柱(六十甲子)")], horizontal=True, index=0)

    if mode.startswith(T("生肖")[:1]):
        shengxiao_list = ["鼠","牛","虎","兔","龙","蛇","马","羊","猴","鸡","狗","猪"]
        zx = st.selectbox(T("选择你的生肖"), shengxiao_list, index=0)
        if st.button(T("计算合婚")):
            args = ["shengxiao.py", zx]
            output = strip_ansi(run_script(args))
            output = sanitize_citations(output)
            if use_tr:
                output = to_tr(output)
            output = collapse_duplicates(output)
            st.code(output, language="text")
    else:
        rizhu_list = [
            "甲子","乙丑","丙寅","丁卯","戊辰","己巳","庚午","辛未","壬申","癸酉",
            "甲戌","乙亥","丙子","丁丑","戊寅","己卯","庚辰","辛巳","壬午","癸未",
            "甲申","乙酉","丙戌","丁亥","戊子","己丑","庚寅","辛卯","壬辰","癸巳",
            "甲午","乙未","丙申","丁酉","戊戌","己亥","庚子","辛丑","壬寅","癸卯",
            "甲辰","乙巳","丙午","丁未","戊申","己酉","庚戌","辛亥","壬子","癸丑",
            "甲寅","乙卯","丙辰","丁巳","戊午","己未","庚申","辛酉","壬戌","癸亥",
        ]
        rz = st.selectbox(T("选择你的日柱"), rizhu_list, index=0)
        if st.button(T("计算合婚")):
            args = ["shengxiao.py", rz]
            output = strip_ansi(run_script(args))
            output = sanitize_citations(output)
            if use_tr:
                output = to_tr(output)
            output = collapse_duplicates(output)
            st.code(output, language="text")




