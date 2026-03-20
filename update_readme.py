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

# الهدف لكل لغة
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

max_seconds = sorted_langs[0][1]

lines = []

for lang, secs in sorted_langs:

    hours = int(secs // 3600)
    minutes = int((secs % 3600) // 60)

    bar_length = int((secs / max_seconds) * 20)
    bar = '█' * bar_length + ' ' * (20 - bar_length)

    target = targets.get(lang, 10)

    lines.append(f"{lang.ljust(12)} {bar} {hours}h {minutes}m / {target}h")

waka_text = "\n".join(lines)

readme_path = "README.md"

with open(readme_path, "r", encoding="utf-8") as f:
    readme = f.read()

pattern = r"(<!-- WakaTime stats will be updated here automatically -->[\s\S]*?</table>)"

replacement = f"""<!-- WakaTime stats will be updated here automatically -->

<table align="center" width="60%">
<tr>
<th align="center" style="font-size:20px; padding:8px;">
<strong>This week I spent my time on 📊</strong>
</th>
</tr>

<tr>
<td>

<pre style="font-size:15px; line-height:1.6;">
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

print("✅ README updated with WakaTime stats")
