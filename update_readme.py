import os
import requests
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
# 3️⃣ بناء البارات الواقعية لكل لغة
# -----------------------------
bar_max_length = 40  # أكبر طول بار
bar_unit = 0.5 * 3600  # كل نصف ساعة = وحدة بار

# نصوص الصفوف لكل لغة
rows = []
for lang, secs in total_time.items():
    hours = int(secs // 3600)
    minutes = int((secs % 3600) // 60)

    bar_length = int(secs / bar_unit)
    bar_length = min(bar_length, bar_max_length)
    bar_length = max(bar_length, 1)

    bar = '█' * bar_length + ' ' * (bar_max_length - bar_length)
    rows.append(f"""
    <tr>
        <td style="padding:5px; font-weight:bold;">{lang}</td>
        <td style="padding:5px; font-family:monospace;">{bar}</td>
        <td style="padding:5px; text-align:right;">{hours}h {minutes}m</td>
    </tr>
    """)

# دمج الصفوف
rows_html = "\n".join(rows)

# -----------------------------
# 4️⃣ إنشاء الجدول الكامل
# -----------------------------
table_html = f"""
<!-- WakaTime stats will be updated here automatically -->
<table align="center" width="100%" style="border-collapse: collapse; font-size:16px;">
<tr>
    <th style="text-align:left; padding:10px; font-size:22px;" colspan="3">📊 This week I spent my time on</th>
</tr>
{rows_html}
</table>
"""

# -----------------------------
# 5️⃣ تحديث README
# -----------------------------
readme_path = "README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    readme = f.read()

import re
pattern = r"(<!-- WakaTime stats will be updated here automatically -->[\s\S]*?</table>)"

if re.search(pattern, readme):
    readme = re.sub(pattern, table_html, readme)
else:
    readme += "\n" + table_html

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme)

print("README updated with WakaTime stats in wider multi-row table ✅")
