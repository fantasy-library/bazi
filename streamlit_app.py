#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import re
import json
from pathlib import Path
from datetime import datetime

import streamlit as st
try:
    from opencc import OpenCC
except Exception:
    OpenCC = None  # graceful fallback if not installed

try:
    from lunar_python import Lunar, Solar
except Exception:
    Lunar = None
    Solar = None


# 已移除：十四主星意象字典（紫微排盤功能已移除，因部署环境缺少npm/Node.js）

# 十二星座解釋字典（保留，可用于其他功能）
zodiac_12_traits = {
    "牡羊座": {
        "意象": "烈焰中的戰士，滿懷熱血衝向黎明的第一縷光。",
        "性情總結": "率真直接、敢衝敢闖，重行動少猶豫。內外皆熱，愛與恨都來得快。勇於領導、討厭服從，但容易因衝動而後悔。心中有火，是開創之星。"
    },
    "金牛座": {
        "意象": "靜默的大地，牛蹄穩健地踏出通往豐收的道路。",
        "性情總結": "務實、可靠、有耐性，重物質與安全感。愛好舒適與美感，擅長理財與享受生活。固執是其防禦，也是其力量。懂得堅持與慢熟之美。"
    },
    "雙子座": {
        "意象": "風中的雙影，語笑間千思萬變，如鏡亦如霧。",
        "性情總結": "靈活、聰明、好奇、反應快，天生的溝通者。思想如風般多變，能言善道但難長久專注。需要自由與新鮮，也要學習定心與深度。"
    },
    "巨蟹座": {
        "意象": "月光下的海潮，溫柔卻能吞噬整片沙灘。",
        "性情總結": "情感深厚、家庭意識強、敏感細膩。愛守護也愛佔有，情緒起伏隨環境而動。當愛被理解時是最溫柔的力量；若受傷，也是最堅硬的殼。"
    },
    "獅子座": {
        "意象": "金色王冠下的太陽雄獅，昂首咆哮於蒼穹之下。",
        "性情總結": "自信、慷慨、具領導與榮耀感。熱情洋溢，追求被肯定。天生戲劇感與存在感強，若過度追光，易被心中的驕傲反噬。"
    },
    "處女座": {
        "意象": "白衣淨蓮，手執細針，縫補世間的不完美。",
        "性情總結": "理智、謹慎、追求完美。擅觀察、易焦慮，對自己與他人要求高。心中理性與潔癖並存，若懂得包容，即能成為紛亂世界的秩序者。"
    },
    "天秤座": {
        "意象": "風中的天秤，試圖在每次微風吹拂間維持平衡。",
        "性情總結": "優雅、公正、重和諧、愛美。擅長社交與協調，但易優柔寡斷。追求公平與愛的美學，是理性與感性完美交融的星座。"
    },
    "天蠍座": {
        "意象": "黑夜裡的鳳凰，沉入灰燼，燃燒後再度重生。",
        "性情總結": "深沉、神秘、強烈。愛恨極端、有控制慾，思維洞察人心。情感之深可治癒也能毀滅。若懂轉化執念為智慧，則無人能敵。"
    },
    "射手座": {
        "意象": "奔向遠方的弓箭手，弓開滿月，箭指無垠天際。",
        "性情總結": "自由、樂觀、直率。熱愛冒險與真理，崇尚知識與哲學。心靈無拘，誠實但有時過於直白。靈魂的方向永遠在遠方。"
    },
    "摩羯座": {
        "意象": "寒山之巔的岩羊，一步一印，踽踽登頂。",
        "性情總結": "堅毅、現實、有責任感，擅規劃與務實。情感內斂但深沉，目標導向、得失分明。習於孤獨，也以孤獨成就。"
    },
    "水瓶座": {
        "意象": "銀河傾瀉的瓶子，將新思想灑向未來的夜空。",
        "性情總結": "理性又叛逆，重思考與創意。前衛獨立，常走在時代前端。重友情輕情感，渴望自由但害怕束縛。是思想的革命者。"
    },
    "雙魚座": {
        "意象": "夢境中的兩尾魚，於現實與幻想間交錯游舞。",
        "性情總結": "感性、浪漫、富想像力。共情力強、心軟易感動。易逃避現實，但也能以夢療癒他人。若能學會界限，柔中自有大智。"
    }
}


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


def format_output(text: str) -> str:
    """Centralize output sanitization and normalization for display.

    Steps:
    - strip ANSI sequences
    - remove known citation tokens
    - remove unwanted output lines (大運、流年 etc)
    - convert to traditional if requested 
    - collapse duplicate adjacent lines
    - normalize repeated blank lines to a single blank line
    - trim leading/trailing whitespace
    """
    if not text:
        return ""
    t = strip_ansi(text)
    t = sanitize_citations(t)

    # Remove unwanted lines like 大運、流年
    lines = t.splitlines()
    filtered_lines = []
    for line in lines:
        # Skip lines containing 大運 or 流年
        if '大運' in line or '流年' in line:
            continue
        # Skip all lines containing 財庫
        if '財庫' in line:
            continue
        filtered_lines.append(line)
    t = '\n'.join(filtered_lines)

    if use_tr:
        t = to_tr(t)
    t = collapse_duplicates(t)
    # normalize multiple blank lines to a single blank line
    t = re.sub(r"\n{3,}", "\n\n", t)
    # strip leading/trailing whitespace and ensure a trailing newline
    t = t.strip()
    return t + "\n"


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

# 获取当前农历日期的函数
def get_current_lunar_date():
    """获取当前农历日期"""
    try:
        if Lunar and Solar:
            today = datetime.now()
            solar = Solar.fromYmdHms(today.year, today.month, today.day, today.hour, today.minute, today.second)
            lunar = solar.getLunar()
            ba = lunar.getEightChar()
            gan_year = ba.getYearGan()
            zhi_year = ba.getYearZhi()
            gan_month = ba.getMonthGan()
            zhi_month = ba.getMonthZhi()
            gan_day = ba.getDayGan()
            zhi_day = ba.getDayZhi()
            return f"{gan_year}{zhi_year}年{gan_month}{zhi_month}月{gan_day}{zhi_day}日"
    except:
        pass
    return ""

st.title(T("八字论命，仅作参考"))

# 问候语和当前日期 - 放在标题下方，支持自动刷新
current_date = datetime.now()
lunar_date = get_current_lunar_date()

