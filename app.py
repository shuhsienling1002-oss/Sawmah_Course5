import streamlit as st
import streamlit.components.v1 as components
import random
import re
import time
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 (System Configuration) ---
st.set_page_config(
    page_title="O losay - 果樹與家", 
    page_icon="🌳", 
    layout="centered"
)

# --- 1. 資料庫 (第 5 課：O losay) ---
VOCAB_MAP = {
    "ira": "有", "ko": "主格標記", "losay": "果樹/作物", "no": "的(屬格)", 
    "loma'": "家", "namo": "你們的", "i": "在", "'a'ayawan": "前面", 
    "niyam": "我們的(排除式)", "kiyafes": "芭樂", "sa'ikoran": "後面", 
    "'alopal": "柿子", "ciheci": "結果實", "to": "時間/介系詞", 
    "mihecahecaan": "每年", "kora": "那個", "hai": "是的", 
    "fangcal": "好/漂亮", "mihecaan": "年/氣候", "anini": "現在/今年", 
    "saka": "所以", "malofic": "豐碩/茂密", "heci": "果實"
}

VOCABULARY = [
    {"amis": "losay", "zh": "果樹/作物", "emoji": "🌳", "root": "losay", "root_zh": "作物"},
    {"amis": "kiyafes", "zh": "芭樂", "emoji": "🍐", "root": "kiyafes", "root_zh": "芭樂"},
    {"amis": "'alopal", "zh": "柿子", "emoji": "🍅", "root": "'alopal", "root_zh": "柿子"},
    {"amis": "'a'ayawan", "zh": "前面", "emoji": "⬆️", "root": "'ayaw", "root_zh": "前"},
    {"amis": "sa'ikoran", "zh": "後面", "emoji": "⬇️", "root": "ikor", "root_zh": "後"},
    {"amis": "ciheci", "zh": "結果實", "emoji": "🍎", "root": "heci", "root_zh": "果實"},
    {"amis": "malofic", "zh": "果實纍纍", "emoji": "🍇", "root": "lofic", "root_zh": "密/多"},
    {"amis": "mihecahecaan", "zh": "每年", "emoji": "🗓️", "root": "miheca", "root_zh": "年"},
    {"amis": "fangcal", "zh": "好/漂亮", "emoji": "✨", "root": "fangcal", "root_zh": "美"},
    {"amis": "ci-", "zh": "有/長出(前綴)", "emoji": "🌱", "root": "ci", "root_zh": "擁有"},
]

SENTENCES = [
    {
        "amis": "Ira ko losay no loma' namo?", 
        "zh": "你們家有果樹嗎？", 
        "note": """
        <br><b>Ira</b>：有 (存在動詞)。
        <br><b>losay</b>：果樹/農作物。
        <br><b>loma' namo</b>：你們家 (<i>namo</i> 你們的)。"""
    },
    {
        "amis": "Ira, i 'a'ayawan no loma' niyam ko kiyafes.", 
        "zh": "有，我們家前面有芭樂樹。", 
        "note": """
        <br><b>i 'a'ayawan</b>：在前面 (方位)。
        <br><b>no loma' niyam</b>：我們家的 (修飾方位)。
        <br><b>kiyafes</b>：芭樂。"""
    },
    {
        "amis": "Ira i sa'ikoran ko 'alopal.", 
        "zh": "後面有柿子樹。", 
        "note": """
        <br><b>i sa'ikoran</b>：在後面 (方位)。
        <br><b>'alopal</b>：柿子。
        <br><b>對比</b>：前院 (<i>'a'ayawan</i>) vs 後院 (<i>sa'ikoran</i>)。"""
    },
    {
        "amis": "Ciheci to mihecahecaan kora losay?", 
        "zh": "那些果樹每年都會結果嗎？", 
        "note": """
        <br><b>Ciheci</b>：長果實 (<i>ci-</i> 有 + <i>heci</i> 果實)。
        <br><b>mihecahecaan</b>：每一年 (重疊表頻率)。
        <br><b>kora</b>：那些 (指示代詞)。"""
    },
    {
        "amis": "Hai, fangcal ko mihecaan anini.", 
        "zh": "是的，今年的氣候很好。", 
        "note": """
        <br><b>fangcal</b>：好/美。
        <br><b>mihecaan</b>：年/年景/氣候。
        <br><b>語意</b>：指風調雨順 (好年冬)。"""
    },
    {
        "amis": "Saka, malofic ko heci.", 
        "zh": "所以，果實纍纍。", 
        "note": """
        <br><b>Saka</b>：所以 (連接詞)。
        <br><b>malofic</b>：茂密的/結實多的 (形容詞)。
        <br><b>heci</b>：果實。"""
    }
]

