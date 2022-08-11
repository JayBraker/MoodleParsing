from requests import Session
from bs4 import BeautifulSoup
from tqdm import tqdm
from csv import DictWriter, Dialect

# Moodle.org is behind a captcha check.. Visit "https://moodle.org/plugins/" and grep session cookie + cf clearance
print("Please visit https://moodle.org/plugins/ to aquire necessary cookies!")
SESS_COOKIE = input("Please enter a valid MoodleSession cookie:")
CF_COOKIE = input("Please enter a valid cf_clearance cookie:")

# Provide plugin names in a list, line separated.
# Each line consists of "internal_rpm_name | moodle_org_frankenstyle_name | repository_url"
plugins_rpm = []
with open("","r") as file:
    file.readline()
    file.readline()
    for line in file.readlines():
        line = line.split("|")
        plugin = {}
        plugin["rpm"] = line[0].strip()
        plugin["moodle_name"] = line[1].strip()
        plugin["repo"] = line[2].strip()
        plugin["version"] = None
        plugins_rpm.append(plugin)

# Authorization against captchas is achieved through Session + cookies fetched
s = Session()
s.cookies.set("MoodleSession", SESS_COOKIE)
s.cookies.set("cf_clearance", CF_COOKIE)
for plugin in tqdm(plugins_rpm):
    name = plugin["moodle_name"]
    # If no moodle_org name was provided it might be a non-listed plugin. Can't fetch version number for that
    if not name:
        continue
    r = s.get(f"https://moodle.org/plugins/{name}/versions", headers={
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
        })
    if r.ok:
        soup = BeautifulSoup(r.content)
        if soup.select("span.moodleversions"):
            ver = soup.select("span.moodleversions")[0].get_text().split(',')[-1]
            ver = ver.strip("Moodle").strip()
            plugin["version"] = ver
        else:
            raise Exception("No Versionnumber found!", r.url)
    else:
        print("[",r.status_code,"]","Could not fetch",r.url)

# Define read friendly table headings
conv = {"version": "Version", "rpm": "RPM Paket", "moodle_name": "Moodle.org", "repo": "Git"}
csv_format = [{conv[k]: v for k, v in plugin.items()} for plugin in plugins_rpm]

# Write list extended by latest supported moodle version to a markdown table
with open("","w") as file:
    file.writelines([" | ".join(conv.values()),"\n---|---|---|---"])
    file.writelines([ (f"\n[{plugin['version']}](https://moodle.org/plugins/{plugin['moodle_name']}/versions)" if 'version' in plugin and plugin['version'] else "\n| ")
                    + f" | {plugin['rpm']} | "
                    + f"{plugin['moodle_name']}"
                    + f" | {plugin['repo']}" for plugin in plugins_rpm])

# Write list to excel friendly csv
with open("","w") as file:
    fieldnames = conv.values()
    writer = DictWriter(file, fieldnames=fieldnames, dialect='excel')
    writer.writeheader()
    for plugin in csv_format:
        writer.writerow(plugin)