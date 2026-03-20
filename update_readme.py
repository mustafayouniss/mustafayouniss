import os
import requests
import re
import base64

# 1. API Key من Secret
API_KEY = os.getenv("WAKATIME_API_KEY")
if not API_KEY:
    raise ValueError("WAKATIME_API_KEY not found in environment variables!")

URL = "https://api.wakatime.com/api/v1/users/current/stats/last_7_days"

creds = base64.b64encode(f"{API_KEY}:".encode()).decode()
headers = {
    "Authorization": f"Basic {creds}",
    "Accept": "application/json",
}

# 2. جلب البيانات من WakaTime
resp = requests.get(URL, headers=headers)
data = resp.json()

if "errors" in data:
    raise ValueError(f"WakaTime API Error: {data['errors']}")

# 3. قائمة اللغات اللي عايزين نظهرها
allowed_languages = ["Python", "C++", "Java", "SQL", "JavaScript", "R", "Matlab", "Go", "C#", "Ruby"]

# 4. فلترة اللغات حسب القائمة
languages = [lang for lang in data['data'].get('languages', []) if lang['name'] in allowed_languages]

if not languages:
    raise ValueError("No programming language data found in WakaTime response!")

# 5. حساب أطول مدة للعرض النسبي
max_seconds = max(lang['total_seconds'] for lang in languages)

# 6. تجهيز النص اللي هيتحط في README
lines = []
for lang in languages:
    name = lang['name']
    secs = lang['total_seconds']
    hours = int(secs // 3600)
    minutes = int((secs % 3600) // 60)
    
    bar_length = int((secs / max_seconds) * 20)  # شريط طوله 20
    bar = '█' * bar_length + ' ' * (20 - bar_length)
    lines.append(f"{name.ljust(12)} {bar} {hours}h {minutes}m")

waka_text = "\n".join(lines)

# 7. تحديث README
readme_path = "README.md"
waka_section = f"\n### ⌨️ WakaTime Language Stats (Last 7 Days)\n\n```\n{waka_text}\n```\n"

with open(readme_path, "r", encoding="utf-8") as f:
    readme = f.read()

if "### ⌨️ WakaTime Language Stats" in readme:
    readme = re.sub(
        r"### ⌨️ WakaTime Language Stats.*?\n\n```.*?```\n",
        waka_section,
        readme,
        flags=re.DOTALL
    )
else:
    readme += waka_section

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme)

print("README.md updated with WakaTime language stats!")
