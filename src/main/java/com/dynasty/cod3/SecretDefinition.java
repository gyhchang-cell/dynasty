package com.dynasty.cod3;

/** Conditions never refer to seasons/fog/eclipses that do not exist in this Forge project. */
public record SecretDefinition(int number,Scope scope,Trigger trigger,boolean oneTime,int cooldown,String requiredItem,String rewardItem) {
    public enum Scope {WORLD,PLAYER}
    public enum Trigger {INTERACT_BLOCK,BREAK_BLOCK,HIT_TARGET,USE_ITEM_AT_POS,ENTER_REGION,TIME_WINDOW,WEATHER_WINDOW,KILL_ENTITY_AT_REGION,PLACE_ITEM,PLAY_INSTRUMENT,READ_PATTERN,EQUIPMENT_CHECK,WORLD_STATE,COMBINATION}
    public boolean enabled(){return number!=10&&number!=12;}
    public static SecretDefinition of(int n){
        var row=Cod3Catalog.find("secrets",String.format(java.util.Locale.ROOT,"secret_%02d",n));
        Trigger type=switch(n){case 1,26->Trigger.PLAY_INSTRUMENT;case 2->Trigger.TIME_WINDOW;case 3,9->Trigger.EQUIPMENT_CHECK;case 5,10,15,16,17,22,23,28,29->Trigger.USE_ITEM_AT_POS;case 4->Trigger.KILL_ENTITY_AT_REGION;case 6,13,19,25->Trigger.BREAK_BLOCK;case 7,14->Trigger.WEATHER_WINDOW;case 8,11,30->Trigger.COMBINATION;case 12,18,21,27->Trigger.ENTER_REGION;case 20,24->Trigger.HIT_TARGET;default->Trigger.INTERACT_BLOCK;};
        String required=switch(n){case 1->"dynasty:yu_di";case 3->"dynasty:qinglong_dao";case 5->"dynasty:baijiu";case 8->"minecraft:water_bucket";case 10->"dynasty:qinglong_scale";case 15->"dynasty:bronze_ingot";case 16->"dynasty:chiling_brush";case 17->"dynasty:cinnabar";case 22->"dynasty:emperor_bone";case 23->"dynasty:healing_salve";case 27->"dynasty:sea_pearl";case 29->"minecraft:potion";default->"";};
        // Unregistered named rewards deliberately reuse real existing items, preserving IDs.
        String reward=switch(n){case 2->"dynasty:jade";case 6->"dynasty:pill_longevity";case 9,29->"dynasty:longyuan_sword";case 15,16,30->"dynasty:blueprint";case 17->"dynasty:bamboo_slip";case 19->"dynasty:silk";case 23->"dynasty:healing_salve";case 25,27->"dynasty:sea_pearl";default->"dynasty:jade";};
        return new SecretDefinition(n,Scope.valueOf(row.get("scope").getAsString()),type,row.get("oneTime").getAsBoolean(),24000,required,reward);
    }
}
