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

# Weekly target لكل لغة بالساعات
targets = {
    "Python": 20,
    "C++": 10,
    "Java": 10,
    "SQL": 10,
    "JavaScript": 10,
    "R": 10,
    "Matlab": 10,
    "Go": 10,
    "C#": 10,
    "Ruby": 10
}

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

sorted_langs = sorted(total_time.items(), key=lambda x: x[1], reverse=True)

MAX_BAR_LENGTH = 20
lines = []

for lang, secs in sorted_langs:
    hours = int(secs // 3600)
    minutes = int((secs % 3600) // 60)

    target_hours = targets.get(lang, 10)
    target_secs = target_hours * 3600
    progress_ratio = min(secs / target_secs, 1.0)

    bar_filled = int(progress_ratio * MAX_BAR_LENGTH)
    bar_empty = MAX_BAR_LENGTH - bar_filled

    # شكل البار مع حدود []
    bar = "[" + "█" * bar_filled + " " * bar_empty + "]"

    # ألوان تقريبية باستخدام emojis (اختياري) لو حابب
    # لو مش حابب الألوان ابقي خلي bar طبيعي بدون emojis
    # مثلا:
    # if progress_ratio >= 0.8:
    #     bar = "[" + "🟩"*bar_filled + " "*(bar_empty) + "]"
    # elif progress_ratio >= 0.5:
    #     bar = "[" + "🟨"*bar_filled + " "*(bar_empty) + "]"
    # else:
    #     bar = "[" + "🟥"*bar_filled + " "*(bar_empty) + "]"

    lines.append(f"{lang.ljust(12)} {bar} {hours}h {minutes}m / {target_hours}h")

waka_text = "\n".join(lines)

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
<pre style="font-size:15px; line-height:1.6; font-family: 'Courier New', monospace;">
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

print("✅ README updated with WakaTime stats (Advanced bars with targets)")
