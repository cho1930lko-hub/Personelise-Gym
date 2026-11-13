# Personelise Gym — Setup & Deployment Guide

यह गाइड repository के मौजूदा code और file structure के अनुसार है। ऐप की सही entry file **`app.py`** है।

## 1. Repository में क्या है?

| Path | उपयोग |
|---|---|
| `app.py` | मुख्य Streamlit Gym Dashboard |
| `requirements.txt` | Python packages |
| `tests/test_app_smoke.py` | Static regression/smoke tests |
| `.github/workflows/python-smoke-checks.yml` | GitHub Actions में automated checks |
| `README.md` | Project overview |

## 2. अपने कंप्यूटर पर चलाएँ

आवश्यकता: Python 3.11 अनुशंसित है (CI इसी version पर चलता है)।

```bash
git clone https://github.com/cho1930lko-hub/Personelise-Gym.git
cd Personelise-Gym

python -m venv .venv
```

Virtual environment activate करें:

**Windows**
```powershell
.venv\\Scripts\\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Dependencies install और app start करें:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Browser में Streamlit द्वारा दिखाया गया local URL खोलें (आमतौर पर `http://localhost:8501`)।

बिना secrets के भी app खुल सकता है। उस स्थिति में AI Coach और Google Sheets integration उपलब्ध नहीं होंगे।

## 3. Google Sheets integration (वैकल्पिक, persistent records के लिए उपयोगी)

ऐप वर्तमान code में Streamlit secrets से ये दो entries पढ़ता है:

- `SHEET_ID`
- `gcp_service_account` के अंदर Google service-account credentials

### A. Google Sheet तैयार करें

1. Google Sheets में एक spreadsheet बनाएँ।
2. उसका spreadsheet ID URL में `/d/` और `/edit` के बीच का हिस्सा है।
3. Google Cloud Console में project चुनें/बनाएँ।
4. **Google Sheets API** और **Google Drive API** enable करें।
5. Service Account बनाएँ और उसकी JSON key सुरक्षित रूप से प्राप्त करें।
6. JSON में मौजूद `client_email` को अपनी spreadsheet पर **Editor** access दें।

ऐप जरूरत पड़ने पर ये worksheet अपने-आप बनाता है:

- `WorkoutLog`
- `BodyStats`
- `WeeklyTracker`
- `Settings`

इसलिए अलग से tab या header बनाने की जरूरत नहीं है। मौजूदा spreadsheet में पहले से मौजूद डेटा हो तो उसे जाँचकर ही इस्तेमाल करें।

### B. Streamlit secrets configure करें

Project में local development के लिए `.streamlit/secrets.toml` बनाएँ। इस फाइल को Git में commit न करें।

नीचे केवल format का उदाहरण है। अपने वास्तविक service-account JSON के values भरें:

```toml
SHEET_ID = "YOUR_GOOGLE_SPREADSHEET_ID"

[gcp_service_account]
type = "service_account"
project_id = "YOUR_PROJECT_ID"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = """-----BEGIN PRIVATE KEY-----
PASTE_YOUR_PRIVATE_KEY_CONTENT_HERE
-----END PRIVATE KEY-----\n"""
client_email = "YOUR_SERVICE_ACCOUNT_EMAIL"
client_id = "YOUR_CLIENT_ID"
token_uri = "https://oauth2.googleapis.com/token"
```

अपने डाउनलोड किए गए JSON में मौजूद अन्य आवश्यक fields भी उसी `[gcp_service_account]` section में रखें। Private key को सही multiline format में paste करें।

**Streamlit Community Cloud पर:** App → **Settings** → **Secrets** में यही TOML configuration paste करें। Local file और Cloud secrets दोनों में credentials सुरक्षित रखें; उन्हें source code या GitHub में न डालें।

### C. Data behaviour की जरूरी जानकारी

