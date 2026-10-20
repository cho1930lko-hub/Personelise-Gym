import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime, date

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="💪 GYM AI Dashboard",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# CSS
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
h1, h2, h3 {
    font-family: 'Exo 2', sans-serif !important;
    letter-spacing: 1px;
}
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
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px #1d4ed866 !important;
}
.stTextInput > div > input,
.stTextArea textarea,
.stNumberInput input {
    background: #0d1117 !important;
    border: 1px solid #1e2d40 !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 15px !important;
}
.stSelectbox > div > div {
    background: #0d1117 !important;
    border: 1px solid #1e2d40 !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
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
.glass {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 15px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 10px;
}
.progress-fill { transition: width 0.5s ease-in-out; }
@media (max-width: 768px) {
    /* Mobile-first layout: give the workout area the full screen width. */
    .main .block-container, [data-testid="stMainBlockContainer"] {
        padding: .75rem .65rem 2rem !important;
        max-width: 100% !important;
    }
    h1 { font-size: 22px !important; line-height: 1.2 !important; }
    h2 { font-size: 20px !important; line-height: 1.25 !important; }
    h3 { font-size: 18px !important; line-height: 1.25 !important; }
    p, label, [data-testid="stCaptionContainer"] {
        overflow-wrap: anywhere;
    }
    [data-testid="stMetric"] {
        padding: 10px !important;
        min-width: 0 !important;
    }
    [data-testid="stMetricValue"] { font-size: 1.25rem !important; }
    [data-testid="stMetricLabel"] { font-size: .75rem !important; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px !important;
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 12px !important;
        padding: 8px 9px !important;
        white-space: nowrap !important;
    }
    .stButton > button, [data-testid="stDownloadButton"] button {
        min-height: 42px !important;
        white-space: normal !important;
        line-height: 1.2 !important;
        padding: 8px 10px !important;
    }
    .stTextInput input, .stNumberInput input, .stTextArea textarea,
    [data-baseweb="select"] {
        font-size: 16px !important;
    }
    .glass {
        padding: 12px !important;
        border-radius: 13px !important;
    }
    [data-testid="stDataFrame"] { max-width: 100% !important; }
}
@media (max-width: 420px) {
    .main .block-container, [data-testid="stMainBlockContainer"] {
        padding-left: .45rem !important;
        padding-right: .45rem !important;
    }
    .stTabs [data-baseweb="tab"] { font-size: 11px !important; padding: 7px 6px !important; }
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
}

/* Workout-focused responsive polish */
[data-testid="stMainBlockContainer"] h3 {
    overflow-wrap: anywhere;
}
[data-testid="stMainBlockContainer"] [data-testid="stCheckbox"] {
    min-height: 42px;
    display: flex;
    align-items: center;
}
[data-testid="stMainBlockContainer"] [data-testid="stNumberInput"] input {
    min-height: 42px;
}
[data-testid="stMainBlockContainer"] [data-testid="stTabs"] {
    margin-top: .5rem;
}
@media (max-width: 768px) {
    /* Allow each Streamlit column group to use the available width. */
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"] {
        gap: .55rem !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: 0 !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stMetric"] {
        border-radius: 12px !important;
        overflow-wrap: anywhere;
    }
    [data-testid="stMainBlockContainer"] .glass {
        margin-bottom: .7rem;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stCheckbox"] label {
        padding: 6px 0 !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stNumberInput"] button {
        min-width: 28px !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stAlert"] {
        padding: .7rem !important;
    }
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# AI SETUP (Groq) — model fixed to llama-3.3-70b-versatile
# ─────────────────────────────────────────────
try:
    from groq import Groq
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
        AI_ENABLED = True
    else:
        AI_ENABLED = False
except Exception:
    AI_ENABLED = False

def ask_ai(question, log_data):
    if not AI_ENABLED:
        return "⚠️ AI offline — Streamlit Secrets में GROQ_API_KEY add करो।"
    try:
        history_rows = []
        for log in log_data[:30]:
            status = str(log.get("Status", ""))
            reps_match = re.search(r"(\d+)\s*reps", status, flags=re.IGNORECASE)
            set_match = re.search(r"Set\s+(\d+)\s*/\s*(\d+)", status, flags=re.IGNORECASE)
            reps_text = f", {reps_match.group(1)} reps" if reps_match else ""
            set_text = f", set {set_match.group(1)}/{set_match.group(2)}" if set_match else ""
            history_rows.append(
                f"Date:{log.get('Date','?')} | {log.get('Body Part','?')} | "
                f"{log.get('Exercise','?')} | {log.get('Weight (kg)',0)}kg"
                f"{reps_text}{set_text}"
            )
        history = "\n".join(history_rows)
        bw          = st.session_state.get("body_weight", 70)
        gw          = st.session_state.get("goal_weight", 65)
        streak      = st.session_state.get("streak", 0)
        weekly_days = sum(1 for v in st.session_state.get("weekly", {}).values() if v)

        prompt = f"""
You are a practical, safety-conscious personal gym coach.

USER PROFILE:
- Current Weight: {bw} kg
- Goal Weight: {gw} kg
- Current Streak: {streak} days
- Days trained this week: {weekly_days}/7
- Goal direction by weight only: {"weight loss" if gw < bw else "weight gain/maintenance"}
- Remember: weight alone cannot establish body composition or whether weight loss is medically appropriate.

RECENT WORKOUT LOG (up to 30 entries; reps/set numbers may be absent in legacy rows):
{history if history else 'No workout history yet — ask about experience and available equipment before prescribing a detailed plan.'}

COACHING RULES:
- Use the actual history; distinguish logged facts from assumptions and say when data is insufficient.
- Where set/reps exist, discuss performance trends. Never invent missing sets, reps, body measurements, or personal details.
- Do not automatically recommend adding 5% weight every session. Recommend gradual progression only when current sets/reps are completed with controlled technique and without pain.
- Include recovery/rest days and avoid training the same muscle hard on consecutive days.
- Give general fitness/nutrition guidance, not medical diagnosis; advise a clinician for injuries, chest pain, faintness, or relevant medical concerns.
- Respond in simple Hindi + English mix, at most 150 words, with concise bullets.
- Avoid extreme diets, unsafe weight-loss promises, and unsupported predictions.
"""
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user",   "content": question}
            ],
            max_tokens=300,
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception:
        return "⚠️ AI Coach अभी जवाब नहीं दे पाया। थोड़ी देर बाद फिर कोशिश करें और Streamlit/Groq connection settings जाँचें।"

# ─────────────────────────────────────────────
# GOOGLE SHEETS SETUP
# ─────────────────────────────────────────────
GSHEET_ENABLED = False
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEET_ENABLED = True
except ImportError:
    pass

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_sheet():
    if not GSHEET_ENABLED:
        return None
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds      = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client     = gspread.authorize(creds)
        sheet      = client.open_by_key(st.secrets["SHEET_ID"])
        return sheet
    except Exception:
        return None

def ensure_worksheets(sheet):
    needed   = ["WorkoutLog", "BodyStats", "WeeklyTracker", "Settings"]
    existing = [ws.title for ws in sheet.worksheets()]
    for name in needed:
        if name not in existing:
            sheet.add_worksheet(title=name, rows=1000, cols=20)
    wl = sheet.worksheet("WorkoutLog")
    if wl.row_values(1) == []:
        wl.append_row(["Date","Time","Body Part","Exercise","Weight (kg)","Status"])
    bs = sheet.worksheet("BodyStats")
    if bs.row_values(1) == []:
        bs.append_row(["Date","Body Weight","Goal Weight","BMI"])

