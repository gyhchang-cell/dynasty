package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.Combatant;
import com.dynasty.blueprint.combat.Faction;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class EcologyGameTests {
    private static TemplateMob fixture(GameTestHelper h,net.minecraft.world.entity.EntityType<TemplateMob> type,int x){
        var mob=type.create(h.getLevel());mob.setNoAi(true);mob.setNoGravity(true);
        mob.setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(x,2,5))));
        h.getLevel().addFreshEntity(mob);return mob;
    }
    @GameTest(template="bow_ritual_test",batch="cod2_ecology")
    public static void battlefieldAllegianceIsScopedPersistentAndUsesCod1Factions(GameTestHelper h){
        var powder=fixture(h,BlueprintEntities.KUIJUN_SISHI.get(),4);var flag=fixture(h,BlueprintEntities.ZHENWANG_ZHANGQIGUAN.get(),7);
        h.assertTrue(Combatant.allied(powder,flag),"Legacy cod1 squad retains its existing allegiance");
        EcologyManager.assignBattlefield(powder);EcologyManager.assignBattlefield(flag);
        h.assertTrue(powder.faction()==Faction.REBELS&&flag.faction()==Faction.DYNASTY_ARMY&&!Combatant.allied(powder,flag),"Authored battlefield contains opposing existing factions");
        powder.setTarget(flag);h.assertTrue(powder.getTarget()==flag,"Existing combat accepts opposing battle squad");
        var saved=new CompoundTag();powder.save(saved);var copy=BlueprintEntities.KUIJUN_SISHI.get().create(h.getLevel());copy.load(saved);
        h.assertTrue(copy.faction()==Faction.REBELS,"Encounter allegiance survives entity disk NBT");powder.discard();flag.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_ecology",timeoutTicks=35)
    public static void serpentActuallyBitesToadWithoutMakingAllWoodlandEnemies(GameTestHelper h){
        var serpent=fixture(h,BlueprintEntities.BISHUI_XUANJIAO_YOUZI.get(),5);var toad=fixture(h,BlueprintEntities.CHIMU_ZHUHA.get(),7);
        var tree=fixture(h,BlueprintEntities.KUMU_SHUJING.get(),11);
        h.assertTrue(!Combatant.allied(serpent,toad)&&Combatant.allied(serpent,tree),"Only the authored food-chain pair breaks woodland alliance");
        serpent.setTarget(toad);toad.setTarget(serpent);h.assertTrue(toad.getTarget()==serpent,"Prey can defend itself");
        float health=toad.getHealth();h.assertTrue(serpent.startSkill(ArmySkills.SERPENT_BITE,toad),"Real cod1 serpent action accepts authored prey");
        h.runAfterDelay(22,()->{h.assertTrue(toad.getHealth()<health,"Server combat contact damages prey");serpent.discard();toad.discard();tree.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",batch="cod2_ecology")
    public static void localCapsAndConnectedWaterRejectCrowdingAndPuddles(GameTestHelper h){
        var rule=EcologyRules.get(new ResourceLocation("dynasty:river_marsh")).orElseThrow();
        var member=rule.members().stream().filter(m->m.mobType().getPath().equals("bishui_xuanjiao_youzi")).findFirst().orElseThrow();
        var pos=h.absolutePos(new BlockPos(7,2,5));h.setBlock(7,2,5,Blocks.WATER);
        h.assertTrue(!EcologyManager.connectedWater(h.getLevel(),pos),"One water block cannot activate wetland ecology");
        for(int x=5;x<=9;x++)for(int z=3;z<=7;z++)h.setBlock(x,2,z,Blocks.WATER);
        h.assertTrue(EcologyManager.connectedWater(h.getLevel(),pos),"Connected broad pool meets shoreline rule");
        var a=fixture(h,BlueprintEntities.BISHUI_XUANJIAO_YOUZI.get(),6);var b=fixture(h,BlueprintEntities.BISHUI_XUANJIAO_YOUZI.get(),8);
        h.assertTrue(!EcologyManager.capAllows(h.getLevel(),pos,rule,member),"Two actual nearby serpents close type cap");
        a.discard();b.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_ecology")
    public static void regionsLoadRealTagsAndCannotTurnPlayerPlatformsIntoHeaven(GameTestHelper h){
        var level=h.getLevel();var pos=h.absolutePos(new BlockPos(7,2,7));
        var forest=EcologyRules.get(new ResourceLocation("dynasty:deep_forest")).orElseThrow();
        var heaven=EcologyRules.get(new ResourceLocation("dynasty:celestial_realm")).orElseThrow();
        h.assertTrue(EcologyManager.dimensionMatches(level,forest),"Actual overworld dimension type tag is loaded");
        h.assertTrue(!EcologyManager.regionMatches(level,pos.above(100),heaven),"High player platform does not grant celestial dimension membership");
        var tickets=new java.util.HashSet<>(level.getForcedChunks());
        h.assertTrue(!LoadedStructureRegions.contains(level,pos,new ResourceLocation("dynasty:ecology/toxic_miao"),24),"Missing authored Miao structure stays inactive");
        h.assertTrue(tickets.equals(level.getForcedChunks()),"Region query acquires no forced chunk tickets");
        h.assertTrue(EcologyRules.ALL.size()==10&&!EcologyRules.ALL.get(9).naturalSpawning()&&EcologyRules.ALL.get(9).members().isEmpty(),"Final altar has no natural guardian pool");
        h.assertTrue(EcologyRules.missingDependencies().contains(new ResourceLocation("dynasty:baimu_mowu")),"Missing cod1 creature is explicit, not replaced");h.succeed();
    }
    private EcologyGameTests(){}
}
