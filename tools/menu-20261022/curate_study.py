from pathlib import Path
import json,re,hashlib
O=Path('docs/menu-20261022/references');rs=json.loads((O/'large-pack-study.json').read_text())
exclude={'Prominence II: 哈斯图尔纪元','Client Mods','Essentials Mods','GD656极致生电整合包','New Simple Mods','Best Fabric+ Minecraft','Lost World - The Broken Script'}
rs=[r for r in rs if r['title'] not in exclude]
for pid in ['59qxFo3W','aYYSB5Qo','tNMCztGm','fPaa752e','qxMV1Wt8','aDL9ps0f','cgxCkrbh']:
 d=json.loads((O/(pid+'.json')).read_text());v=json.loads((O/(pid+'-manifest.json')).read_text())
 rs.append({'project_id':pid,'title':d['title'],'url':'https://modrinth.com/modpack/'+d['slug'],'downloads':d['downloads'],'mod_count':v['mod_count'],'version_id':v['version_id'],'evidence':[d['description']],'source_sha256':hashlib.sha256(d['body'].encode()).hexdigest(),'scope':'作者说明及发布包清单；不是逐个菜单截图或启动验证。'})
assert len(rs)==100 and len({r['project_id'] for r in rs})==100
for r in rs:
 d=json.loads((O/(r['project_id']+'.json')).read_text());v=json.loads((O/(r['project_id']+'-manifest.json')).read_text());assert v['mod_count']>=100
 r['description']=d['description'];r['menu_dependencies']=[m for m in v['mods'] if re.search(r'fancymenu|menulogue|modmenu|drippy|loadingscreen|continue|title|smoothmenu',m,re.I)]
 text=d['description']+' '+d['body'];obs=[]
 if r['menu_dependencies']:obs.append('清单可核实菜单/界面依赖：'+', '.join(Path(x).name for x in r['menu_dependencies'])+'；依赖存在不等同于已观察到具体菜单布局。')
 if re.search('quest|任务',text,re.I):obs.append('作者说明包含任务/引导；借鉴信息分层，通用教学从物品悬停移除，专属机制仍可查阅。')
 if re.search('custom|hand.?craft|定制|原创',text,re.I):obs.append('作者强调定制内容；借鉴品牌识别延伸至二级页面，不套用对方资产。')
 if re.search('immers|atmospher|aesthetic|视觉|氛围',text,re.I):obs.append('作者强调氛围/视觉；借鉴背景与控件的统一明暗关系，保证文字对比。')
 if not obs:obs.append('依作者主题说明确定内容入口定位；保留熟悉的创建流程，用本项目配色建立识别。')
 r['observations']=obs
(O/'reviewed-100.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2))
lines=['# 大型整合包来源研究（100 个）','','研究对象为作者说明与真实发布包的 modrinth.index.json。每个候选至少有 100 个 mods/*.jar 引用；不是只用项目名凑数。按项目 ID 去重，并排除 Better MC/Medieval MC 的加载器变体以及 Prominence 汉化重复版。下载量是筛选信号，不证明质量。本记录不宣称逐一启动 100 个包，也不宣称看过 100 个菜单截图。','','本轮界面原则：保留现有王朝主视觉；青玉底、古铜主操作与纸色文字贯穿创建页面；较小圆角与边缘覆盖；原生输入、标签切换、游戏模式及创建逻辑不替换；仅移除基础通用教学，保留技能与数据。','']
for i,r in enumerate(rs,1):
 lines+=['## '+str(i)+'. '+r['title'],'',f"作者来源：{r['url']}；版本 `{r['version_id']}`；清单核实 {r['mod_count']} 个模组引用。",'']+r['observations']+['']
Path('docs/menu-20261022/reference-study.md').write_text('\n'.join(lines))
for i,r in enumerate(rs,1):print(i,r['title'],r['mod_count'],'|',r['description'][:140],'|',str(r['menu_dependencies'])[:100])