- Workout entries `WorkoutLog` में append होती हैं।
- Body-weight entries `BodyStats` में history के रूप में append होती हैं।
- `Settings` और `WeeklyTracker` save करते समय मौजूदा code उन tabs को clear करके फिर से लिखता है। इन दो tabs में unrelated/manual records न रखें।
- Google Sheets configuration न होने या request fail होने पर app में save warning आ सकती है। जरूरी record spreadsheet में verify करें।
- Streamlit Cloud पर local `gym_data.json` को permanent backup न मानें। Persistent और cross-session records के लिए Google Sheets integration configure करें।

## 4. AI Coach (वैकल्पिक)

AI Coach Groq API और `llama-3.3-70b-versatile` model का उपयोग करता है।

1. Groq Console से API key बनाएँ।
2. Local `.streamlit/secrets.toml` में यह entry जोड़ें, या Cloud App → Settings → Secrets में जोड़ें:

```toml
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
```

3. App restart/redeploy करें।

API key कभी GitHub पर commit न करें। AI configuration न होने पर बाकी dashboard इस्तेमाल किया जा सकता है।

## 5. Streamlit Community Cloud पर deploy करें

1. Streamlit Community Cloud खोलें: https://share.streamlit.io/
2. GitHub account connect करें।
3. **Create app / New app** चुनें।
4. Repository: `cho1930lko-hub/Personelise-Gym`
5. Branch: `main`
6. Main file path: **`app.py`**
7. Deploy करें।
8. Deploy होने के बाद App settings → Secrets में जरूरत के अनुसार Google Sheets और Groq secrets जोड़ें।
9. App reboot/redeploy करके Workout save, Google Sheets tabs और AI Coach को अलग-अलग verify करें।

> पुराने निर्देशों में `gym_dashboard.py` और नई repository बनाने की बात थी। वे इस repository के वर्तमान structure से मेल नहीं खाते। मौजूदा repository ही चुनें और entry file `app.py` रखें।

## 6. Tests और GitHub Actions

Local checks चलाएँ:

```bash
python -m compileall -q app.py tests
python -m unittest discover -s tests -v
```

GitHub Actions workflow `.github/workflows/python-smoke-checks.yml` इन checks को `main` पर push, `main` के लिए pull request और manual workflow dispatch पर चलाता है।

ध्यान दें: मौजूदा tests static/smoke checks हैं। ये live Google Sheets credentials, Groq API, browser UI या deployed app के end-to-end behaviour को verify नहीं करते।

## 7. Troubleshooting

| समस्या | क्या जाँचें |
|---|---|
| App start नहीं होता | सही entry file `app.py`, Python version और `pip install -r requirements.txt` |
| Google Sheets connect नहीं होती | `SHEET_ID`, `[gcp_service_account]`, APIs enabled हैं या नहीं, और spreadsheet पर service-account email का Editor access |
| AI Coach offline है | `GROQ_API_KEY` सही है या नहीं; Groq account/API availability जाँचें |
| Save warning दिखती है | Local save और Google Sheets save अलग-अलग जाँचें; sheet में record मौजूद है या नहीं verify करें |
| Deploy के बाद local data गायब है | Cloud local file को permanent storage न मानें; Google Sheets integration configure करें |

## 8. Security checklist

- [ ] API keys और service-account JSON को GitHub पर upload/commit न करें।
- [ ] Local `.streamlit/secrets.toml` को `.gitignore` में रखें।
- [ ] GitHub history में credential चला गया हो तो उसे revoke/rotate करें; केवल file हटाना पर्याप्त नहीं।
- [ ] Spreadsheet केवल जरूरी service account और विश्वसनीय लोगों के साथ share करें।
- [ ] Backup के लिए Google Sheet का अलग सुरक्षित export रखें।

---

**Current app scope:** यह repository अभी workout tracking, workout history, body stats और optional AI Coach पर केंद्रित है। Membership, admission fee, invoices, payment ledger और receipt management इस setup guide में implemented features के रूप में नहीं बताए गए हैं।
