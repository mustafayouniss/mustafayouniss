import os
import requests
import re
import base64

# API Key من Secret
API_KEY = os.getenv("WAKATIME_API_KEY")
if not API_KEY:
    raise ValueError("WAKATIME_API_KEY not found in environment variables!")

URL = "https://wakatime.com/api/v1/users/current/summaries?range=last_7_days"
creds = base64.b64encode(f"{API_KEY}:".encode()).decode()
headers = {"Authorization": f"Basic {creds}", "Accept": "application/json"}

resp = requests.get(URL, headers=headers)
data = resp.json()
if "errors" in data:
    raise ValueError(f"WakaTime API Error: {data['errors']}")

# اللغات المسموح بها فقط
allowed_languages = ["Python", "C++", "Java", "SQL", "JavaScript", "R", "Matlab", "Go", "C#", "Ruby"]

# نجمع الوقت لكل لغة على مدار الأيام
total_time = {}
for day in data['data']:
    for lang in day.get('languages', []):
        name = lang['name']
        if name not in allowed_languages:
            continue
        seconds = lang['total_seconds']
        total_time[name] = total_time.get(name, 0) + seconds

if not total_time:
    raise ValueError("No programming language data found in WakaTime response!")

# أقصى وقت للتدرج (bar)
max_seconds = max(total_time.values())

lines = []
for lang, secs in total_time.items():
    hours = int(secs // 3600)
    minutes = int((secs % 3600) // 60)
    bar_length = int((secs / max_seconds) * 20)
    bar = '█' * bar_length + ' ' * (20 - bar_length)
    lines.append(f"{lang.ljust(12)} {bar} {hours}h {minutes}m")

waka_text = "\n".join(lines)

# تحديث README داخل placeholder
readme_path = "README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    readme = f.read()

pattern = r"(<!-- WakaTime stats will be updated here automatically -->\n```[\s\S]*?```)"
replacement = f"<!-- WakaTime stats will be updated here automatically -->\n```\n{waka_text}\n```"

if re.search(pattern, readme):
    readme = re.sub(pattern, replacement, readme)
else:
    # لو placeholder مش موجود، نضيفه في آخر README
    readme += "\n### 📊 This week I spent my time on\n" + replacement

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme)

print("✅ README updated with WakaTime stats (hours + mins)")
