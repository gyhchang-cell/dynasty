package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.SkillDefinition;
import java.util.List;

/** Authored contact ticks; names also select independent client animation clips. */
public final class ArmySkills {
    public static final int THRUST=10,BRACE=11,VOLLEY=12,ROLL=13,CUT=14,GRAPPLE=15,STAB=16,DETONATE=17,SLAM=18,KNEE=19;
    public static final int AXE_CLAMP=20,AXE_COUNTER=21;
    public static final int GHOST_THRUST=22,GHOST_PHASE=23;
    public static final int CORPSE_SMASH=24;
    public static final int CHILD_LAUGH=25,CHILD_CURSE=26;
    public static final int PAPER_SLASH=27,PAPER_SHED=28;
    public static final int SKULL_DIVE=29,SKULL_BLOOD=30;
    public static final int TOAD_TONGUE=31,TOAD_LEAP=32,TOAD_BURST=33;
    public static final int TREE_WAKE=34,TREE_SWEEP=35,TREE_ROOTS=36;
    public static final int SCORPION_EMERGE=37,SCORPION_CLAW=38,SCORPION_SONG=39;
    public static final int SERPENT_BITE=40,SERPENT_COIL=41,STONE_UPPERCUT=42,STONE_SLAM=43;
    public static final int DOG_BITE=44,DOG_ALARM=45;
    public static final int BRONZE_FRONT_STAB=46,BRONZE_REAR_STAB=47,BRONZE_FIRE=48,BRONZE_POISON=49;
    public static final int SPIDER_DRILL=50,SPIDER_DROP=51;
    public static final List<SkillDefinition> ALL=List.of(
        skill(SPIDER_DRILL,"spider_drill",12,1,23,42,0,2.8,100,1,.3,true,12),
        skill(SPIDER_DROP,"spider_drop",20,60,20,160,0,8,360,1.4F,.6,true,20),
        skill(BRONZE_FRONT_STAB,"bronze_front_stab",10,1,15,32,0,2.6,50,1,.2,true,10),
        skill(BRONZE_REAR_STAB,"bronze_rear_stab",10,1,15,32,0,2.6,50,1,.2,true,10),
        skill(BRONZE_FIRE,"bronze_fire",18,60,24,180,0,5,50,.4F,0,true,18,28,38,48,58,68),
        skill(BRONZE_POISON,"bronze_poison",18,60,24,180,0,5,50,.4F,0,true,18,28,38,48,58,68),
        skill(DOG_BITE,"dog_bite",8,1,13,30,0,2.3,80,1,.1,true,8),
        skill(DOG_ALARM,"dog_alarm",20,1,19,200,0,20,360,0,0,true,20),
        skill(STONE_UPPERCUT,"stone_uppercut",16,1,23,50,0,2.8,120,1,.45,true,16),
        skill(STONE_SLAM,"stone_slam",30,1,29,110,0,3,0,1.6F,.65,true,30),
        skill(SERPENT_BITE,"serpent_bite",12,1,17,38,0,2.8,65,1,0,true,12),
        skill(SERPENT_COIL,"serpent_coil",18,25,21,180,0,3.2,70,.5F,0,true,18),
        skill(THRUST,"spear_thrust",12,1,13,34,0,3.5,28,1,.9,true,12),
        skill(BRACE,"spear_brace",8,25,15,65,0,6,25,3,1.1,false,8),
        skill(VOLLEY,"crossbow_volley",14,9,23,46,3,24,50,1,.1,true,14,18,22),
        skill(ROLL,"crossbow_roll",6,15,11,80,0,4,60,0,0,false,6,20),
        skill(CUT,"scout_cut",9,7,14,36,0,2.8,100,.65F,.15,true,9,15),
        skill(GRAPPLE,"scout_grapple",12,31,15,110,8,20,35,1.2F,.5,true,12),
        skill(STAB,"powder_stab",8,10,12,28,0,2.5,95,.6F,.1,true,8,12,17),
        skill(DETONATE,"powder_detonate",20,1,15,200,0,4,360,3.5F,1.4,false,20),
        skill(SLAM,"banner_slam",18,1,21,62,0,3.3,360,1,.65,true,18),
        skill(KNEE,"scout_knee",6,1,11,30,0,2.5,50,1.2F,.5,true,6),
        skill(AXE_CLAMP,"guard_axe_clamp",16,7,19,44,0,3.2,105,1.15F,.25,true,16,22),
        skill(AXE_COUNTER,"guard_axe_counter",10,1,23,100,0,3.6,360,1.8F,1.1,false,10),
        skill(GHOST_THRUST,"ghost_frost_thrust",14,1,19,38,0,3.8,30,1,.15,true,14),
        skill(GHOST_PHASE,"ghost_phase",0,6,10,120,0,16,360,0,0,false,0),
        skill(CORPSE_SMASH,"corpse_smash",20,1,25,55,0,3.3,110,1.5F,.7,true,20),
        skill(CHILD_LAUGH,"child_laugh",12,1,17,50,0,6,360,.5F,0,true,12),
        skill(CHILD_CURSE,"child_curse",40,1,19,180,1.5,10,360,0,0,true,40),
        skill(PAPER_SLASH,"paper_slash",6,1,13,24,0,2.8,105,1,.08,true,6),
        skill(PAPER_SHED,"paper_shed",6,1,9,1,0,12,360,0,0,false,6),
        skill(SKULL_DIVE,"skull_dive",14,12,18,60,0,12,40,1,0,true,14),
        skill(SKULL_BLOOD,"skull_blood",20,1,29,160,0,8,360,0,0,true,20),
        skill(TOAD_TONGUE,"toad_tongue",10,1,17,36,0,5,30,1,0,true,10),
        skill(TOAD_LEAP,"toad_leap",10,20,10,45,3.5,24,60,1,0,true,10),
        skill(TOAD_BURST,"toad_burst",12,1,19,200,0,24,360,1,0,true,12),
        skill(TREE_WAKE,"tree_wake",20,1,9,1,0,24,360,0,0,false,20),
        skill(TREE_SWEEP,"tree_sweep",18,1,23,48,0,3.7,140,1,.65,true,18),
        skill(TREE_ROOTS,"tree_roots",28,1,31,180,3,10,360,0,0,true,28),
        skill(SCORPION_EMERGE,"scorpion_emerge",22,1,9,1,0,24,360,0,0,false,22),
        skill(SCORPION_CLAW,"scorpion_claw",12,9,19,40,0,3,80,1,0,true,12,20),
        skill(SCORPION_SONG,"scorpion_song",20,1,27,180,0,5,360,0,0,true,20));
    private ArmySkills(){}
    private static SkillDefinition skill(int id,String key,int w,int a,int r,int cd,double min,double max,double angle,
            float damage,double knockback,boolean interrupt,int... contacts){
        return new SkillDefinition(id,key,w,a,r,cd,min,max,angle,damage,knockback,interrupt,true,
            java.util.Arrays.stream(contacts).boxed().toList());
    }
    public static SkillDefinition byId(int id){return ALL.stream().filter(s->s.id()==id).findFirst().orElse(null);}
}