def gsheet_save_workout(entry):
    try:
        sheet = get_sheet()
        if not sheet: return False
        ws = sheet.worksheet("WorkoutLog")
        ws.append_row([
            entry["Date"], entry["Time"], entry["Body Part"],
            entry["Exercise"], entry["Weight (kg)"], entry["Status"]
        ])
        return True
    except Exception:
        return False

def gsheet_load_workouts():
    try:
        sheet = get_sheet()
        if not sheet: return []
        ws      = sheet.worksheet("WorkoutLog")
        records = ws.get_all_records()
        return list(reversed(records))
    except Exception:
        return []

def gsheet_save_body_stats(bw, gw):
    try:
        sheet = get_sheet()
        if not sheet: return False
        # BodyStats history
        bs  = sheet.worksheet("BodyStats")
        bmi = round(bw / (1.70 ** 2), 2)
        bs.append_row([date.today().strftime("%d-%m-%Y"), bw, gw, bmi])
        # Settings (latest values)
        sw = sheet.worksheet("Settings")
        sw.clear()
        sw.append_row(["Key", "Value"])
        sw.append_row(["body_weight", bw])
        sw.append_row(["goal_weight", gw])
        sw.append_row(["streak",      st.session_state.get("streak", 0)])
        sw.append_row(["last_workout",st.session_state.get("last_workout", "")])
        return True
    except Exception:
        return False

def gsheet_load_settings():
    try:
        sheet = get_sheet()
        if not sheet: return {}
        ws      = sheet.worksheet("Settings")
        records = ws.get_all_records()
        return {r["Key"]: r["Value"] for r in records}
    except Exception:
        return {}

def gsheet_save_weekly(weekly_dict):
    try:
        sheet = get_sheet()
        if not sheet: return False
        ws       = sheet.worksheet("WeeklyTracker")
        ws.clear()
        ws.append_row(["Day", "Done", "Week"])
        week_num = date.today().isocalendar()[1]
        for day, done in weekly_dict.items():
            ws.append_row([day, str(done), week_num])
        return True
    except Exception:
        return False

def gsheet_load_weekly():
    try:
        sheet = get_sheet()
        if not sheet: return {}
        ws      = sheet.worksheet("WeeklyTracker")
        records = ws.get_all_records()
        return {r["Day"]: r["Done"] == "True" for r in records}
    except Exception:
        return {}

def gsheet_load_body_stats_history():
    """BMI history chart के लिए"""
    try:
        sheet = get_sheet()
        if not sheet: return []
        ws      = sheet.worksheet("BodyStats")
        records = ws.get_all_records()
        return records
    except Exception:
        return []

# ─────────────────────────────────────────────
# LOCAL SAVE / LOAD (fallback)
# ─────────────────────────────────────────────
SAVE_FILE = "gym_data.json"

