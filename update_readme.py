import os
import requests
import re
import base64
import math

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

max_seconds = max(total_time.values())

# -----------------------------
# 3️⃣ بناء النص مع البارات المنطقية
# -----------------------------
lines = []
bar_max_length = 20
min_bar_length = 2  # طول الحد الأدنى للبار عشان يظهر

for lang, secs in total_time.items():
    hours = int(secs // 3600)
    minutes = int((secs % 3600) // 60)

    # استخدام اللوغاريتم لتقليل الفروقات الكبيرة
    bar_length = int((math.log(secs + 1) / math.log(max_seconds + 1)) * bar_max_length)
    bar_length = max(bar_length, min_bar_length)

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
<td>

<pre style="font-size:16px; line-height:1.6;">
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

print("README updated with WakaTime stats (hours + mins)")
