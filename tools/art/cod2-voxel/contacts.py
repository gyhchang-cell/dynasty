"""Author offline contact correction keys; never install runtime IK or gameplay code.

Long arms lift slightly through their shoulder, turtle feet counter their hip,
and a falling whole-body winged rig settles on the floor. Its authored timeline
and hit ticks remain unchanged. Dense position keys prevent interpolation dips.
"""
import json
import numpy as np
import review


def descendants(bones, root):
    result={root}
    for b in bones:
        if b.get('parent') in result:result.add(b['name'])
    return result


def parent_vertical(bones, channels, name, time):
    world={};pivots={b['name']:np.array(b['pivot']) for b in bones}
    for b in bones:
        parent=world.get(b.get('parent'),np.eye(4))
        if b['name']==name:return float(parent[1,1])
        ch=channels.get(b['name'],{});rot=np.array(b.get('rotation',[0,0,0]),dtype=float)
        if 'rotation' in ch:rot+=review.sample(ch['rotation'],time)
        scale=review.sample(ch['scale'],time) if 'scale' in ch else [1,1,1]
        world[b['name']]=parent@review.transform(rotation=rot,scale=scale)
    raise ValueError(name)


def simplify(keys, tolerance=.0125):
    """Keep only keys needed to stay within 1/80 of a model unit of the contact curve."""
    entries=list(keys.items());times=np.array([float(t) for t,_ in entries]);values=np.array([v for _,v in entries])
    keep={0,len(entries)-1};work=[(0,len(entries)-1)]
    while work:
        first,last=work.pop()
        if last-first<2:continue
        alpha=(times[first+1:last]-times[first])/(times[last]-times[first])
        prediction=values[first]+alpha[:,None]*(values[last]-values[first])
        errors=np.max(np.abs(values[first+1:last]-prediction),axis=1)
        split=int(np.argmax(errors))+first+1
        if errors[split-first-1]>tolerance:
            keep.add(split);work.extend([(first,split),(split,last)])
    return {entries[i][0]:entries[i][1] for i in sorted(keep)}


def settle(names=None):
    for name in names or ['jubi_shigandang','juli_bixi_kuilei','tongbi_feitian_yecha']:
        review.select(name)
        bones=json.loads(review.GEO.read_text())['minecraft:geometry'][0]['bones']
        data=json.loads(review.ANIM.read_text())
        for clip,animation in data['animations'].items():
            short=clip.rsplit('.',1)[1]
            if name=='jubi_shigandang':
                controlled=['foot'] if short in ['walk','run'] else ['body'] if short=='death' else ['right_shoulder'] if short in ['attack','slam'] else []
            elif name=='juli_bixi_kuilei':
                parts=['piston','foot'] if short=='death' else ['foot']
                controlled=[f'{fore}_{side}_{part}' for fore in ['front','rear'] for side in ['left','right'] for part in parts] if short in ['stomp','death'] else []
            elif name=='tongbi_feitian_yecha':
                controlled=['torso'] if short=='death' else ['giant_arm_0'] if short in ['attack','grab'] else []
            elif name=='youdeng_guimianfu':controlled=['body']
            elif name=='xueju_mangguyu':controlled=['spine_0']
            elif name=='shashui_funigui':
                controlled=[f'{side}_whip_0' for side in ['left','right']] if short!='death' else []
            elif name in ['qingtong_shuangtoushekui','xunshan_mujiaquan','bazu_digongzhu','mingsha_shixie','baimu_mowu','bishui_xuanjiao_youzi','chimu_zhuha','fufa_jijiu','juma_changqiangbing','kuijun_sishi','kumu_shujing','liannu_zhenzu','ludun_jiashi','muxue_feilu','pijia_panjiang_huwei','tiesuo_chihou','shibian_lishi','yinbing_guizu','yinyang_zhijiao_youhun','zhenwang_zhangqiguan','shanjing_shanxiao','zuwu_daoshou','fuhun_baibu_tongzi','zhiren_jianke','xianzhen_duantoujiang','qianji_bailian_yanshi','yanshi_clockwork_spider']:
                # Species-wide authoring contact adjustment, identity root vertical axis.
                # The scorpion's production IK wrappers are preserved and never keyed.
                controlled=['root']
            else:raise ValueError('Unreviewed contact rig: '+name)
            for bone in controlled:
                ch=animation['bones'].setdefault(bone,{})
                original=ch.get('position',[0,0,0]);keys={}
                wanted=descendants(bones,bone)
                # Geometry is evaluated against this exact authored file before adding correction.
                review.ANIM.write_text(json.dumps(data,indent=2)+'\n')
                for tick in np.arange(0,animation['animation_length']*20+.001,.125):
                    points=[p for p,_,b in review.geometry(short,tick) if b in wanted]
                    if not points:continue
                    minimum=float(np.concatenate(points)[:,1].min())
                    value=review.sample(original,tick/20).tolist()
                    if minimum < -.03:
                        coefficient=parent_vertical(bones,animation['bones'],bone,tick/20)
                        if coefficient < .35:raise AssertionError('Contact correction axis too oblique: '+name+'/'+bone)
                        value[1]+=(.08-minimum)/coefficient
                    keys[str(tick/20)]=[round(v,5) for v in value]
                ch['position']=simplify(keys)
        review.ANIM.write_text(json.dumps(data,indent=2)+'\n')
        print(name,'authored contact keys')


if __name__=='__main__':settle()
