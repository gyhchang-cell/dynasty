"""Execute coordinator integrity checker unchanged except a separate receipt filename.
The original coordinator snapshot is immutable and retained after semantic reclassification.
"""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'audit_guard_references.py'
s=p.read_text();old='f"coordinator-integrity-{len(rows)}.json"';assert s.count(old)==1
s=s.replace(old,'f"integrity-final-{len(rows)}.json"')
exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
