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
    from py_iztro import Astro
    PY_IZTRO_AVAILABLE = True
except ImportError:
    PY_IZTRO_AVAILABLE = False
try:
    from opencc import OpenCC
except Exception:
    OpenCC = None  # graceful fallback if not installed


# 十四主星意象字典
ziwei_14stars_imagery = {
    "紫微": {
        "意象": "帝王端坐於雲端紫殿，掌星辰之令，威而不怒，孤而尊。",
        "重點": "象徵『統御與中心』。具帝王氣，重權責有格局，信念堅定；但易流於孤高與掌控慾重。若能以仁德領導，威而不僭，即為真紫微之光。"
    },
    "天機": {
        "意象": "天上齒輪轉動不息，似風掀心海，靈光閃爍間萬變如棋。",
        "重點": "智慧、靈動、思維敏捷。心思縝密、策略高手；但過於聰慧則多憂，易陷進思慮之網。若能停心定志，機巧轉成智慧之光。"
    },
    "太陽": {
        "意象": "烈日高懸，光芒照耀群山，燃盡己身而成萬物光源。",
        "重點": "熱情與榮耀的化身。正直、正氣、樂於助人，具強烈領導與表現慾；但炙熱過度則傷及自身。需學會溫度的拿捏。"
    },
    "武曲": {
        "意象": "寒鐵鍛成，斷裂亦不屈，一刀斬斷虛妄之霧。",
        "重點": "代表執行力與堅毅。實幹、重紀律、講原則，勇於承擔；但剛過無柔，則難近人情。若能兼具柔軟，堅鋼方可通達。"
    },
    "天同": {
        "意象": "清泉淙淙流過花間，樂天安然，笑看雲舒雲卷。",
        "重點": "和平與包容之象。為人善良、親切、有同理，喜歡和諧；但過於安逸則易失進取心。懂得自我激勵方能化福氣為力量。"
    },
    "廉貞": {
        "意象": "火焰中的紅蓮，媚而堅，燒盡方綻。",
        "重點": "慾望與改革並存。具強烈魅力與行動力，敢愛敢恨；但權慾重、感情複雜。需以紀律淨化慾望，讓熱情化為創造。"
    },
    "天府": {
        "意象": "金庫深藏，流光不顯，厚土孕寶，中藏無盡資源。",
        "重點": "象徵『穩定與守成』。性格踏實、包容、有理性與安全感；但略保守慢熱。若能在安全中勇敢拓展，福祿自然長久。"
    },
    "太陰": {
        "意象": "明月照水，盈虧交替之間，映出人心的柔光與陰影。",
        "重點": "典雅內斂、情感豐富。重感受與美感，擅理財與規劃；但易多愁與退縮。若能平衡情與理，將轉化成深邃的洞察力。"
    },
    "貪狼": {
        "意象": "夜行之狼，眼中閃著慾望與自由之火，遊走在人性邊界。",
        "重點": "慾望、魅力、創造力的代表。多才多藝、社交活躍、敢冒險；但貪玩好奇、易沉迷。若能節制慾念，便能化欲為力，轉俗為華。"
    },
    "巨門": {
        "意象": "黑門深沉，其內光影交錯；一句話，可成刀亦成橋。",
        "重點": "思辨與言語之星。分析力強、口才好、洞察他人；但易爭辯與多疑。當誠語代替辯語，智慧即由口而生。"
    },
    "天相": {
        "意象": "明鏡如水，映照眾生之影，柔光不爭，自有威儀。",
        "重點": "平衡與守德之象。穩重、正直、善輔佐；但缺決斷與主見。若能信任自身價值，輔中亦藏權。"
    },
    "天梁": {
        "意象": "蒼松凌雪，高舉不折，庇蔭萬物於風霜之下。",
        "重點": "象徵仁厚與長壽。重道德、願助人、有智慧，但偶顯保守與教條。學會聽而非說，即可廣納眾智。"
    },
    "七殺": {
        "意象": "獨行的戰士，長劍出鞘，寒光破霧，無懼孤獨。",
        "重點": "破局與行動的力量。果敢、敢冒險、具開創精神；但衝動且孤傲。若能節制剛烈，以勇包柔，方成真英雄。"
    },
    "破軍": {
        "意象": "鳳凰於火中重生，毀舊以立新，破碎而後方見真形。",
        "重點": "變革與創造之代言。勇於冒險、不畏顛覆，具強烈革命精神；但情緒波動大、難長久。善用滅與生的循環，即為破軍之道。"
    }
}

