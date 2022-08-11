import sys
import re
import urllib.request
import json

build_no = sys.argv[1] if len(sys.argv) > 1 else "\d+"
# Usage of urllib to work straight with any recent python3 installation, no pip needed
url = "https://docs.moodle.org/dev/Releases"
request = urllib.request.Request(url)
try:
    response = urllib.request.urlopen(request)
except Exception as e:
    print(e)
if not response.getcode() == 200:
    print(response.getcode())
    exit(1)
html = response.read().decode()
h_read_pattern = re.compile(r"<th>Moodle (?P<release>\d.+)\n<\/th>\n<td>\d+ \w+ \d\d\d\d\n<\/td>\n<td>(?P<build>{bn})".format(bn = build_no))
ret = {}
for match in h_read_pattern.findall(html):
    ret[match[1]] = match[0]
print(json.dumps(ret))
