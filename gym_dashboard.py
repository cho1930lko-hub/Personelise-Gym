import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import json
import pandas as pd

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="💪 Smart Gym Dashboard",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Exo+2:wght@400;700;900&display=swap');

.stApp {
    background: linear-gradient(135deg, #060b14 0%, #0a0f1e 50%, #060b14 100%);
    font-family: 'Rajdhani', sans-serif;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #090e1a 100%) !important;
    border-right: 1px solid #1e2d40;
}
[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8 !important;
    font-size: 15px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
}
h1, h2, h3 { font-family: 'Exo 2', sans-serif !important; letter-spacing: 1px; }
[data-testid="metric-container"] {
    background: #0d1117;
    border: 1px solid #1e2d40;
    border-radius: 12px;
    padding: 16px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #1e40af, #1d4ed8) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 15px !important;
}
.stTextInput > div > input, .stTextArea textarea {
    background: #0d1117 !important;
    border: 1px solid #1e2d40 !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 15px !important;
}
.stCheckbox label {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #cbd5e1 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #64748b !important;
}
.stTabs [aria-selected="true"] { color: #60a5fa !important; }
hr { border-color: #1e2d40 !important; }
.stAlert { border-radius: 12px !important; font-family: 'Rajdhani', sans-serif !important; }
.stDataFrame { border-radius: 12px !important; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# EXERCISE DATA
# ─────────────────────────────────────────────
MUSCLE_DATA = {
    "💪 Biceps": {
        "color": "#ef4444",
        "exercises": [
            {"name": "Dumbbell Curl",       "sets": "3×12", "tip": "Elbow fixed रखो, shoulder नहीं हिलाओ"},
            {"name": "Barbell Curl",         "sets": "4×10", "tip": "Back straight, controlled movement"},
            {"name": "Hammer Curl",          "sets": "3×12", "tip": "Neutral grip, brachialis target"},
            {"name": "Preacher Curl",        "sets": "3×10", "tip": "Full extension लो, slow negative"},
            {"name": "Concentration Curl",   "sets": "3×15", "tip": "Mind-muscle connection पर focus"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+biceps+workout+hindi",
        "info": "💡 Biceps = Arm का front muscle. Peak बनाने के लिए Preacher Curl best है।"
    },
    "🦾 Triceps": {
        "color": "#f97316",
        "exercises": [
            {"name": "Tricep Pushdown",      "sets": "4×12", "tip": "Elbows body से touch रहें"},
            {"name": "Overhead Extension",   "sets": "3×12", "tip": "Core tight, elbow flare मत करो"},
            {"name": "Skull Crushers",       "sets": "3×10", "tip": "Weight को control करो"},
            {"name": "Close Grip Bench",     "sets": "3×10", "tip": "Grip shoulder-width रखो"},
            {"name": "Tricep Dips",          "sets": "3×15", "tip": "Chest को forward lean मत करो"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+triceps+workout+hindi",
        "info": "💡 Triceps = Arm का 2/3 हिस्सा! Arms बड़े करने हैं तो Triceps पर ज्यादा focus करो।"
    },
    "🏔️ Shoulder": {
        "color": "#eab308",
        "exercises": [
            {"name": "Overhead Press",       "sets": "4×10", "tip": "Core brace, knees slightly bent"},
            {"name": "Lateral Raise",        "sets": "3×15", "tip": "Slow & controlled, elbow slight bend"},
            {"name": "Front Raise",          "sets": "3×12", "tip": "Don't use momentum"},
            {"name": "Arnold Press",         "sets": "3×12", "tip": "Full rotation of wrist"},
            {"name": "Rear Delt Fly",        "sets": "3×15", "tip": "Bend forward 45°, elbow wide"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+shoulder+workout+hindi",
        "info": "💡 3D Shoulders चाहिए? तीनों heads: Front, Side, Rear — तीनों train करो।"
    },
    "🫁 Chest": {
        "color": "#ec4899",
        "exercises": [
            {"name": "Flat Bench Press",         "sets": "4×10", "tip": "Arch back slightly, feet flat"},
            {"name": "Incline Dumbbell Press",   "sets": "3×12", "tip": "Upper chest के लिए best"},
            {"name": "Cable Flyes",              "sets": "3×15", "tip": "Full stretch at bottom"},
            {"name": "Push-Ups",                 "sets": "3×20", "tip": "Elbows 45°, chest to floor"},
            {"name": "Decline Press",            "sets": "3×12", "tip": "Lower chest target"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+chest+workout+hindi",
        "info": "💡 Big Chest = Compound movements first (Bench Press), then isolation (Flyes)।"
    },
    "🦵 Legs": {
        "color": "#22c55e",
        "exercises": [
            {"name": "Squats",               "sets": "4×12", "tip": "Knees over toes, deep squat लो"},
            {"name": "Leg Press",            "sets": "4×15", "tip": "Full depth, knees don't cave in"},
            {"name": "Romanian Deadlift",    "sets": "3×12", "tip": "Hamstring stretch feel करो"},
            {"name": "Leg Extension",        "sets": "3×15", "tip": "Quad squeeze at top"},
            {"name": "Calf Raises",          "sets": "4×20", "tip": "Slow negatives, full range"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+leg+workout+hindi",
        "info": "💡 Leg day skip मत करो! Body का 70% muscle legs में है।"
    },
    "🏛️ Back": {
        "color": "#3b82f6",
        "exercises": [
            {"name": "Deadlift",             "sets": "4×6",  "tip": "Back flat, hinge at hips"},
            {"name": "Pull-Ups",             "sets": "3×10", "tip": "Full extension, chin over bar"},
            {"name": "Barbell Row",          "sets": "4×10", "tip": "Elbows back, squeeze lats"},
            {"name": "Lat Pulldown",         "sets": "3×12", "tip": "Chest up, lean back slightly"},
            {"name": "Seated Cable Row",     "sets": "3×15", "tip": "Shoulder blades squeeze"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+back+workout+hindi",
        "info": "💡 V-taper चाहिए? Lat Pulldown + Pull-Ups = width, Rows = thickness।"
    },
    "🏃 Cardio": {
        "color": "#a855f7",
        "exercises": [
            {"name": "Treadmill Run",        "sets": "20 min", "tip": "Incline 5-10% add करो"},
            {"name": "Jump Rope",            "sets": "5×3 min","tip": "Wrist से jump करो"},
            {"name": "Cycling",              "sets": "30 min", "tip": "Medium resistance"},
            {"name": "HIIT Intervals",       "sets": "20 min", "tip": "30s max effort, 30s rest"},
            {"name": "Stair Climber",        "sets": "15 min", "tip": "Don't hold rails"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+cardio+fat+loss+hindi",
        "info": "💡 Fat loss के लिए HIIT > Steady cardio। Less time, more results।"
    },
    "🧘 Yoga": {
        "color": "#06b6d4",
        "exercises": [
            {"name": "Sun Salutation",       "sets": "5 rounds", "tip": "Slow breathing"},
            {"name": "Warrior Pose",         "sets": "Hold 30s", "tip": "Hip alignment"},
            {"name": "Downward Dog",         "sets": "Hold 1 min","tip": "Heels push down"},
            {"name": "Child's Pose",         "sets": "Hold 2 min","tip": "Forehead to floor"},
            {"name": "Shavasana",            "sets": "5 min",    "tip": "Complete relaxation"},
        ],
        "video": "https://www.youtube.com/results?search_query=yoga+for+beginners+hindi",
        "info": "💡 Yoga = Recovery + Flexibility + Mental Peace।"
    },
}

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "checked": {},
    "workout_log": [],
    "streak": 0,
    "weekly": {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

days_hindi = {
    "Mon": "सोम", "Tue": "मंगल", "Wed": "बुध", "Thu": "गुरु",
    "Fri": "शुक्र", "Sat": "शनि", "Sun": "रवि"
}
if not st.session_state.weekly:
    st.session_state.weekly = {d: False for d in days_hindi}

# ─────────────────────────────────────────────
# GOOGLE SHEETS
# Sheet name: "Gym Workout Log"
# Headers:    Date | Time | Body Part | Exercise | Weight (kg) | Status
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_sheet():
    try:
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds_dict = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
        creds  = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        return client.open("Gym Workout Log").sheet1
    except Exception:
        return None

def save_to_sheet(date_str, time_str, body_part, exercise, weight=0):
    sheet = get_sheet()
    if sheet:
        try:
            sheet.append_row([
                date_str, time_str, body_part,
                exercise, f"{weight} kg", "✔ Done"
            ])
            return True
        except Exception:
            return False
    return False

# Sheet connection status check
def sheet_status():
    try:
        s = get_sheet()
        return s is not None
    except Exception:
        return False

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:10px 0 20px;'>
        <div style='font-size:40px'>⚡</div>
        <div style='font-family:Exo 2,sans-serif; font-size:22px; font-weight:900;
                    background:linear-gradient(135deg,#60a5fa,#a78bfa);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    letter-spacing:2px;'>GYM AI</div>
        <div style='color:#475569; font-size:11px; margin-top:4px;'>Smart Fitness Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    # Google Sheet Status
    connected = sheet_status()
    dot_color = "#22c55e" if connected else "#ef4444"
    dot_text  = "Sheet Connected ✅" if connected else "Sheet Not Connected ❌"
    st.markdown(f"""
    <div style='background:#0d1117; border:1px solid #1e2d40; border-radius:10px;
                padding:8px 12px; margin-bottom:12px; font-size:12px;
                display:flex; align-items:center; gap:8px;'>
        <span style='color:{dot_color}; font-size:16px;'>●</span>
        <span style='color:{dot_color};'>{dot_text}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🏋️ Workout Menu")
    menu = st.radio("Select", list(MUSCLE_DATA.keys()), label_visibility="collapsed")

    st.markdown("---")

    total_done = sum(1 for v in st.session_state.checked.values() if v)
    c1, c2 = st.columns(2)
    with c1: st.metric("🔥 Streak", f"{st.session_state.streak}d")
    with c2: st.metric("✅ Done",   str(total_done))

    st.markdown("---")
    st.markdown("**📊 सभी Groups**")
    for grp, data in MUSCLE_DATA.items():
        d   = sum(1 for ex in data["exercises"]
                  if st.session_state.checked.get(f"{grp}_{ex['name']}", False))
        t   = len(data["exercises"])
        p   = int((d / t) * 100)
        clr = data["color"]
        st.markdown(f"""
        <div style='margin-bottom:8px'>
            <div style='display:flex; justify-content:space-between;
                        font-size:12px; color:#94a3b8; margin-bottom:3px;'>
                <span>{grp}</span>
                <span style='color:{clr}; font-weight:700'>{p}%</span>
            </div>
            <div style='background:#1e2d40; border-radius:99px; height:5px;'>
                <div style='width:{p}%; height:100%; background:{clr}; border-radius:99px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='color:#475569; font-size:11px; text-align:center;'>
        Made with ❤️ for Fitness<br>by Shadab
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────
muscle     = MUSCLE_DATA[menu]
color      = muscle["color"]
exercises  = muscle["exercises"]

done_count  = sum(1 for ex in exercises
                  if st.session_state.checked.get(f"{menu}_{ex['name']}", False))
total_count = len(exercises)
pct         = int((done_count / total_count) * 100)

st.markdown(f"""
<div style='padding:20px 0 10px;'>
    <h1 style='margin:0; font-size:36px; font-weight:900;
               background:linear-gradient(135deg,{color},{color}88);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent;
               font-family:Exo 2,sans-serif; letter-spacing:2px;'>
        {menu.upper()} WORKOUT
    </h1>
    <p style='color:#64748b; margin:4px 0 0; font-size:14px;'>
        {date.today().strftime("%A, %d %B %Y")}
        &nbsp;|&nbsp; {done_count}/{total_count} exercises complete
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
                    background:linear-gradient(90deg,{color},{color}99);
                    border-radius:99px; box-shadow:0 0 10px {color}66;'></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.info(muscle["info"])

# ─────────────────────────────────────────────
# TABS — 2 tabs only (AI हटाया)
# ─────────────────────────────────────────────
tab1, tab2 = st.tabs(["🏋️ Workout", "📊 Log & Stats"])

# ══════════════════════════════════════════
# TAB 1 — WORKOUT
# ══════════════════════════════════════════
with tab1:
    col_ex, col_right = st.columns([3, 2])

    with col_ex:
        st.markdown("### Exercise List")
        st.caption("⚖️ पहले weight डालो → फिर ✅ tick करो → Google Sheet में save होगा")

        for ex in exercises:
            key     = f"{menu}_{ex['name']}"
            is_done = st.session_state.checked.get(key, False)
            bg      = f"{color}18" if is_done else "#0d1117"
            border  = color        if is_done else "#1e2d40"
            nc      = color        if is_done else "#e2e8f0"
            strike  = "line-through" if is_done else "none"

            col_chk, col_inf, col_set, col_wt = st.columns([1, 5, 2, 2])

            with col_chk:
                checked = st.checkbox("", value=is_done, key=f"cb_{key}")
                if checked != is_done:
                    st.session_state.checked[key] = checked
                    if checked:
                        now    = datetime.now()
                        wt_val = st.session_state.get(f"wt_{key}", 0.0)
                        bp     = menu.split(" ", 1)[1] if " " in menu else menu
                        entry  = {
                            "Date":        now.strftime("%d-%m-%Y"),
                            "Time":        now.strftime("%I:%M %p"),
                            "Body Part":   bp,
                            "Exercise":    ex["name"],
                            "Weight (kg)": wt_val,
                            "Status":      "✔ Done"
                        }
                        st.session_state.workout_log.insert(0, entry)
                        saved = save_to_sheet(
                            entry["Date"], entry["Time"],
                            entry["Body Part"], entry["Exercise"], wt_val
                        )
                        if saved:
                            st.toast(f"✅ {ex['name']} — {wt_val} kg → Sheet saved!", icon="💪")
                        else:
                            st.toast(f"✅ {ex['name']} logged! (Sheet offline)", icon="⚠️")
                    st.rerun()

            with col_inf:
                st.markdown(f"""
                <div style='padding:8px 12px; border-radius:10px;
                            background:{bg}; border:1px solid {border};'>
                    <div style='font-size:15px; font-weight:700;
                                color:{nc}; text-decoration:{strike};'>{ex["name"]}</div>
                    <div style='font-size:12px; color:#64748b; margin-top:2px;'>
                        💡 {ex["tip"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_set:
                st.markdown(f"""
                <div style='padding:8px; text-align:center; border-radius:10px;
                            background:{color}22; border:1px solid {color}44;
                            color:{color}; font-weight:700; font-size:13px; margin-top:2px;'>
                    {ex["sets"]}
                </div>
                """, unsafe_allow_html=True)

            with col_wt:
                st.number_input(
                    "⚖️ kg", min_value=0.0, max_value=300.0,
                    step=0.5, value=0.0,
                    key=f"wt_{key}",
                    label_visibility="visible"
                )

            st.markdown("")

        st.markdown("---")

        # YouTube Button
        st.markdown(f"""
        <a href="{muscle['video']}" target="_blank" style="text-decoration:none;">
            <div style='background:linear-gradient(135deg,#cc0000,#ff0000);
                        color:white; padding:14px; border-radius:12px;
                        text-align:center; font-size:16px; font-weight:700;
                        font-family:Rajdhani,sans-serif;
                        box-shadow:0 4px 20px #ff000044;'>
                🎥 YouTube पर {menu} Workout देखो →
            </div>
        </a>
        """, unsafe_allow_html=True)

    # ── Right Column ──
    with col_right:
        # Weekly Tracker
        st.markdown("### 📅 इस हफ्ते")
        cols7 = st.columns(7)
        for i, (day, hindi) in enumerate(days_hindi.items()):
            with cols7[i]:
                val    = st.session_state.weekly[day]
                bg_day = color  if val else "#1e2d40"
                tc     = "#000" if val else "#64748b"
                st.markdown(f"""
                <div style='background:{bg_day}; border-radius:8px; padding:8px 2px;
                            text-align:center;
                            box-shadow:{"0 0 8px "+color+"66" if val else "none"};'>
                    <div style='font-size:10px; font-weight:700; color:{tc};'>{hindi}</div>
                    <div style='font-size:14px;'>{"✓" if val else "·"}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("", key=f"day_{day}", help=day):
                    st.session_state.weekly[day] = not val
                    st.rerun()

        gym_days = sum(1 for v in st.session_state.weekly.values() if v)
        st.markdown(
            f"<div style='text-align:center;margin:10px 0;color:{color};font-weight:700;'>"
            f"{gym_days}/7 दिन Gym 🏆</div>",
            unsafe_allow_html=True
        )
        st.markdown("---")

        # Quick Stats
        st.markdown("### 📈 Quick Stats")
        today_str = date.today().strftime("%d-%m-%Y")
        s1, s2 = st.columns(2)
        with s1: st.metric("आज", f"{done_count}/{total_count}")
        with s2: st.metric("Today Log",
                            len([l for l in st.session_state.workout_log
                                 if l["Date"] == today_str]))
        s3, s4 = st.columns(2)
        with s3: st.metric("🔥 Streak", f"{st.session_state.streak}d")
        with s4: st.metric("📝 Total",  len(st.session_state.workout_log))

        st.markdown("---")

        # Streak Update
        st.markdown("### 🔥 Streak Update")
        ns = st.number_input("Streak days:", min_value=0, max_value=365,
                             value=st.session_state.streak, step=1)
        if st.button("🔥 Save करो"):
            st.session_state.streak = ns
            st.success(f"Streak: {ns} days! 🔥")

# ══════════════════════════════════════════
# TAB 2 — LOG & STATS
# ══════════════════════════════════════════
with tab2:
    st.markdown("### 📊 Workout Statistics")

    total_ex    = sum(1 for v in st.session_state.checked.values() if v)
    total_log   = len(st.session_state.workout_log)
    groups_done = len(set(l["Body Part"] for l in st.session_state.workout_log))
    today_log   = len([l for l in st.session_state.workout_log
                       if l["Date"] == date.today().strftime("%d-%m-%Y")])

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("💪 Total Done",  total_ex)
    with c2: st.metric("📝 Log Entries", total_log)
    with c3: st.metric("🏋️ Groups",     groups_done)
    with c4: st.metric("📅 आज",         today_log)

    st.markdown("---")
    st.markdown("### 📋 Workout Log")

    if st.session_state.workout_log:
        df = pd.DataFrame(st.session_state.workout_log)

        st.dataframe(
            df, use_container_width=True, hide_index=True,
            column_config={
                "Date":        st.column_config.TextColumn("📅 Date",        width="small"),
                "Time":        st.column_config.TextColumn("⏰ Time",        width="small"),
                "Body Part":   st.column_config.TextColumn("💪 Body Part",   width="medium"),
                "Exercise":    st.column_config.TextColumn("🏋️ Exercise",   width="large"),
                "Weight (kg)": st.column_config.NumberColumn("⚖️ Weight kg", width="small"),
                "Status":      st.column_config.TextColumn("✅ Status",      width="small"),
            }
        )

        cd, cl = st.columns([3, 1])
        with cd:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ CSV Download करो", data=csv,
                file_name=f"gym_log_{date.today().strftime('%d_%m_%Y')}.csv",
                mime="text/csv", use_container_width=True
            )
        with cl:
            if st.button("🗑️ Clear Log", use_container_width=True):
                st.session_state.workout_log = []
                st.rerun()

        st.markdown("---")

        # Body Part Breakdown
        st.markdown("### 📊 Body Part Breakdown")
        bd = df["Body Part"].value_counts().reset_index()
        bd.columns = ["Body Part", "Count"]
        st.bar_chart(bd.set_index("Body Part"))

        # Weight Progress
        st.markdown("### ⚖️ Weight Progress")
        if "Weight (kg)" in df.columns:
            ex_opts = df[df["Weight (kg)"] > 0]["Exercise"].unique().tolist()
            if ex_opts:
                sel   = st.selectbox("Exercise select करो:", ex_opts)
                ex_df = df[df["Exercise"] == sel][["Date", "Weight (kg)"]].copy()
                ex_df = ex_df[ex_df["Weight (kg)"] > 0]
                if not ex_df.empty:
                    st.line_chart(ex_df.set_index("Date"))
            else:
                st.info("पहले कुछ exercises में weight डालो — chart यहाँ दिखेगा।")
    else:
        st.markdown("""
        <div style='text-align:center; padding:60px; color:#334155;'>
            <div style='font-size:48px;'>📋</div>
            <div style='font-size:18px; margin-top:12px;'>अभी कोई log नहीं है</div>
            <div style='font-size:13px; color:#1e2d40; margin-top:6px;'>
                Workout tab → exercises tick करो
            </div>
        </div>
        """, unsafe_allow_html=True)
