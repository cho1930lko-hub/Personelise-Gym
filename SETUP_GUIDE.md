# 🏋️ Smart AI Gym Dashboard — Setup Guide

---

## 📁 Files List
- `gym_dashboard.py` — Main app file
- `requirements.txt` — Dependencies

---

## 🚀 Step 1: GitHub पर Upload करो

1. GitHub.com खोलो → अपना account login करो
2. New Repository बनाओ: `gym-ai-dashboard`
3. दोनों files upload करो:
   - `gym_dashboard.py`
   - `requirements.txt`
4. Commit करो ✅

---

## ☁️ Step 2: Streamlit Cloud पर Deploy करो

1. **share.streamlit.io** खोलो
2. GitHub से login करो
3. "New App" → अपना repo select करो
4. Main file: `gym_dashboard.py`
5. Deploy! ✅

---

## 🔑 Step 3: Secrets Add करो (Streamlit Cloud)

App settings → Secrets में यह paste करो:

```toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxx"
SERVICE_ACCOUNT_JSON = '''
{
  "type": "service_account",
  "project_id": "your-project",
  ...your credentials JSON here...
}
'''
```

### GROQ Key कैसे पाएं (FREE):
1. console.groq.com खोलो
2. Account बनाओ (free)
3. API Keys → Create Key
4. Copy करो → Secrets में paste करो

---

## 📊 Step 4: Google Sheet बनाओ (Optional)

1. Google Sheet बनाओ: **"Gym Workout Log"**
2. Sheet 1 में headers:
   `Date | Time | Body Part | Exercise | Status`
3. Google Cloud Console → Service Account बनाओ
4. JSON key download करो
5. Sheet में service account email को Editor access दो

---

## ✅ App Features

| Feature | Status |
|---------|--------|
| 8 Body Parts (Biceps, Triceps...) | ✅ |
| Exercise Checklist | ✅ |
| Progress Bar | ✅ |
| YouTube Video Links | ✅ |
| Weekly Day Tracker | ✅ |
| AI Coach (Groq) | ✅ |
| Workout Log Table | ✅ |
| CSV Download | ✅ |
| Google Sheets Auto-Save | ✅ |
| Streak Counter | ✅ |

---

## ❓ Problems? 

Groq API error आए → console.groq.com से new key लो
Google Sheet error → Sheet name exactly "Gym Workout Log" रखो
App crash हो → requirements.txt check करो