STORY_DATA = [
    {"amis": "Ira ko losay no loma' namo?", "zh": "你們家有果樹嗎？"},
    {"amis": "Ira, i 'a'ayawan no loma' niyam ko kiyafes.", "zh": "有，我們家前面有芭樂樹。"},
    {"amis": "Ira i sa'ikoran ko 'alopal.", "zh": "後面有柿子樹。"},
    {"amis": "Ciheci to mihecahecaan kora losay?", "zh": "那些果樹每年都會結果嗎？"},
    {"amis": "Hai, fangcal ko mihecaan anini.", "zh": "是的，今年的氣候很好。"},
    {"amis": "Saka, malofic ko heci.", "zh": "所以，果實纍纍。"}
]

# --- 2. 視覺系統 (CSS 注入 - Orchard Fresh Theme) ---
st.markdown("""
    <style>
    /* 引入 Fredoka One (圓潤可愛) 和 Noto Sans TC */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Noto+Sans+TC:wght@300;500;700&display=swap');
    
    /* 背景：極致淺綠，清新感 */
    .stApp { background-color: #F1F8E9; color: #33691E; font-family: 'Noto Sans TC', sans-serif; }
    
    /* 頭部：果園風格 */
    .header-container { 
        background: #FFFFFF; 
        border: 3px solid #8BC34A;
        border-bottom: 6px solid #8BC34A;
        box-shadow: 0 4px 10px rgba(139, 195, 74, 0.3); 
        border-radius: 20px; 
        padding: 25px; 
        text-align: center; 
        margin-bottom: 30px; 
    }
    
    .main-title { 
        font-family: 'Fredoka One', cursive; 
        color: #8BC34A; 
        font-size: 42px; 
        text-shadow: 2px 2px 0px #DCEDC8; 
        margin-bottom: 5px; 
        letter-spacing: 1px;
    }
    
    .sub-title { 
        color: #FF7043; 
        font-size: 16px; 
        font-weight: bold;
        background: #FFF3E0;
        padding: 5px 15px;
        border-radius: 15px;
        display: inline-block;
        border: 2px dashed #FF7043;
    }
    
    /* Tab 樣式：圓潤標籤 */
    .stTabs [data-baseweb="tab"] { 
        color: #7CB342 !important; 
        font-family: 'Fredoka One', cursive;
        font-size: 18px;
    }
    .stTabs [aria-selected="true"] { 
        border-bottom: 4px solid #FF7043 !important; 
        color: #FF7043 !important; 
    }
    
    /* 按鈕：果實色 */
    .stButton>button { 
        border: none !important; 
        background: #8BC34A !important; 
        color: #FFF !important; 
        font-family: 'Fredoka One', cursive !important;
        font-size: 18px !important;
        width: 100%; 
        border-radius: 15px; 
        transition: 0.2s; 
        box-shadow: 0 4px 0px #689F38;
    }
    .stButton>button:hover { 
        background: #9CCC65 !important; 
        transform: translateY(-2px);
        box-shadow: 0 6px 0px #689F38;
    }
    .stButton>button:active {
        transform: translateY(2px);
        box-shadow: 0 2px 0px #689F38;
    }
    
    /* 測驗卡片：野餐墊風格 */
    .quiz-card { 
        background: #FFFFFF; 
        border: 2px solid #AED581; 
        padding: 20px; 
        border-radius: 15px; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .quiz-tag { 
        background: #F06292; 
        color: #FFF; 
        padding: 4px 10px; 
        border-radius: 10px; 
        font-weight: bold; 
        font-size: 14px; 
        margin-right: 10px; 
        font-family: 'Fredoka One', cursive;
    }
    
    /* 翻譯區塊：便條紙風格 */
    .zh-translation-block {
        background: #FFF9C4; /* 淺黃色 */
        border-left: 5px solid #FDD835;
        padding: 20px;
        margin-top: 0px; 
        border-radius: 0 10px 10px 0;
        color: #5D4037;
        font-size: 16px;
        line-height: 2.0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 核心技術：沙盒渲染引擎 (v9.5 - Orchard Edition) ---
def get_html_card(item, type="word"):
    pt = "100px" if type == "full_amis_block" else "80px"
    mt = "-40px" if type == "full_amis_block" else "-30px" 

    style_block = f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Noto+Sans+TC:wght@300;500;700&display=swap');
        body {{ background-color: transparent; color: #33691E; font-family: 'Noto Sans TC', sans-serif; margin: 0; padding: 5px; padding-top: {pt}; overflow-x: hidden; }}
        
        /* 互動單字：果綠波浪線 */
        .interactive-word {{ position: relative; display: inline-block; text-decoration: underline; text-decoration-color: #8BC34A; text-decoration-style: wavy; cursor: pointer; margin: 0 3px; color: #33691E; transition: 0.3s; font-size: 19px; font-weight: 500; }}
        .interactive-word:hover {{ color: #FF7043; text-decoration-color: #FF7043; }}
        
        .interactive-word .tooltip-text {{ visibility: hidden; min-width: 80px; background-color: #FFCC80; color: #E65100; text-align: center; border: 2px solid #E65100; border-radius: 10px; padding: 5px; position: absolute; z-index: 100; bottom: 145%; left: 50%; transform: translateX(-50%); opacity: 0; transition: opacity 0.3s; font-size: 14px; white-space: nowrap; box-shadow: 0 4px 10px rgba(0,0,0,0.1); font-weight: bold; }}
        .interactive-word:hover .tooltip-text {{ visibility: visible; opacity: 1; }}
        
        .play-btn-inline {{ background: #8BC34A; border: none; color: #FFF; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; margin-left: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; transition: 0.3s; vertical-align: middle; box-shadow: 0 2px 0 #558B2F; }}
        .play-btn-inline:hover {{ background: #FF7043; box-shadow: 0 2px 0 #BF360C; transform: scale(1.1); }}
        
        /* 單字卡樣式 - 圓角卡片 */
        .word-card-static {{ background: #FFFFFF; border: 2px solid #C5E1A5; border-bottom: 4px solid #C5E1A5; padding: 15px; border-radius: 15px; display: flex; justify-content: space-between; align-items: center; margin-top: {mt}; height: 100px; box-sizing: border-box; }}
        .wc-root-tag {{ font-size: 12px; background: #DCEDC8; color: #558B2F; padding: 3px 8px; border-radius: 8px; font-weight: bold; margin-right: 5px; }}
        .wc-amis {{ color: #558B2F; font-size: 24px; font-weight: bold; margin: 5px 0; font-family: 'Fredoka One', cursive; }}
        .wc-zh {{ color: #8D6E63; font-size: 16px; }}
        .play-btn-large {{ background: #FF7043; border: none; color: #FFF; border-radius: 50%; width: 42px; height: 42px; cursor: pointer; font-size: 20px; transition: 0.2s; box-shadow: 0 3px 0 #BF360C; }}
        .play-btn-large:hover {{ background: #FF8A65; transform: scale(1.1); }}
        
        .amis-full-block {{ line-height: 2.2; font-size: 18px; margin-top: {mt}; }}
        .sentence-row {{ margin-bottom: 12px; display: block; }}
    </style>
    <script>
        function speak(text) {{ window.speechSynthesis.cancel(); var msg = new SpeechSynthesisUtterance(); msg.text = text; msg.lang = 'id-ID'; msg.rate = 0.9; window.speechSynthesis.speak(msg); }}
    </script>"""

    header = f"<!DOCTYPE html><html><head>{style_block}</head><body>"
    body = ""
    
    if type == "word":
        v = item
        body = f"""<div class="word-card-static">
            <div>
                <div style="margin-bottom:5px;"><span class="wc-root-tag">ROOT: {v['root']}</span> <span style="font-size:12px; color:#9E9E9E;">({v['root_zh']})</span></div>
                <div class="wc-amis">{v['emoji']} {v['amis']}</div>
                <div class="wc-zh">{v['zh']}</div>
            </div>
            <button class="play-btn-large" onclick="speak('{v['amis'].replace("'", "\\'")}')">🔊</button>
        </div>"""

    elif type == "full_amis_block": 
        all_sentences_html = []
        for sentence_data in item:
            s_amis = sentence_data['amis']
            words = s_amis.split()
            parts = []
            for w in words:
                clean_word = re.sub(r"[^\w']", "", w).lower()
                translation = VOCAB_MAP.get(clean_word, "")
                js_word = clean_word.replace("'", "\\'") 
                
                if translation:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
                else:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
                parts.append(chunk)
            
            full_amis_js = s_amis.replace("'", "\\'")
            sentence_html = f"""
            <div class="sentence-row">
                {' '.join(parts)}
                <button class="play-btn-inline" onclick="speak('{full_amis_js}')" title="播放此句">🔊</button>
            </div>
            """
            all_sentences_html.append(sentence_html)
            
        body = f"""<div class="amis-full-block">{''.join(all_sentences_html)}</div>"""
    
    elif type == "sentence": 
        s = item
        words = s['amis'].split()
        parts = []
        for w in words:
            clean_word = re.sub(r"[^\w']", "", w).lower()
            translation = VOCAB_MAP.get(clean_word, "")
            js_word = clean_word.replace("'", "\\'") 
            
            if translation:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
            else:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
            parts.append(chunk)
            
        full_js = s['amis'].replace("'", "\\'")
        body = f'<div style="font-size: 18px; line-height: 1.6; margin-top: {mt};">{" ".join(parts)}</div><button style="margin-top:10px; background:#FF7043; border:none; color:#FFF; padding:6px 15px; border-radius:20px; cursor:pointer; font-family:Fredoka One; box-shadow: 0 3px 0 #BF360C;" onclick="speak(`{full_js}`)">▶ 播放整句</button>'

    return header + body + "</body></html>"

# --- 4. 測驗生成引擎 ---
def generate_quiz():
    questions = []
    
    # 1. 聽音辨義
    q1 = random.choice(VOCABULARY)
    q1_opts = [q1['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q1], 2)]
    random.shuffle(q1_opts)
    questions.append({"type": "listen", "tag": "🎧 聽音辨義", "text": "請聽語音，選擇正確的單字", "audio": q1['amis'], "correct": q1['amis'], "options": q1_opts})
    
    # 2. 中翻阿
    q2 = random.choice(VOCABULARY)
    q2_opts = [q2['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q2], 2)]
    random.shuffle(q2_opts)
    questions.append({"type": "trans", "tag": "🧩 中翻阿", "text": f"請選擇「<span style='color:#FF7043'>{q2['zh']}</span>」的阿美語", "correct": q2['amis'], "options": q2_opts})
    
    # 3. 阿翻中
    q3 = random.choice(VOCABULARY)
    q3_opts = [q3['zh']] + [v['zh'] for v in random.sample([x for x in VOCABULARY if x != q3], 2)]
    random.shuffle(q3_opts)
    questions.append({"type": "trans_a2z", "tag": "🔄 阿翻中", "text": f"單字 <span style='color:#FF7043'>{q3['amis']}</span> 的意思是？", "correct": q3['zh'], "options": q3_opts})

    # 4. 詞根偵探
    q4 = random.choice(VOCABULARY)
    other_roots = list(set([v['root'] for v in VOCABULARY if v['root'] != q4['root']]))
    if len(other_roots) < 2: other_roots += ["roma", "lalan", "cidal"]
    q4_opts = [q4['root']] + random.sample(other_roots, 2)
    random.shuffle(q4_opts)
    questions.append({"type": "root", "tag": "🧬 詞根偵探", "text": f"單字 <span style='color:#FF7043'>{q4['amis']}</span> 的詞根是？", "correct": q4['root'], "options": q4_opts, "note": f"詞根意思：{q4['root_zh']}"})
    
    # 5. 語感聽解
    q5 = random.choice(STORY_DATA)
    questions.append({"type": "listen_sent", "tag": "🔊 語感聽解", "text": "請聽句子，選擇正確的中文翻譯", "audio": q5['amis'], "correct": q5['zh'], "options": [q5['zh']] + [s['zh'] for s in random.sample([x for x in STORY_DATA if x != q5], 2)]})

    # 6. 句型翻譯
    q6 = random.choice(STORY_DATA)
    q6_opts = [q6['amis']] + [s['amis'] for s in random.sample([x for x in STORY_DATA if x != q6], 2)]
    random.shuffle(q6_opts)
    questions.append({"type": "sent_trans", "tag": "📝 句型翻譯", "text": f"請選擇中文「<span style='color:#FF7043'>{q6['zh']}</span>」對應的阿美語", "correct": q6['amis'], "options": q6_opts})

    # 7. 克漏字
    q7 = random.choice(STORY_DATA)
    words = q7['amis'].split()
    valid_indices = []
    for i, w in enumerate(words):
        clean_w = re.sub(r"[^\w']", "", w).lower()
        if clean_w in VOCAB_MAP:
            valid_indices.append(i)
    
    if valid_indices:
        target_idx = random.choice(valid_indices)
        target_raw = words[target_idx]
        target_clean = re.sub(r"[^\w']", "", target_raw).lower()
        
        words_display = words[:]
        words_display[target_idx] = "______"
        q_text = " ".join(words_display)
        
        correct_ans = target_clean
        distractors = [k for k in VOCAB_MAP.keys() if k != correct_ans and len(k) > 2]
        if len(distractors) < 2: distractors += ["kako", "ira"]
        opts = [correct_ans] + random.sample(distractors, 2)
        random.shuffle(opts)
        
        questions.append({"type": "cloze", "tag": "🕳️ 文法克漏字", "text": f"請填空：<br><span style='color:#33691E; font-size:18px;'>{q_text}</span><br><span style='color:#8D6E63; font-size:14px;'>{q7['zh']}</span>", "correct": correct_ans, "options": opts})
    else:
        questions.append(questions[0]) 

    questions.append(random.choice(questions[:4])) 
    random.shuffle(questions)
    return questions

def play_audio_backend(text):
    try:
        tts = gTTS(text=text, lang='id'); fp = BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    except: pass

# --- 5. UI 呈現層 ---
st.markdown("""
<div class="header-container">
    <h1 class="main-title">O losay</h1>
    <div class="sub-title">第 5 課：果樹與家</div>
    <div style="font-size: 12px; margin-top:10px; color:#7CB342; font-family: 'Fredoka One', cursive;">Code-CRF v6.4 | Theme: Orchard Fresh</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🌳 互動課文", 
    "🍐 核心單字", 
    "🧬 句型解析", 
    "⚔️ 實戰測驗"
])

with tab1:
    st.markdown("### // 文章閱讀")
    st.caption("👆 點擊單字可聽發音並查看翻譯")
    
    st.markdown("""<div style="background:#FFFFFF; padding:10px; border: 2px solid #C5E1A5; border-radius:15px;">""", unsafe_allow_html=True)
    components.html(get_html_card(STORY_DATA, type="full_amis_block"), height=400, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    zh_content = "<br>".join([item['zh'] for item in STORY_DATA])
    st.markdown(f"""
    <div class="zh-translation-block">
        {zh_content}
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("### // 單字與詞根")
    for v in VOCABULARY:
        components.html(get_html_card(v, type="word"), height=150)

with tab3:
    st.markdown("### // 語法結構分析")
    for s in SENTENCES:
        st.markdown("""<div style="background:#FFFFFF; padding:15px; border:2px dashed #AED581; border-radius: 15px; margin-bottom:15px;">""", unsafe_allow_html=True)
        components.html(get_html_card(s, type="sentence"), height=160)
        st.markdown(f"""
        <div style="color:#33691E; font-size:16px; margin-bottom:10px; border-top:1px solid #AED581; padding-top:10px;">{s['zh']}</div>
        <div style="color:#689F38; font-size:14px; line-height:1.8; border-top:1px dashed #AED581; padding-top:5px;"><span style="color:#FF7043; font-family:Fredoka One; font-weight:bold;">ANALYSIS:</span> {s.get('note', '')}</div>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = generate_quiz()
        st.session_state.quiz_step = 0; st.session_state.quiz_score = 0
    
    if st.session_state.quiz_step < len(st.session_state.quiz_questions):
        q = st.session_state.quiz_questions[st.session_state.quiz_step]
        st.markdown(f"""<div class="quiz-card"><div style="margin-bottom:10px;"><span class="quiz-tag">{q['tag']}</span> <span style="color:#8D6E63;">Q{st.session_state.quiz_step + 1}</span></div><div style="font-size:18px; color:#33691E; margin-bottom:10px;">{q['text']}</div></div>""", unsafe_allow_html=True)
        if 'audio' in q: play_audio_backend(q['audio'])
        opts = q['options']; cols = st.columns(min(len(opts), 3))
        for i, opt in enumerate(opts):
            with cols[i % 3]:
                if st.button(opt, key=f"q_{st.session_state.quiz_step}_{i}"):
                    if opt.lower() == q['correct'].lower():
                        st.success("✅ 正確 (Correct)"); st.session_state.quiz_score += 1
                    else:
                        st.error(f"❌ 錯誤 - 正解: {q['correct']}"); 
                        if 'note' in q: st.info(q['note'])
                    time.sleep(1.5); st.session_state.quiz_step += 1; st.rerun()
    else:
        st.markdown(f"""<div style="text-align:center; padding:30px; border:4px solid #8BC34A; border-radius:20px; background:#FFFFFF;"><h2 style="color:#8BC34A; font-family:Fredoka One;">MISSION COMPLETE</h2><p style="font-size:20px; color:#558B2F;">得分: {st.session_state.quiz_score} / {len(st.session_state.quiz_questions)}</p></div>""", unsafe_allow_html=True)
        if st.button("🔄 重新挑戰 (Reboot)"): del st.session_state.quiz_questions; st.rerun()

st.markdown("---")
st.caption("Powered by Code-CRF v6.4 | Architecture: Chief Architect")
