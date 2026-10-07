package com.dynasty.blueprint;

/** Shared locomotion semantics; every species retains its own authored rig, clips and attack clock. */
public enum AnimationProfile {
    LIGHT_HUMANOID(false,32),HEAVY_HUMANOID(false,24),ARCHER(false,32),BLADE(false,32),SPEAR(false,32),CASTER(false,32),
    QUADRUPED(false,32),MULTILEG(false,24),SERPENT(false,32),FLOATING(true,24),GIANT_CONSTRUCT(false,24);
    private final boolean floating;private final int secondaryDistance;
    AnimationProfile(boolean floating,int secondaryDistance){this.floating=floating;this.secondaryDistance=secondaryDistance;}
    public boolean floating(){return floating;}
    public int secondaryDistance(){return secondaryDistance;}
    public boolean loops(String clip){return switch(clip){case "idle","walk","run","fly","climb","burrow","camouflage"->true;default->false;};}
    /** Rate changes affect only locomotion. Attack/death clips continue to seek the authoritative server epoch. */
    public double playbackRate(String clip,double horizontalSpeed,double movementAttribute,boolean sprinting){
        if(!clip.equals("walk")&&!clip.equals("run")&&!clip.equals("fly"))return 1;
        if(floating)return 1;
        double nominal=Math.max(.035,movementAttribute*(sprinting?.6:.35));
        return net.minecraft.util.Mth.clamp(horizontalSpeed/nominal,.65,1.5);
    }
    public static AnimationProfile forKind(TemplateMob.Kind kind){
        return switch(kind){
            case SWORD->BLADE;case SPEAR->SPEAR;case CROSSBOW->ARCHER;case SHIELD,AXE_GUARD,CORPSE->HEAVY_HUMANOID;
            case PRIEST,FLAG->CASTER;case SCOUT,POWDER,PAPER->LIGHT_HUMANOID;case BEAST,TOAD->QUADRUPED;
            case SCORPION->MULTILEG;case SERPENT->SERPENT;case GHOST,CHILD,SKULL->FLOATING;case STONE_GUARD,TREE->GIANT_CONSTRUCT;
        };
    }
}
