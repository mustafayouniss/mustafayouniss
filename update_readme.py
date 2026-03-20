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

max_seconds = sorted_langs[0][1]

rows = []

for lang, secs in sorted_langs:

    hours = int(secs // 3600)
    minutes = int((secs % 3600) // 60)

    bar_length = int((secs / max_seconds) * 25)
    bar = '▓' * bar_length + '░' * (25 - bar_length)

    rows.append(f"""
<tr>
<td width="20%" style="font-size:17px;"><strong>{lang}</strong></td>
<td width="60%" style="font-family:monospace; font-size:16px;">{bar}</td>
<td width="20%" align="right" style="font-size:16px;">{hours}h {minutes}m</td>
</tr>
""")

waka_rows = "\n".join(rows)

replacement = f"""<!-- WakaTime stats will be updated here automatically -->

<table align="center" width="100%">
<tr>
<th colspan="3" align="center" style="font-size:22px; padding:12px;">
<strong>This week I spent my time on 📊</strong>
</th>
</tr>

{waka_rows}

</table>
"""

readme_path = "README.md"

with open(readme_path, "r", encoding="utf-8") as f:
    readme = f.read()

pattern = r"(<!-- WakaTime stats will be updated here automatically -->[\s\S]*?</table>)"

if re.search(pattern, readme):
    readme = re.sub(pattern, replacement, readme)
else:
    readme += "\n" + replacement

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme)

print("✅ README updated with WakaTime stats")
