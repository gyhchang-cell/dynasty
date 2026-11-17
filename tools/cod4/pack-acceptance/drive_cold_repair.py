"""Cold English repaired jar, all original information pages, actual scrollbar bottom."""
from drive import *
import re,zipfile
ids=['fire_talisman','thunder_talisman','wind_talisman','stealth_talisman','vajra_talisman','soul_talisman','return_talisman']
wait_file('READY.json',600);command('focus-own-private-window','focus');command('cold-en-repair-talismans','talismans')
audit=load(O/'cold-en-repair-talismans-audit.json');results=[]
for item in ids:
 command(item+'-seed-inventory','jei',item='dynasty:'+item,role='OUTPUT')
 s=command(item+'-info-top','info',item='dynasty:'+item);row=s['jeiScreen']['layouts'][0]
 assert s['language']=='en_us' and row['description']==audit[item]['description']
 norm=lambda s:re.sub(r'\s+','',s)
 assert norm(''.join(row['description']))==norm(''.join(line for box in row['actualWrappedText'] for line in box['lines']))
 # Widget content rectangle is y214..317 at this fixed GUI scale; y311 can be inside a nearly-full thumb.
 bottom=command(item+'-scroll-track-bottom','nativeMouse',x=558,y=316,button=0)
 results.append({'item':item,'top':s,'bottom':bottom});print(item,'cold English actual layout + bottom capture',flush=True)
 command(item+'-escape','nativeKey',key=256)
(O/'cold-english-repair-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
tmp=O/'command.pending';tmp.write_text(json.dumps({'id':'finish-cold-repair','op':'finish'}));os.replace(tmp,O/'command.json')
print('Cold English supplemental sequence complete',flush=True)