# 十二星座解釋字典
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

tabs = st.tabs([T("八字排盘"), T("紫微排盤"), T("合婚查询")]) 


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
    st.subheader(T("紫微排盤"))
    
    if not PY_IZTRO_AVAILABLE:
        st.warning(T("⚠️ 紫微排盤功能需要安裝 py-iztro 庫。請運行: pip install py-iztro pythonmonkey"))
    else:
        # 检查 ziwei_calc.py 脚本是否存在
        ziwei_calc_script = Path(__file__).parent / "ziwei_calc.py"
        if not ziwei_calc_script.exists():
            st.error(T("⚠️ 找不到 ziwei_calc.py 脚本文件，请确保该文件存在。"))
        
        col1, col2 = st.columns(2)
        with col1:
            ziwei_use_gregorian = st.toggle(T("使用公历输入"), value=True, key="ziwei_gregorian")
            ziwei_year = st.number_input(T("年"), value=2000, min_value=1900, max_value=2100, step=1, key="ziwei_year")
            ziwei_month = st.number_input(T("月"), value=8, min_value=1, max_value=12, step=1, key="ziwei_month")
            ziwei_day = st.number_input(T("日"), value=16, min_value=1, max_value=31, step=1, key="ziwei_day")
        with col2:
            ziwei_gender_choice = st.radio(T("出生性别"), [T("男 ♂"), T("女 ♀")], horizontal=True, index=0, key="ziwei_gender")
            
            # 时辰选择映射
            time_options = {
                T("早子时 (23:00-00:59)"): 0,
                T("丑时 (01:00-02:59)"): 1,
                T("寅时 (03:00-04:59)"): 2,
                T("卯时 (05:00-06:59)"): 3,
                T("辰时 (07:00-08:59)"): 4,
                T("巳时 (09:00-10:59)"): 5,
                T("午时 (11:00-12:59)"): 6,
                T("未时 (13:00-14:59)"): 7,
                T("申时 (15:00-16:59)"): 8,
                T("酉时 (17:00-18:59)"): 9,
                T("戌时 (19:00-20:59)"): 10,
                T("亥时 (21:00-22:59)"): 11,
                T("晚子时 (00:00-00:59)"): 12,
            }
            ziwei_time_option = st.selectbox(T("时辰"), list(time_options.keys()), index=2, key="ziwei_time")
        
        ziwei_calc_btn = st.button(T("计算紫微排盤"), type="primary", key="ziwei_calc")
        
        if ziwei_calc_btn:
            try:
                # 显示开始计算的消息
                st.info(T("🔄 開始計算紫微排盤..."))
                
                with st.spinner(T("正在計算紫微排盤，請稍候...")):
                    date_str = f"{ziwei_year}-{ziwei_month}-{ziwei_day}"
                    gender = T("女") if ziwei_gender_choice.endswith('♀') else T("男")
                    ziwei_time_index = time_options[ziwei_time_option]
                    
                    # 通过子进程调用独立脚本，避免 pythonmonkey 导致 Streamlit 崩溃
                    env = os.environ.copy()
                    env["PYTHONIOENCODING"] = "utf-8"
                    env["PYTHONUTF8"] = "1"
                    
                    result_process = subprocess.run(
                        [sys.executable, str(ziwei_calc_script), 
                         date_str, str(ziwei_time_index), gender, 
                         str(ziwei_use_gregorian).lower(), "zh-TW"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        cwd=str(Path(__file__).parent),
                        env=env,
                        timeout=30
                    )
                    
                    if result_process.returncode != 0:
                        error_output = result_process.stderr or result_process.stdout
                        raise Exception(f"子进程执行失败 (返回码: {result_process.returncode}): {error_output}")
                    
                    # 解析 JSON 结果
                    result_json = json.loads(result_process.stdout.strip())
                    
                    if "error" in result_json:
                        raise Exception(result_json["error"])
                    
                    # 使用 pydantic 模型重新构造结果对象
                    from py_iztro.core.models import AstrolabeModel
                    result = AstrolabeModel(**result_json)
                
                # 显示基本信息
                st.success(T("✓ 排盘成功"))
                st.info(T("**基本信息**"))
                # 查找命宫和身宫位置的主星
                soul_palace_major_stars = ""
                body_palace_major_stars = ""
                for palace in result.palaces:
                    if palace.earthly_branch == result.earthly_branch_of_soul_palace:
                        if palace.major_stars:
                            soul_palace_major_stars = "、".join([
                                star.name + (f"({star.mutagen})" if star.mutagen else "")
                                for star in palace.major_stars
                            ])
                        elif not palace.major_stars:
                            # 从对宫借星
                            opposite_branch_map = {
                                "子": "午", "午": "子", "丑": "未", "未": "丑",
                                "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
                                "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳"
                            }
                            opposite_branch = opposite_branch_map.get(palace.earthly_branch)
                            if opposite_branch:
                                for p in result.palaces:
                                    if p.earthly_branch == opposite_branch and p.major_stars:
                                        soul_palace_major_stars = "、".join([
                                            star.name + (f"({star.mutagen})" if star.mutagen else "")
                                            for star in p.major_stars
                                        ]) + "(借對宮)"
                                        break
                    if palace.earthly_branch == result.earthly_branch_of_body_palace:
                        if palace.major_stars:
                            body_palace_major_stars = "、".join([
                                star.name + (f"({star.mutagen})" if star.mutagen else "")
                                for star in palace.major_stars
                            ])
                        elif not palace.major_stars:
                            # 从对宫借星
                            opposite_branch_map = {
                                "子": "午", "午": "子", "丑": "未", "未": "丑",
                                "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
                                "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳"
                            }
                            opposite_branch = opposite_branch_map.get(palace.earthly_branch)
                            if opposite_branch:
                                for p in result.palaces:
                                    if p.earthly_branch == opposite_branch and p.major_stars:
                                        body_palace_major_stars = "、".join([
                                            star.name + (f"({star.mutagen})" if star.mutagen else "")
                                            for star in p.major_stars
                                        ]) + "(借對宮)"
                                        break
                
                info_text = f"""
性別: {result.gender}
公曆: {result.solar_date}
農曆: {result.lunar_date}
干支: {result.chinese_date}
時辰: {result.time} ({result.time_range})
星座: {result.sign}
生肖: {result.zodiac}
命主: {result.soul} (命宮地支: {result.earthly_branch_of_soul_palace}, 主星: {soul_palace_major_stars or '無'})
身主: {result.body} (身宮地支: {result.earthly_branch_of_body_palace}, 主星: {body_palace_major_stars or '無'})
五行局: {result.five_elements_class}
"""
                st.code(info_text, language="text")
                
                # 显示星座解释
                if result.sign in zodiac_12_traits:
                    zodiac_info = zodiac_12_traits[result.sign]
                    st.subheader(f"【{result.sign}】星座解釋")
                    st.write(f"**意象：**\n{zodiac_info['意象']}")
                    st.write(f"\n**性情總結：**\n{zodiac_info['性情總結']}")
                    st.divider()
                
                # 显示命宫主星的解释
                if soul_palace_major_stars and soul_palace_major_stars != '無':
                    # 提取主星名称（去掉四化和借對宮标记）
                    major_star_names = []
                    for star_str in soul_palace_major_stars.replace("(借對宮)", "").split("、"):
                        # 提取星名（去掉四化标记如"紫微(科)"）
                        star_name = star_str.split("(")[0].strip()
                        if star_name and star_name in ziwei_14stars_imagery:
                            major_star_names.append(star_name)
                    
                    # 显示每个主星的解释（默认展开）
                    for star_name in major_star_names:
                        if star_name in ziwei_14stars_imagery:
                            star_info = ziwei_14stars_imagery[star_name]
                            st.subheader(f"【{star_name}】主星解釋")
                            st.write(f"**意象：**\n{star_info['意象']}")
                            st.write(f"\n**重點：**\n{star_info['重點']}")
                            st.divider()  # 添加分隔线
                
                # 显示十二宫
                st.info(T("**十二宮**"))
                
                # 对宫对应关系（地支）
                opposite_palace_map = {
                    "子": "午", "午": "子",
                    "丑": "未", "未": "丑",
                    "寅": "申", "申": "寅",
                    "卯": "酉", "酉": "卯",
                    "辰": "戌", "戌": "辰",
                    "巳": "亥", "亥": "巳"
                }
                
                palace_info = []
                for palace in result.palaces:
                    # 处理主星：如果本宫没有主星，从对宫借星
                    if not palace.major_stars:
                        # 查找对宫
                        opposite_branch = opposite_palace_map.get(palace.earthly_branch)
                        opposite_palace = None
                        if opposite_branch:
                            for p in result.palaces:
                                if p.earthly_branch == opposite_branch:
                                    opposite_palace = p
                                    break
                        
                        # 如果找到对宫且有主星，则借星
                        if opposite_palace and opposite_palace.major_stars:
                            borrowed_stars = "、".join([
                                star.name + (f"({star.mutagen})" if star.mutagen else "")
                                for star in opposite_palace.major_stars
                            ])
                            major_stars = f"{borrowed_stars}(借對宮)"
                        else:
                            major_stars = ""
                    else:
                        major_stars = "、".join([
                            star.name + (f"({star.mutagen})" if star.mutagen else "")
                            for star in palace.major_stars
                        ])
                    
                    minor_stars = "、".join([
                        star.name + (f"({star.mutagen})" if star.mutagen else "")
                        for star in palace.minor_stars
                    ])
                    adjective_stars = "、".join([star.name for star in palace.adjective_stars])
                    
                    # 替换宫位名称：僕役 -> 部屬，官祿 -> 事業
                    palace_name = palace.name.replace("僕役", "部屬").replace("官祿", "事業")
                    palace_text = f"【{palace_name}】"
                    if palace.is_body_palace:
                        palace_text += " 身宮"
                    if palace.is_original_palace:
                        palace_text += " 來因宮"
                    palace_text += f"\n  地支: {palace.earthly_branch}  天干: {palace.heavenly_stem}"
                    if major_stars:
                        palace_text += f"\n  主星: {major_stars}"
                    if minor_stars:
                        palace_text += f"\n  輔星: {minor_stars}"
                    if adjective_stars:
                        palace_text += f"\n  雜耀: {adjective_stars}"
                    palace_text += f"\n  大限: {palace.decadal.heavenly_stem}{palace.decadal.earthly_branch} ({palace.decadal.range[0]}-{palace.decadal.range[1]}歲)"
                    palace_info.append(palace_text)
                
                st.code("\n".join(palace_info), language="text")
                    
            except subprocess.TimeoutExpired:
                st.error(T("⚠️ 计算超时（超过30秒）。请稍后重试。"))
            except json.JSONDecodeError as e:
                st.error(f"{T('JSON解析失败')}: {str(e)}")
                st.info(T("请检查 ziwei_calc.py 脚本是否正确执行。"))
            except Exception as e:
                import traceback
                error_msg = str(e)
                st.error(f"{T('计算失败')}: {error_msg}")
                with st.expander(T("查看错误详情"), expanded=True):
                    st.exception(e)
                    st.code(traceback.format_exc())
                
                st.info(T("请检查输入的日期是否有效，或尝试使用农历输入。"))


with tabs[2]:
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




