import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import json
import requests

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="💪 Smart AI Gym Dashboard",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS — Dark Neon Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Exo+2:wght@400;700;900&display=swap');

/* Background */
.stApp {
    background: linear-gradient(135deg, #060b14 0%, #0a0f1e 50%, #060b14 100%);
    font-family: 'Rajdhani', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #090e1a 100%) !important;
    border-right: 1px solid #1e2d40;
}
[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8 !important;
    font-size: 15px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    padding: 4px 0 !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    color: #60a5fa !important;
}

/* Headers */
h1, h2, h3 {
    font-family: 'Exo 2', sans-serif !important;
    letter-spacing: 1px;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #0d1117;
    border: 1px solid #1e2d40;
    border-radius: 12px;
    padding: 16px !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1e40af, #1d4ed8) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(29, 78, 216, 0.4) !important;
}

/* Text Input */
.stTextInput > div > input, .stTextArea textarea {
    background: #0d1117 !important;
    border: 1px solid #1e2d40 !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 15px !important;
}

/* Checkboxes */
.stCheckbox label {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #cbd5e1 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #64748b !important;
}
.stTabs [aria-selected="true"] {
    color: #60a5fa !important;
}

/* Divider */
hr {
    border-color: #1e2d40 !important;
}

/* Info/Success/Warning boxes */
.stAlert {
    border-radius: 12px !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* Dataframe */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden;
}

/* Select box */
.stSelectbox > div {
    background: #0d1117 !important;
    border: 1px solid #1e2d40 !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# EXERCISE DATA
# ─────────────────────────────────────────────
MUSCLE_DATA = {
    "💪 Biceps": {
        "color": "#ef4444",
        "exercises": [
            {"name": "Dumbbell Curl", "sets": "3×12", "tip": "Elbow fixed रखो, shoulder नहीं हिलाओ"},
            {"name": "Barbell Curl", "sets": "4×10", "tip": "Back straight, controlled movement"},
            {"name": "Hammer Curl", "sets": "3×12", "tip": "Neutral grip, brachialis target"},
            {"name": "Preacher Curl", "sets": "3×10", "tip": "Full extension लो, slow negative"},
            {"name": "Concentration Curl", "sets": "3×15", "tip": "Mind-muscle connection पर focus"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+biceps+workout+hindi",
        "info": "💡 Biceps = Arm का front muscle. Peak बनाने के लिए Preacher Curl best है।"
    },
    "🦾 Triceps": {
        "color": "#f97316",
        "exercises": [
            {"name": "Tricep Pushdown", "sets": "4×12", "tip": "Elbows body से touch रहें"},
            {"name": "Overhead Extension", "sets": "3×12", "tip": "Core tight, elbow flare मत करो"},
            {"name": "Skull Crushers", "sets": "3×10", "tip": "Weight को control करो, don't drop"},
            {"name": "Close Grip Bench", "sets": "3×10", "tip": "Grip shoulder-width रखो"},
            {"name": "Tricep Dips", "sets": "3×15", "tip": "Chest को forward lean मत करो"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+triceps+workout+hindi",
        "info": "💡 Triceps = Arm का 2/3 हिस्सा! Arms बड़े करने हैं तो Triceps पर ज्यादा focus करो।"
    },
    "🏔️ Shoulder": {
        "color": "#eab308",
        "exercises": [
            {"name": "Overhead Press", "sets": "4×10", "tip": "Core brace, knees slightly bent"},
            {"name": "Lateral Raise", "sets": "3×15", "tip": "Slow & controlled, elbow slight bend"},
            {"name": "Front Raise", "sets": "3×12", "tip": "Don't use momentum, controlled"},
            {"name": "Arnold Press", "sets": "3×12", "tip": "Full rotation of wrist"},
            {"name": "Rear Delt Fly", "sets": "3×15", "tip": "Bend forward 45°, elbow wide"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+shoulder+workout+hindi",
        "info": "💡 3D Shoulders चाहिए? तीनों heads: Front, Side, Rear — तीनों train करो।"
    },
    "🫁 Chest": {
        "color": "#ec4899",
        "exercises": [
            {"name": "Flat Bench Press", "sets": "4×10", "tip": "Arch back slightly, feet flat"},
            {"name": "Incline Dumbbell Press", "sets": "3×12", "tip": "Upper chest के लिए best"},
            {"name": "Cable Flyes", "sets": "3×15", "tip": "Full stretch at bottom"},
            {"name": "Push-Ups", "sets": "3×20", "tip": "Elbows 45°, chest to floor"},
            {"name": "Decline Press", "sets": "3×12", "tip": "Lower chest target"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+chest+workout+hindi",
        "info": "💡 Big Chest = Compound movements first (Bench Press), then isolation (Flyes)।"
    },
    "🦵 Legs": {
        "color": "#22c55e",
        "exercises": [
            {"name": "Squats", "sets": "4×12", "tip": "Knees over toes, deep squat लो"},
            {"name": "Leg Press", "sets": "4×15", "tip": "Full depth, knees don't cave in"},
            {"name": "Romanian Deadlift", "sets": "3×12", "tip": "Hamstring stretch feel करो"},
            {"name": "Leg Extension", "sets": "3×15", "tip": "Quad squeeze at top"},
            {"name": "Calf Raises", "sets": "4×20", "tip": "Slow negatives, full range"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+leg+workout+hindi",
        "info": "💡 Leg day skip मत करो! Body का 70% muscle legs में है — testosterone boost होता है।"
    },
    "🏛️ Back": {
        "color": "#3b82f6",
        "exercises": [
            {"name": "Deadlift", "sets": "4×6", "tip": "Back flat, hinge at hips"},
            {"name": "Pull-Ups", "sets": "3×10", "tip": "Full extension, chin over bar"},
            {"name": "Barbell Row", "sets": "4×10", "tip": "Elbows back, squeeze lats"},
            {"name": "Lat Pulldown", "sets": "3×12", "tip": "Chest up, lean back slightly"},
            {"name": "Seated Cable Row", "sets": "3×15", "tip": "Shoulder blades squeeze"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+back+workout+hindi",
        "info": "💡 V-taper चाहिए? Lat Pulldown + Pull-Ups = width, Rows = thickness।"
    },
    "🏃 Cardio": {
        "color": "#a855f7",
        "exercises": [
            {"name": "Treadmill Run", "sets": "20 min", "tip": "Incline 5-10% add करो"},
            {"name": "Jump Rope", "sets": "5×3 min", "tip": "Wrist से jump करो, arms still"},
            {"name": "Cycling", "sets": "30 min", "tip": "Medium resistance, steady pace"},
            {"name": "HIIT Intervals", "sets": "20 min", "tip": "30s max effort, 30s rest"},
            {"name": "Stair Climber", "sets": "15 min", "tip": "Don't hold rails, steady"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+cardio+fat+loss+hindi",
        "info": "💡 Fat loss के लिए HIIT > Steady cardio। Less time, more results।"
    },
    "🧘 Yoga": {
        "color": "#06b6d4",
        "exercises": [
            {"name": "Sun Salutation", "sets": "5 rounds", "tip": "Slow breathing, each pose hold"},
            {"name": "Warrior Pose", "sets": "Hold 30s", "tip": "Hip alignment, knee over ankle"},
            {"name": "Downward Dog", "sets": "Hold 1 min", "tip": "Heels push down, spine long"},
            {"name": "Child's Pose", "sets": "Hold 2 min", "tip": "Forehead to floor, arms extended"},
            {"name": "Shavasana", "sets": "5 min", "tip": "Complete body relaxation"},
        ],
        "video": "https://www.youtube.com/results?search_query=yoga+for+beginners+hindi",
        "info": "💡 Yoga = Recovery + Flexibility + Mental Peace। हर workout के बाद 10 min yoga करो।"
    },
}

# ─────────────────────────────────────────────
# SESSION STATE INITIALIZE
# ─────────────────────────────────────────────
if "checked" not in st.session_state:
    st.session_state.checked = {}
if "workout_log" not in st.session_state:
    st.session_state.workout_log = []
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "ai_response" not in st.session_state:
    st.session_state.ai_response = ""

# ─────────────────────────────────────────────
# GOOGLE SHEETS CONNECT
# ─────────────────────────────────────────────
def get_sheet():
    try:
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        # Streamlit secrets से credentials लो
        creds_dict = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("Gym Workout Log").sheet1
        return sheet
    except Exception as e:
        return None

def save_to_sheet(date_str, time_str, body_part, exercise):
    sheet = get_sheet()
    if sheet:
        try:
            sheet.append_row([date_str, time_str, body_part, exercise, "✔"])
            return True
        except:
            return False
    return False

# ─────────────────────────────────────────────
# GROQ AI FUNCTION
# ─────────────────────────────────────────────
def ask_ai_groq(prompt, muscle_group):
    try:
        groq_key = st.secrets.get("GROQ_API_KEY", "")
        if not groq_key:
            return "⚠️ GROQ_API_KEY secrets में add करो।"

        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }
        system_msg = f"""तुम एक expert Hindi-speaking fitness coach हो।
आज user {muscle_group} workout कर रहा है।
हमेशा Hindi/Hinglish में जवाब दो।
Practical, actionable advice दो।
Response 150-200 words में रखो।
Emojis use करो।"""

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 400,
            "temperature": 0.7
        }
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"❌ Error: {response.status_code}"
    except Exception as e:
        return f"❌ AI error: {str(e)}"

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px;'>
        <div style='font-size:40px'>⚡</div>
        <div style='font-family: Exo 2, sans-serif; font-size:22px; font-weight:900;
                    background: linear-gradient(135deg, #60a5fa, #a78bfa);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                    letter-spacing: 2px;'>GYM AI</div>
        <div style='color:#475569; font-size:11px; margin-top:4px;'>Smart Fitness Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🏋️ Workout Menu")
    menu = st.radio(
        "Select Body Part",
        list(MUSCLE_DATA.keys()),
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Streak Counter
    total_done = sum(1 for v in st.session_state.checked.values() if v)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🔥 Streak", f"{st.session_state.streak} days")
    with col2:
        st.metric("✅ Done", f"{total_done}")

    st.markdown("---")

    # All Groups Progress
    st.markdown("**📊 सभी Groups**")
    for grp, data in MUSCLE_DATA.items():
        done = sum(1 for ex in data["exercises"]
                   if st.session_state.checked.get(f"{grp}_{ex['name']}", False))
        total = len(data["exercises"])
        pct = int((done / total) * 100)
        color = data["color"]
        st.markdown(f"""
        <div style='margin-bottom:8px'>
            <div style='display:flex; justify-content:space-between; font-size:12px;
                        color:#94a3b8; margin-bottom:3px;'>
                <span>{grp}</span>
                <span style='color:{color}; font-weight:700'>{pct}%</span>
            </div>
            <div style='background:#1e2d40; border-radius:99px; height:5px;'>
                <div style='width:{pct}%; height:100%; background:{color};
                            border-radius:99px; transition:width 0.5s;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='color:#475569; font-size:11px; text-align:center; padding-top:4px;'>
        Made with ❤️ for Fitness<br>Powered by AI
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────
muscle = MUSCLE_DATA[menu]
color = muscle["color"]
exercises = muscle["exercises"]

# Header
done_count = sum(1 for ex in exercises
                 if st.session_state.checked.get(f"{menu}_{ex['name']}", False))
total_count = len(exercises)
pct = int((done_count / total_count) * 100)

st.markdown(f"""
<div style='padding: 20px 0 10px;'>
    <h1 style='margin:0; font-size:36px; font-weight:900;
               background: linear-gradient(135deg, {color}, {color}88);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;
               font-family: Exo 2, sans-serif; letter-spacing:2px;'>
        {menu.upper()} WORKOUT
    </h1>
    <p style='color:#64748b; margin:4px 0 0; font-size:14px;'>
        {date.today().strftime("%A, %d %B %Y")} &nbsp;|&nbsp;
        {done_count}/{total_count} exercises complete
    </p>
</div>
""", unsafe_allow_html=True)

# Progress Bar
st.markdown(f"""
<div style='margin-bottom:20px;'>
    <div style='display:flex; justify-content:space-between; margin-bottom:6px;'>
        <span style='color:#94a3b8; font-size:13px;'>आज की Progress</span>
        <span style='color:{color}; font-weight:700; font-size:13px;'>{pct}% Complete</span>
    </div>
    <div style='background:#1e2d40; border-radius:99px; height:10px; overflow:hidden;'>
        <div style='width:{pct}%; height:100%;
                    background: linear-gradient(90deg, {color}, {color}99);
                    border-radius:99px;
                    box-shadow: 0 0 10px {color}66;
                    transition: width 0.5s ease;'></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Info Box
st.info(muscle["info"])

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🏋️ Workout", "🤖 AI Coach", "📊 Log & Stats"])

# ══════════════════════════════════════════════
# TAB 1 — WORKOUT
# ══════════════════════════════════════════════
with tab1:
    col_ex, col_right = st.columns([3, 2])

    with col_ex:
        st.markdown(f"### Exercise List")

        for ex in exercises:
            key = f"{menu}_{ex['name']}"
            is_done = st.session_state.checked.get(key, False)

            # Colored card background
            bg = f"{color}18" if is_done else "#0d1117"
            border = color if is_done else "#1e2d40"
            name_color = color if is_done else "#e2e8f0"
            strike = "line-through" if is_done else "none"

            col_check, col_info, col_sets = st.columns([1, 6, 2])

            with col_check:
                checked = st.checkbox("", value=is_done, key=f"cb_{key}")
                if checked != is_done:
                    st.session_state.checked[key] = checked
                    if checked:
                        # Log entry
                        now = datetime.now()
                        log_entry = {
                            "Date": now.strftime("%d-%m-%Y"),
                            "Time": now.strftime("%I:%M %p"),
                            "Body Part": menu.split(" ", 1)[1] if " " in menu else menu,
                            "Exercise": ex["name"],
                            "Status": "✔ Done"
                        }
                        st.session_state.workout_log.insert(0, log_entry)
                        # Google Sheet save
                        save_to_sheet(
                            log_entry["Date"],
                            log_entry["Time"],
                            log_entry["Body Part"],
                            log_entry["Exercise"]
                        )
                        st.toast(f"✅ {ex['name']} logged!", icon="💪")
                    st.rerun()

            with col_info:
                st.markdown(f"""
                <div style='padding: 8px 12px; border-radius:10px;
                            background:{bg}; border:1px solid {border};'>
                    <div style='font-size:15px; font-weight:700;
                                color:{name_color}; text-decoration:{strike};'>
                        {ex["name"]}
                    </div>
                    <div style='font-size:12px; color:#64748b; margin-top:2px;'>
                        💡 {ex["tip"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_sets:
                st.markdown(f"""
                <div style='padding: 8px; text-align:center; border-radius:10px;
                            background:{color}22; border:1px solid {color}44;
                            color:{color}; font-weight:700; font-size:13px; margin-top:2px;'>
                    {ex["sets"]}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("")

        st.markdown("---")

        # YouTube Button
        st.markdown(f"""
        <a href="{muscle['video']}" target="_blank" style="text-decoration:none;">
            <div style='background: linear-gradient(135deg, #cc0000, #ff0000);
                        color:white; padding:14px 20px; border-radius:12px;
                        text-align:center; font-size:16px; font-weight:700;
                        font-family: Rajdhani, sans-serif; letter-spacing:1px;
                        cursor:pointer; box-shadow: 0 4px 20px #ff000044;'>
                🎥 YouTube पर {menu} Workout देखो →
            </div>
        </a>
        """, unsafe_allow_html=True)

    with col_right:
        # Weekly Tracker
        st.markdown("### 📅 इस हफ्ते")
        days_hindi = {
            "Mon": "सोम", "Tue": "मंगल", "Wed": "बुध",
            "Thu": "गुरु", "Fri": "शुक्र", "Sat": "शनि", "Sun": "रवि"
        }

        if "weekly" not in st.session_state:
            st.session_state.weekly = {d: False for d in days_hindi}

        cols = st.columns(7)
        for i, (day, hindi) in enumerate(days_hindi.items()):
            with cols[i]:
                val = st.session_state.weekly[day]
                bg_day = color if val else "#1e2d40"
                text_col = "#000" if val else "#64748b"
                st.markdown(f"""
                <div style='background:{bg_day}; border-radius:8px; padding:8px 2px;
                            text-align:center; cursor:pointer; transition:all 0.2s;
                            box-shadow: {"0 0 10px " + color + "66" if val else "none"};'>
                    <div style='font-size:10px; font-weight:700; color:{text_col};'>{hindi}</div>
                    <div style='font-size:14px;'>{"✓" if val else "·"}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("", key=f"day_{day}", help=day):
                    st.session_state.weekly[day] = not st.session_state.weekly[day]
                    st.rerun()

        gym_days = sum(1 for v in st.session_state.weekly.values() if v)
        st.markdown(f"""
        <div style='text-align:center; margin:10px 0;
                    color:{color}; font-weight:700; font-size:14px;'>
            {gym_days}/7 दिन Gym 🏆
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Quick Stats
        st.markdown("### 📈 Quick Stats")
        s1, s2 = st.columns(2)
        with s1:
            st.metric("आज Complete", f"{done_count}/{total_count}")
        with s2:
            st.metric("Total Today", f"{len([l for l in st.session_state.workout_log if l['Date'] == date.today().strftime('%d-%m-%Y')])}")

        s3, s4 = st.columns(2)
        with s3:
            st.metric("🔥 Streak", f"{st.session_state.streak} days")
        with s4:
            st.metric("📝 Log", f"{len(st.session_state.workout_log)}")

        st.markdown("---")

        # Streak Update
        st.markdown("### 🔥 Streak Update")
        new_streak = st.number_input("आज gym गए? Streak update करो:", min_value=0, max_value=365,
                                      value=st.session_state.streak, step=1)
        if st.button("🔥 Streak Save करो"):
            st.session_state.streak = new_streak
            st.success(f"Streak updated: {new_streak} days! 🔥")

# ══════════════════════════════════════════════
# TAB 2 — AI COACH
# ══════════════════════════════════════════════
with tab2:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #0d1117, #0a1628);
                border: 1px solid {color}44; border-radius:16px; padding:20px;
                margin-bottom:20px; box-shadow: 0 0 30px {color}22;'>
        <h2 style='margin:0 0 6px; color:{color}; font-family: Exo 2, sans-serif;'>
            🤖 AI Fitness Coach
        </h2>
        <p style='color:#64748b; margin:0; font-size:14px;'>
            Hindi में पूछो — workout, diet, plan, tips — सब कुछ!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Prompt Buttons
    st.markdown("**⚡ Quick Questions:**")
    muscle_name = menu.split(" ", 1)[1] if " " in menu else menu

    quick_prompts = [
        f"आज {muscle_name} के लिए best 3 exercises बताओ",
        f"Fat loss के लिए {muscle_name} workout plan",
        "Beginner के लिए gym routine",
        "Pre-workout meal क्या खाएं",
        "Muscle gain के लिए diet plan",
        "Recovery के tips दो"
    ]

    cols = st.columns(3)
    for i, prompt in enumerate(quick_prompts):
        with cols[i % 3]:
            if st.button(f"💬 {prompt[:30]}...", key=f"qp_{i}"):
                st.session_state.ai_question = prompt

    st.markdown("---")

    # Manual Input
    ai_q = st.text_area(
        "✍️ अपना सवाल लिखो:",
        value=st.session_state.get("ai_question", ""),
        placeholder=f"जैसे: {muscle_name} workout में क्या गलतियाँ avoid करूं?",
        height=80,
        key="ai_input"
    )

    col_ask, col_clear = st.columns([3, 1])
    with col_ask:
        if st.button("🤖 AI से पूछो →", use_container_width=True):
            if ai_q.strip():
                with st.spinner("🧠 AI सोच रहा है..."):
                    response = ask_ai_groq(ai_q, menu)
                    st.session_state.ai_response = response
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.ai_response = ""
            st.rerun()

    # AI Response Display
    if st.session_state.ai_response:
        st.markdown(f"""
        <div style='background:#080c14; border:1px solid {color}33; border-radius:14px;
                    padding:20px; margin-top:16px;
                    border-left: 3px solid {color};'>
            <div style='color:#64748b; font-size:11px; margin-bottom:10px;
                        text-transform:uppercase; letter-spacing:1px;'>
                🤖 AI Coach का जवाब:
            </div>
            <div style='color:#e2e8f0; font-size:15px; line-height:1.8;
                        white-space:pre-wrap;'>
                {st.session_state.ai_response}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='color:#475569; font-size:12px; text-align:center;'>
        ⚙️ AI चलाने के लिए <code>GROQ_API_KEY</code> Streamlit Secrets में add करो।
        Free key: <a href='https://console.groq.com' target='_blank' style='color:#60a5fa;'>console.groq.com</a>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 3 — LOG & STATS
# ══════════════════════════════════════════════
with tab3:
    st.markdown("### 📊 Workout Statistics")

    # Top Stats
    col1, col2, col3, col4 = st.columns(4)
    total_exercises_done = sum(1 for v in st.session_state.checked.values() if v)
    total_log = len(st.session_state.workout_log)
    groups_done = len(set(
        l["Body Part"] for l in st.session_state.workout_log
    ))
    today_log = len([
        l for l in st.session_state.workout_log
        if l["Date"] == date.today().strftime("%d-%m-%Y")
    ])

    with col1:
        st.metric("💪 Total Exercises", total_exercises_done)
    with col2:
        st.metric("📝 Log Entries", total_log)
    with col3:
        st.metric("🏋️ Groups Trained", groups_done)
    with col4:
        st.metric("📅 आज", today_log)

    st.markdown("---")

    # Workout Log Table
    st.markdown("### 📋 Workout Log")

    if st.session_state.workout_log:
        import pandas as pd
        df = pd.DataFrame(st.session_state.workout_log)

        # Color by body part
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Date": st.column_config.TextColumn("📅 Date", width="small"),
                "Time": st.column_config.TextColumn("⏰ Time", width="small"),
                "Body Part": st.column_config.TextColumn("💪 Body Part", width="medium"),
                "Exercise": st.column_config.TextColumn("🏋️ Exercise", width="large"),
                "Status": st.column_config.TextColumn("✅ Status", width="small"),
            }
        )

        # Download Button
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ CSV Download करो",
            data=csv,
            file_name=f"gym_log_{date.today().strftime('%d_%m_%Y')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        # Clear Log
        if st.button("🗑️ Log Clear करो", use_container_width=True):
            st.session_state.workout_log = []
            st.success("Log cleared!")
            st.rerun()
    else:
        st.markdown("""
        <div style='text-align:center; padding:60px; color:#334155;'>
            <div style='font-size:48px;'>📋</div>
            <div style='font-size:18px; margin-top:12px;'>अभी कोई log नहीं है</div>
            <div style='font-size:13px; color:#1e2d40; margin-top:6px;'>
                Workout tab पर जाओ और exercises tick करो
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Body Part Breakdown
    if st.session_state.workout_log:
        st.markdown("### 🥧 Body Part Breakdown")
        import pandas as pd
        df2 = pd.DataFrame(st.session_state.workout_log)
        breakdown = df2["Body Part"].value_counts().reset_index()
        breakdown.columns = ["Body Part", "Exercises Done"]
        st.bar_chart(breakdown.set_index("Body Part"))
