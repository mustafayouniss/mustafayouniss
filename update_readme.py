import os
import requests
import re
import base64

# -----------------------------
# 1️⃣ إعداد WakaTime API
# -----------------------------
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

# -----------------------------
# 2️⃣ تصفية اللغات المطلوبة
# -----------------------------
allowed_languages = ["Python", "C++", "Java", "SQL", "JavaScript", "R", "Matlab", "Go", "C#", "Ruby"]

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

# -----------------------------
# 3️⃣ بناء النص مع البارات الواقعية
# -----------------------------
lines = []
bar_max_length = 20
bar_unit = 0.5 * 3600  # كل نصف ساعة = وحدة بار

for lang, secs in total_time.items():
    hours = int(secs // 3600)
    minutes = int((secs % 3600) // 60)

    # حساب طول البار حسب الوقت الفعلي
    bar_length = int(secs / bar_unit)
    bar_length = min(bar_length, bar_max_length)
    bar_length = max(bar_length, 1)  # طول أدنى للبار

    bar = '█' * bar_length + ' ' * (bar_max_length - bar_length)
    lines.append(f"{lang.ljust(12)} {bar} {hours}h {minutes}m")

waka_text = "\n".join(lines)

# -----------------------------
# 4️⃣ تحديث README
# -----------------------------
readme_path = "README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    readme = f.read()

pattern = r"(<!-- WakaTime stats will be updated here automatically -->[\s\S]*?</table>)"
replacement = f"""<!-- WakaTime stats will be updated here automatically -->

<table align="center" width="100%">
<tr>
<th align="center" style="font-size:22px; padding:10px;">
<strong>This week I spent my time on 📊</strong>
</th>
</tr>

<tr>
<td style="padding: 0; width: 100%;">

<pre style="font-size:16px; line-height:1.6; width:100%; margin:0; white-space: pre-wrap;">
{waka_text}
</pre>

</td>
</tr>
</table>
"""

if re.search(pattern, readme):
    readme = re.sub(pattern, replacement, readme)
else:
    readme += "\n### 📊 This week I spent my time on\n" + replacement

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme)

print("README updated with WakaTime stats (hours + mins, realistic bars, wider table)")
