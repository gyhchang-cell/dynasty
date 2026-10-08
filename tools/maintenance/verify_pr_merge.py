"""PR merge invariants: bilingual resources, retained parent keys and quest identity."""
from pathlib import Path
import collections, json, re, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise ValueError("duplicate JSON key: "+key)
        result[key]=value
    return result
langs={n:json.loads((ROOT/f"src/main/resources/assets/dynasty/lang/{n}.json").read_text(),object_pairs_hook=unique) for n in ("en_us","zh_cn")}
assert langs["en_us"].keys()==langs["zh_cn"].keys(),"Unpaired language keys"
def placeholders(text):
    return collections.Counter(re.findall(r"%(?:[0-9]+\$)?[sd]",text.replace("%%","")))
for key in langs["en_us"]:
    assert placeholders(langs["en_us"][key])==placeholders(langs["zh_cn"][key]),key
for ref in sys.argv[1:]:
    for lang,current in langs.items():
        old=json.loads(subprocess.check_output(["git","show",f"{ref}:src/main/resources/assets/dynasty/lang/{lang}.json"],cwd=ROOT),object_pairs_hook=unique)
        assert old.keys()<=current.keys(),(ref,lang,"lost keys",old.keys()-current.keys())
    paths=subprocess.check_output(["git","ls-tree","-r","--name-only",ref,"modpack/config/ftbquests/quests/chapters"],cwd=ROOT,text=True).splitlines()
    for path in paths:
        old=subprocess.check_output(["git","show",f"{ref}:{path}"],cwd=ROOT,text=True)
        current=(ROOT/path).read_text()
        old_ids=set(re.findall(r'id: "([0-9a-fA-F]{16})"',old))
        new_ids=set(re.findall(r'id: "([0-9a-fA-F]{16})"',current))
        assert old_ids<=new_ids,(ref,path,"lost quest/task/reward IDs")
        # Detect identity/reward/dependency loss independently of generated descriptions.
        for line in old.splitlines():
            if line.lstrip().startswith(("id:","rewards:","dependencies:")):
                assert line in current,(ref,path,"quest contract changed",line)
count=0
for path in (ROOT/"src/main/resources").rglob("*.json"):
    json.loads(path.read_text());count+=1
print(f"PASS {len(langs['en_us'])} paired keys; duplicate/placeholder checks; {count} JSON resources; parent language/FTB contracts retained")
