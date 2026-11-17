import sys
sys.dont_write_bytecode=True
from pathlib import Path
B=Path(__file__).resolve().parent
old=(B/'batch-042/review.py').read_text()
head=old[:old.index("add('requiem-bottled")]
tail=old[old.index('def attach_declarations'):]
a=tail.index('    for suffix in ');z=tail.index('        sample=',a)
tail=tail[:a]+"    for suffix in sorted({('/'+e['path']) for e in row['evidence']}):\n"+tail[z:]
for n in (43,44,45):
    base=B/('batch-%03d'%n)
    content=(head+"\n# Handwritten semantic specifications are loaded from a local research-only file.\nexec((BASE/'notes.py').read_text())\n"+tail).replace('batch-042','batch-%03d'%n)
    (base/'review.py').write_text(content)
    integrity=(B/'batch-042/record-document-integrity.py').read_text().replace('batch-042','batch-%03d'%n).replace("'reused_batch038_files_not_credit':646,'new_downloaded_files_not_credit':0,", "'git_object_sources_only':True,")
    (base/'record-document-integrity.py').write_text(integrity)
