"""Read native refusal/transform consumer; missing concrete configured class mapping stays0."""
from ledger import B,O,R,verify
import json,hashlib,datetime
f=O/'helpers/herschel-immune/batch-039.json';raw=f.read_bytes();assert hashlib.sha256(raw).hexdigest()=='2b455c9f0bddbfaa7ed654cf859de2523c740c8be374d6f0bd39bc85a69251dc';d=json.loads(raw);repo='Lycanite/LycanitesMobs';root=B/'sources/Lycanite__LycanitesMobs';meta=json.loads((root/'source.json').read_text());tree=json.loads((root/'tree.json').read_text());blobs={v['path']:v['sha'] for v in tree['tree'] if v['type']=='blob'}
refs=[]
for h in d['rows'][0]['source_refs']:
 rel=h['source_key'].split('/',1)[1];p=root/rel;data=p.read_bytes();sha=hashlib.sha256(data).hexdigest();assert sha==h['file_sha256'];assert h['fixed_commit']==meta['commit']==tree['sha'];assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==blobs[rel];a,z=h['lines'];assert 1<=a<=z<=len(data.decode().splitlines());refs.append({'path':str(p.relative_to(R)),'source_path':rel,'lines':[a,z],'file_sha256':sha,'url':h['url']})
k='lycanites-pending-refused-fire-budget-native-replacement-lifetime'
reason='主岗完整复读Djinn类、Zephyr类、两级attackEntityFrom、invulnerable/source applicability、tamed位查询、transform1305–1427和CreatureInfo.register274–326。火拒伤前累积原始incoming float（含非正无guard），未驯服server tick达10才替换；未驯服雷直接同transform，两个入口不拆。构造失败null保留旧目标；构造成功后spawnEntity布尔忽略便setDead旧目标并返回新对象；不是伤害已成功也不是新目标已入世。无明确旧UUID/当前HP/火预算copy或免控收据。CreatureInfo.enabled=false这里只log而无return，不能据此说禁用必不注册；具体Djinn JSON→class映射未取得原字节，通用register不冒称具体默认注册已证。'
record={'id':k,'repo':repo,'commit':meta['commit'],'status':'pending_concrete_registration_resource','research_credit':0,'reason':reason,'remaining_for_promotion':'补可核实Djinn具体注册映射来源并完成语义对照后决定；自然spawn实测不是参考额外门槛，当前只缺固定配置字节而非要求启动游戏。helper一次TLS失败已记录，主岗只搜本地tools/docs/build无djinn/zephyr JSON，不重复联网请求，不关证书校验。','source_refs':refs}
f2=O/'candidates.json';pending=json.loads(f2.read_text());old=next((i for i,v in enumerate(pending) if v['id']==k),None)
if old is None:pending.append(record)
else:pending[old]=record
f2.write_text(json.dumps(pending,ensure_ascii=False,indent=2)+'\n')
(O/'HERSCHEL-039-REVIEW.json').write_text(json.dumps({'helper_file_sha256':hashlib.sha256(raw).hexdigest(),'main_review_new_effective':0,'helper_original_credit':0,'main_full_listed_methods_read':True,'state':'pending_concrete_configuration_mapping_support0','observation':reason,'external_request_repeated_by_main':False,'candidate_key':k,'source_refs':refs,'production_changes':False,'game_started':False,'compile_run':False,'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},ensure_ascii=False,indent=2)+'\n');verify()
