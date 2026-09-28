"""Tiny structural reader for generated FTB lists (not a permissive SNBT parser).

Keeps quest_links and images out of the quest task graph. Quoted braces/escapes in
descriptions and commands must not be interpreted as structural punctuation.
"""
import re


def list_compounds(text, field):
    match=re.search(r"^\t"+re.escape(field)+r":\s*\[",text,re.M)
    if not match:
        return []
    depth,quote,escaped,start=1,False,False,None
    objects=[]
    for i in range(match.end(),len(text)):
        ch=text[i]
        if quote:
            if escaped: escaped=False
            elif ch=="\\": escaped=True
            elif ch=='"': quote=False
            continue
        if ch=='"': quote=True
        elif ch in "[{":
            if ch=="{" and depth==1: start=i
            depth+=1
        elif ch in "]}":
            depth-=1
            if ch=="}" and depth==1 and start is not None:
                objects.append(text[start:i+1]);start=None
            if depth==0:
                return objects
    raise ValueError("Unclosed generated list: "+field)


def object_id(block):
    match=re.search(r'\bid:\s*"([0-9a-fA-F]{16})"',block)
    return match[1] if match else None

