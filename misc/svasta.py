
import re
import json

var = '/*<![CDATA[*/TDAKV = {"kvwheelchair":"false","kvchildfriendly":"false",' \
      '"kvsurfaceUsable":"","kvfireplace":"false","kvdistanceshops":"300","kvroom":"4.5",' \
      '"kvzip":"8312","kvplace":"Winterberg ZH","kvnav1":"rent","kvnav2":"search",' \
      '"kvrentalprice":"2630","kvfiberglass":"false","kvsurfaceProperty":"",' \
      '"kvyearbuilt":"2017","kvbalcony":"true","kvcanton":"ZH","kvisdn":"false",' \
      '"kvdistanckindergarten":"800","kvhighfloor":"false","kvgarage":"true","kvanimal":"false",' \
      '"kvdistanceprimaryschool":"800","kvbuiltold":"false","kvobjecttype":"APPT3",' \
      '"kvpurchaseprice":"","kvdistanceupperschool":"1500","kvminergy":"false","kvparking":"true"' \
      ',"kvsurfaceliving":"125","kvpagetype":"objectpage","kvbuiltnew":"true","kvavailablefrom":"by agreement"' \
      ',"kvstreet":"Poststrasse 7","kvswimmingpool":"false","kvlift":"true","kvcabletv":"true"};/*]]>*/'


match = re.search(r'/\*<!\[CDATA\[\*\/TDAKV\s=\s+([\d\w\W]+);\/\*\]\]>\*\/', var)
d = json.loads(match.group(1))

for key, val in d.items():
    print('{}: {}'.format(key, val))

# izlaz
# kvwheelchair: false
# kvchildfriendly: false
# kvsurfaceUsable:
# kvfireplace: false
# kvdistanceshops: 300
# kvroom: 4.5
# kvzip: 8312
# kvplace: Winterberg ZH
# ...


import socket

s = socket.socket()
s.connect(('www.example.com', 80))
# tek kada