def save_data():
    try:
        data = {
            "checked":      st.session_state.checked,
            "workout_log":  st.session_state.workout_log,
            "streak":       st.session_state.streak,
            "weekly":       st.session_state.weekly,
            "last_workout": st.session_state.last_workout,
            "body_weight":  st.session_state.body_weight,
            "goal_weight":  st.session_state.goal_weight,
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            for k, v in data.items():
                if k not in st.session_state:
                    st.session_state[k] = v
        except Exception:
            pass

# ─────────────────────────────────────────────
# EXERCISE DATA
# ─────────────────────────────────────────────
MUSCLE_DATA = {
    "💪 Biceps": {
        "color": "#ef4444",
        "exercises": [
            {"name": "Dumbbell Curl (Standing/Alternating)", "tip": "Elbow fixed रखो, shoulder नहीं हिलाओ, full squeeze at top"},
            {"name": "Barbell Curl (Straight or EZ Bar)",   "tip": "Back straight, controlled movement, no swinging"},
            {"name": "Incline Dumbbell Curl",                "tip": "Bench 45-60° पर, deep stretch at bottom for long head"},
            {"name": "Hammer Curl",                          "tip": "Neutral grip, brachialis target — thickness बढ़ाने के लिए best"},
            {"name": "Preacher Curl",                        "tip": "Full extension लो, slow negative, peak बनाने के लिए king"},
            {"name": "Concentration Curl",                   "tip": "Mind-muscle connection पर focus, elbow thigh पर fix"},
            {"name": "Cable Curl",                           "tip": "Constant tension बनाए रखो, peak contraction"},
            {"name": "Bayesian Cable Curl",                  "tip": "Cable के पीछे खड़े होकर, awesome stretch + tension"},
            {"name": "Drag Curl",                            "tip": "Bar को body के साथ drag करो, long head hit"},
            {"name": "Spider Curl",                          "tip": "Bench पर पेट के बल लेटकर, strict form, no cheating"},
        ],
        "youtube_search": "biceps workout gym exercises Hindi",
        "info": "💡 Biceps = Arm का front muscle. Peak के लिए Preacher + Incline Curl best। Thickness के लिए Hammer + Drag Curl।",
    },
    "🔱 Triceps": {
        "color": "#f97316",
        "exercises": [
            {"name": "Close Grip Bench Press",      "tip": "Elbows tucked, powerful push, full lockout"},
            {"name": "Skull Crusher (EZ Bar)",      "tip": "Elbows fixed, slow descent, full extension at top"},
            {"name": "Cable Pushdown (Straight)",   "tip": "Elbows glued to sides, squeeze at bottom"},
            {"name": "Overhead Tricep Extension",   "tip": "Full stretch at bottom, lock out at top"},
            {"name": "Dips (Tricep Focus)",         "tip": "Stay upright, elbows back, chest अधिक lean मत करो"},
            {"name": "Rope Pushdown",               "tip": "Rope को नीचे spread करो, full contraction"},
            {"name": "Single Arm Cable Extension",  "tip": "One arm at a time, better isolation"},
            {"name": "Diamond Push-Up",             "tip": "Hands diamond shape, elbows in, bodyweight finisher"},
        ],
        "youtube_search": "triceps workout gym exercises Hindi",
        "info": "💡 Triceps arm का 2/3 हिस्सा हैं। Big arms चाहिए तो Triceps पर focus जरूरी।",
    },
    "🏔️ Shoulders": {
        "color": "#3b82f6",
        "exercises": [
            {"name": "Seated Dumbbell Shoulder Press", "tip": "Full range, controlled movement, core tight रखो"},
            {"name": "Overhead Press (Barbell)",       "tip": "Core brace करो, knees slightly bent, strict form"},
            {"name": "Arnold Press",                   "tip": "Full rotation दो, front + side delts दोनों hit"},
            {"name": "Lateral Raise (Dumbbell)",       "tip": "Slow & controlled, pinky ऊपर, elbow slight bend"},
            {"name": "Cable Lateral Raise",            "tip": "Constant tension, best side delt builder"},
            {"name": "Front Raise",                    "tip": "Momentum मत यूज करो, controlled lift"},
            {"name": "Rear Delt Fly (Dumbbell)",       "tip": "Chest supported, elbows wide, squeeze rear delts"},
            {"name": "Face Pull (Cable)",              "tip": "Rear delts + upper traps + rotator cuff के लिए best"},
            {"name": "Upright Row (EZ Bar)",           "tip": "Elbows high, traps + side delts hit"},
        ],
        "youtube_search": "shoulder workout gym exercises Hindi",
        "info": "💡 3D Shoulders के लिए Front, Side और Rear Delts — तीनों को equal importance दो।",
    },
    "🫁 Chest": {
        "color": "#ec4899",
        "exercises": [
            {"name": "Flat Barbell Bench Press",    "tip": "Shoulder blades squeezed, slight arch, full control"},
            {"name": "Incline Dumbbell Press",      "tip": "Upper chest के लिए best movement, 30-45° incline"},
            {"name": "Flat Dumbbell Bench Press",   "tip": "Better stretch than barbell, deep contraction"},
            {"name": "Incline Barbell Bench Press", "tip": "Upper chest thickness के लिए powerful"},
            {"name": "Cable Flyes (Mid Chest)",     "tip": "Full stretch at bottom + strong squeeze at top"},
            {"name": "Low to High Cable Flyes",     "tip": "Upper chest को target करने के लिए best isolation"},
            {"name": "Decline Dumbbell Press",      "tip": "Lower chest development के लिए"},
            {"name": "Chest Dips",                  "tip": "Lean forward, elbows flared — lower chest killer"},
            {"name": "Pec Deck / Machine Fly",      "tip": "Mind-muscle connection, slow negatives"},
            {"name": "Push-Ups (Wide/Diamond)",     "tip": "Home या finisher के लिए, chest to floor"},
        ],
        "youtube_search": "chest workout gym exercises Hindi",
        "info": "💡 Big & Full Chest: Heavy Compound पहले, फिर Isolation। Upper chest पर extra focus दो।",
    },
    "🦵 Legs": {
        "color": "#22c55e",
        "exercises": [
            {"name": "Barbell Back Squat",        "tip": "Deep squat लो, knees track over toes, chest up"},
            {"name": "Leg Press",                 "tip": "Full depth, feet shoulder width, knees cave-in मत होने दो"},
            {"name": "Romanian Deadlift",         "tip": "Hamstring में deep stretch feel करो, back straight"},
            {"name": "Bulgarian Split Squat",     "tip": "Rear foot elevated, front quad burn होगा"},
            {"name": "Walking Lunges (Dumbbell)", "tip": "Step forward, back knee almost touch floor"},
            {"name": "Leg Extension",             "tip": "Quad squeeze at top, slow negative"},
            {"name": "Seated Leg Curl",           "tip": "Hamstrings target, full contraction"},
            {"name": "Lying Leg Curl",            "tip": "Hamstring burn के लिए best"},
            {"name": "Standing Calf Raises",      "tip": "Full stretch at bottom + squeeze at top"},
            {"name": "Seated Calf Raises",        "tip": "Soleus muscle target, slow movement"},
        ],
        "youtube_search": "leg workout gym exercises squats Hindi",
        "info": "💡 Legs = Body का सबसे बड़ा muscle group। Skip मत करो!",
    },
    "🏛️ Back": {
        "color": "#6366f1",
        "exercises": [
            {"name": "Conventional Deadlift",       "tip": "Back flat, hips hinge, powerful pull from legs"},
            {"name": "Pull-Ups (Wide Grip)",         "tip": "Full stretch at bottom, chin over bar, controlled negative"},
            {"name": "Bent Over Barbell Row",        "tip": "Back parallel to floor, elbows back, squeeze shoulder blades"},
            {"name": "Lat Pulldown (Wide Grip)",     "tip": "Chest up, bar को chest की तरफ लाओ, lats stretch"},
            {"name": "Seated Cable Row",             "tip": "Neutral grip, shoulder blades strongly squeeze करो"},
            {"name": "Single Arm Dumbbell Row",      "tip": "One knee on bench, big stretch + powerful pull"},
            {"name": "Chest Supported T-Bar Row",    "tip": "Lower back strain कम, thickness के लिए excellent"},
            {"name": "Face Pull",                    "tip": "Rear delts + upper back + traps के लिए best"},
            {"name": "Straight Arm Pulldown",        "tip": "Lats isolation, arms straight रखो"},
            {"name": "Shrugs (Dumbbell or Barbell)", "tip": "Traps के लिए, full shrug + hold at top"},
        ],
        "youtube_search": "back workout gym exercises deadlift Hindi",
        "info": "💡 V-Taper बनाने के लिए: Wide Pull-Ups से Width, Bent Over Row से Thickness।",
    },
    "🏃 Cardio": {
        "color": "#a855f7",
        "exercises": [
            {"name": "Treadmill Run",    "tip": "Incline 5-10% रखो, last 5 min speed बढ़ाओ"},
            {"name": "HIIT Intervals",   "tip": "30s sprint + 30s rest, 90-100% effort sprint में दो"},
            {"name": "Cycling",          "tip": "Medium resistance, steady pace maintain करो"},
            {"name": "Jump Rope",        "tip": "Wrist से jump करो, low height jumps रखो"},
            {"name": "Stair Climber",    "tip": "Rails पकड़ने से बचो, core tight रखो"},
            {"name": "Rowing Machine",   "tip": "Legs first, then pull arms — full body cardio"},
            {"name": "Battle Ropes",     "tip": "Core engaged, explosive waves, 30s on 30s off"},
        ],
        "youtube_search": "cardio HIIT workout fat loss gym Hindi",
        "info": "💡 Fat loss के लिए HIIT सबसे effective है। 3-4 दिन HIIT + बाकी दिन light cardio best।",
    },
    "🧘 Yoga": {
        "color": "#06b6d4",
        "exercises": [
            {"name": "Sun Salutation",      "tip": "Slow controlled breathing, flow maintain करो"},
            {"name": "Warrior Pose",        "tip": "Knee ankle के ऊपर रखो, hips aligned"},
            {"name": "Downward Dog",        "tip": "Heels नीचे push करो, back straight रखो"},
            {"name": "Plank to Chaturanga", "tip": "Core tight रखो, elbows close to body"},
            {"name": "Cobra Pose",          "tip": "Lower back से lift करो, shoulders relaxed"},
            {"name": "Chair Pose",          "tip": "Weight heels पर रखो, knees stable"},
            {"name": "Seated Forward Fold", "tip": "Back straight रखो, धीरे stretch करो"},
            {"name": "Child's Pose",        "tip": "Deep breathing, पूरी body relax करो"},
            {"name": "Shavasana",           "tip": "Complete relaxation, mind calm रखो"},
        ],
        "youtube_search": "yoga workout gym recovery flexibility Hindi",
        "info": "💡 Yoga = Recovery + Flexibility + Strength + Mental Peace। Gym के बाद ये routine best है।",
    },
    "🥗 Diet & Nutrition": {
        "color": "#10b981",
        "exercises": [
            {"name": "High Protein Breakfast",     "tip": "Eggs + Oats + Paneer — सुबह 30g protein लो"},
            {"name": "Pre-Workout Meal",           "tip": "Banana + Peanut Butter — workout से 1hr पहले"},
            {"name": "Post-Workout Nutrition",     "tip": "Whey Protein + Rice — workout के 30 min में"},
            {"name": "Indian Bulking Diet",        "tip": "Dal + Chawal + Ghee + Chicken — calorie surplus"},
            {"name": "Fat Loss Diet Plan",         "tip": "Deficit 300-500 cal, high protein, low sugar"},
            {"name": "Vegetarian Protein Sources", "tip": "Paneer, Tofu, Rajma, Soybean, Curd — daily लो"},
            {"name": "Hydration Plan",             "tip": "3-4 लीटर पानी daily, workout में electrolytes"},
            {"name": "Cheat Meal Strategy",        "tip": "हफ्ते में 1 cheat meal ठीक है — overdo मत करो"},
        ],
        "youtube_search": "Indian gym diet plan muscle building fat loss Hindi",
        "info": "💡 Diet = Results का 70%। Gym कितना भी करो, खाना सही नहीं तो results नहीं।",
    },
}

# ─────────────────────────────────────────────
# SESSION STATE DEFAULTS
# ─────────────────────────────────────────────
days_hindi = {
    "Mon": "सोम", "Tue": "मंगल", "Wed": "बुध", "Thu": "गुरु",
    "Fri": "शुक्र", "Sat": "शनि", "Sun": "रवि"
}

defaults = {
    "checked":        {},
    "workout_log":    [],
    "streak":         0,
    "weekly":         {d: False for d in days_hindi},
    "last_workout":   "",
    "sw_running":     False,
    "sw_start_ts":    0.0,
    "sw_accumulated": 0.0,
    "rest_timer":     0,
    "body_weight":    70.0,
    "goal_weight":    65.0,
    "gs_loaded":      False,   # Google Sheet एक बार load हुई या नहीं
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Local JSON load (fallback)
load_data()

# ─────────────────────────────────────────────
# GOOGLE SHEET — startup load (सिर्फ एक बार)
# ─────────────────────────────────────────────
sheet_obj = get_sheet()
if sheet_obj and not st.session_state.gs_loaded:
    try:
        ensure_worksheets(sheet_obj)

        # Workout log
        gs_log = gsheet_load_workouts()
        if gs_log:
            st.session_state.workout_log = gs_log

        # Settings (body_weight, goal_weight, streak, last_workout)
        gs_settings = gsheet_load_settings()
        if gs_settings:
            for key in ["body_weight", "goal_weight"]:
                if key in gs_settings:
                    st.session_state[key] = float(gs_settings[key])
            if "streak" in gs_settings:
                st.session_state.streak = int(gs_settings["streak"])
            if "last_workout" in gs_settings:
                st.session_state.last_workout = str(gs_settings["last_workout"])

        # Weekly tracker
        gs_weekly = gsheet_load_weekly()
        if gs_weekly:
            st.session_state.weekly = gs_weekly

        st.session_state.gs_loaded = True
    except Exception:
        pass

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:10px 0 20px;'>
        <div style='font-size:38px;'>⚡</div>
        <div style='font-family:"Exo 2",sans-serif;font-size:20px;font-weight:900;
                    background:linear-gradient(135deg,#60a5fa,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    letter-spacing:2px;'>GYM AI</div>
        <div style='color:#475569;font-size:10px;margin-top:4px;'>Smart Fitness Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    # Google Sheet status indicator
    if sheet_obj:
        st.markdown("""
        <div style='text-align:center;background:#052e16;border:1px solid #166534;
                    border-radius:8px;padding:6px;margin-bottom:10px;'>
            <span style='color:#22c55e;font-size:12px;font-weight:700;'>
                🟢 Google Sheet Connected
            </span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align:center;background:#1c0a00;border:1px solid #92400e;
                    border-radius:8px;padding:6px;margin-bottom:10px;'>
            <span style='color:#f97316;font-size:12px;font-weight:700;'>
                🟡 Local Storage Only
            </span>
        </div>
        """, unsafe_allow_html=True)

    # Weekly split: recommend a different focus each day, while allowing manual override.
    weekly_split = [
        ("Chest", "🫁 Chest", "Push movements; chest-focused session"),
        ("Back", "🏛️ Back", "Pull movements; back-focused session"),
        ("Legs", "🦵 Legs", "Quads, hamstrings and glutes"),
        ("Shoulders", "🏔️ Shoulders", "Shoulders and controlled accessory work"),
        ("Biceps", "💪 Biceps", "Biceps and arm isolation"),
        ("Triceps", "🔱 Triceps", "Triceps and arm isolation"),
        ("Recovery", "🧘 Yoga", "Yoga, mobility or active recovery"),
    ]
    day_index = datetime.now().weekday()
    day_label, recommended_group, day_tip = weekly_split[day_index]
    available_groups = list(MUSCLE_DATA.keys())
    default_index = next(
        (i for i, group in enumerate(available_groups) if group == recommended_group),
        0
    )
    # Refresh the suggested selection when the calendar day changes; preserve manual
    # selection during the same day.
    today_key = date.today().isoformat()
    if st.session_state.get("daily_workout_date") != today_key:
        st.session_state["daily_workout_group"] = recommended_group
        st.session_state["daily_workout_date"] = today_key

    st.markdown("### 📅 आज का Workout Plan")
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#10233b,#172554);
                border:1px solid #31527a;border-radius:12px;padding:12px;margin-bottom:10px;'>
        <div style='font-size:12px;color:#93c5fd;font-weight:700;letter-spacing:1px;'>
            {datetime.now().strftime("%A").upper()} • WEEKLY SPLIT
        </div>
        <div style='font-size:21px;font-weight:800;color:#f8fafc;margin:5px 0;'>
            {recommended_group}
        </div>
        <div style='font-size:12px;color:#cbd5e1;'>{day_tip}</div>
        <div style='font-size:11px;color:#93c5fd;margin-top:7px;'>
            हर दिन अलग focus • अपनी सुविधा से group बदल सकते हो
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🏋️ Workout Menu")
    menu = st.radio(
        "आज का muscle group चुनें",
        available_groups,
        index=default_index,
        label_visibility="collapsed",
        key="daily_workout_group"
    )

    st.markdown("---")
    total_done = sum(1 for v in st.session_state.checked.values() if v)
    c1, c2 = st.columns(2)
    with c1: st.metric("🔥 Streak", f"{st.session_state.streak}d")
    with c2: st.metric("✅ Done",   str(total_done))

    st.markdown("---")
    st.markdown("**📊 All Groups**")
    for grp, data in MUSCLE_DATA.items():
        d = sum(1 for ex in data["exercises"]
                if st.session_state.checked.get(f"{grp}_{ex['name']}", False))
        t   = len(data["exercises"])
        p   = int((d / t) * 100)
        clr = data["color"]
        st.markdown(f"""
        <div style='margin-bottom:7px;'>
            <div style='display:flex;justify-content:space-between;
                        font-size:11px;color:#94a3b8;margin-bottom:3px;'>
                <span>{grp}</span>
                <span style='color:{clr};font-weight:700;'>{p}%</span>
            </div>
            <div style='background:#1e2d40;border-radius:99px;height:4px;'>
                <div style='width:{p}%;height:100%;background:{clr};
                            border-radius:99px;transition:width 0.5s ease;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.session_state.workout_log:
        csv_all = pd.DataFrame(st.session_state.workout_log).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", data=csv_all,
                           file_name=f"gym_{date.today()}.csv",
                           mime="text/csv", use_container_width=True)
    st.markdown("""
    <div style='color:#475569;font-size:10px;text-align:center;margin-top:10px;'>
        Made with ❤️ for Fitness
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────
muscle    = MUSCLE_DATA[menu]
color     = muscle["color"]
exercises = muscle["exercises"]

done_count  = sum(1 for ex in exercises
                  if st.session_state.checked.get(f"{menu}_{ex['name']}", False))
total_count = len(exercises)
pct         = int((done_count / total_count) * 100)

st.markdown(f"""
<div style='padding:20px 0 8px;'>
    <h1 style='margin:0;font-size:34px;font-weight:900;
               background:linear-gradient(135deg,{color},{color}88);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               font-family:"Exo 2",sans-serif;letter-spacing:2px;'>
        {menu.upper()} WORKOUT
    </h1>
    <p style='color:#64748b;margin:4px 0 0;font-size:14px;'>
        {date.today().strftime("%A, %d %B %Y")}
        &nbsp;|&nbsp; {done_count}/{total_count} exercises complete
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style='margin-bottom:16px;'>
    <div style='display:flex;justify-content:space-between;
                font-size:13px;color:#94a3b8;margin-bottom:6px;'>
        <span>आज की Progress</span>
        <span style='color:{color};font-weight:700;'>{pct}% Complete</span>
    </div>
    <div style='background:#1e2d40;border-radius:99px;height:10px;overflow:hidden;'>
        <div class='progress-fill' style='width:{pct}%;height:100%;
             background:linear-gradient(90deg,{color},{color}99);
             border-radius:99px;box-shadow:0 0 10px {color}66;'></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.info(muscle["info"])

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🏋️ Workout", "📊 Log & Stats", "🤖 AI Coach", "📈 Body History"])

# ══════════════════════════════════════════
# TAB 1 — WORKOUT
# ══════════════════════════════════════════
with tab1:
    col_ex, col_right = st.columns([3, 2])

    with col_ex:
        st.markdown("### Exercise List")
        st.caption("⚖️ पहले weight डालो → फिर ✅ tick करो")

        for ex in exercises:
            key = f"{menu}_{ex['name']}"
            is_done = st.session_state.checked.get(key, False)
            bg = f"{color}18" if is_done else "#0d1117"
            border = color if is_done else "#1e2d40"
            nc = color if is_done else "#e2e8f0"
            strike = "line-through" if is_done else "none"

            st.markdown(f"""
            <div style='padding:10px 12px;border-radius:10px;
                        background:{bg};border:1px solid {border};margin:8px 0 4px;'>
                <div style='font-size:15px;font-weight:700;color:{nc};
                            text-decoration:{strike};'>{ex["name"]}</div>
                <div style='font-size:12px;color:#94a3b8;margin-top:3px;'>💡 {ex["tip"]}</div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("📝 सेट, रेप्स और वजन दर्ज करें", expanded=False):
                sets_count = st.number_input(
                    "कितने सेट?", min_value=1, max_value=8, value=3, step=1,
                    key=f"sets_count_{key}"
                )
                set_entries = []
                for set_no in range(int(sets_count)):
                    st.markdown(f"**Set {set_no + 1}**")
                    sw1, sw2 = st.columns(2)
                    with sw1:
                        set_weight = st.number_input(
                            "वजन (kg)", min_value=0.0, max_value=300.0,
                            value=0.0, step=0.5, key=f"set_weight_{key}_{set_no}"
                        )
                    with sw2:
                        set_reps = st.number_input(
                            "Reps", min_value=1, max_value=100, value=10, step=1,
                            key=f"set_reps_{key}_{set_no}"
                        )
                    set_entries.append((float(set_weight), int(set_reps)))

                if st.button("✅ सेट सेव करें" if not is_done else "↻ दोबारा लॉग करें",
                             key=f"save_sets_{key}", use_container_width=True):
                    if any(weight <= 0 for weight, _ in set_entries):
                        st.warning("हर सेट के लिए वजन 0 से अधिक दर्ज करें।")
                    else:
                        now = datetime.now()
                        today = now.strftime("%d-%m-%Y")
                        if st.session_state.last_workout != today:
                            st.session_state.streak += 1
                            st.session_state.last_workout = today
                        today_day = now.strftime("%a")
                        if today_day in st.session_state.weekly:
                            st.session_state.weekly[today_day] = True

                        body_part = menu.split(" ", 1)[1] if " " in menu else menu
                        entries = []
                        for set_no, (weight, reps) in enumerate(set_entries, start=1):
                            entries.append({
                                "Date": today,
                                "Time": now.strftime("%I:%M %p"),
                                "Body Part": body_part,
                                "Exercise": ex["name"],
                                "Weight (kg)": weight,
                                "Status": f"✔ Set {set_no}/{len(set_entries)} · {reps} reps"
                            })

                        # Keep the existing WorkoutLog columns; each set is a row.
                        st.session_state.workout_log = entries + st.session_state.workout_log
                        st.session_state.checked[key] = True
                        st.session_state.rest_timer = 60
                        save_data()
                        failed_saves = sum(1 for entry in entries if not gsheet_save_workout(entry))
                        if failed_saves:
                            st.warning(
                                f"{len(entries) - failed_saves}/{len(entries)} सेट Google Sheets में सेव हुए। "
                                "बाकी सेटों के लिए कनेक्शन जाँचें; लोकल लॉग में सभी सेट मौजूद हैं।"
                            )
                        else:
                            st.success(f"{len(entries)} सेट लॉग हो गए — {ex['name']} 💪")
                        st.rerun()

            st.markdown("")

        st.markdown("---")

        # YouTube Section
        st.markdown("### 🎥 YouTube Video Guide")
        yt_query      = muscle["youtube_search"].replace(" ", "+")
        yt_search_url = f"https://www.youtube.com/results?search_query={yt_query}"

        st.markdown(f"""
        <div style='background:#0d1117;border:1px solid #1e2d40;border-radius:14px;
                    padding:20px;text-align:center;'>
            <div style='font-size:40px;margin-bottom:8px;'>▶️</div>
            <div style='color:#e2e8f0;font-size:16px;font-weight:700;margin-bottom:6px;'>
                {menu} Videos
            </div>
            <div style='color:#64748b;font-size:13px;margin-bottom:16px;'>
                YouTube पर best workout videos देखो
            </div>
            <a href="{yt_search_url}" target="_blank"
               style='background:linear-gradient(135deg,#ff0000,#cc0000);
                      color:white;padding:10px 24px;border-radius:10px;
                      text-decoration:none;font-weight:700;font-family:Rajdhani,sans-serif;
                      font-size:15px;display:inline-block;'>
                🔴 YouTube पर Search करो
            </a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**⚡ Quick Searches:**")
        menu_name = menu.split(' ', 1)[1] if ' ' in menu else menu
        suggestions = [
            f"{menu_name} workout for beginners Hindi",
            f"Best {menu_name} exercises gym",
            f"{menu_name} diet plan Indian",
            f"Indian gym diet nutrition tips Hindi",
        ]
        for s in suggestions:
            encoded = s.replace(" ", "+")
            st.markdown(f"🔗 [{s}](https://www.youtube.com/results?search_query={encoded})")

    # RIGHT COLUMN
    with col_right:

        # STOPWATCH
        st.markdown("### ⏱️ Stopwatch")
        if st.session_state.sw_running:
            elapsed_now = st.session_state.sw_accumulated + (time.time() - st.session_state.sw_start_ts)
        else:
            elapsed_now = st.session_state.sw_accumulated

        total_secs = int(elapsed_now)
        sw_h = total_secs // 3600
        sw_m = (total_secs % 3600) // 60
        sw_s = total_secs % 60
        sw_display = f"{sw_h:02}:{sw_m:02}:{sw_s:02}" if sw_h > 0 else f"{sw_m:02}:{sw_s:02}"
        sw_color   = "#22c55e" if st.session_state.sw_running else "#e2e8f0"

        st.markdown(f"""
        <div class='glass' style='text-align:center;padding:20px;'>
            <div style='font-size:42px;font-weight:900;color:{sw_color};
                        font-family:"Exo 2",sans-serif;letter-spacing:3px;'>
                {sw_display}
            </div>
            <div style='color:#64748b;font-size:12px;margin-top:4px;'>
                {'🟢 Running...' if st.session_state.sw_running else 'Workout Time'}
            </div>
        </div>
        """, unsafe_allow_html=True)

        sw1, sw2, sw3 = st.columns(3)
        with sw1:
            if st.button("▶️ Start", use_container_width=True, key="sw_start"):
                if not st.session_state.sw_running:
                    st.session_state.sw_running  = True
                    st.session_state.sw_start_ts = time.time()
                st.rerun()
        with sw2:
            if st.button("⏸ Pause", use_container_width=True, key="sw_pause"):
                if st.session_state.sw_running:
                    st.session_state.sw_accumulated += time.time() - st.session_state.sw_start_ts
                    st.session_state.sw_running = False
                st.rerun()
        with sw3:
            if st.button("🔴 Reset", use_container_width=True, key="sw_reset"):
                st.session_state.sw_running     = False
                st.session_state.sw_accumulated = 0.0
                st.session_state.sw_start_ts    = 0.0
                st.rerun()

        if st.session_state.sw_running:
            time.sleep(1)
            st.rerun()

        st.markdown("---")

        # REST TIMER
        st.markdown("### 💤 Rest Timer")
        rest_val = st.session_state.rest_timer
        rest_clr = "#22c55e" if rest_val > 30 else ("#f97316" if rest_val > 0 else "#475569")

        st.markdown(f"""
        <div class='glass' style='text-align:center;padding:18px;'>
            <div style='font-size:36px;font-weight:900;color:{rest_clr};
                        font-family:"Exo 2",sans-serif;letter-spacing:2px;'>
                {rest_val:02}s
            </div>
            <div style='color:#64748b;font-size:12px;margin-top:4px;'>Rest Time</div>
        </div>
        """, unsafe_allow_html=True)

        r1, r2, r3 = st.columns(3)
        with r1:
            if st.button("30s", use_container_width=True): st.session_state.rest_timer = 30; st.rerun()
        with r2:
            if st.button("60s", use_container_width=True): st.session_state.rest_timer = 60; st.rerun()
        with r3:
            if st.button("90s", use_container_width=True): st.session_state.rest_timer = 90; st.rerun()
        if rest_val > 0:
            if st.button("⏹ Stop Rest", use_container_width=True):
                st.session_state.rest_timer = 0; st.rerun()

        st.markdown("---")

        # WEEKLY TRACKER
        st.markdown("### 📅 इस हफ्ते")
        cols7 = st.columns(7)
        for i, (day, hindi) in enumerate(days_hindi.items()):
            with cols7[i]:
                val    = st.session_state.weekly.get(day, False)
                bg_day = color  if val else "#1e2d40"
                tc     = "#000" if val else "#64748b"
                st.markdown(f"""
                <div style='background:{bg_day};border-radius:8px;padding:6px 2px;
                            text-align:center;
                            box-shadow:{"0 0 8px "+color+"66" if val else "none"};'>
                    <div style='font-size:9px;font-weight:700;color:{tc};'>{hindi}</div>
                    <div style='font-size:13px;'>{"✓" if val else "·"}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("", key=f"day_{day}", help=day):
                    st.session_state.weekly[day] = not val
                    save_data()
                    gsheet_save_weekly(st.session_state.weekly)
                    st.rerun()

        gym_days = sum(1 for v in st.session_state.weekly.values() if v)
        st.markdown(f"""
        <div style='text-align:center;margin:8px 0;color:{color};font-weight:700;font-size:14px;'>
            {gym_days}/7 दिन Gym 🏆
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # QUICK STATS
        st.markdown("### 📈 Quick Stats")
        today_str = date.today().strftime("%d-%m-%Y")
        s1, s2 = st.columns(2)
        with s1: st.metric("आज",       f"{done_count}/{total_count}")
        with s2: st.metric("Today Log", len([l for l in st.session_state.workout_log
                                              if l["Date"] == today_str]))
        s3, s4 = st.columns(2)
        with s3: st.metric("🔥 Streak", f"{st.session_state.streak}d")
        with s4: st.metric("📝 Total",  len(st.session_state.workout_log))

        st.markdown("---")

        # BODY STATS
        st.markdown("### ⚖️ Body Stats")
        bw = st.number_input("वजन (kg):", min_value=30.0, max_value=200.0,
                             value=float(st.session_state.body_weight), step=0.5,
                             key="bw_input")
        gw = st.number_input("Goal (kg):", min_value=30.0, max_value=200.0,
                             value=float(st.session_state.goal_weight), step=0.5,
                             key="gw_input")
        if st.button("💾 Save Stats", use_container_width=True):
            st.session_state.body_weight = bw
            st.session_state.goal_weight = gw
            save_data()
            # Google Sheet में save करो
            ok = gsheet_save_body_stats(bw, gw)
            gsheet_save_weekly(st.session_state.weekly)
            if ok:
                st.success("✅ Saved! (Local + Google Sheet)")
            else:
                st.success("✅ Saved! (Local only)")

        if bw > 0:
            bmi     = bw / (1.70 ** 2)
            bmi_cat = ("Underweight" if bmi < 18.5
                       else "Normal"    if bmi < 25
                       else "Overweight" if bmi < 30
                       else "Obese")
            bmi_clr = ("#22c55e" if bmi_cat == "Normal"
                       else "#f97316" if bmi_cat == "Overweight"
                       else "#ef4444" if bmi_cat == "Obese"
                       else "#60a5fa")
            diff = abs(bw - gw)
            prog = max(0, min(100, int((1 - diff / max(bw, gw)) * 100)))
            st.markdown(f"""
            <div class='glass'>
                <div style='font-size:13px;color:#94a3b8;'>
                    BMI: <b style='color:{bmi_clr};'>{bmi:.1f} ({bmi_cat})</b>
                </div>
                <div style='font-size:13px;color:#94a3b8;margin-top:4px;'>
                    Goal: <b style='color:#22c55e;'>{gw} kg</b>
                    &nbsp;|&nbsp; बचा: <b style='color:#ef4444;'>{diff:.1f} kg</b>
                </div>
                <div style='background:#1e2d40;border-radius:99px;height:6px;margin-top:10px;'>
                    <div style='width:{prog}%;height:100%;background:#22c55e;
                                border-radius:99px;transition:width 0.5s;'></div>
                </div>
                <div style='font-size:11px;color:#475569;margin-top:4px;'>
                    Goal Progress: {prog}%
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # GYM MUSIC
        st.markdown("### 🎧 Gym Music")
        music_choice = st.selectbox("Select:", ["Off", "🔥 Motivation", "💪 Hard Mix", "🎧 EDM"],
                                    key="music_sel")
        music_urls = {
            "🔥 Motivation": "https://www.youtube.com/embed/U3ASj1L6_sY",
            "💪 Hard Mix":   "https://www.youtube.com/embed/2Vv-BfVoq4g",
            "🎧 EDM":        "https://www.youtube.com/embed/fLexgOxsZu0",
        }
        if music_choice in music_urls:
            st.markdown(f"""
            <div style='border-radius:12px;overflow:hidden;margin-top:6px;border:1px solid #1e2d40;'>
            <iframe width="100%" height="120"
                src="{music_urls[music_choice]}"
                frameborder="0" allowfullscreen>
            </iframe>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 2 — LOG & STATS
# ══════════════════════════════════════════
with tab2:
    st.markdown("### 📊 Workout Statistics")

    total_log   = len(st.session_state.workout_log)
    today_log_c = len([l for l in st.session_state.workout_log
                        if l["Date"] == date.today().strftime("%d-%m-%Y")])
    groups_done = len(set(l["Body Part"] for l in st.session_state.workout_log))

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("💪 Total Done",  total_done)
    with c2: st.metric("📝 Log Entries", total_log)
    with c3: st.metric("🏋️ Groups",     groups_done)
    with c4: st.metric("📅 आज",         today_log_c)

    if st.session_state.workout_log:
        df = pd.DataFrame(st.session_state.workout_log)

        st.markdown("---")
        st.markdown("### 📋 Recent Workout Log")
        for row in st.session_state.workout_log[:5]:
            st.markdown(f"""
            <div class='glass' style='display:flex;align-items:center;gap:12px;'>
                <span style='color:#64748b;font-size:12px;min-width:80px;'>📅 {row['Date']}</span>
                <span style='color:#e2e8f0;font-weight:700;flex:1;'>{row['Exercise']}</span>
                <span style='color:{color};font-weight:700;'>⚖️ {row['Weight (kg)']} kg</span>
                <span style='color:#22c55e;font-size:13px;'>✅</span>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("📋 Full Log Table देखो"):
            st.dataframe(df, use_container_width=True, hide_index=True,
                         column_config={
                             "Date":        st.column_config.TextColumn("📅 Date",     width="small"),
                             "Time":        st.column_config.TextColumn("⏰ Time",     width="small"),
                             "Body Part":   st.column_config.TextColumn("💪 Part",     width="medium"),
                             "Exercise":    st.column_config.TextColumn("🏋️ Exercise", width="large"),
                             "Weight (kg)": st.column_config.NumberColumn("⚖️ kg",     width="small"),
                             "Status":      st.column_config.TextColumn("✅ Status",   width="small"),
                         })

        st.markdown("---")
        st.markdown("### 📈 Progress & Analytics")

        # Normalize legacy and multi-set records without changing the saved schema.
        analytics = df.copy()
        analytics["Weight (kg)"] = pd.to_numeric(analytics["Weight (kg)"], errors="coerce").fillna(0)
        analytics["Parsed Date"] = pd.to_datetime(
            analytics["Date"], dayfirst=True, errors="coerce"
        )
        analytics["Reps"] = pd.to_numeric(
            analytics["Status"].astype(str).str.extract(r"(\d+)\s*reps", expand=False),
            errors="coerce"
        )
        analytics["Volume (kg)"] = analytics["Weight (kg)"] * analytics["Reps"].fillna(0)
        valid_dates = analytics["Parsed Date"].dropna()
        today_date = pd.Timestamp(date.today())
        last_7_start = today_date - pd.Timedelta(days=6)
        days_last_7 = analytics.loc[
            analytics["Parsed Date"].between(last_7_start, today_date), "Parsed Date"
        ].dt.date.nunique()
        top_part = analytics["Body Part"].value_counts().index[0] if not analytics.empty else "—"
        total_volume = analytics["Volume (kg)"].sum()
        logged_sets = int(analytics["Reps"].notna().sum())

        a1, a2, a3, a4 = st.columns(4)
        with a1:
            st.metric("📅 Training Days", f"{days_last_7}/7", help="पिछले 7 दिनों में दर्ज अलग-अलग workout days")
        with a2:
            st.metric("🏋️ Logged Sets", logged_sets, help="नए multi-set रिकॉर्ड जिनमें reps दर्ज हैं")
        with a3:
            st.metric("📦 Volume", f"{total_volume:,.0f} kg", help="केवल उन सेटों का weight × reps जिनमें reps दर्ज हैं")
        with a4:
            st.metric("🎯 Most Trained", top_part)

        st.caption("पुराने लॉग में reps उपलब्ध न होने पर volume में उन्हें शामिल नहीं किया जाता।")

        st.markdown("---")
        st.markdown("### 📊 Muscle Group Training")
        group_counts = analytics.groupby("Body Part").agg(
            Entries=("Exercise", "count"),
            Workout_Days=("Parsed Date", lambda values: values.dropna().dt.date.nunique())
        ).sort_values("Entries", ascending=False)
        if not group_counts.empty:
            st.bar_chart(group_counts[["Entries"]])
            with st.expander("मसल ग्रुप के विस्तृत आँकड़े"):
                st.dataframe(group_counts.rename(columns={
                    "Entries": "Log Entries", "Workout_Days": "Training Days"
                }), use_container_width=True)

        st.markdown("---")
        st.markdown("### ⚖️ Exercise Progress")
        valid_weights = analytics[analytics["Weight (kg)"] > 0].copy()
        ex_opts = sorted(valid_weights["Exercise"].dropna().unique().tolist())
        if ex_opts:
            selected_exercise = st.selectbox(
                "Exercise चुनें", ex_opts, key="progress_exercise_select"
            )
            ex_df = valid_weights[valid_weights["Exercise"] == selected_exercise].copy()
            ex_df = ex_df.dropna(subset=["Parsed Date"]).sort_values("Parsed Date")
            if not ex_df.empty:
                daily_progress = ex_df.groupby("Parsed Date").agg(
                    **{"Weight (kg)": ("Weight (kg)", "max")}
                )
                st.line_chart(daily_progress)
                first_best = float(ex_df.iloc[0]["Weight (kg)"])
                max_weight = float(ex_df["Weight (kg)"].max())
                latest_weight = float(ex_df.iloc[-1]["Weight (kg)"])
                p1, p2, p3 = st.columns(3)
                with p1:
                    st.metric("पहला दर्ज वजन", f"{first_best:g} kg")
                with p2:
                    st.metric("सबसे अधिक वजन", f"{max_weight:g} kg")
                with p3:
                    st.metric("आखिरी दर्ज वजन", f"{latest_weight:g} kg")
                if ex_df["Reps"].notna().any():
                    st.markdown("#### 🔁 Reps Progress")
                    reps_df = ex_df.dropna(subset=["Reps"]).groupby("Parsed Date").agg(
                        Reps=("Reps", "max")
                    )
                    if not reps_df.empty:
                        st.line_chart(reps_df)
            else:
                st.info("इस exercise के लिए तारीख वाला रिकॉर्ड उपलब्ध नहीं है।")
        else:
            st.info("Progress chart के लिए पहले किसी exercise में वजन दर्ज करें।")

        st.markdown("---")
        st.markdown("### 🗓️ Recent Training History")
        history = analytics.dropna(subset=["Parsed Date"]).copy()
        if not history.empty:
            history["Date"] = history["Parsed Date"].dt.strftime("%d-%m-%Y")
            recent_days = sorted(history["Parsed Date"].dt.date.unique(), reverse=True)[:14]
            day_options = [d.strftime("%d-%m-%Y") for d in recent_days]
            selected_days = st.multiselect(
                "तारीख के अनुसार फ़िल्टर करें", day_options,
                default=day_options[:min(7, len(day_options))],
                key="history_date_filter"
            )
            filtered_history = history[
                history["Date"].isin(selected_days)
            ][["Date", "Time", "Body Part", "Exercise", "Weight (kg)", "Status"]]
            st.dataframe(filtered_history, use_container_width=True, hide_index=True)
        else:
            st.info("तारीख वाले workout रिकॉर्ड उपलब्ध नहीं हैं।")

        st.markdown("---")
        cd, cl = st.columns([3, 1])
        with cd:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ CSV Download करो", data=csv,
                               file_name=f"gym_log_{date.today()}.csv",
                               mime="text/csv", use_container_width=True)
        with cl:
            if st.button("🗑️ Clear Log", use_container_width=True):
                st.session_state.workout_log = []
                save_data(); st.rerun()
    else:
        st.markdown("""
        <div style='text-align:center;padding:60px;color:#334155;'>
            <div style='font-size:48px;'>📋</div>
            <div style='font-size:18px;margin-top:12px;color:#475569;'>अभी कोई log नहीं है</div>
            <div style='font-size:13px;color:#1e2d40;margin-top:6px;'>
                Workout tab → exercises tick करो 💪
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 3 — AI COACH
# ══════════════════════════════════════════
with tab3:
    st.markdown("### 🤖 AI Gym Coach")

    if not AI_ENABLED:
        st.warning("⚠️ AI enable करने के लिए Streamlit Secrets में GROQ_API_KEY add करो।")
        st.markdown("""
        <div class='glass'>
            <b>Steps:</b><br>
            1. 👉 <a href='https://console.groq.com' target='_blank' style='color:#60a5fa;'>
               console.groq.com</a> पर जाओ → Free API key लो<br>
            2. Streamlit Cloud → App Settings → Secrets<br>
            3. यह add करो:<br>
            <code style='color:#60a5fa;'>GROQ_API_KEY = "your_key_here"</code>
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.session_state.workout_log:
            last_bp = st.session_state.workout_log[0]["Body Part"]
            suggestions = {
                "Chest":     "👉 आज Back + Biceps करो",
                "Back":      "👉 आज Chest + Triceps करो",
                "Legs":      "👉 आज Shoulders + Cardio करो",
                "Biceps":    "👉 आज Triceps + Chest करो",
                "Triceps":   "👉 आज Back + Biceps करो",
                "Shoulders": "👉 आज Legs करो 🦵",
                "Cardio":    "👉 आज Strength training करो 💪",
            }
            sugg = suggestions.get(last_bp, "👉 आज Full Body करो 🔥")
            st.markdown(f"""
            <div class='glass'>
                🧠 <b>Smart Suggestion:</b> आखिरी workout था
                <b style='color:#60a5fa;'>{last_bp}</b><br>
                <span style='color:#22c55e;font-weight:700;'>{sugg}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("#### ⚡ Quick Ask")
    q1, q2 = st.columns(2)
    with q1:
        if st.button("💪 Next Workout Plan", use_container_width=True):
            with st.spinner("AI सोच रहा है..."):
                ans = ask_ai("Next workout plan बनाओ — कल क्या करूँ?", st.session_state.workout_log)
            st.success(ans)
        if st.button("🔥 Fat Loss Tips", use_container_width=True):
            with st.spinner("AI सोच रहा है..."):
                ans = ask_ai("Fat loss के लिए best tips दो।", st.session_state.workout_log)
            st.success(ans)
    with q2:
        if st.button("📈 Strength बढ़ाओ", use_container_width=True):
            with st.spinner("AI सोच रहा है..."):
                ans = ask_ai("Strength और muscle कैसे बढ़ाऊ?", st.session_state.workout_log)
            st.success(ans)
        if st.button("🥗 Diet Plan", use_container_width=True):
            with st.spinner("AI सोच रहा है..."):
                ans = ask_ai("Simple Indian diet plan दो gym के लिए।", st.session_state.workout_log)
            st.success(ans)

    st.markdown("---")
    st.markdown("#### 💬 Custom Question पूछो")
    q = st.text_input("आज क्या पूछना है? (Hindi या English)")
    if st.button("🚀 Ask AI Coach", use_container_width=True):
        if q:
            with st.spinner("AI सोच रहा है..."):
                answer = ask_ai(q, st.session_state.workout_log)
            st.success(answer)
        else:
            st.warning("पहले question लिखो!")

    st.markdown("---")
    st.markdown("#### 📅 30-Day Smart Plan")
    if st.button("📅 Generate 30-Day Plan", use_container_width=True):
        if AI_ENABLED:
            with st.spinner("AI plan बना रहा है..."):
                plan = ask_ai(
                    "Mujhe ek 30-day gym workout plan do with weekly split, sets, reps aur diet tips. "
                    "Hindi + English mix mein. Short aur clear.",
                    st.session_state.workout_log
                )
            st.success(plan)
        else:
            st.markdown("""
**📅 30-Day Smart Plan:**

**Week 1-2 (Foundation):**
- Mon: Chest + Triceps
- Tue: Back + Biceps
- Wed: Cardio / HIIT
- Thu: Shoulders
- Fri: Legs
- Sat: Yoga / Rest
- Sun: Rest

**Week 3-4 (Progressive Overload):**
- हर exercise में 5% weight बढ़ाओ
- Protein: 1.6g per kg body weight
- नींद: 7-8 घंटे
            """)

# ══════════════════════════════════════════
# TAB 4 — BODY HISTORY (नया Tab!)
# ══════════════════════════════════════════
with tab4:
    st.markdown("### 📈 Body Weight & BMI History")

    if sheet_obj:
        history_data = gsheet_load_body_stats_history()
        if history_data:
            df_body = pd.DataFrame(history_data)
            df_body["Date"] = pd.to_datetime(df_body["Date"], dayfirst=True)
            df_body = df_body.sort_values("Date")

            # Weight Chart
            st.markdown("#### ⚖️ Weight Progress")
            st.line_chart(df_body.set_index("Date")[["Body Weight", "Goal Weight"]])

            # BMI Chart
            st.markdown("#### 🩺 BMI History")
            st.line_chart(df_body.set_index("Date")["BMI"])

            # Summary
            latest = df_body.iloc[-1]
            first  = df_body.iloc[0]
            lost   = round(float(first["Body Weight"]) - float(latest["Body Weight"]), 1)

            h1, h2, h3 = st.columns(3)
            with h1: st.metric("📅 शुरुआत",   f"{first['Body Weight']} kg")
            with h2: st.metric("📅 अभी",       f"{latest['Body Weight']} kg")
            with h3: st.metric("📉 Change",    f"{lost:+.1f} kg",
                               delta_color="inverse")

            st.markdown("---")
            with st.expander("📋 Full History Table"):
                st.dataframe(df_body, use_container_width=True, hide_index=True)
        else:
            st.info("अभी कोई body stats नहीं हैं। Workout tab → Body Stats → Save Stats दबाओ।")
    else:
        st.warning("""
        ⚠️ Google Sheet connect नहीं है।
        Body history देखने के लिए Streamlit Secrets में credentials add करो।
        """)
        st.markdown("""
        <div class='glass'>
            <b>📋 Google Sheet Setup Steps:</b><br><br>
            <b>1.</b> Google Cloud Console पर जाओ → Service Account बनाओ<br>
            <b>2.</b> JSON key download करो<br>
            <b>3.</b> Streamlit Secrets में यह add करो:<br><br>
            <code style='color:#60a5fa;'>
            SHEET_ID = "your_sheet_id"<br><br>
            [gcp_service_account]<br>
            type = "service_account"<br>
            project_id = "..."<br>
            private_key = "..."<br>
            client_email = "...@....iam.gserviceaccount.com"<br>
            </code><br>
            <b>4.</b> उस email को Google Sheet में Editor access दो
        </div>
        """, unsafe_allow_html=True)
