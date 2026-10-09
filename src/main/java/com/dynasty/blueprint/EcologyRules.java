package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.Faction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;
import static com.dynasty.blueprint.EcologyRule.*;

/** Ten authored regions. Bosses are deliberately absent from all natural spawn lists. */
public final class EcologyRules {
    private static ResourceLocation id(String path){return new ResourceLocation(path.contains(":")?path:"dynasty:"+path);}
    private static Member mob(String name,int weight,int cap,boolean existing,String... prey){
        return new Member(id(name),weight,1,Math.min(cap,3),cap,false,false,existing,
                Arrays.stream(prey).map(EcologyRules::id).collect(java.util.stream.Collectors.toUnmodifiableSet()));
    }
    private static Member flying(String name,int cap){return new Member(id(name),2,1,1,cap,true,false,false,Set.of());}
    private static Member elite(String name,boolean flying){return new Member(id(name),1,1,1,1,flying,true,false,Set.of());}
    private static EcologyRule rule(String name,String dimensions,String biome,String structures,int radius,int low,int high,
            TimeWindow time,int light,boolean water,boolean natural,Caps caps,String state,Member... members){
        return new EcologyRule(id(name),id("ecology/"+dimensions),biome==null?null:id(biome),structures==null?null:id(structures),
                radius,low,high,time,Weather.ANY,light,water,natural,caps,List.of(members),
                Set.of(Faction.DYNASTY_ARMY,Faction.REBELS),Set.of(),state);
    }
    public static final List<EcologyRule> ALL=List.of(
        rule("deep_forest","overworld","blueprint/shanxiao_habitat",null,0,-63,240,TimeWindow.ALL,15,false,true,new Caps(12,3,0),"MIDNIGHT_HOWL; RAIN_CAMOUFLAGE",
            mob("shanjing_shanxiao",4,3,true,"minecraft:rabbit","minecraft:chicken","minecraft:pig","tiesuo_chihou","kuijun_sishi"),
            mob("kumu_shujing",3,2,true,"baimu_mowu"),mob("baimu_mowu",2,2,false,"shanjing_shanxiao"),mob("chimu_zhuha",4,2,true)),
        rule("ancient_battlefield","overworld",null,"blueprint/battlefields",32,-32,220,TimeWindow.NIGHT,7,false,false,new Caps(16,2,1),"ARMY_VS_REBELS; THUNDER_CHARGE_DEPENDENCY",
            mob("zuwu_daoshou",8,4,true),mob("juma_changqiangbing",2,2,true),mob("liannu_zhenzu",2,3,true),mob("ludun_jiashi",1,2,true),
            mob("zhenwang_zhangqiguan",1,1,true),mob("kuijun_sishi",1,3,true),mob("tiesuo_chihou",2,2,true),elite("xianzhen_duantoujiang",false)),
        rule("ruined_village","overworld",null,"ecology/ruined_villages",16,-63,220,TimeWindow.NIGHT,7,false,false,new Caps(8,2,1),"DAY_DORMANCY; FIRE_REPEL; MIDNIGHT_PROCESSION",
            mob("zhiren_jianke",3,3,true),mob("fuhun_baibu_tongzi",1,1,true),mob("yinyang_zhijiao_youhun",1,1,false),mob("shibian_lishi",1,2,true)),
        rule("underground_tomb","overworld",null,"ecology/tombs",0,-63,64,TimeWindow.ALL,15,false,false,new Caps(8,3,1),"CONSTRUCT_VS_SPIRITS; THUNDER_CHARGE",
            mob("shibian_lishi",1,2,true),flying("muxue_feilu",3),mob("qingtong_shuangtoushekui",1,2,false),mob("juli_bixi_kuilei",1,1,false),elite("banshan_jiazhou_shikuang",false)),
        rule("river_marsh","overworld","ecology/wetlands",null,0,-62,220,TimeWindow.ALL,15,true,true,new Caps(6,0,1),"FULL_MOON_SURFACE",
            mob("shashui_funigui",2,3,false),mob("bishui_xuanjiao_youzi",3,2,true,"chimu_zhuha"),mob("chimu_zhuha",4,2,true),elite("fubo_xunhai_yecha",false)),
        rule("cave_rift","overworld","ecology/caves",null,0,-63,40,TimeWindow.ALL,7,false,true,new Caps(8,4,0),"DARK_PERCEPTION; FIRE_BAT_AGGRESSION",
            mob("mingsha_shixie",4,3,true,"xueju_mangguyu"),mob("bazu_digongzhu",2,2,false,"mingsha_shixie"),flying("youdeng_guimianfu",3),mob("xueju_mangguyu",2,3,false)),
        rule("snow_peak","overworld","ecology/snow_peaks",null,0,140,319,TimeWindow.ALL,15,false,true,new Caps(5,3,1),"BLIZZARD_SHELTER_RAGE",
            elite("hanshan_tongjia_juyuan",false),elite("liefeng_jindiao_yushi",true),flying("tongbi_feitian_yecha",2)),
        rule("celestial_realm","celestial","ecology/celestial",null,0,-63,319,TimeWindow.ALL,15,false,false,new Caps(4,3,1),"HEAVEN_PERMIT; ECLIPSE_CHAINS; COD1_PROJECTION_ADAPTER_REQUIRED"),
        rule("toxic_miao","overworld",null,"ecology/toxic_miao",24,-63,220,TimeWindow.OUTSIDE_NOON,12,false,false,new Caps(8,3,1),"NOON_RETREAT; DUSK_HUNT",
            elite("gudu_tianzhunv",false),mob("baimu_mowu",2,2,false),elite("baimian_huxiangu",false)),
        rule("final_altar","final",null,null,0,-63,319,TimeWindow.ALL,15,false,false,new Caps(0,0,0),"FIXED_RUNE_GUARDIANS_ONLY")
    );
    public static final List<String> UNBOUND_SOURCE_ROLES=List.of("天机罗刹鸟","云中巡守仙吏虚影","蛇母麾下蛇群","玄冰异兽");
    private static final Map<ResourceLocation,Set<ResourceLocation>> FOOD_CHAIN=foodChain();
    private static Map<ResourceLocation,Set<ResourceLocation>> foodChain(){
        var out=new HashMap<ResourceLocation,Set<ResourceLocation>>();
        for(var rule:ALL)for(var member:rule.members())out.computeIfAbsent(member.mobType(),key->new HashSet<>()).addAll(member.predatorTargets());
        out.replaceAll((key,value)->Set.copyOf(value));return Map.copyOf(out);
    }
    public static Optional<EcologyRule> get(ResourceLocation id){return ALL.stream().filter(r->r.id().equals(id)).findFirst();}
    public static boolean predates(Entity hunter,Entity prey){
        var a=ForgeRegistries.ENTITY_TYPES.getKey(hunter.getType());var b=ForgeRegistries.ENTITY_TYPES.getKey(prey.getType());
        return a!=null&&b!=null&&FOOD_CHAIN.getOrDefault(a,Set.of()).contains(b);
    }
    public static List<ResourceLocation> missingDependencies(){
        return ALL.stream().flatMap(r->r.members().stream()).map(Member::mobType).distinct()
                .filter(id->!ForgeRegistries.ENTITY_TYPES.containsKey(id)).sorted().toList();
    }
    private EcologyRules(){}
}
