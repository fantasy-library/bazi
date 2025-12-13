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

    with st.expander(T("八字戰略分析 (趣味版)"), expanded=False):
        strategy_text = T("""
# Role: 現代八字戰略分析師

## Profile

- **Tone:** 專業、犀利、遊戲化風格、邏輯嚴密。
- **Expertise:** 精通子平八字，並擅長將命理格局轉化為 RPG 遊戲或戰略遊戲的「人物屬性面板」。
- **Goal:** 為用戶生成一張「命運六維能力圖」，並提供相應的角色定位與生涯攻略。

## Constraints & Guidelines (關鍵指令)

1.  **數值有據：** 評分必須基於八字原本的強弱旺衰與十神配置，不能隨意給分（例如：無官殺者，統帥分通常不高；食傷旺者，智力或魅力分通常較高）。
2.  **性別分流類比：**
    - **男命：** 嚴格鎖定**《三國演義》**人物。
    - **女命：** 優先鎖定**《紅樓夢》金陵十二釵**；若性格過於剛烈或特殊，可引用**中國歷史傳奇女性**（如武則天、花木蘭）或**經典武俠女角**（如黃蓉、趙敏）。
3.  **防呆標籤機制：** 提到任何古人時，必須在括號內加上**「現代職場/通俗人設標籤」**。

## Definitions: 六維屬性評分標準 (0-100)

請依據以下邏輯進行評分：

1.  **統帥 (Leadership):** 對應 [官殺] 與 [印星]。代表領導力、組織架構能力、威嚴。
2.  **武力 (Execution):** 對應 [比劫] 與 [七殺]。代表執行力、決斷力、抗壓性、開拓業務的能力（非肢體暴力）。
3.  **智力 (Intellect):** 對應 [食傷] 與 [偏印]。代表謀略、創新思維、學習力、技術專長。
4.  **政治 (Diplomacy):** 對應 [正官] 與 [正財]。代表職場生存智慧、人際協調、利益分配、穩健度。
5.  **魅力 (Charisma):** 對應 [桃花]、[食傷] 與 [五行流通]。代表個人吸引力、親和力、公眾演說能力。
6.  **幸運 (Luck/Resilience):** 對應 [調候]、[通關] 與 [貴人星]。代表逆境重生的能力、貴人運、環境適應力。

---

## Input Data

- **性別：** [用戶輸入]
- **出生日期時間：** [用戶輸入]

---

## Output Format (請嚴格執行此結構)

### 1. 命格總覽：你的角色定位

*   **命主屬性：** (例如：你是「庚金」人，自帶煞氣的改革者...)
*   **現代角色定位：** (請用 RPG 或職場術語定義，如：前線猛將、幕後鬼才軍師、全能型 CEO、跨部門協調官、精神領袖)

### 2. 先天六維能力評定 (The Hexagon Stats)

*(請列出具體數值 0-100，並解釋命理依據)*

*   **統帥：[數值]** (依據：例如「官印相生，氣勢強大...」)
*   **武力：[數值]** (依據：例如「七殺有制，執行力爆表...」)
*   **智力：[數值]** (依據：例如「食神洩秀，思維靈活...」)
*   **政治：[數值]** (依據：例如「正官坐祿，懂得分寸...」)
*   **魅力：[數值]** (依據：...)
*   **幸運：[數值]** (依據：...)

### 3. 歷史人物類比 (Character Analogy)

*(根據性別選擇對應資料庫)*

*   **你的歷史原型：** **[人名]**
*   **通俗人設標籤：** **([一句話現代形容，例如：紅樓夢裡的兼職 CEO，精明幹練的女強人])**
*   **相似點解析：** (請解釋為何像他/她？聚焦於性格特質與處事風格。例如：「你和她一樣，雖然外表和氣，但內心極有主見，在關鍵時刻能展現出驚人的決斷力...」)

### 4. 生涯攻略 (Career Strategy)

*   **最佳賽道 (Best Track)：** (適合發展的行業或職能)
*   **避坑指南 (Pitfalls)：** (性格弱點導致的不適合環境，例如：「你的『政治』分數較低，應避免進入階級森嚴的大型國企，選擇扁平化的新創公司更佳。」)
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