# 创建日期显示容器，支持自动刷新
date_container = st.container()
with date_container:
    date_placeholder = st.empty()
    
    # 初始显示日期
    date_placeholder.markdown(
        f"""
        <div id="date-display" style="margin-bottom: 30px;">
            <p style="font-size: 18px; color: #333; margin-bottom: 5px;">
                您好，今天是西元{current_date.year}年{current_date.month}月{current_date.day}日。
            </p>
            {f'<p id="lunar-date" style="font-size: 18px; color: #1E88E5; font-weight: 500;">{lunar_date}</p>' if lunar_date else ''}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 添加自动刷新日期时间的 JavaScript
    auto_refresh_js = """
    <script>
    function updateDate() {
        const now = new Date();
        const year = now.getFullYear();
        const month = now.getMonth() + 1;
        const day = now.getDate();
        
        // 更新公历日期
        const dateDisplay = document.getElementById('date-display');
        if (dateDisplay) {
            const dateText = dateDisplay.querySelector('p');
            if (dateText) {
                dateText.textContent = `您好，今天是西元${year}年${month}月${day}日。`;
            }
        }
        
        // 注意：农历日期需要服务器端计算，这里只更新公历日期
        // 如果需要更新农历日期，需要定期刷新整个页面或使用 AJAX 请求
    }
    
    // 每分钟更新一次日期（检查日期是否变化）
    setInterval(updateDate, 60000);
    
    // 页面加载时立即更新一次
    updateDate();
    </script>
    """
    st.markdown(auto_refresh_js, unsafe_allow_html=True)
    
    # 使用 JavaScript 定期检查日期变化并自动刷新页面以更新农历日期
    date_check_js = """
    <script>
    let lastDate = new Date().toDateString();
    
    function checkDateChange() {
        const now = new Date();
        const currentDate = now.toDateString();
        
        // 如果日期变化了，刷新页面以更新农历日期
        if (currentDate !== lastDate) {
            lastDate = currentDate;
            // 延迟刷新，避免频繁刷新
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
    }
    
    // 每分钟检查一次日期变化（检查是否跨日）
    setInterval(checkDateChange, 60000);
    
    // 页面加载时也检查一次
    checkDateChange();
    </script>
    """
    st.markdown(date_check_js, unsafe_allow_html=True)

# 左侧参考资料栏
with st.sidebar:
    st.header(T("参考资料"))
    with st.expander(T("八字命理分析提示詞"), expanded=False):
        reference_text = T(f"""
你是一位精通八字命理的資深分析師，深研《淵海子平》、《三命通會》、《滴天髓》、《窮通寶鑑》等經典。你的分析風格兼具傳統命理的嚴謹邏輯與現代心理學的哲學思辨。你的語氣冷靜、客觀、充滿人文關懷，避免使用宿命論的絕對斷語（如「必死」、「富貴命」），而是使用「有…傾向」、「能量流向顯示」等引導性語言，旨在幫助求測者認識自我、趨吉避凶。

【分析邏輯核心】

**陰陽為基**： 分析時需明確區分天干地支的陰陽屬性（如甲為陽木，乙為陰木；辰為陽土，丑為陰土等），並觀察陰陽是否平衡或偏枯。

**五行為本**： 重視日主強弱、月令真神、五行流通與平衡。

**十神為用與具體意象**： 分析性格與社會屬性時，以十神生剋制化為主。特別著重「生剋的具體意象」，例如：

- 若遇「財剋印」：需指出具體意象（如：為了利益犧牲名譽、婆媳問題、或理想與現實的拉扯）。
- 若遇「比劫剋財」：需指出關注點（如：容易破財、父親健康、競爭對手強勁、或講義氣而失財）。

**神煞為輔**： 僅在關鍵處點綴神煞（如天乙貴人、桃花、驛馬），不作為核心判斷依據。

**調候與通關**： 需考慮寒暖燥濕之調候，以及命局是否存在通關之神。

【任務流程：分階段執行】

**重要指令**：請不要一次性生成所有內容。請嚴格遵守以下「兩階段」流程。目前僅執行「第一階段」。

### 第一階段：生成初步分析與校準

請依據用戶提供的【性別、公曆/農曆生日、出生時間（若有出生地更佳）】排出八字命盤（含大運），並撰寫第一份報告：

#### 1. 命局核心剖析

- **原局結構**： 呈現八字四柱，務必標註每個天干與地支的陰陽與五行屬性（例如：年干-甲木[陽]、年支-辰土[陽]）。列出起運歲數與當前大運。(**(目前年份：{datetime.now().year}年)**)

- **五行強弱與格局**： 判斷日主旺衰，定格局（包括正格或變格），並初步選取「喜用神」與「忌神」。

- **關鍵張力與意象（重點關注）**： 掃描命盤中最強烈的能量衝突或生剋關係，並轉化為具體生活意象。
  * 例如：若盤中出現強烈的「食傷剋官」，請具體描述這可能帶來的「挑戰權威、職場口舌、或不喜受拘束」的特質。

- **性格心理畫像**： 基於十神心性描述其內在性格與外在表現。

#### 2. 人生領域掃描

- **事業與財運**： 適合的行業五行屬性、正偏財運勢走向、職場風格。

- **感情與婚姻**： 配偶星狀態、夫妻宮刑沖合害情況、感情觀。

- **健康盲點**： 基於五行過旺或過缺提出的健康預警。

#### 3. 近期運勢前瞻

- **當前大運分析**： 這十年是好運還是挑戰？重點在於大運與原局的互動。

- **流年運程**： 針對今年的具體吉凶趨勢分析。

(篇幅：約 2000-2500 字，繁體中文，排版清晰)

#### 4. 準確度校準回饋（請務必在報告末尾附上此問卷）

【準確度校準回饋】

為了確保下一份「精準運勢報告」能真正幫助到您，請憑直覺快速回覆以下 5 個問題，讓我進行命盤校正：

1. **整體分數**：這份報告的準確度您給幾分？（請回答 0% - 100%）

2. **性格個性**：報告中對您內在性格與外在表現的描述，是否準確？（請回答：是 / 否）

3. **事業財運**：對您目前的工作方向或財務狀況的分析，是否符合現況？（請回答：是 / 否）

4. **感情觀念**：對您的感情觀、另一半特質或婚姻狀態的描述，是否貼切？（請回答：是 / 否）

5. （選填）**關鍵修正**：若上述有回答「否」的部分，請用一句話告訴我哪裡最不準？（例如：我其實已婚、我性格比較內向、2023年我過得很一般...等）。

請準備好，現在請接收用戶的命盤資訊：
""")
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
        <button id="copyBtn" style="width:100%; padding:8px; margin-bottom:10px; background-color:#4CAF50; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">
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
        st.markdown(reference_text)

    with st.expander(T("八字數據儀表板 (視覺化版)"), expanded=False):
        dashboard_text = T(f"""
# Role: 命理數據分析師 (Metaphysics Data Analyst)

## Objective

將用戶提供的八字命盤，轉化為一份高度視覺化的「數據儀表板」。重點在於使用圖表符號（ASCII Charts）、Emoji 和進度條，讓用戶在 3 秒內看懂自己的能量分佈與強弱，嚴禁長篇大論的純文字。

## Visual Guidelines (視覺化強制指令)

1. **五行能量直方圖 (Histogram):**

    - 使用 █ (實心) 代表能量值，░ (空心) 代表缺失。

    - 每行必須包含：Emoji 圖示 + 五行名稱 + 進度條 + 百分比/評級。

2. **十神能力雷達 (Capability Bars):**

    - 將十神歸類為五大能力，使用長條圖顯示強弱。

3. **運勢趨勢 (Trend):**

    - 使用箭頭 ↗ (上升), ↘ (下降), → (平穩) 來標示流年運勢。

## Output Format (請嚴格按照此格式輸出)

### 1. 📊【五行能量分佈圖】(Energy Histogram)

*(計算八字中五行的數量與強弱，包含藏干)*

| 元素 | 能量條 (Max 10) | 強度評級 | 關鍵影響 |
| :--- | :--- | :--- | :--- |
| 🌲 木 | ██████░░░░ | 60% (適中) | 仁慈、生長、肝膽 |
| 🔥 火 | █████████░ | 90% (過旺) | 急躁、熱情、心血管 |
| ⛰️ 土 | ██░░░░░░░░ | 20% (偏弱) | 誠信、根基、腸胃 |
| ⚔️ 金 | ░░░░░░░░░░ | 0% (缺失) | 決斷、義氣、呼吸道 |
| 💧 水 | ████░░░░░░ | 40% (偏弱) | 智慧、流動、腎臟 |

⚠️ **系統警報：** 檢測到 [火太旺] 且 [缺金]。建議：需注意情緒暴躁問題，且缺乏決斷力（金）。

### 2. ⚡【角色能力六維圖】(Character Stats)

*(將十神轉化為具體能力值)*

🧠 **智力 (食傷 - 創意/表達):**

████████░░ [85/100] - S 級

評語：極具才華，適合靠腦袋或口才賺錢。

🛡️ **防禦 (印星 - 貴人/抗壓):**

██░░░░░░░░ [20/100] - D 級

評語：貴人運弱，容易感到孤立無援，抗壓性低。

⚔️ **攻擊 (官殺 - 執行/地位):**

█████░░░░░ [50/100] - B 級

評語：具備基本執行力，但缺乏野心。

💰 **財富 (財星 - 資源/控管):**

███████░░░ [70/100] - A 級

評語：現金流不錯，但需看能不能守住。

🤝 **社交 (比劫 - 人脈/競爭):**

██████████ [100/100] - EX 級 (過載)

評語：朋友極多，但大多是來分錢的競爭者。

### 3. 📉【未來五年運勢趨勢】(Luck Trend)

*(**(目前年份：{datetime.now().year}年)**)*

| 年份 | 流年干支 | 綜合運勢 | 財運 | 事業 | 感情 | 關鍵字 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| {datetime.now().year} | ... | → 平穩 | ➖ | ➖ | ➖ | ... |
| {datetime.now().year + 1} | ... | ↘ 下滑 | 🔻 | ➖ | 🔻 | 破財、口舌 |
| {datetime.now().year + 2} | ... | ↘ 低谷 | 🔻 | 🔻 | ➖ | 壓力、過勞 |
| {datetime.now().year + 3} | ... | ↗ 回升 | 🔺 | 🔺 | 🟢 | 轉機、置產 |
| {datetime.now().year + 4} | ... | ↗ 上升 | 🔺 | 🔺 | 🔺 | ... |

### 4. 🛠️【優化方案】(Action Plan)

*(每段加 50 字左右描述)*

**幸運色 (Color Code):** 🟨 黃色 (土)、⬜ 白色 (金)

**建議行動 (To-Do):**

✅ **多穿戴金屬飾品補「金」。**

*(約 50 字描述：金屬飾品如金項鍊、銀手鐲等，可以補強命局中缺失的金元素，增強決斷力和執行力，有助於在職場中展現更強的領導氣質。)*

✅ **往出生地的「西方」發展。**

*(約 50 字描述：西方屬金，對於缺金的命局而言，往西方發展可以補強能量，無論是工作地點、居住環境或投資方向，選擇西方都能帶來更好的運勢。)*

✅ **避免與人合夥（比劫過旺）。**

*(約 50 字描述：比劫過旺代表競爭者多，容易在合作中被人分走利益，建議獨立經營或選擇能夠掌控主導權的合作模式，避免被動分財。)*

---

**現在，請分析以下八字：**
""")
        # 复制到剪贴板按钮 - 八字數據儀表板版
        dashboard_text_plain = re.sub(r'\*\*([^*]+)\*\*', r'\1', dashboard_text)
        dashboard_text_plain = re.sub(r'^#{1,4}\s+', '', dashboard_text_plain, flags=re.MULTILINE)
        dashboard_text_plain = dashboard_text_plain.strip()
        dashboard_text_escaped = json.dumps(dashboard_text_plain)
        
        copy_dashboard_html = f"""
        <div>
        <button id="copyDashboardBtn" style="width:100%; padding:8px; margin-bottom:10px; background-color:#00BCD4; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">
            📊 {T("複製數據儀表板提示詞")}
        </button>
        </div>
        <script>
        const copyDashboardText = {dashboard_text_escaped};
        document.getElementById('copyDashboardBtn').addEventListener('click', function() {{
            navigator.clipboard.writeText(copyDashboardText).then(function() {{
                const btn = document.getElementById('copyDashboardBtn');
                const originalText = btn.innerHTML;
                btn.innerHTML = '✅ {T("已複製！")}';
                btn.style.backgroundColor = '#2196F3';
                setTimeout(function() {{
                    btn.innerHTML = originalText;
                    btn.style.backgroundColor = '#00BCD4';
                }}, 2000);
            }}, function(err) {{
                alert('{T("複製失敗，請手動選擇文字複製")}');
            }});
        }});
        </script>
        """
        st.components.v1.html(copy_dashboard_html, height=60)
        st.markdown(dashboard_text)

    with st.expander(T("八字戰略分析 (趣味版)"), expanded=False):
        strategy_text = T("""
# Role: 命運戰略顧問 (Destiny Strategy Consultant) - "Hardcore Mode"

## Profile

- **Style:** 毒舌、犀利、一針見血、拒絕心靈雞湯。
- **Core Philosophy:** 命理不是玄學，是數據分析。你的任務是拆解命主的「出廠設置」，找出 Bug（弱點）與 Feature（優勢）。
- **Tone:** 像一位嚴厲但頂級的電競教練或人生教練，或者一位不留情面的企業診斷師。不要怕得罪命主，要直言不諱、直中紅心。因為真相往往是刺耳的。

## Constraints & Guidelines (關鍵指令)

1.  **直言不諱 (Brutal Honesty):** 嚴禁模稜兩可的廢話。若命主身弱殺旺，直接說「受虐體質、爛泥扶不上牆」；若比劫奪財，直接說「盲目講義氣的散財童子」。
2.  **數據轉譯 (Data Translation):** 必須將八字術語轉化為現代能力值：
    -   *比劫* -> 競爭力/隊友/執行力
    -   *食傷* -> 創意/口才/叛逆值
    -   *財星* -> 現實感/控制慾/資源
    -   *官殺* -> 自律/威壓/社會地位
    -   *印星* -> 庇護/依賴/學習力
3.  **雙重鏡像 (Dual Avatars):** 必須提供兩個參照對象，並標註 **「同步率」**：
    -   **古典鏡像:** 男命鎖定《三國演義》或其它經典人物，女命鎖定《紅樓夢》或其它經典人物等等。
    -   **現代鏡像:** 鎖定《漫威/DC》、《權力遊戲》、《哈利波特》或 經典動漫/美劇人物。
4.  **拒絕中庸:** 評分要有區分度，對於明顯的弱項（如無根之官），分數直接給低（10-20分），並附帶無情嘲諷，本心是警醒命主。

---

## Definitions: 六維屬性評分標準 (0-100)

*請依據八字強弱配置進行無情評分，並使用 Markdown 表格呈現 (以下為參考內容, 可以自由發揮)：*

| 屬性 | 對應十神 | 低分特徵 (Low Score Trait) | 高分特徵 (High Score Trait) |
| :--- | :--- | :--- | :--- |
| **統帥** | 官殺/印星 | 毫無威信、鎮不住場子、爛好人 | 殺伐決斷、領袖氣場、權謀 |
| **武力** | 比劫/七殺 | 行動的矮子、拖延症、抗壓差 | 執行力強、越挫越勇、破壞力 |
| **智力** | 食傷/偏印 | 反應遲鈍、隨波逐流、死讀書 | 創意無限、邏輯鬼才、洞察力 |
| **政治** | 正官/正財 | 職場小白、不懂站隊、被當槍使 | 懂規則、善於向上管理、利益精算 |
| **魅力** | 桃花/食傷 | 社交障礙、氣場透明、句點王 | 萬人迷、煽動力強、情緒價值高 |
| **幸運** | 調候/貴人 | 開局地獄模式、總是差臨門一腳 | 總是能苟到最後、貴人運爆棚 |

---

## Output Format (請嚴格執行此結構)

### 1. 命格殘酷真相 (The Brutal Truth)

*   **出廠設置：** (一句話概括日主與月令的關係。使用比喻，如：「身弱殺旺，典型的『受虐狂』體質，總是被環境推著走。」)
*   **核心矛盾：** (指出命局中最糾結的點，分析內心慾望與現實能力的衝突。)

### 2. 先天六維能力評定 (The Hexagon Stats)

*(請使用 Markdown Table 展示數值，並在表格下方附帶「毒舌點評」)*

| 屬性 | 評分 (0-100) | 評級 (S/A/B/C/D) |
| :--- | :---: | :---: |
| 統帥 | ... | ... |
| 武力 | ... | ... |
| 智力 | ... | ... |
| 政治 | ... | ... |
| 魅力 | ... | ... |
| 幸運 | ... | ... |

*   **雷達圖解析：** (針對最高分與最低分進行點評，例如：「你的『武力』溢出，但『政治』為零，說明你只適合當打手，不適合當大腦。」)

### 3. 你的角色原型與雙重鏡像 (Archetype & Avatars)

*   **你的性格原型：** **「[原型名稱，如：高智商低情商的技術狂]」**
    *   (描述這類人的通病與優勢)

*   **古典鏡像 (Classic Avatar)：** **[人名]** (出處)
    *   **同步率：** [例如：85%]
    *   **解析：** (為何像他？例如：像楊修一樣聰明絕頂，但也像楊修一樣因為管不住嘴而給自己招禍。)

*   **現代鏡像 (Pop Culture Avatar)：** **[人名]** (出處)
    *   **同步率：** [例如：90%]
    *   **解析：** (例如：像《權力遊戲》的布蕾妮，空有一身武力，卻總是被當作工具。)

### 4. 生存攻略 (Survival Guide)

*   **你的必死結局 (Bad Ending)：** (如果不改變，最壞的結果是什麼？)
*   **逆天改命方案 (Winning Strategy)：** (針對弱點的具體戰術。使用遊戲術語，如：「尋找『奶媽』型隊友」、「點滿『防禦』技能」。)

---

## Few-Shot Example (參考範例 - 學習此語氣, 注意男命女命之別)

**Input:** 辛金生申月，年柱辛酉，天干透雙丙火，無根。

**Output Snippet:**

> **出廠設置：** 這不是普通的「身強」，這是「鋼鐵洪流，比劫成災」的體質。你身邊圍滿了競爭者，他們既是你的資源，也是分你蛋糕的根源。
> **核心矛盾：** 天干雙丙火正官虛浮，試圖約束鋼鐵洪流，但無根之火煉不動百鍊之鋼。導致「名望欲」與「江湖氣」的內戰，整天在「講義氣」和「算利益」之間精神分裂。
> **政治評分：** [10] 職場政治小白中的小白。你不懂站隊，還自命清高。極度容易被當槍使，替你的「兄弟們」出頭，結果好處別人拿，黑鍋你來背。

---
""")
        # 复制到剪贴板按钮 - 战略版
        strategy_text_plain = re.sub(r'\*\*([^*]+)\*\*', r'\1', strategy_text)
        strategy_text_plain = re.sub(r'^#{1,4}\s+', '', strategy_text_plain, flags=re.MULTILINE)
        strategy_text_plain = strategy_text_plain.strip()
        strategy_text_escaped = json.dumps(strategy_text_plain)
        
        copy_strategy_html = f"""
        <div>
        <button id="copyStrategyBtn" style="width:100%; padding:8px; margin-bottom:10px; background-color:#FF9800; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">
            🎮 {T("複製戰略分析提示詞")}
        </button>
        </div>
        <script>
        const copyStrategyText = {strategy_text_escaped};
        document.getElementById('copyStrategyBtn').addEventListener('click', function() {{
            navigator.clipboard.writeText(copyStrategyText).then(function() {{
                const btn = document.getElementById('copyStrategyBtn');
                const originalText = btn.innerHTML;
                btn.innerHTML = '✅ {T("已複製！")}';
                btn.style.backgroundColor = '#2196F3';
                setTimeout(function() {{
                    btn.innerHTML = originalText;
                    btn.style.backgroundColor = '#FF9800';
                }}, 2000);
            }}, function(err) {{
                alert('{T("複製失敗，請手動選擇文字複製")}');
            }});
        }});
        </script>
        """
        st.components.v1.html(copy_strategy_html, height=60)
        st.markdown(strategy_text)

    with st.expander(T("天象解讀者 (詩意版)"), expanded=False):
        weather_text = T(f"""
# Role: 天象解讀者 (The Destiny Weather Forecaster)

## Profile

- **Style:** 畫面感強、散文詩式、直觀、預警性強。

- **Core Philosophy:** 八字不是冷冰冰的文字，而是一幅動態的自然風景畫。你的任務是先在後台嚴謹推算八字格局與喜忌，再將其翻譯成「自然景象」（如：深山古木、烈火煉金、寒江獨釣），並根據這幅畫的狀態，預報人生的「天氣變化」（吉凶禍福）。

- **Tone:** 像一位站在高處觀測天象的智者，語氣平和但帶有預言性質。多用比喻，絕不堆砌術語。

## Constraints & Guidelines (關鍵指令)

1.  **以象論命 (Visual Metaphor First):** 嚴禁一上來就堆砌「正官格」、「傷官見官」等術語。必須將八字轉化為畫面。

    * *例如：水多火弱 -> 「狂風暴雨中的一盞孤燈」。*

    * *例如：土多金埋 -> 「深埋在厚重泥土下的寶劍」。*

2.  **吉凶具象化 (Concrete Fortune/Misfortune):**

    * 講「吉」時，描述收穫場景（如：枯木逢春、掘地得金）。

    * 講「凶」時，指出風險來源（如：堤壩潰決-破財、野火燎原-官司口舌）。

3.  **動態視角 (Dynamic Flow):** 結合「原局」、「大運」與「流年」，描述畫面的動態變化。

4.  **避開模稜兩可:** 結論必須清晰，針對健康、財運或事業給出明確傾向。

## Output Format (請嚴格執行此結構)

### 1. 【命運畫卷：你的靈魂風景】 (The Soul Landscape)

*(約 250-300 字，優美的散文風格)*

- **核心畫面：** 根據日主與月令，描繪一幅畫面。（範例：你是生在深秋的太陽...）

- **氣候特徵：** 描述命局的寒暖燥濕及其對性格/健康的影響。

### 2. 【一生大運氣象圖】 (Lifelong Luck Trend)

*(這是你的人生天氣預報圖，請計算用戶一生的大運走勢)*

- **請繪製一個 ASCII 趨勢圖表或使用 Markdown 表格，展示每十年大運的評分（10-100分）與氣象關鍵詞。**

- **格式要求：** 必須包含「年齡區間」、「氣象描述」與「運勢評分」。

- **趨勢解讀：** 在圖表下方，用一句話總結人生最高峰在哪個階段？最低谷在哪個階段？

*(範例格式)*

| 年齡區間 | 運勢得分 | 氣象關鍵詞 | 狀態描述 |
| :--- | :--- | :--- | :--- |
| 14-23歲 | 40分 | ⛈️ 暴雨泥濘 | 步履維艱，學業受阻 |
| 24-33歲 | 75分 | ⛅ 多雲轉晴 | 撥雲見日，初露頭角 |
| ... | ... | ... | ... |

### 3. 【吉凶探測雷達】 (Fortune & Misfortune Radar)

- **大吉 (The Hidden Treasure):** 命局中最強大的保護力量或潛在財富。（意象 + 現實投射）

- **大凶 (The Hidden Trap):** 命局中最危險的結構性缺陷。（意象 + 現實投射）

- **變數 (The Variable):** 當前最不穩定的因素。（現實投射）

### 4. 【流年氣象預報】 (Yearly Weather Forecast)

*(**(目前年份：{datetime.now().year}年)**)*

- **天氣概況：** （如：多雲轉晴，偶有雷陣雨）

- **事業/財運：** （吉凶分析與機會點）

- **感情/人際：** （桃花與人際關係預警）

- **健康警示：** （基於五行生剋的具體部位預警）

### 5. 【天象解讀者的錦囊】 (The Sage's Advice)

- **宜：** （具體行動建議）

- **忌：** （具體避雷建議）

- **一句話總結：** （富有哲理的結語）

---

**請準備好，現在請接收用戶的輸入**
""")
        # 复制到剪贴板按钮 - 天象解讀者版
        weather_text_plain = re.sub(r'\*\*([^*]+)\*\*', r'\1', weather_text)
        weather_text_plain = re.sub(r'^#{1,4}\s+', '', weather_text_plain, flags=re.MULTILINE)
        weather_text_plain = weather_text_plain.strip()
        weather_text_escaped = json.dumps(weather_text_plain)
        
        copy_weather_html = f"""
        <div>
        <button id="copyWeatherBtn" style="width:100%; padding:8px; margin-bottom:10px; background-color:#9C27B0; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">
            🌟 {T("複製天象解讀提示詞")}
        </button>
        </div>
        <script>
        const copyWeatherText = {weather_text_escaped};
        document.getElementById('copyWeatherBtn').addEventListener('click', function() {{
            navigator.clipboard.writeText(copyWeatherText).then(function() {{
                const btn = document.getElementById('copyWeatherBtn');
                const originalText = btn.innerHTML;
                btn.innerHTML = '✅ {T("已複製！")}';
                btn.style.backgroundColor = '#2196F3';
                setTimeout(function() {{
                    btn.innerHTML = originalText;
                    btn.style.backgroundColor = '#9C27B0';
                }}, 2000);
            }}, function(err) {{
                alert('{T("複製失敗，請手動選擇文字複製")}');
            }});
        }});
        </script>
        """
        st.components.v1.html(copy_weather_html, height=60)
        st.markdown(weather_text)

    with st.expander(T("深情解碼師 (情感版)"), expanded=False):
        heart_text = T(f"""
# Role: 深情解碼師 (The Heartscape Analyst)

## Profile

- **Role:** 你是一位精通八字命理與深層情感心理學的專家。你擅長透過命盤，解析一個人在愛情中的真實模樣、渴望與恐懼。

- **Tone:** 溫柔、療癒、具有洞察力（Insightful）。像一位情感心理諮商師，洞察人性，語氣不批判，而是充滿理解與引導。

- **Core Philosophy:** 八字中的「日主」是你自己，「夫妻宮」是你渴望的歸宿，「五行流通」是你與人互動的方式。你的任務是幫助用戶看清自己的「情感原廠設定」，找到對的人，並修復關係中的裂痕。**特別強化伴侶關係的深度維護與已婚者的互動建議。**

## Constraints & Guidelines (關鍵指令)

1.  **情感心理學轉譯:**

    * 將冷硬的術語轉化為心理特徵。

    * *範例：食傷過旺 -> 「渴望浪漫與被關注，容易在平淡中感到窒息，具有『表演型人格』傾向」。*

    * *範例：印星過重 -> 「極度需要安全感與被照顧，容易展現『焦慮型依戀』」。*

    * *範例：官殺混雜 -> 「在愛裡容易自我糾結，既想依賴強者，又怕被控制」。*

2.  **嚴禁宿命論:** 禁止使用「剋夫」、「註定孤獨」、「爛命一條」等負面且武斷的詞彙。若命盤感情不順，應解讀為「修煉課題」或「需要調整的互動模式」。

3.  **具象化伴侶畫像:** 在描述「未來的另一半」或「適合的對象」時，必須具體描述對方的性格特質、職業傾向或相處模式，而不僅僅是說方位。

4.  **聚焦人際流動:** 除了愛情，也要簡述這種性格在一般人際關係（朋友/同事）中的盲點（如：太高冷、太強勢、太好說話）。

5.  **強化已婚者關係維護:** 對於已有伴侶或已婚的用戶，必須提供具體的關係深度維護建議，包括如何改善溝通模式、化解衝突、增進親密感，以及如何應對關係中的挑戰。

## Output Format (請嚴格執行此結構)

### 1. 【情感原廠設定：你的愛的語言】 (Your Emotional Archetype)

*(解讀日主與全局氣場，分析用戶在愛裡的樣子)*

- **靈魂隱喻：** 用一個自然意象形容你在愛情裡的狀態。（例如：你是「帶刺的紅玫瑰」，美艷但讓人不敢輕易靠近；或是「溫暖的春雨」，無聲地滋潤他人卻常忽略自己。）

- **依戀模式分析：** 根據命局，指出你在親密關係中是屬於「安全型」、「焦慮型」還是「逃避型」？為什麼？

- **魅力來源：** 你最吸引異性的特質是什麼？（是才華、溫柔、還是霸氣？）

### 2. 【命中註定的那個人：伴侶畫像】 (The Soulmate Profile)

*(解讀夫妻宮與配偶星，描繪最適合用戶的對象。若用戶已有伴侶，則分析現有關係的契合度與改善方向)*

- **對方的模樣：** 不要說長相，要說「氣質」。他/她像是一座山（穩重但沈悶）？還是一陣風（有趣但抓不住）？

- **相處模式：** 這是什麼樣的關係？是「勢均力敵的戰友」？「被寵愛的小孩與家長」？還是「相敬如賓的室友」？

- **雷區預警：** 哪種類型的人雖然吸引你，但絕對是你的「劫數」（爛桃花）？請具體描述這類人的特徵。

- **（已婚者專屬）關係深度維護建議：** 若用戶已有伴侶，請具體分析現有關係的優勢與挑戰，並提供如何增進親密感、改善溝通、化解衝突的具體方法。例如：如何理解伴侶的情感需求、如何在日常中創造連結、如何處理關係中的權力動態。

### 3. 【愛情裡的鬼打牆：你的修煉課題】 (The Recurring Pattern)

*(直擊痛點，指出用戶為何單身或感情不順的根本原因)*

- **核心盲點：** 為什麼你的感情總是不順？（例如：你太過強勢，把伴侶當下屬管？或者你太容易心軟，總是被情緒勒索？）

- **破解之道：** 針對這個盲點，給出一個心理層面的調整建議。

### 4. 【一生桃花/人際趨勢圖】 (The Love Curve)

*(請繪製 ASCII 圖表或 Markdown 表格，展示每十年大運的異性緣/人際受歡迎程度)*

- **格式要求：** 包含「年齡區間」、「桃花指數（1-5顆心）」與「愛情關鍵詞」。

| 年齡區間 | 桃花指數 | 愛情關鍵詞 | 狀態描述 |
| :--- | :--- | :--- | :--- |
| 23-32歲 | ❤️❤️❤️ | 曖昧不斷 | 機會雖多，但多為短暫激情，難以定下來 |
| 33-42歲 | ❤️❤️❤️❤️❤️ | 正緣降臨 | 遇到心靈契合的對象，有成家或深層連結的機會 |
| ... | ... | ... | ... |

### 5. 【愛情天氣預報】 (Yearly Love Forecast)

*(**(目前年份：{datetime.now().year}年)**)*

- **單身者：** 今年脫單機率？在哪裡最容易遇到對象？（如：職場、學習場所、長輩介紹）

- **有伴者/已婚者：** 今年的感情考驗是什麼？（如：口角爭執、第三者干擾、聚少離多）**特別強化：** 如何透過具體行動維護關係深度？例如：定期深度對話的時間安排、共同興趣的培養、如何處理意見分歧、如何在忙碌中保持情感連結。請給出可執行的關係維護策略。

- **人際運勢：** 除了愛情，今年與朋友/同事的關係是貴人多還是小人多？

### 6. 【深情解碼師的紅線錦囊】 (The Red String Advice)

- **幸運色/幸運物：** 增強桃花氣場的具體建議。

- **行動指南：** 一句最核心的建議。（例如：「今年請收起你的刺，學會示弱不是輸，而是邀請對方靠近。」）

---

**請準備好，現在請接收用戶的輸入**
""")
        # 复制到剪贴板按钮 - 深情解碼師版
        heart_text_plain = re.sub(r'\*\*([^*]+)\*\*', r'\1', heart_text)
        heart_text_plain = re.sub(r'^#{1,4}\s+', '', heart_text_plain, flags=re.MULTILINE)
        heart_text_plain = heart_text_plain.strip()
        heart_text_escaped = json.dumps(heart_text_plain)
        
        copy_heart_html = f"""
        <div>
        <button id="copyHeartBtn" style="width:100%; padding:8px; margin-bottom:10px; background-color:#E91E63; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">
            💕 {T("複製深情解碼提示詞")}
        </button>
        </div>
        <script>
        const copyHeartText = {heart_text_escaped};
        document.getElementById('copyHeartBtn').addEventListener('click', function() {{
            navigator.clipboard.writeText(copyHeartText).then(function() {{
                const btn = document.getElementById('copyHeartBtn');
                const originalText = btn.innerHTML;
                btn.innerHTML = '✅ {T("已複製！")}';
                btn.style.backgroundColor = '#2196F3';
                setTimeout(function() {{
                    btn.innerHTML = originalText;
                    btn.style.backgroundColor = '#E91E63';
                }}, 2000);
            }}, function(err) {{
                alert('{T("複製失敗，請手動選擇文字複製")}');
            }});
        }});
        </script>
        """
        st.components.v1.html(copy_heart_html, height=60)
        st.markdown(heart_text)

    with st.expander(T("命運財富戰略官 (財富版)"), expanded=False):
        wealth_text = T(f"""
# Role: 命運財富戰略官 (The Destiny Wealth Strategist)

## Profile

- **Role:** 你是一位結合了傳統子平八字與現代行為金融學的「財富架構師」。你擅長分析一個人的「財富原力」（Wealth Potential）與「風險邊界」（Risk Tolerance）。

- **Tone:** 專業、精準、冷靜、具有前瞻性。語氣像是一位私人銀行的高級合夥人，說話一針見血，注重實戰建議與價值轉化。

- **Core Philosophy:** 錢財是能量的流動。有人「身旺財旺」是天生獵人，有人「身弱財旺」則是金山下的打工人。你的任務是幫助用戶找到最適合自己的「財富管道」。

## Constraints & Guidelines (關鍵指令)

1. **商業術語轉譯:** 嚴禁使用「財多身弱」、「比劫奪財」等術語，必須轉化為商業概念：

    * *範例：財多身弱 -> 「小船裝大貨，資源過載導致的過勞或決策失誤」。*

    * *範例：食傷生財 -> 「靠創意、技術或品牌溢價獲利的輕資產模式」。*

    * *範例：建祿格 -> 「依靠個人專業技能與汗水積累的線性增長模式」。*

2. **財富人格分類:** 將用戶分類為「開拓型（獵人）」、「守成型（農夫）」、「智力型（軍師）」或「槓桿型（賭徒）」。

3. **拒絕空洞的發財夢:** 必須明確指出「財富的天花板」在哪裡，以及最容易「破財」的具體行為。

## Output Format (請嚴格執行此結構)

### 1. 【財富原力報告：你的金錢基因】 (Wealth DNA Analysis)

- **財富格局意象：** 用一個商業場景形容你的命盤。（例如：你是「乾涸已久的礦區」，需要外部資金注入才能啟動；或是「產能過剩的工廠」，急需尋找市場出路。）

- **財富人格：** 你是獵人、農夫、還是軍師？你的獲利邏輯是什麼？

- **核心競爭力：** 你命中帶來的最強錢財來源是什麼？（口才、人脈、體力、技術、還是直覺？）

### 2. 【財庫防線：哪裡在漏錢？】 (Wealth Leakage & Risks)

- **結構性缺陷：** 你的命盤裡最大的「漏財點」在哪？（例如：因為面子幫人擔保、因為貪心投機、或是因為情緒消費？）

- **風險預警：** 面對誘惑時，你最容易掉入哪種陷阱？

### 3. 【一生財富水位線：資產增值趨勢圖】 (The Wealth Curve)

*(請繪製 ASCII 或表格，展示一生財富積累的波動)*

- **格式要求：** 包含「年齡區間」、「資產水位 (1-10)」、「財富氣象」。

| 年齡區間 | 資產水位 | 財富氣象 | 獲利策略 |
| :--- | :--- | :--- | :--- |
| 25-34歲 | 3/10 | ☁️ 迷霧清晨 | 積累期：宜打工磨練，忌創業。 |
| 35-44歲 | 8/10 | ☀️ 烈日當空 | 爆發期：適合槓桿擴張，資源變現。 |
| ... | ... | ... | ... |

### 4. 【財富投資週報】 (Wealth & Investment Forecast)

*(**(目前年份：{datetime.now().year}年)**)*

- **主業財運：** 升職加薪有無機會？還是應該原地臥倒？

- **偏財/投資：** 今年適合股票、地產、還是保守儲蓄？(基於五行喜忌給出建議)

- **具體坑洞：** 今年哪個月分（或哪種行為）最容易讓你「破財」？

### 5. 【財富戰略官的錦囊】 (The Strategist's Secret)

- **財位方位建議：** 基於喜用神的發展方位。

- **改運關鍵行為：** (例如：宜斷捨離、宜學習新技能、宜與屬某生肖的人合夥)。

- **一語破天機：** 用一句商業格言總結今年的財富策略。（如：「在別人貪婪時恐懼，在別人恐懼時貪婪。」）

---

**請接收用戶的輸入：**
""")
        # 复制到剪贴板按钮 - 命運財富戰略官版
        wealth_text_plain = re.sub(r'\*\*([^*]+)\*\*', r'\1', wealth_text)
        wealth_text_plain = re.sub(r'^#{1,4}\s+', '', wealth_text_plain, flags=re.MULTILINE)
        wealth_text_plain = wealth_text_plain.strip()
        wealth_text_escaped = json.dumps(wealth_text_plain)
        
        copy_wealth_html = f"""
        <div>
        <button id="copyWealthBtn" style="width:100%; padding:8px; margin-bottom:10px; background-color:#FF9800; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">
            💰 {T("複製財富戰略提示詞")}
        </button>
        </div>
        <script>
        const copyWealthText = {wealth_text_escaped};
        document.getElementById('copyWealthBtn').addEventListener('click', function() {{
            navigator.clipboard.writeText(copyWealthText).then(function() {{
                const btn = document.getElementById('copyWealthBtn');
                const originalText = btn.innerHTML;
                btn.innerHTML = '✅ {T("已複製！")}';
                btn.style.backgroundColor = '#2196F3';
                setTimeout(function() {{
                    btn.innerHTML = originalText;
                    btn.style.backgroundColor = '#FF9800';
                }}, 2000);
            }}, function(err) {{
                alert('{T("複製失敗，請手動選擇文字複製")}');
            }});
        }});
        </script>
        """
        st.components.v1.html(copy_wealth_html, height=60)
        st.markdown(wealth_text)

    with st.expander(T("八字視覺化 - RPG 裝備鑑定 (遊戲化版)"), expanded=False):
        rpg_text = T(f"""
# Role: 命運裝備鑑定師 (Destiny Inventory Appraiser)

## Profile

- **Style:** 遊戲化、極簡、數據圖表化。

- **Core Philosophy:** 命運是一場 RPG 遊戲，八字是玩家的「初始裝備包」。你的任務不是算命，而是進行「裝備盤點」與「技能分析」，讓玩家一眼看懂自己手裡有什麼牌，缺什麼裝備。

- **Tone:** 專業、俐落，像遊戲中的 NPC 商人或公會導師。

## Constraints & Guidelines (關鍵指令)

1. **裝備化隱喻 (Itemization):**

    - 將十神轉化為遊戲裝備：

    * *七殺/正官 -> 武器 (攻擊力/控制力)*

    * *正印/偏印 -> 防具 (防禦力/抗性)*

    * *食神/傷官 -> 飾品/魔法書 (技能/魔力)*

    * *比肩/劫財 -> 隊友/召喚獸 (體力/肉盾)*

    * *正財/偏財 -> 金幣/資源包 (資源獲取率)*

2. **狀態視覺化 (Status Visualization):**

    - 使用 Markdown 表格展示「裝備欄」。

    - 使用進度條（如 [||||||....]）或等級（S/A/B/C/F）來表示強度。

3. **吉凶即「Buff/Debuff」:**

    - 吉運 = 增益狀態 (Buff) (如：幸運光環、金幣加倍)。

    - 凶運 = 負面狀態 (Debuff) (如：中毒、暈眩、破防)。

4. **拒絕廢話:** 每個欄位只講重點，不要長篇大論。

## Output Format (請嚴格執行此結構)

### 1. 【玩家面板：基礎屬性】 (Player Stats)

*(請根據日主強弱與格局，生成以下表格)*

| 屬性 | 數值/等級 | 鑑定評語 |
| :--- | :--- | :--- |
| 職業定位 | [如：狂戰士 / 補師 / 刺客] | (一句話描述：如「高攻低防，適合單打獨鬥」) |
| HP (身強弱) | [如：80% (極厚)] | (如：血條極厚，耐打，但行動遲緩) |
| MP (能量值) | [如：20% (枯竭)] | (如：缺乏食傷洩秀，才華無法施展) |
| 幸運 (調候) | [如：C 級] | (如：生於寒冬無火，開局難度 Hard 模式) |

### 2. 【背包與裝備盤點】 (Inventory Check)

*(分析八字中的關鍵十神，將其具象化)*

⚔️ **主手武器 (最強的進攻手段 - 月令/透干):**

- **裝備名稱：** [如：七殺・破軍長矛]

- **效果：** [如：攻擊力極高，但有 30% 機率反噬自身（傷身/招小人）。]

🛡️ **身體防具 (保護機制 - 印星):**

- **裝備名稱：** [如：無 (裸裝狀態)]

- **效果：** [如：缺乏印星護體，對外界傷害（批評/壓力）零抗性，容易破防。]

💰 **資源背包 (財星狀態):**

- **狀態：** [如：破洞的錢袋]

- **效果：** [如：比劫奪財，金幣獲取率高，但掉落率也高，存不住錢。]

### 3. 【流年副本預告：(目前年份：{datetime.now().year}年)】 (Yearly Dungeon Preview)

*(**(目前年份：{datetime.now().year}年)**)*

- **副本環境：** [如：火焰山 (火旺之年)]

- **新增 Buff (吉)：** [如：【文昌光環】今年學習技能速度 +50%。]

- **新增 Debuff (凶)：** [如：【驛馬騷動】強制位移，工作或居住地將發生變動，且伴隨混亂。]

- **BOSS 戰預警：** [如：今年最大的敵人是「過度自信」，小心在投資副本中團滅。]

### 4. 【導師的攻略建議】 (Walkthrough Guide)

- **推薦技能樹：** (建議補強什麼五行？例如：點滿「土屬性」防禦，多穿黃色裝備，多與誠信的人組隊。)

- **關鍵道具：** (具體的開運建議，如：佩戴金屬飾品，或往西方地圖移動。)

---

**請準備好，現在請接收用戶的命盤資訊：**
""")
        # 复制到剪贴板按钮 - RPG 裝備鑑定版
        rpg_text_plain = re.sub(r'\*\*([^*]+)\*\*', r'\1', rpg_text)
        rpg_text_plain = re.sub(r'^#{1,4}\s+', '', rpg_text_plain, flags=re.MULTILINE)
        rpg_text_plain = rpg_text_plain.strip()
        rpg_text_escaped = json.dumps(rpg_text_plain)
        
        copy_rpg_html = f"""
        <div>
        <button id="copyRpgBtn" style="width:100%; padding:8px; margin-bottom:10px; background-color:#673AB7; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">
            🎮 {T("複製RPG裝備鑑定提示詞")}
        </button>
        </div>
        <script>
        const copyRpgText = {rpg_text_escaped};
        document.getElementById('copyRpgBtn').addEventListener('click', function() {{
            navigator.clipboard.writeText(copyRpgText).then(function() {{
                const btn = document.getElementById('copyRpgBtn');
                const originalText = btn.innerHTML;
                btn.innerHTML = '✅ {T("已複製！")}';
                btn.style.backgroundColor = '#2196F3';
                setTimeout(function() {{
                    btn.innerHTML = originalText;
                    btn.style.backgroundColor = '#673AB7';
                }}, 2000);
            }}, function(err) {{
                alert('{T("複製失敗，請手動選擇文字複製")}');
            }});
        }});
        </script>
        """
        st.components.v1.html(copy_rpg_html, height=60)
        st.markdown(rpg_text)

    with st.expander(T("八字企業營運診斷書 (商業版)"), expanded=False):
        corporate_text = T(f"""
# Role: 首席企業危機顧問 (Chief Corporate Crisis Consultant)

## Objective

將用戶提供的八字命盤視為一家「控股公司」。請忽略傳統命理術語，完全使用商業管理術語與視覺化圖表來分析這家公司的體質、內部鬥爭以及未來股價趨勢。

## Metaphor Mapping (核心隱喻)

- **日主 (CEO):** 公司的領導核心。身強=獨裁強勢；身弱=依賴董事會/傀儡。

- **印星 (母公司/顧問):** 資源供給、靠山、企業文化。

- **比劫 (股東/合夥人):** 融資來源，但也可能是惡意併購者或冗員。

- **食傷 (研發/行銷部):** 產品創新、對外宣傳、燒錢部門。

- **財星 (財務部/資產):** 現金流、營收、固定資產。

- **官殺 (法務/監管層):** 內部管理、外部法規、市場競爭壓力。

## Visual Requirements (視覺化強制指令)

1. **部門權重圖:** 使用 ▮ 代表該部門在公司內的勢力大小。

2. **績效燈號:** 🟢 (運作良好), 🟡 (需注意), 🔴 (危機/赤字), ⚪ (部門裁撤/無力)。

3. **鬥爭警報:** 若八字有沖剋，視為「部門內鬥」，需具體描述（如：研發部攻擊法務部）。

## Output Format (請嚴格按照此格式輸出)

### 🏢【Bazi Corp. 企業體質診斷報告】

#### 1. 👤 CEO 執行力評估 (Day Master Status)

- **CEO 類型:** [例如：強勢獨裁型 / 溫和守成型 / 被架空傀儡型]

- **掌控權限:** ▮▮▮▮▮▮▮▮░░ [80%] - 高

- **顧問評語:** [一句話描述 CEO 狀態，例如：個人能力極強，不聽股東意見，容易一意孤行。]

#### 2. 📊 部門營運狀況 (Departmental Performance)

*(依據五行十神強弱，繪製組織架構圖)*

| 部門 (十神) | 權力/預算佔比 (Histogram) | 績效 | 營運狀態簡報 |
| :--- | :--- | :--- | :--- |
| 📢 行銷研發 (食傷) | ▮▮▮▮▮▮░░░░ (60%) | 🟢 | 創意十足，產品推陳出新，是獲利主力。 |
| 💰 財務資產 (財星) | ▮▮▮░░░░░░░ (30%) | 🟡 | 現金流尚可，但行銷部門花費過高，存錢不易。 |
| ⚖️ 法務監管 (官殺) | ░░░░░░░░░░ (0%) | 🔴 | 管理真空。公司缺乏制度，員工紀律散漫。 |
| 🤝 股東關係 (比劫) | ▮▮▮▮▮▮▮▮▮░ (90%) | 🔴 | 股權過度稀釋。合夥人太多，意見分歧，容易分贓不均。 |
| 📚 母公司支援 (印星) | ▮▮░░░░░░░░ (20%) | ⚪ | 缺乏外部資源挹注，需自力更生。 |

#### 3. ⚔️ 董事會內部鬥爭 (Internal Conflict Log)

*(分析八字內的沖剋關係)*

⚠️ **重大警報：** [群劫爭財] (股東 vs 財務部)

- **現象：** 股東/競爭對手 (比劫) 正在強行瓜分公司資產 (財星)。

- **商業解讀：** 容易發生合夥糾紛、被朋友借錢不還、或市場出現惡性削價競爭導致利潤歸零。

⚠️ **次要警報：** [傷官見官] (研發部 vs 法務部)

- **現象：** 創新部門 (食傷) 挑戰 監管部門 (官殺)。

- **商業解讀：** 公司為了創新而遊走法律邊緣，容易招惹官司或口舌是非，職場上易頂撞上司。

#### 4. 📈 未來五年股價趨勢 (Stock Forecast)

*(**(目前年份：{datetime.now().year}年)**)*

*(**重要：請結合大運與流年進行綜合判斷，分析大運對原局的影響，以及流年與大運的互動關係。)*

| 財年 | 大運 | 流年干支 | 市場環境 (大運+流年) | 股價預測 | 財務建議 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| {datetime.now().year} | [當前大運] | ... | [大運與流年互動分析] | 📈 強勢上漲 | 行銷部門發力，可擴大投資，獲利極佳。 |
| {datetime.now().year + 1} | [大運] | ... | [大運與流年互動分析] | 📉 過熱回檔 | 市場過熱，競爭者大增 (比劫)，需防守現金流。 |
| {datetime.now().year + 2} | [大運] | ... | [大運與流年互動分析] | ➡️ 盤整持平 | 轉攻為守，整理內部資產，適合置產或儲蓄。 |
| {datetime.now().year + 3} | [大運] | ... | [大運與流年互動分析] | ... | ... |
| {datetime.now().year + 4} | [大運] | ... | [大運與流年互動分析] | ... | ... |

#### 5. 🛠️ 顧問整改方案 (Restructuring Plan)

- **裁員/縮編:** 減少無效社交 (比劫)，避免無意義的應酬。

- **招募/增資:** 需引進強力的「管理專才」(官殺/五行金)，建立公司制度 (自律)。

- **幸運色系 (企業 VI 色):** 白色、金色 (增強管理與決斷力)。

---

**現在，請針對以下八字進行「企業診斷」：**
""")
        # 复制到剪贴板按钮 - 企業營運診斷版
        corporate_text_plain = re.sub(r'\*\*([^*]+)\*\*', r'\1', corporate_text)
        corporate_text_plain = re.sub(r'^#{1,4}\s+', '', corporate_text_plain, flags=re.MULTILINE)
        corporate_text_plain = corporate_text_plain.strip()
        corporate_text_escaped = json.dumps(corporate_text_plain)
        
        copy_corporate_html = f"""
        <div>
        <button id="copyCorporateBtn" style="width:100%; padding:8px; margin-bottom:10px; background-color:#1976D2; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">
            🏢 {T("複製企業診斷提示詞")}
        </button>
        </div>
        <script>
        const copyCorporateText = {corporate_text_escaped};
        document.getElementById('copyCorporateBtn').addEventListener('click', function() {{
            navigator.clipboard.writeText(copyCorporateText).then(function() {{
                const btn = document.getElementById('copyCorporateBtn');
                const originalText = btn.innerHTML;
                btn.innerHTML = '✅ {T("已複製！")}';
                btn.style.backgroundColor = '#2196F3';
                setTimeout(function() {{
                    btn.innerHTML = originalText;
                    btn.style.backgroundColor = '#1976D2';
                }}, 2000);
            }}, function(err) {{
                alert('{T("複製失敗，請手動選擇文字複製")}');
            }});
        }});
        </script>
        """
        st.components.v1.html(copy_corporate_html, height=60)
        st.markdown(corporate_text)

# Global typography and styling
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
    /* 改进输入框样式 */
    .stNumberInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #ddd;
        padding: 8px 12px;
    }
    .stNumberInput > div > div > input:focus {
        border-color: #1E88E5;
        box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.1);
    }
    /* 改进按钮样式 */
    .stButton > button {
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 500;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    /* 性别按钮颜色通过 JavaScript 动态设置 */
    </style>
    """,
    unsafe_allow_html=True,
)

tabs = st.tabs([T("八字排盘"), T("合婚查询")]) 


with tabs[0]:
    st.subheader(T("八字排盘"))
    
    # 日期时间输入区域
    st.markdown("### " + T("出生日期时间"))
    date_cols = st.columns(5)
    with date_cols[0]:
        year = st.number_input(T("年"), value=1990, min_value=1850, max_value=2100, step=1, key="year_input")
    with date_cols[1]:
        month = st.number_input(T("月"), value=1, min_value=1, max_value=12, step=1, key="month_input")
    with date_cols[2]:
        day = st.number_input(T("日"), value=1, min_value=1, max_value=31, step=1, key="day_input")
    with date_cols[3]:
        hour = st.number_input(T("时"), value=12, min_value=0, max_value=23, step=1, key="hour_input")
    with date_cols[4]:
        minute = st.number_input(T("分"), value=0, min_value=0, max_value=59, step=1, key="minute_input")
    
    # 选项和性别选择
    col1, col2 = st.columns(2)
    with col1:
        use_gregorian = st.toggle(T("使用公历输入"), value=True)
        is_leap = st.checkbox(T("闰月 (农历专用)"), value=False)
        advanced_bazi = st.checkbox(T("高级: 直接输入八字(年干支/月干支/日干支/时干支)"))
    
    with col2:
        # 性别选择 - 使用改进的按钮样式
        st.markdown(T("出生性别"))
        
        # 初始化性别选择状态
        if 'gender' not in st.session_state:
            st.session_state.gender = 'male'
        
        
        # 使用 JavaScript 动态设置按钮颜色
        gender_js = """
        <script>
        function setGenderButtonColors() {
            // 查找所有按钮
            const buttons = document.querySelectorAll('button[data-testid*="baseButton"]');
            buttons.forEach(btn => {
                const text = btn.textContent || btn.innerText;
                if (text.includes('♂')) {
                    // 男性按钮 - 蓝色
                    if (btn.getAttribute('data-testid').includes('primary')) {
                        btn.style.backgroundColor = '#42A5F5';
                        btn.style.color = 'white';
                        btn.style.border = '2px solid #1E88E5';
                        btn.style.boxShadow = '0 4px 8px rgba(66, 165, 245, 0.3)';
                    } else {
                        btn.style.backgroundColor = '#E3F2FD';
                        btn.style.color = '#1565C0';
                        btn.style.border = '2px solid #42A5F5';
                    }
                } else if (text.includes('♀')) {
                    // 女性按钮 - 粉色
                    if (btn.getAttribute('data-testid').includes('primary')) {
                        btn.style.backgroundColor = '#EC407A';
                        btn.style.color = 'white';
                        btn.style.border = '2px solid #C2185B';
                        btn.style.boxShadow = '0 4px 8px rgba(236, 64, 122, 0.3)';
                    } else {
                        btn.style.backgroundColor = '#FCE4EC';
                        btn.style.color = '#C2185B';
                        btn.style.border = '2px solid #EC407A';
                    }
                }
            });
        }
        // 页面加载后执行
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', setGenderButtonColors);
        } else {
            setGenderButtonColors();
        }
        // Streamlit 更新后也执行
        setTimeout(setGenderButtonColors, 100);
        setTimeout(setGenderButtonColors, 500);
        </script>
        """
        st.markdown(gender_js, unsafe_allow_html=True)
        
        gender_cols = st.columns(2)
        with gender_cols[0]:
            # 男性按钮 - 蓝色
            if st.button("♂ " + T("男"), key="male_btn", use_container_width=True,
                        type="primary" if st.session_state.gender == 'male' else "secondary"):
                st.session_state.gender = 'male'
                st.rerun()
        
        with gender_cols[1]:
            # 女性按钮 - 粉色
            if st.button("♀ " + T("女"), key="female_btn", use_container_width=True,
                        type="primary" if st.session_state.gender == 'female' else "secondary"):
                st.session_state.gender = 'female'
                st.rerun()
        
        # 设置 gender_choice 用于后续逻辑
        gender_choice = T("男 ♂") if st.session_state.gender == 'male' else T("女 ♀")

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
            # female flag - 使用session state来跟踪性别选择
            if st.session_state.gender == 'female':
                args.append("-n")

        output = format_output(run_script(args))
        st.code(output, language="text")


with tabs[1]:
    st.subheader(T("合婚查询"))
    mode = st.radio(T("合婚类型"), [T("生肖"), T("日柱(六十甲子)")], horizontal=True, index=0)

    if mode.startswith(T("生肖")[:1]):
        shengxiao_list = ["鼠","牛","虎","兔","龙","蛇","马","羊","猴","鸡","狗","猪"]
        zx = st.selectbox(T("选择你的生肖"), shengxiao_list, index=0)
        if st.button(T("计算合婚")):
            args = ["shengxiao.py", zx]
            output = format_output(run_script(args))
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
            output = format_output(run_script(args))
            st.code(output, language="text")




