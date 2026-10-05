package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.SkillDefinition;
import java.util.List;

/** Authored contact ticks; names also select independent client animation clips. */
public final class ArmySkills {
    public static final int THRUST=10,BRACE=11,VOLLEY=12,ROLL=13,CUT=14,GRAPPLE=15,STAB=16,DETONATE=17,SLAM=18,KNEE=19;
    public static final List<SkillDefinition> ALL=List.of(
        skill(THRUST,"spear_thrust",12,1,13,34,0,3.5,28,1,.9,true,12),
        skill(BRACE,"spear_brace",8,25,15,65,0,6,25,3,1.1,false,8),
        skill(VOLLEY,"crossbow_volley",14,9,23,46,3,24,50,1,.1,true,14,18,22),
        skill(ROLL,"crossbow_roll",6,15,11,80,0,4,60,0,0,false,6,20),
        skill(CUT,"scout_cut",9,7,14,36,0,2.8,100,.65F,.15,true,9,15),
        skill(GRAPPLE,"scout_grapple",12,31,15,110,8,20,35,1.2F,.5,true,12),
        skill(STAB,"powder_stab",8,10,12,28,0,2.5,95,.6F,.1,true,8,12,17),
        skill(DETONATE,"powder_detonate",20,1,15,200,0,4,360,3.5F,1.4,false,20),
        skill(SLAM,"banner_slam",18,1,21,62,0,3.3,360,1,.65,true,18),
        skill(KNEE,"scout_knee",6,1,11,30,0,2.5,50,1.2F,.5,true,6));
    private ArmySkills(){}
    private static SkillDefinition skill(int id,String key,int w,int a,int r,int cd,double min,double max,double angle,
            float damage,double knockback,boolean interrupt,int... contacts){
        return new SkillDefinition(id,key,w,a,r,cd,min,max,angle,damage,knockback,interrupt,true,
            java.util.Arrays.stream(contacts).boxed().toList());
    }
    public static SkillDefinition byId(int id){return ALL.stream().filter(s->s.id()==id).findFirst().orElse(null);}
}
