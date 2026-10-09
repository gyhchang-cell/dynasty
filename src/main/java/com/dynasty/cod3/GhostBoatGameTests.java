package com.dynasty.cod3;

import com.dynasty.expansion.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.inventory.MerchantMenu;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.gametest.*;
import java.util.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class GhostBoatGameTests {
    private static final String KEY="site_ghost_market_boat";
    private static final Set<UUID> NPCS=new HashSet<>();
    private static final List<ServerPlayer> PLAYERS=new ArrayList<>();
    private static BlockPos room(GameTestHelper h){
        for(int x=0;x<=8;x++)for(int z=0;z<=8;z++){h.setBlock(new BlockPos(x,1,z),Blocks.STONE);for(int y=2;y<=5;y++)h.setBlock(new BlockPos(x,y,z),Blocks.AIR);}
        var at=h.absolutePos(new BlockPos(3,2,3));h.getLevel().setBlockAndUpdate(at,SmallInteractions.ENTRIES.get("ghost_market_boat").get().defaultBlockState());NPCS.add(SmallInteractions.ghostBoatId(h.getLevel(),at));return at;
    }
    private static ServerPlayer player(GameTestHelper h,BlockPos at){return player(h,at,new GameProfile(UUID.randomUUID(),"ghost-boat"));}
    private static ServerPlayer player(GameTestHelper h,BlockPos at,GameProfile profile){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),profile);p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setPos(Vec3.atBottomCenterOf(at));PLAYERS.add(p);return p;
    }
    private static void use(GameTestHelper h,ServerPlayer p,BlockPos at){h.getLevel().getBlockState(at).use(h.getLevel(),p,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(at),Direction.UP,at,false));}
    private static DynastyNpcEntity boat(GameTestHelper h,BlockPos at){return (DynastyNpcEntity)h.getLevel().getEntity(SmallInteractions.ghostBoatId(h.getLevel(),at));}
    private static void light(GameTestHelper h,ServerPlayer p,BlockPos at){p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("soul_incense"),2));use(h,p,at);}
    private static boolean choose(ServerPlayer p,String choice){var s=NpcDialogue.session(p.getUUID());return s!=null&&NpcDialogue.choose(p,s.token(),choice);}
    private static void ready(ServerPlayer p){EquipmentBehaviors.saved(p).putLong(KEY+"_start",p.level().getGameTime()-2400);}
    @AfterBatch(batch="cod4_ghost_boat")
    public static void cleanup(net.minecraft.server.level.ServerLevel level){
        for(var p:PLAYERS){p.closeContainer();NpcDialogue.logout(new PlayerEvent.PlayerLoggedOutEvent(p));}PLAYERS.clear();
        for(var id:NPCS){var e=level.getEntity(id);if(e!=null)e.discard();}NPCS.clear();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_ghost_boat",setupTicks=20)
    public static void onlyRealPaidIncenseSpawnsOnePhysicalNativeBoatman(GameTestHelper h){
        var at=room(h);var p=player(h,at);use(h,p,at);h.assertTrue(boat(h,at)==null&&NpcDialogue.session(p.getUUID())==null,"Unpaid inspection is a clue, not a merchant/reward");
        for(var d:Direction.Plane.HORIZONTAL)for(int distance=1;distance<=2;distance++){h.getLevel().setBlockAndUpdate(at.relative(d,distance),Blocks.STONE.defaultBlockState());h.getLevel().setBlockAndUpdate(at.relative(d,distance).above(),Blocks.STONE.defaultBlockState());}
        light(h,p,at);h.assertTrue(p.getMainHandItem().getCount()==2&&!EquipmentBehaviors.saved(p).getBoolean(KEY+"_incense_lit"),"No standing space consumes neither incense nor payment history");
        room(h);use(h,p,at);var npc=boat(h,at);h.assertTrue(npc!=null&&npc.role.equals("huang_laohan")&&p.getMainHandItem().getCount()==1,"Exactly one actual existing registered boatman and one incense payment");
        var root=EquipmentBehaviors.saved(p);h.assertTrue(root.getLong(KEY+"_start")==h.getLevel().getGameTime()&&root.getLong(KEY+"_next")==h.getLevel().getGameTime()+2400,"Original two-minute duration retained");
        for(int i=0;i<8;i++)use(h,p,at);h.assertTrue(boat(h,at)==npc&&p.getMainHandItem().getCount()==1&&!root.getBoolean(KEY+"_talked")&&!SecretTracker.ghostBoatClaimed(p),"Opening creates no duplicate, second payment, accepted TALK or reward");
        var q=player(h,at);NpcDialogue.open(q,npc);h.assertTrue(NpcDialogue.session(q.getUUID())==null&&!npc.trade(q),"Another player cannot borrow a visible boat or shift-trade without paying");light(h,q,at);
        h.assertTrue(boat(h,at)==npc&&q.getMainHandItem().getCount()==1&&!EquipmentBehaviors.saved(q).getBoolean(KEY+"_talked"),"Characters share native merchant stock while keeping paid incense and dialogue progress separate");
        var elsewhere=h.absolutePos(new BlockPos(6,2,6));h.getLevel().setBlockAndUpdate(elsewhere,SmallInteractions.ENTRIES.get("ghost_market_boat").get().defaultBlockState());use(h,p,elsewhere);h.assertTrue(boat(h,elsewhere)==null&&root.getLong(KEY+"_anchor")==at.asLong(),"A paid surviving boat does not light unrelated physical boats for free");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_ghost_boat",setupTicks=20)
    public static void actualNonceTalkAndCinnabarDeliveryOwnNativePaymentAndReward(GameTestHelper h){
        var at=room(h);var p=player(h,at);light(h,p,at);var npc=boat(h,at);var first=NpcDialogue.session(p.getUUID());
        h.assertTrue(!NpcDialogue.choose(p,first.token(),"deliver")&&!npc.trade(p),"Unshown delivery and direct shift-trade cannot bypass actual TALK");
        h.assertTrue(choose(p,"talk")&&EquipmentBehaviors.saved(p).getBoolean(KEY+"_talked"),"Actual displayed nonce-protected TALK records the route");h.assertTrue(!NpcDialogue.choose(p,first.token(),"trade"),"Previous node token cannot replay");
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("cinnabar"),2));use(h,p,at);h.assertTrue(!choose(p,"deliver")&&p.getMainHandItem().getCount()==2&&!SecretTracker.ghostBoatClaimed(p),"Early delivery neither charges nor bypasses original time");ready(p);
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.REDSTONE));h.assertTrue(!choose(p,"deliver")&&!SecretTracker.ghostBoatClaimed(p),"Choice rechecks actual held item at execution");p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("cinnabar"),2));use(h,p,at);var delivery=NpcDialogue.session(p.getUUID());
        h.assertTrue(choose(p,"deliver")&&SecretTracker.ghostBoatClaimed(p)&&p.getMainHandItem().getCount()==1&&p.getInventory().countItem(ExpansionContent.item("bamboo_slip"))==1&&p.getInventory().countItem(ExpansionContent.item("copper_coin"))==2,"Original secret 17 pays exactly one cinnabar for one bamboo slip; original Site's two coins remain once");
        h.assertTrue(NpcDialogue.session(p.getUUID()).node().equals("done")&&!NpcDialogue.choose(p,delivery.token(),"deliver")&&!SmallInteractions.deliverGhostBoat(p,npc),"Successful delivery replaces nonce; native ledger prevents replay");
        var adv=p.server.getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","cod4_ghost_market_boat"));h.assertTrue(p.getAdvancements().getOrStartProgress(adv).isDone(),"Original COD4 task advancement is actually completed");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_ghost_boat",setupTicks=20)
    public static void nativeMerchantMenuKeepsActualCostsStockAndReloadIdentity(GameTestHelper h){
        var at=room(h);var p=player(h,at);light(h,p,at);h.assertTrue(choose(p,"talk")&&choose(p,"trade")&&p.containerMenu instanceof MerchantMenu,"Existing dialogue TRADE opens native MerchantMenu");var npc=boat(h,at);var menu=(MerchantMenu)p.containerMenu;
        var offer=npc.getOffers().stream().filter(o->o.getResult().is(ExpansionContent.item("tea"))).findFirst().orElseThrow();menu.setSelectionHint(npc.getOffers().indexOf(offer));menu.getSlot(0).set(new ItemStack(ExpansionContent.item("copper_coin"),7));h.assertTrue(menu.quickMoveStack(p,2).isEmpty()&&offer.getUses()==0,"Insufficient native payment yields no stock");menu.getSlot(0).set(new ItemStack(ExpansionContent.item("copper_coin"),8));
        h.assertTrue(!menu.quickMoveStack(p,2).isEmpty()&&menu.getSlot(0).getItem().isEmpty()&&offer.getUses()==1&&p.getInventory().countItem(ExpansionContent.item("tea"))==1,"Actual vanilla take consumes eight coins for original tea and increments native stock");h.assertTrue(menu.quickMoveStack(p,2).isEmpty(),"Empty repeated take cannot replay trade");p.closeContainer();npc.setTradingPlayer(null);
        var saved=npc.saveWithoutId(new CompoundTag());int size=npc.getOffers().size();npc.discard();var restored=NpcContent.NPCS.get("huang_laohan").get().create(h.getLevel());restored.load(saved);h.getLevel().addFreshEntity(restored);use(h,p,at);
        h.assertTrue(boat(h,at)==restored&&restored.getOffers().size()==size&&restored.getOffers().stream().anyMatch(o->o.getResult().is(ExpansionContent.item("tea"))&&o.getUses()==1),"Native entity NBT keeps same scene UUID, anchor, existing offers and used stock; reopening duplicates nothing");h.assertTrue(choose(p,"trade"),"Rejoined boat uses same merchant engine");
        h.getLevel().setBlockAndUpdate(at,Blocks.STONE.defaultBlockState());restored.tick();h.assertTrue(restored.getTradingPlayer()==null&&!p.containerMenu.stillValid(p),"Removed physical Site closes native trading authority");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_ghost_boat",setupTicks=20,timeoutTicks=260)
    public static void staleSceneForeignNonceDistanceAndTimeoutCannotDeliver(GameTestHelper h){
        var at=room(h);var p=player(h,at);light(h,p,at);choose(p,"talk");ready(p);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("cinnabar")));use(h,p,at);var session=NpcDialogue.session(p.getUUID());var q=player(h,at);
        h.assertTrue(!NpcDialogue.choose(q,session.token(),"deliver"),"Nonce belongs to original character");p.setPos(p.getX()+30,p.getY(),p.getZ());h.assertTrue(!NpcDialogue.choose(p,session.token(),"deliver")&&p.getMainHandItem().getCount()==1,"Remote delivery rejects before payment");p.setPos(Vec3.atBottomCenterOf(at));use(h,p,at);var removed=NpcDialogue.session(p.getUUID());h.getLevel().setBlockAndUpdate(at,Blocks.STONE.defaultBlockState());
        h.assertTrue(!NpcDialogue.choose(p,removed.token(),"deliver")&&!SecretTracker.get(h.getLevel()).claim(p,17,at),"Removed physical Site/old generic count cannot manufacture the secret");h.getLevel().setBlockAndUpdate(at,SmallInteractions.ENTRIES.get("ghost_market_boat").get().defaultBlockState());use(h,p,at);var current=NpcDialogue.session(p.getUUID());
        h.runAfterDelay(201,()->{h.assertTrue(!NpcDialogue.choose(p,current.token(),"deliver")&&p.getMainHandItem().getCount()==1&&!SecretTracker.ghostBoatClaimed(p),"Actual 200-tick nonce expiry rejects delivery without charge");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_ghost_boat",setupTicks=20)
    public static void originalRepeatableSecretCooldownIsRetainedWithoutReplayingSiteCoins(GameTestHelper h){
        var at=room(h);var p=player(h,at);light(h,p,at);choose(p,"talk");ready(p);
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("cinnabar"),3));use(h,p,at);h.assertTrue(choose(p,"deliver"),"First native repeatable secret delivery succeeds");
        h.assertTrue(!SecretDefinition.of(17).oneTime()&&SecretTracker.ghostBoatClaimed(p)&&!SmallInteractions.deliverGhostBoat(p,boat(h,at)),"Original secret 17 is repeatable, but its native one-day cooldown rejects early payment");
        String receipt=p.level().dimension().location()+":secret_17";p.getPersistentData().getCompound(net.minecraft.world.entity.player.Player.PERSISTED_NBT_TAG).putLong(receipt,h.getLevel().getGameTime()-24000);
        use(h,p,at);h.assertTrue(NpcDialogue.session(p.getUUID()).node().equals("asked")&&choose(p,"deliver"),"Reopening after original cooldown offers genuine paid delivery again");
        h.assertTrue(p.getMainHandItem().getCount()==1&&p.getInventory().countItem(ExpansionContent.item("bamboo_slip"))==2&&p.getInventory().countItem(ExpansionContent.item("copper_coin"))==2,"Two separately paid native repeatable rewards retain original behavior; one-time Site coins remain exactly two");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_ghost_boat",setupTicks=20)
    public static void paidLegacySiteEarnsOnlyMissingNativeSecretAndCloneKeepsClaim(GameTestHelper h){
        var at=room(h);var p=player(h,at);var root=EquipmentBehaviors.saved(p);root.putBoolean(KEY+"_done",true);root.putInt(KEY+"_count",1);root.putLong(KEY+"_start",h.getLevel().getGameTime()-2400);root.putLong(KEY+"_next",h.getLevel().getGameTime()+2400);
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("cinnabar"),2));use(h,p,at);h.assertTrue(choose(p,"talk")&&choose(p,"deliver"),"Old completed paid incense infers lighting but still requires actual TALK and missing cinnabar delivery, without obsolete second wait");
        h.assertTrue(p.getMainHandItem().getCount()==1&&p.getInventory().countItem(ExpansionContent.item("bamboo_slip"))==1&&p.getInventory().countItem(ExpansionContent.item("copper_coin"))==0,"Legacy coins are never repaid and only original missing secret reward is added");
        var clone=player(h,at,p.getGameProfile());SecretTracker.clone(new PlayerEvent.Clone(clone,p,true));clone.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("cinnabar")));use(h,clone,at);h.assertTrue(SecretTracker.ghostBoatClaimed(clone)&&NpcDialogue.session(clone.getUUID()).node().equals("done")&&!choose(clone,"deliver")&&clone.getMainHandItem().getCount()==1,"Original player-persisted native claim and Site history survive clone without reward replay");
        var other=player(h,at);use(h,other,at);h.assertTrue(!SecretTracker.ghostBoatClaimed(other)&&!EquipmentBehaviors.saved(other).getBoolean(KEY+"_incense_lit")&&NpcDialogue.session(other.getUUID())==null,"Another character inherits neither completion nor paid incense; real network multiplayer remains pending");h.succeed();
    }
}
