package com.dynasty.cod3;

import com.dynasty.block.DynastyPortalBlock;
import com.dynasty.expansion.ExpansionContent;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.*;
import net.minecraft.world.inventory.MerchantMenu;
import net.minecraft.world.item.*;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraftforge.gametest.*;
import java.util.UUID;

@GameTestHolder("dynasty_cod4")
@PrefixGameTestTemplate(false)
public final class NpcContentTradeGameTests {
    private static ServerPlayer player(ServerLevel level){
        var p=new ServerPlayer(level.getServer(),level,new GameProfile(UUID.randomUUID(),"npc-stock"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(level.getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setPos(0,120,0);return p;
    }
    private static MerchantOffer offer(DynastyNpcEntity npc,String result){return npc.getOffers().stream().filter(o->o.getResult().is(ExpansionContent.item(result))).findFirst().orElseThrow();}
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void dragonPalaceNativeShopChargesCoinsLimitsStockAndMigratesOldOffers(GameTestHelper h){
        var sea=h.getLevel().getServer().getLevel(DynastyPortalBlock.DRAGON_PALACE);h.assertTrue(sea!=null,"Real Dragon Palace server dimension exists");
        var npc=NpcContent.NPCS.get("huang_laohan").get().create(sea);npc.setNoAi(true);npc.setPos(0,120,0);
        var old=npc.saveWithoutId(new CompoundTag());h.assertTrue(npc.getOffers().stream().noneMatch(o->o.getResult().is(ExpansionContent.item("sea_pearl"))),"Old native offer list remains available before migration");
        var restored=NpcContent.NPCS.get("huang_laohan").get().create(sea);restored.load(old);restored.ensureContentTrades();
        int size=restored.getOffers().size();for(int i=0;i<20;i++)restored.ensureContentTrades();
        h.assertTrue(restored.getOffers().size()==size&&restored.getOffers().stream().filter(o->o.getResult().is(ExpansionContent.item("sea_pearl"))).count()==1,"Old saves receive exactly one pearl offer while retaining existing goods");
        var p=player(sea);h.assertTrue(restored.trade(p)&&p.containerMenu instanceof MerchantMenu,"Actual native merchant menu opens inside Dragon Palace");
        var menu=(MerchantMenu)p.containerMenu;var pearl=offer(restored,"sea_pearl");menu.setSelectionHint(restored.getOffers().indexOf(pearl));
        menu.getSlot(0).set(new ItemStack(ExpansionContent.item("copper_coin"),47));
        h.assertTrue(menu.getSlot(2).getItem().isEmpty()&&menu.quickMoveStack(p,2).isEmpty()&&pearl.getUses()==0,"Insufficient actual input yields no pearl and consumes no stock");
        for(int i=0;i<8;i++){
            menu.getSlot(0).set(new ItemStack(ExpansionContent.item("copper_coin"),48));
            h.assertTrue(!menu.quickMoveStack(p,2).isEmpty()&&menu.getSlot(0).getItem().isEmpty(),"One actual native trade charges exactly forty-eight copper coins");
            h.assertTrue(menu.quickMoveStack(p,2).isEmpty()&&pearl.getUses()==i+1,"Repeating take with no payment cannot replay a trade");
        }
        menu.getSlot(0).set(new ItemStack(ExpansionContent.item("copper_coin"),48));
        h.assertTrue(menu.quickMoveStack(p,2).isEmpty()&&menu.getSlot(0).getItem().getCount()==48&&p.getInventory().countItem(ExpansionContent.item("sea_pearl"))==8,"Eight-stock shop rejects ninth purchase without charging");
        var saved=restored.saveWithoutId(new CompoundTag());var reloaded=NpcContent.NPCS.get("huang_laohan").get().create(sea);reloaded.load(saved);reloaded.ensureContentTrades();
        h.assertTrue(offer(reloaded,"sea_pearl").getUses()==8&&reloaded.getOffers().size()==size,"Native persisted merchant stock survives reload and repeated migration");
        p.setPos(100,120,0);restored.tick();h.assertTrue(!menu.stillValid(p)&&restored.getTradingPlayer()==null,"Walking away closes native trading authority");p.closeContainer();h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void onlyExistingPalaceBoatTraderAddsSeaPearlAndMaterialsTradeForActualOutputs(GameTestHelper h){
        var land=NpcContent.NPCS.get("huang_laohan").get().create(h.getLevel());land.ensureContentTrades();
        h.assertTrue(land.getOffers().stream().noneMatch(o->o.getResult().is(ExpansionContent.item("sea_pearl"))),"Overworld boat traders do not sell palace-only pearl stock");
        var sea=h.getLevel().getServer().getLevel(DynastyPortalBlock.DRAGON_PALACE);var other=NpcContent.NPCS.get("ba_tu").get().create(sea);other.ensureContentTrades();
        h.assertTrue(other.getOffers().stream().noneMatch(o->o.getResult().is(ExpansionContent.item("sea_pearl"))),"Entering the realm does not turn every NPC into a pearl shop");
        for(String[] entry:new String[][]{{"baibao_jin","fox_pelt","copper_coin"},{"ba_tu","wolf_fang","copper_coin"},{"hei_po","python_gall","healing_salve"},{"hei_po","locust_dust","healing_salve"},{"huang_laohan","crab_shell","copper_coin"},{"huang_laohan","kappa_scale","copper_coin"}}){
            var npc=NpcContent.NPCS.get(entry[0]).get().create(h.getLevel());var legacy=npc.saveWithoutId(new CompoundTag());npc.load(legacy);npc.ensureContentTrades();
            var trade=npc.getOffers().stream().filter(o->o.getBaseCostA().is(ExpansionContent.item(entry[1]))&&o.getResult().is(ExpansionContent.item(entry[2]))).findFirst().orElseThrow();
            var paid=trade.getCostA().copy();h.assertTrue(trade.take(paid,ItemStack.EMPTY)&&paid.isEmpty(),"Actual native ingredient payment accepted: "+entry[1]);
            int size=npc.getOffers().size();npc.ensureContentTrades();h.assertTrue(npc.getOffers().size()==size&&trade.getResult().getCount()>0,"Material trade is useful and does not duplicate old-save offers: "+entry[1]);
        }
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void palaceAnchorCreatesOneActualExistingMerchantAndNeverReplaysAfterReload(GameTestHelper h){
        var sea=h.getLevel().getServer().getLevel(DynastyPortalBlock.DRAGON_PALACE);var pos=new BlockPos(2048,120,2048);sea.getChunkAt(pos);
        sea.setBlockAndUpdate(pos.above(),net.minecraft.world.level.block.Blocks.AIR.defaultBlockState());sea.setBlockAndUpdate(pos.above(2),net.minecraft.world.level.block.Blocks.AIR.defaultBlockState());
        sea.setBlockAndUpdate(pos,StoryAnchor.npcState("huang_laohan"));var anchor=(StoryAnchor.Anchor)sea.getBlockEntity(pos);anchor.onLoad();
        var uuid=UUID.nameUUIDFromBytes((sea.dimension().location()+":"+pos+":huang_laohan").getBytes(java.nio.charset.StandardCharsets.UTF_8));
        var entity=sea.getEntity(uuid);h.assertTrue(entity instanceof DynastyNpcEntity,"Real chunk-load anchor creates the existing registered merchant");var npc=(DynastyNpcEntity)entity;
        npc.setNoAi(true);npc.ensureContentTrades();h.assertTrue(offer(npc,"sea_pearl").getCostA().getCount()==48,"Actual naturally placed palace identity owns pearl stock");
        var data=anchor.saveWithoutMetadata();h.assertTrue(data.getBoolean("NpcSpawned"),"Successful spawn marks the existing persistent anchor");
        anchor.load(data);anchor.onLoad();h.assertTrue(sea.getEntity(uuid)==npc,"Reload and repeated chunk-load hook do not create duplicate merchant");
        npc.discard();sea.setBlockAndUpdate(pos,net.minecraft.world.level.block.Blocks.AIR.defaultBlockState());h.succeed();
    }
}
