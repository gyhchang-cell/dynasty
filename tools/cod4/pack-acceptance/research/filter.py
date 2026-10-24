"""Exclude geometry translations, registries, static titles and non-client command text."""
from analyze import *
STRICT=re.compile(r'(?:\b(?:\w+\.)?translatable(?:WithFallback)?\s*\(|new\s+TranslationTextComponent\s*\(|\bI18n\.(?:get|format)\s*\(|\b(?:\w*Lang)\.(?:\w+\.)?(?:translate\w*|lang|builder)\s*\(|\b(?:GuiText|ButtonToolTips)\.\w+\.(?:text|getLocal)\s*\(|\b(?:Tooltips\.of\(GuiText|TooltipUtil\.withArgs)\b)')
def run():
 rows=json.loads((OUT/'candidates.json').read_text());eligible=[];excluded=[]
 for r in rows:
  calls=[c for c in r['localization_calls'] if STRICT.search(c)]
  reason=None
  if not calls:reason='No concrete localization call; geometry translate/name-key/static helper excluded'
  elif re.search(r'/commands?/|/data/|/registration/|/registers/|/material/definition/|/recipe/builder/',r['path'],re.I) or re.search(r'generateLang|registerItems|registerBlocks|registryInit|appendLoot',r['method'],re.I):reason='Not client text lifecycle'
  elif r['method']==Path(r['path']).stem and len(calls)==1 and len(r['body'])<900:reason='Constructor only establishes static title'
  elif re.search(r'getTranslationKey|getTextKey|canTranslate',r['method']):reason='Static key access not text lifecycle'
  if reason:excluded.append({'candidate':r['candidate'],'reason':reason});continue
  r['localization_calls']=calls;eligible.append(r)
 (OUT/'eligible.json').write_text(json.dumps(eligible,ensure_ascii=False,indent=2));(OUT/'excluded.json').write_text(json.dumps(excluded,indent=2))
 print('Eligible for review',len(eligible));print(collections.Counter(r['repo'] for r in eligible))
if __name__=='__main__':run()
