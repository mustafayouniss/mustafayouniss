import os
import requests
import re
import base64

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

allowed_languages = [
    "Python","C++","Java","SQL","JavaScript",
    "R","Matlab","Go","C#","Ruby"
]

TARGET_HOURS = 20  # توحيد الـ target لكل لغة

# جمع الوقت لكل لغة
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

# ترتيب اللغات حسب الوقت
sorted_langs = sorted(total_time.items(), key=lambda x: x[1], reverse=True)

MAX_BAR_LENGTH = 20
lines = []

for lang, secs in sorted_langs:
    hours = int(secs // 3600)
    minutes = int((secs % 3600) // 60)

    # نسبة الإنجاز بالنسبة للـ target
    target_secs = TARGET_HOURS * 3600
    progress_ratio = min(secs / target_secs, 1.0)

    filled_length = int(progress_ratio * MAX_BAR_LENGTH)
    empty_length = MAX_BAR_LENGTH - filled_length

    # البار داخل مستطيل
    bar = "┌" + "─"*MAX_BAR_LENGTH + "┐\n"
    bar += "│" + "█"*filled_length + "░"*empty_length + "│\n"
    bar += "└" + "─"*MAX_BAR_LENGTH + "┘"

    lines.append(f"{lang.ljust(12)}\n{bar} {hours}h {minutes}m / {TARGET_HOURS}h")

waka_text = "\n\n".join(lines)  # مسافة بين اللغات

# تحديث README
readme_path = "README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    readme = f.read()

pattern = r"(<!-- WakaTime stats will be updated here automatically -->[\s\S]*?</table>)"

replacement = f"""<!-- WakaTime stats will be updated here automatically -->

<table align="center" width="65%">
<tr>
<th align="center" style="font-size:20px; padding:8px;">
<strong>This week I spent my time on 📊</strong>
</th>
</tr>

<tr>
<td>
<pre style="font-size:14px; line-height:1.6; font-family: 'Courier New', monospace;">
{waka_text}
</pre>
</td>
</tr>
</table>
"""

if re.search(pattern, readme):
    readme = re.sub(pattern, replacement, readme)
else:
    readme += "\n" + replacement

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme)

print("✅ README updated with WakaTime stats (Bars inside rectangles)")
