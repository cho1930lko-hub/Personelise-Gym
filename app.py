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
    initial_sidebar_state="expanded"
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
    h1 { font-size: 22px !important; }
    .block-container { padding: 1rem !important; }
    .stMetric { font-size: 12px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 13px !important; }
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
        history = "\n".join([
            f"Date:{l['Date']} | {l['Body Part']} | {l['Exercise']} | {l.get('Weight (kg)',0)}kg"
            for l in log_data[:20]
        ])
        bw          = st.session_state.get("body_weight", 70)
        gw          = st.session_state.get("goal_weight", 65)
        streak      = st.session_state.get("streak", 0)
        weekly_days = sum(1 for v in st.session_state.get("weekly", {}).values() if v)

        prompt = f"""
You are an expert personal gym trainer and nutritionist.

USER PROFILE:
- Current Weight: {bw} kg
- Goal Weight: {gw} kg
- Current Streak: {streak} days
- Days trained this week: {weekly_days}/7
- Goal type: {"Fat Loss" if gw < bw else "Muscle Gain"}

RECENT WORKOUT HISTORY (last 20 sessions):
{history if history else 'No history yet — beginner user'}

YOUR JOB:
- Analyze their actual data above
- Give PERSONALIZED advice based on their weight, goal, streak, history
- Point out what muscle groups they are MISSING or OVERTRAINING
- Suggest specific weights to increase based on their logs
- Give advice in Hindi + English mix
- Max 150 words, use bullet points
- Do NOT give generic advice — be SPECIFIC to their data
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
    except Exception as e:
        return f"❌ AI Error: {str(e)}"

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

    st.markdown("### 🏋️ Workout Menu")
    menu = st.radio("Select", list(MUSCLE_DATA.keys()), label_visibility="collapsed")

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
            key     = f"{menu}_{ex['name']}"
            is_done = st.session_state.checked.get(key, False)
            bg      = f"{color}18" if is_done else "#0d1117"
            border  = color        if is_done else "#1e2d40"
            nc      = color        if is_done else "#e2e8f0"
            strike  = "line-through" if is_done else "none"

            col_chk, col_inf, col_wt = st.columns([1, 6, 2])

            with col_chk:
                checked = st.checkbox("", value=is_done, key=f"cb_{key}")
                if checked != is_done:
                    wt_val = st.session_state.get(f"wt_{key}", 0.0)
                    if checked and wt_val == 0:
                        st.warning("⚠️ पहले weight डालो!")
                    else:
                        st.session_state.checked[key] = checked
                        if checked:
                            now   = datetime.now()
                            today = now.strftime("%d-%m-%Y")
                            if st.session_state.last_workout != today:
                                st.session_state.streak      += 1
                                st.session_state.last_workout = today
                            today_day = now.strftime("%a")
                            if today_day in st.session_state.weekly:
                                st.session_state.weekly[today_day] = True
                            entry = {
                                "Date":        today,
                                "Time":        now.strftime("%I:%M %p"),
                                "Body Part":   menu.split(" ", 1)[1] if " " in menu else menu,
                                "Exercise":    ex["name"],
                                "Weight (kg)": wt_val,
                                "Status":      "✔ Done"
                            }
                            st.session_state.workout_log.insert(0, entry)
                            st.session_state.rest_timer = 60
                            save_data()
                            # Google Sheet में भी save करो
                            gsheet_save_workout(entry)
                            st.toast(f"✅ {ex['name']} logged! 💪", icon="🔥")
                        st.rerun()

            with col_inf:
                st.markdown(f"""
                <div style='padding:8px 12px;border-radius:10px;
                            background:{bg};border:1px solid {border};'>
                    <div style='font-size:15px;font-weight:700;
                                color:{nc};text-decoration:{strike};'>{ex["name"]}</div>
                    <div style='font-size:12px;color:#64748b;margin-top:2px;'>
                        💡 {ex["tip"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_wt:
                st.number_input("⚖️ kg", min_value=0.0, max_value=300.0,
                                step=0.5, value=0.0,
                                key=f"wt_{key}", label_visibility="visible")
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
        st.markdown("### 🔥 Advanced Analytics")
        avg_wt      = df["Weight (kg)"].mean()
        top_part    = df["Body Part"].value_counts().idxmax()
        days_worked = len(set(df["Date"]))
        consistency = min(int((days_worked / 7) * 100), 100)
        cardio_cnt  = len(df[df["Body Part"] == "Cardio"])
        fat_score   = min(cardio_cnt * 10, 100)

        a1, a2, a3 = st.columns(3)
        with a1: st.metric("⚖️ Avg Weight",  f"{avg_wt:.1f} kg")
        with a2: st.metric("🏆 Top Focus",   top_part)
        with a3: st.metric("📅 Consistency", f"{consistency}%")

        st.markdown(f"""
        <div style='margin:12px 0 4px;font-size:13px;color:#94a3b8;'>
            🔥 Fat Loss Score: <b style='color:#ef4444;'>{fat_score}/100</b>
        </div>
        <div style='background:#1e2d40;border-radius:99px;height:8px;'>
            <div style='width:{fat_score}%;height:100%;
                        background:linear-gradient(90deg,#f97316,#ef4444);
                        border-radius:99px;transition:width 0.5s;'></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📊 Body Part Breakdown")
        bd = df["Body Part"].value_counts().reset_index()
        bd.columns = ["Body Part", "Count"]
        st.bar_chart(bd.set_index("Body Part"))

        st.markdown("### ⚖️ Weight Progress")
        ex_opts = df[df["Weight (kg)"] > 0]["Exercise"].unique().tolist()
        if ex_opts:
            sel   = st.selectbox("Exercise चुनो:", ex_opts)
            ex_df = df[df["Exercise"] == sel][["Date", "Weight (kg)"]].copy()
            ex_df = ex_df[ex_df["Weight (kg)"] > 0].copy()
            ex_df["Date"] = pd.to_datetime(ex_df["Date"], dayfirst=True)
            ex_df = ex_df.sort_values("Date")
            if not ex_df.empty:
                st.line_chart(ex_df.set_index("Date"))
                weights = ex_df["Weight (kg)"].values
                if len(weights) >= 3:
                    trend  = weights[-1] - weights[0]
                    future = weights[-1] + (trend / len(weights)) * 7
                    st.info(f"🔮 अगले 7 दिन में अनुमानित weight: **{future:.1f} kg**")
        else:
            st.info("पहले exercises में weight डालो — chart यहाँ दिखेगा।")

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
