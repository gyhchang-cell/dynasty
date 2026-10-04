"""Exact-source cod2 work map. A catalog never implies runtime completion."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path('/Users/a15356015027/Desktop/code x提示词/cod2.txt')
OUT = ROOT / 'docs/blueprint-cod2'
DUNGEONS = ['chensha_xuangong','qianji_jiguancheng','xuehai_guzhanchang','heifeng_alanruo',
            'yinsi_wangsicheng','chilian_gumiaoku','chongxiao_yinxianguan','donglongku',
            'fengmo_wanrenfeng','sixiang_fengtian']
ECOLOGY = ['mountain_forest','ancient_battlefield','abandoned_village','ancient_tomb',
           'deep_water','deep_cavern','snowy_peak','celestial_domain','miasma_domain','final_altar']
EVENTS = ['yinbing_jiedao','zhizha_yingqin','luoshui_yuansuo','shanlu_fubing','juejing_biaoche',
          'tianlei_dihuo','shenjing_yixiang','mangseng_huamo','loulan_huancheng','shuangxiong_sidou',
          'baiyao_yeyou','kuangdao_tafang','qixing_xumingdeng','shuixiang_miju','gubei_potu',
          'huangye_laoyu','huoliuxing_zhui','xuanniao_zhige','baozou_muniu','efeng_fusha',
          'xingsu_cuoluan','fenzang_bujun','tiangou_shiri','guzhou_ziheng','shenmu_xiansheng',
          'dianjing_poke','doujiang_sidou','miwu_huilang','yinqian_shiyi','shenlong_feisheng']

def main():
    source = SOURCE.read_text()
    lines = source.splitlines()
    groups = {}
    for category, start, end, ids in [
        ('dungeons','# 第六项','# 第七项',DUNGEONS),
        ('ecology','# 第七项','# 第八项',ECOLOGY),
        ('events','# 第八项','# 第九项',EVENTS)]:
        begin = next(i for i,s in enumerate(lines) if s.startswith(start))
        finish = next(i for i,s in enumerate(lines) if s.startswith(end))
        entries = [i for i in range(begin,finish) if re.match(r'^### \d+\. ',lines[i])]
        assert len(entries) == len(ids)
        records = []
        for index, first in enumerate(entries):
            last = entries[index+1] if index+1 < len(entries) else finish
            text = '\n'.join(lines[first:last]).strip()
            records.append({'id':ids[index], 'name':lines[first].split('【')[1].split('】')[0],
                'sourceLines':[first+1,last], 'sourceRequirements':text,
                'status':'NOT_STARTED', 'existingArchitecture':[
                    'structure/DynastyStructures.java', 'blueprint/TemplateMob.java',
                    'blueprint/combat/Faction.java', 'ritual/ZhenyuanRitualService.java'],
                'missing':'Exact cod1 monsters/elites/Boss/artifact dependencies and cod2 runtime',
                'plannedFiles':['dungeon/','ecology/','worldevent/','client/character/'][
                    0 if category=='dungeons' else 1 if category=='ecology' else 2],
                'tests':'未实机验证'})
        groups[category] = records
    report = {'source':str(SOURCE), 'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'scope':'Only cod2 sections 6–10; no existing entity or final Boss replacement',
        'baseline':{'command':'./gradlew build --offline','result':'BUILD SUCCESSFUL in 8s',
            'ordinaryTests':'NO-SOURCE; not GameTests or client verification'},
        'cod1RuntimeEntities':['zuwu_daoshou','ludun_jiashi','fufa_jijiu','shanjing_shanxiao'],
        'cod1MissingDependencies':'26 base mobs, 15 elites, 12 bosses, 25 artifacts, 12 avatars',
        **groups,
        'models':{'status':'NOT_STARTED','requiredClasses':8,'tests':'未实机验证'},
        'animations':{'status':'NOT_STARTED','requiredProfiles':11,'tests':'未实机验证'}}
    OUT.mkdir(parents=True,exist_ok=True)
    path = OUT/'IMPLEMENTATION_MAP.json'
    if path.exists():
        old = json.loads(path.read_text())
        assert old['sha256']==report['sha256'], 'Source changed; reconcile implementation evidence explicitly'
        for category in groups:
            previous = {r['id']:r for r in old[category]}
            for record in report[category]:
                for key in ('status','tests','implementationFiles','missing'):
                    if key in previous[record['id']]: record[key]=previous[record['id']][key]
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('Exact-source implementation map:',len(groups['dungeons']),'dungeons,',len(groups['ecology']),'ecology rules,',len(groups['events']),'events')

if __name__=='__main__':main()
