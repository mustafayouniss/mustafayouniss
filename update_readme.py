import os
import requests
import matplotlib.pyplot as plt
import re
import base64

API_KEY = os.getenv("WAKATIME_API_KEY")
if not API_KEY:
    raise ValueError("WAKATIME_API_KEY not found in environment variables!")

URL = "URL = "https://api.wakatime.com/api/v1/users/current/stats/last_7_days""

creds = base64.b64encode(f"{API_KEY}:".encode()).decode()
headers = {
    "Authorization": f"Basic {creds}",
}

resp = requests.get(URL, headers=headers)
data = resp.json()

if "errors" in data:
    raise ValueError(f"WakaTime API Error: {data['errors']}")

languages = data['data'].get('languages', [])
if not languages:
    raise ValueError("No language data found in WakaTime response!")


lang_names = [lang['name'] for lang in languages]
lang_hours = [round(lang['total_seconds'] / 3600, 2) for lang in languages]

plt.figure(figsize=(10, 6))
plt.bar(lang_names, lang_hours, color="skyblue")
plt.title("⏱ Hours coded per language (Last 7 Days)")
plt.xlabel("Language")
plt.ylabel("Hours")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

image_path = "wakatime_languages.png"
plt.savefig(image_path)
plt.close()

readme_path = "README.md"
waka_section = f"\n### ⌨️ WakaTime Language Stats\n\n![WakaTime Stats]({image_path})\n"

with open(readme_path, "r", encoding="utf-8") as f:
    readme = f.read()

if "### ⌨️ WakaTime Language Stats" in readme:
    readme = re.sub(
        r"### ⌨️ WakaTime Language Stats.*?\n\n!\[.*?\]\(.*?\)\n",
        waka_section,
        readme,
        flags=re.DOTALL
    )
else:
    readme += waka_section

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme)

print("README.md updated with WakaTime language stats!")
