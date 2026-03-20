import os
import requests
import re
import base64

API_KEY = os.getenv("WAKATIME_API_KEY")
if not API_KEY:
    raise ValueError("WAKATIME_API_KEY not found in environment variables!")

URL = "https://api.wakatime.com/api/v1/users/current/stats/last_7_days"

creds = base64.b64encode(f"{API_KEY}:".encode()).decode()
headers = {
    "Authorization": f"Basic {creds}",
    "Accept": "application/json",
}

resp = requests.get(URL, headers=headers)
data = resp.json()

if "errors" in data:
    raise ValueError(f"WakaTime API Error: {data['errors']}")

languages = data['data'].get('languages', [])
if not languages:
    raise ValueError("No language data found in WakaTime response!")

max_seconds = max(lang['total_seconds'] for lang in languages)

lines = []
for lang in languages:
    name = lang['name']
    secs = lang['total_seconds']
    hours = int(secs // 3600)
    minutes = int((secs % 3600) // 60)
    
    bar_length = int((secs / max_seconds) * 20)
    bar = '█' * bar_length + ' ' * (20 - bar_length)
    lines.append(f"{name.ljust(12)} {bar} {hours}h {minutes}m")

waka_text = "\n".join(lines)

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
