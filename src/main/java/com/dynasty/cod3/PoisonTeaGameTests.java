package com.dynasty.cod3;

import com.dynasty.expansion.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.gametest.*;
import java.util.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class PoisonTeaGameTests {
    private static final String KEY="site_wayside_tea_stall";
    private static final Set<UUID> NPCS=new HashSet<>();
    private static final List<ServerPlayer> PLAYERS=new ArrayList<>();
    private static BlockPos room(GameTestHelper h){for(int x=0;x<=8;x++)for(int z=0;z<=8;z++){h.setBlock(new BlockPos(x,1,z),Blocks.STONE);for(int y=2;y<=5;y++)h.setBlock(new BlockPos(x,y,z),Blocks.AIR);}var at=h.absolutePos(new BlockPos(3,2,3));h.getLevel().setBlockAndUpdate(at,SmallInteractions.ENTRIES.get("wayside_tea_stall").get().defaultBlockState());NPCS.add(SmallInteractions.poisonTeaVendorId(h.getLevel(),at));return at;}
    private static ServerPlayer player(GameTestHelper h,BlockPos at){return player(h,at,new GameProfile(UUID.randomUUID(),"tea-native"));}
    private static ServerPlayer player(GameTestHelper h,BlockPos at,GameProfile profile){var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),profile);p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setPos(Vec3.atBottomCenterOf(at.south(2)));PLAYERS.add(p);return p;}
    private static void use(GameTestHelper h,ServerPlayer p,BlockPos at){h.getLevel().getBlockState(at).use(h.getLevel(),p,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(at),Direction.UP,at,false));}
    private static boolean choose(ServerPlayer p,String choice){var s=NpcDialogue.session(p.getUUID());return s!=null&&NpcDialogue.choose(p,s.token(),choice);}
    private static DynastyNpcEntity vendor(GameTestHelper h,BlockPos at){return (DynastyNpcEntity)h.getLevel().getEntity(SmallInteractions.poisonTeaVendorId(h.getLevel(),at));}
    private static void ready(ServerPlayer p){EquipmentBehaviors.saved(p).putLong(KEY+"_start",p.level().getGameTime()-2400);}
    @AfterBatch(batch="cod4_poison_tea")
    public static void cleanup(net.minecraft.server.level.ServerLevel level){for(var p:PLAYERS){p.closeContainer();NpcDialogue.logout(new PlayerEvent.PlayerLoggedOutEvent(p));}PLAYERS.clear();for(var id:NPCS){var e=level.getEntity(id);if(e!=null)e.discard();}NPCS.clear();}
    @GameTest(template="bow_ritual_test",batch="cod4_poison_tea",setupTicks=20)
    public static void actualInspectionAndNonceExposeCluesButDoNotFinishSecret(GameTestHelper h){
        var at=room(h);var p=player(h,at);use(h,p,at);var npc=vendor(h,at);var first=NpcDialogue.session(p.getUUID());h.assertTrue(npc!=null&&npc.role.equals("huang_laohan")&&first.node().equals("first"),"Actual existing vendor opens original dialogue engine's tea choice graph");
        h.assertTrue(EquipmentBehaviors.saved(p).getLong(KEY+"_next")==h.getLevel().getGameTime()+2400&&!EquipmentBehaviors.saved(p).getBoolean(KEY+"_inspected"),"Original two-minute deadline retained; mere opening is not accepted observation");
        h.assertTrue(!NpcDialogue.choose(p,first.token(),"flip")&&choose(p,"inspect"),"Unshown action rejects; actual displayed observation advances clue node");h.assertTrue(EquipmentBehaviors.saved(p).getBoolean(KEY+"_inspected")&&NpcDialogue.session(p.getUUID()).node().equals("inspected")&&!NpcDialogue.choose(p,first.token(),"drink"),"Accepted observation records actual choice and replaces nonce");
        h.assertTrue(!choose(p,"flip")&&!SecretTracker.poisonTeaClaimed(p)&&h.getLevel().getBlockState(at).is(SmallInteractions.ENTRIES.get("wayside_tea_stall").get()),"Early flip does not touch physical table or grant secret");
        var data=npc.saveWithoutId(new net.minecraft.nbt.CompoundTag());npc.discard();var restored=NpcContent.NPCS.get("huang_laohan").get().create(h.getLevel());restored.load(data);h.getLevel().addFreshEntity(restored);use(h,p,at);h.assertTrue(vendor(h,at)==restored&&NpcDialogue.session(p.getUUID()).node().equals("inspected"),"Native vendor and player inspection receipts survive reload without duplicate entity");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_poison_tea",setupTicks=20)
    public static void falseChoiceActuallyPoisonsWithFiniteNativeDurationAndNoReward(GameTestHelper h){
        var at=room(h);var p=player(h,at);p.getFoodData().setFoodLevel(17);p.setNoGravity(true);for(int i=0;i<61;i++)p.tick();use(h,p,at);var old=NpcDialogue.session(p.getUUID());h.assertTrue(choose(p,"drink")&&p.hasEffect(MobEffects.POISON)&&p.getEffect(MobEffects.POISON).getDuration()==400&&p.getEffect(MobEffects.POISON).getAmplifier()==0,"Direct drink has actual bounded twenty-second native poison, not just a failure line");
        h.assertTrue(!NpcDialogue.choose(p,old.token(),"drink")&&!choose(p,"drink"),"Successful drink replaces nonce and cannot spam-refresh before its bounded cooldown");for(int i=0;i<30;i++){p.tick();p.doTick();}
        h.assertTrue(p.getHealth()<p.getMaxHealth()&&p.getHealth()>=1&&p.getEffect(MobEffects.POISON).getDuration()==370,"Actual native ticks after original spawn protection deal poison health loss and expire duration: health="+p.getHealth()+", duration="+p.getEffect(MobEffects.POISON).getDuration());h.assertTrue(!SecretTracker.poisonTeaClaimed(p)&&!EquipmentBehaviors.saved(p).getBoolean(KEY+"_done")&&p.getInventory().countItem(ExpansionContent.item("silk"))==0,"Poison false clue never completes secret or grants reward");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_poison_tea",setupTicks=20)
    public static void nativeBreakPermissionAndActualOverturnedTableOwnOriginalReward(GameTestHelper h){
        var at=room(h);var p=player(h,at);use(h,p,at);choose(p,"inspect");ready(p);p.gameMode.changeGameModeForPlayer(GameType.ADVENTURE);
        h.assertTrue(!choose(p,"flip")&&!SecretTracker.poisonTeaClaimed(p)&&!h.getLevel().getBlockState(at).getValue(BlockStateProperties.LIT),"Actual vanilla Adventure permission refuses native flip, physical change and reward");p.gameMode.changeGameModeForPlayer(GameType.SURVIVAL);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.IRON_PICKAXE));
        p.addEffect(new MobEffectInstance(MobEffects.POISON,200));var before=h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new AABB(at).inflate(2),e->e.getItem().is(SmallInteractions.ENTRIES.get("wayside_tea_stall").get().asItem())).size();
        h.assertTrue(choose(p,"flip")&&SecretTracker.poisonTeaClaimed(p)&&p.getInventory().countItem(ExpansionContent.item("silk"))==1&&h.getLevel().getBlockState(at).getValue(BlockStateProperties.LIT),"Real native destroy succeeds and original secret 19 rewards one silk; actual Site returns as persistent overturned table");
        h.assertTrue(!SecretTracker.teaFlipBreak(p,at)&&!p.hasEffect(MobEffects.POISON)&&NpcDialogue.session(p.getUUID())==null&&!vendor(h,at).isNoAi(),"Transient native-break scope closes, original first cleanse retained and vendor released to original AI");
        h.assertTrue(h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new AABB(at).inflate(2),e->e.getItem().is(SmallInteractions.ENTRIES.get("wayside_tea_stall").get().asItem())).size()==before,"Native interactive flip creates no duplicate placeable Site even with a correct harvesting tool");
        var adv=p.server.getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","cod4_wayside_tea_stall"));h.assertTrue(p.getAdvancements().getOrStartProgress(adv).isDone()&&!SecretTracker.get(h.getLevel()).claim(p,19,at),"Actual old task advancement completes; cleared proof and original receipt prevent replay");use(h,p,at);h.assertTrue(p.getInventory().countItem(ExpansionContent.item("silk"))==1,"Repeated inspection does not repay original secret");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_poison_tea",setupTicks=20)
    public static void physicalSceneAndPersonalNonceRejectRemoteForeignOrMissingClue(GameTestHelper h){
        var at=room(h);var p=player(h,at);use(h,p,at);ready(p);h.assertTrue(!SmallInteractions.flipPoisonTea(p,vendor(h,at))&&!SecretTracker.get(h.getLevel()).claim(p,19,at),"Old generic ready/count without actual observation and native flip proof cannot grant reward");choose(p,"inspect");var s=NpcDialogue.session(p.getUUID());var q=player(h,at);use(h,q,at);h.assertTrue(!NpcDialogue.choose(q,s.token(),"flip")&&!EquipmentBehaviors.saved(q).getBoolean(KEY+"_inspected"),"Shared vendor does not transfer another character's nonce or observation");
        p.setPos(p.getX()+30,p.getY(),p.getZ());h.assertTrue(!NpcDialogue.choose(p,s.token(),"flip"),"Remote button rejects before native break");p.setPos(Vec3.atBottomCenterOf(at.south(2)));use(h,p,at);var fresh=NpcDialogue.session(p.getUUID());h.getLevel().setBlockAndUpdate(at,Blocks.STONE.defaultBlockState());h.assertTrue(!NpcDialogue.choose(p,fresh.token(),"flip")&&!SecretTracker.poisonTeaClaimed(p),"Replaced Scene invalidates queued choice");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_poison_tea",setupTicks=20)
    public static void ordinaryMiningStillDropsTheOriginalSiteWithoutGrantingSecret(GameTestHelper h){
        var at=room(h);var p=player(h,at);
        var rule=h.getLevel().getGameRules().getRule(net.minecraft.world.level.GameRules.RULE_DOBLOCKDROPS);boolean original=rule.get();rule.set(true,h.getLevel().getServer());
        try{
            for(String tool:new String[]{"pickaxe","axe"})for(String id:SmallInteractions.IDS){
                if(tool.equals("axe")&&!java.util.Set.of("old_weapon_rack","abandoned_armory","puzzle_box","ghost_market_boat","wayside_tea_stall","old_bellows","broken_waterwheel").contains(id))continue;
                var block=SmallInteractions.ENTRIES.get(id).get();h.getLevel().setBlockAndUpdate(at,block.defaultBlockState());p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(tool.equals("pickaxe")?Items.IRON_PICKAXE:Items.IRON_AXE));
                h.assertTrue(p.gameMode.destroyBlock(at)&&h.getLevel().getBlockState(at).isAir(),"Ordinary native "+tool+" mining still removes registered Site: "+id);
                var drops=h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new AABB(at).inflate(2),e->e.getItem().is(block.asItem()));
                h.assertTrue(drops.stream().mapToInt(e->e.getItem().getCount()).sum()==1&&!SecretTracker.poisonTeaClaimed(p)&&!SecretTracker.teaFlipBreak(p,at),"Only interactive flip suppresses a duplicate Site; ordinary correct-tool harvest yields one original block and no fake secret: "+id+"/"+tool);for(var drop:drops)drop.discard();
            }
            h.succeed();
        }finally{rule.set(original,h.getLevel().getServer());}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_poison_tea",setupTicks=20)
    public static void legacyMilkCompletionCloneAndSecondCharacterKeepSeparateNativeSecret(GameTestHelper h){
        var at=room(h);var p=player(h,at);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.MILK_BUCKET));use(h,p,at);ready(p);EquipmentBehaviors.saved(p).putLong(KEY+"_next",h.getLevel().getGameTime());p.addEffect(new MobEffectInstance(MobEffects.POISON,200));use(h,p,at);
        h.assertTrue(EquipmentBehaviors.saved(p).getBoolean(KEY+"_done")&&!p.hasEffect(MobEffects.POISON)&&p.getMainHandItem().is(Items.MILK_BUCKET)&&!SecretTracker.poisonTeaClaimed(p),"Original milk completion/cleanse and nonconsumption remain; it never fakes original secret 19");p.setItemInHand(InteractionHand.MAIN_HAND,ItemStack.EMPTY);use(h,p,at);choose(p,"inspect");p.addEffect(new MobEffectInstance(MobEffects.POISON,200));h.assertTrue(choose(p,"flip")&&p.hasEffect(MobEffects.POISON)&&p.getInventory().countItem(ExpansionContent.item("silk"))==1,"Old completed site earns only missing native secret with actual flip, no second wait/cleanse/old rewards");
        var clone=player(h,at,p.getGameProfile());SecretTracker.clone(new PlayerEvent.Clone(clone,p,true));use(h,clone,at);h.assertTrue(SecretTracker.poisonTeaClaimed(clone)&&clone.getInventory().countItem(ExpansionContent.item("silk"))==0,"Native player/dimension one-time claim survives death without a second reward");
        var q=player(h,at);use(h,q,at);h.assertTrue(!SecretTracker.poisonTeaClaimed(q)&&!EquipmentBehaviors.saved(q).getBoolean(KEY+"_inspected")&&NpcDialogue.session(q.getUUID()).node().equals("first"),"Overturned persistent Site remains usable by a separate character without inherited personal progress");choose(q,"inspect");ready(q);h.assertTrue(choose(q,"flip")&&q.getInventory().countItem(ExpansionContent.item("silk"))==1&&p.getInventory().countItem(ExpansionContent.item("silk"))==1,"Shared physical Site supports two independent actual personal native claims, not real network multiplayer evidence");h.succeed();
    }
}
