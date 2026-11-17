"""Summarize recorded installed-app bridge trials; never counts a click as a confirmed block."""
import collections, hashlib, json, re, sys
from pathlib import Path

def summarize(path):
    path=Path(path)
    lines=path.read_text().splitlines()
    poses=[s for s in lines if " POSE " in s]
    cycles=[]; current=None; previous=""
    for line in poses:
        m=re.search(r"phase=(\w+) count=(\d+)",line)
        if not m: continue
        phase,count=m[1],int(m[2])
        if phase in ("takeoff","flight") and (current is None or previous not in ("takeoff","flight") or count<current["confirmedPlacements"]):
            if current: cycles.append(current)
            current={"confirmedPlacements":0,"firstPose":line}
        if current:
            current["confirmedPlacements"]=max(current["confirmedPlacements"],count)
            current["lastPose"]=line
        previous=phase
    if current: cycles.append(current)
    failure=[s for s in lines if " STATE " in s and any(t in s for t in ["落空","未落在","未能及时","读数失效","失去前台"])]
    down=next((float(s.split()[0]) for s in lines if " R down repeat=0" in s),None)
    up=next((float(s.split()[0]) for s in lines if " R up" in s),None)
    stop=next((float(s.split()[0]) for s in lines if " STATE 本跳已完成" in s),None)
    return {"log":str(path),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
        "landings":sum(" ground false " in a and " ground true " in b for a,b in zip(poses,poses[1:])),
        "placementsPerCycle":[c["confirmedPlacements"] for c in cycles],
        "placementHistogram":dict(collections.Counter(c["confirmedPlacements"] for c in cycles)),
        "cycles":cycles,"modeEvents":[s for s in lines if " MODE " in s],"failureEvents":failure,
        "heldSeconds":round(up-down,3) if up and down else None,
        "releaseToStopSeconds":round(stop-up,3) if stop and up else None,
        "firstPose":poses[0] if poses else None,"lastPose":poses[-1] if poses else None,
        "result":lines[-1] if lines else None}

if __name__=="__main__":
    print(json.dumps([summarize(p) for p in sys.argv[1:]],ensure_ascii=False,indent=2))
