package com.dynasty.armorqa;

import com.dynasty.expansion.*;
import com.google.gson.*;
import net.minecraft.client.Minecraft;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.client.event.ClientChatReceivedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;
import static com.dynasty.armorqa.ArmorNetworkQa.*;

/** Natural site real-client entry and timed continuation; never modifies production progression clocks. */
public final class InteractionNetworkQa {
    static final JsonArray SITES=JsonParser.parseReader(new InputStreamReader(Objects.requireNonNull(InteractionNetworkQa.class.getResourceAsStream("/qa-interaction-sites.json")),StandardCharsets.UTF_8)).getAsJsonArray();
    static int current=-1,sequence=-1,ticks,localCase=-1,localTicks;
    static boolean finished;
    static String phase="entry";
    static boolean sent,captured;
    static BlockPos activeBlock;
    static String observerBefore,observerStacksBefore;
    static Map<String,Integer> observerInventoryBefore;
    static final List<Map<String,Object>> rows=new ArrayList<>(),messages=new ArrayList<>();
    static BlockPos pos(String value){String[] a=value.split(",\\s*");return new BlockPos(Integer.parseInt(a[0]),Integer.parseInt(a[1]),Integer.parseInt(a[2]));}
    static String privateState(ServerPlayer player){
        var out=new CompoundTag();var root=EquipmentBehaviors.saved(player);
        for(String k:root.getAllKeys())if(k.startsWith("site_")||k.equals("cod4Battlefields"))out.put(k,Objects.requireNonNull(root.get(k)).copy());
        for(String k:player.getPersistentData().getAllKeys())if(Set.of("cod3_progress_8","cod3_progress_17","cod3_progress_19","cod3_progress_28","cod3_progress_29","cod3_progress_30").contains(k))out.put(k,Objects.requireNonNull(player.getPersistentData().get(k)).copy());
        return out.toString();
    }
    static ItemStack offering(String id){return switch(id){
        case "wayside_shrine","ghost_market_boat"->item("soul_incense").copyWithCount(2);
        case "nameless_tomb"->new ItemStack(Items.POPPY,2);
        case "broken_stele"->new ItemStack(Items.PAPER,2);
        case "broken_waterwheel"->item("qimen_cable").copyWithCount(2);
        case "old_bellows"->new ItemStack(Items.CHARCOAL,2);
        case "ancient_well"->new ItemStack(Items.WATER_BUCKET);
        case "sword_scar_wall"->new ItemStack(Items.IRON_SWORD);
        default->ItemStack.EMPTY;
    };}
    static void prepare(int n)throws Exception {prepare(n,"entry");}
    static void prepare(int n,String nextPhase)throws Exception {
        current=n;sequence++;phase=nextPhase;ticks=0;var site=TimedInteractionWorkflow.site(n,nextPhase);var at=pos(site.get("pos").getAsString());var approach=pos(site.get("approach").getAsString());
        if(site.get("id").getAsString().equals("sword_scar_wall"))approach=approach.east(2);
        var level=server.overworld();level.getChunk(at.getX()>>4,at.getZ()>>4);
        activeBlock=at;String id=site.get("id").getAsString();require(level.getBlockState(at).is(SmallInteractions.ENTRIES.get(id).get()),"Native generator must reproduce existing site "+id);
        var ps=players(server);var observer=ps.get(nextPhase.equals("observer_ack")?1:0);var actor=ps.get(nextPhase.equals("observer_ack")?0:1);
        observer.teleportTo(level,approach.getX()+2.5,approach.getY(),approach.getZ()+3.5,180,0);
        actor.teleportTo(level,approach.getX()+.5,approach.getY(),approach.getZ()+.5,180,0);
        ItemStack supplied=nextPhase.equals("complete")&&id.equals("ghost_market_boat")?item("cinnabar"):offering(id);
        if(nextPhase.equals("complete")&&id.equals("mortuary_room"))supplied=net.minecraft.world.item.alchemy.PotionUtils.setPotion(new ItemStack(Items.POTION),net.minecraft.world.item.alchemy.Potions.HEALING);
        actor.getInventory().setItem(0,supplied);
        if(nextPhase.equals("complete")&&id.equals("old_bellows"))TimedInteractionWorkflow.supplyNaturalFurnace(at);actor.getInventory().selected=0;actor.inventoryMenu.broadcastChanges();
        observerStacksBefore=TimedInteractionWorkflow.inventorySnapshot(observer);observerBefore=privateState(observer);observerInventoryBefore=TimedInteractionWorkflow.inventory(observer);
        write("interaction-command.json",obj("case",sequence,"siteIndex",n,"phase",phase,"actingRole",nextPhase.equals("observer_ack")?"host":"peer","yaw",TimedInteractionWorkflow.yaw(id,nextPhase,actor),"sneak",TimedInteractionWorkflow.sneak(id,nextPhase,actor),"id",id,"pos",site.get("pos").getAsString(),"approach",approach.toShortString(),"held",ForgeRegistries.ITEMS.getKey(actor.getMainHandItem().getItem()).toString(),"actorBefore",privateState(actor),"actorInventoryBefore",TimedInteractionWorkflow.inventory(actor),"actorStacksBefore",TimedInteractionWorkflow.inventorySnapshot(actor),"observerBefore",observerBefore,"tick",level.getGameTime()));

    }
    static void client(Minecraft m)throws Exception {
        if(!has("interaction-command.json"))return;
        var command=JsonParser.parseString(Files.readString(OUT.resolve("interaction-command.json"))).getAsJsonObject();int n=command.get("case").getAsInt();
        if(n!=localCase){localCase=n;localTicks=0;sent=false;captured=false;messages.clear();NativeDialogueClientDriver.reset(n,command.get("phase").getAsString().equals("repeat")?"":command.get("id").getAsString());m.player.closeContainer();m.setScreen(null);}
        localTicks++;
        boolean acting=ROLE.equals(command.get("actingRole").getAsString());
        if(acting&&!sent){
            if(!has(ROLE+"-teleport-seen-"+n))return;
            var at=pos(command.get("pos").getAsString());var approach=pos(command.get("approach").getAsString());
            if(!m.level.hasChunkAt(at)||!m.level.getBlockState(at).is(SmallInteractions.ENTRIES.get(command.get("id").getAsString()).get()))return;
            if(m.player.distanceToSqr(Vec3.atBottomCenterOf(approach))>3)return;
            if(!ForgeRegistries.ITEMS.getKey(m.player.getMainHandItem().getItem()).toString().equals(command.get("held").getAsString()))return;
            float yaw=command.get("yaw").getAsFloat();boolean sneak=command.get("sneak").getAsBoolean();
            m.player.setYRot(yaw);m.player.setXRot(35);m.options.keyShift.setDown(sneak);m.player.setShiftKeyDown(sneak);
            // Send normal native input packets before the block-use packet, in the same TCP order.
            m.player.connection.send(new net.minecraft.network.protocol.game.ServerboundPlayerCommandPacket(m.player,sneak?net.minecraft.network.protocol.game.ServerboundPlayerCommandPacket.Action.PRESS_SHIFT_KEY:net.minecraft.network.protocol.game.ServerboundPlayerCommandPacket.Action.RELEASE_SHIFT_KEY));
            m.player.connection.send(new net.minecraft.network.protocol.game.ServerboundMovePlayerPacket.Rot(yaw,35,m.player.onGround()));
            var result=m.gameMode.useItemOn(m.player,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(at),Direction.SOUTH,at,false));
            write("native-use-"+n+".json",obj("result",result.toString(),"player",m.player.getUUID().toString(),"site",command.get("id").getAsString(),"clientPos",m.player.position().toString(),"packetPath","MultiPlayerGameMode.useItemOn native client C2S"));
            sent=true;localTicks=0;
        }
        if(acting&&sent&&!NativeDialogueClientDriver.drive(m,command.get("phase").getAsString().equals("complete")))return;
        if(acting&&sent&&command.get("id").getAsString().equals("sword_scar_wall")&&command.get("phase").getAsString().equals("complete")&&!NativeSwordDanceDriver.drive(m,n))return;
        if(acting&&sent&&localTicks>=15)mark("action-finished-"+n);
        if(!captured&&has("action-finished-"+n)&&localTicks>=15&&draw){
            var screen=m.screen;var widgets=new ArrayList<String>();
            if(screen!=null)for(var child:screen.children())if(child instanceof net.minecraft.client.gui.components.AbstractWidget w)widgets.add(w.getMessage().getString());
            write(ROLE+"-interaction-frame-"+n+".json",obj("captureEvent","AFTER_LEVEL real rendered client","case",n,"site",command.get("id").getAsString(),"screen",screen==null?"null":screen.getClass().getName(),"screenTitle",screen==null?"":screen.getTitle().getString(),"widgetMessages",widgets,"receivedResolvedMessages",List.copyOf(messages),"localPlayer",m.player.getUUID().toString(),"language",m.options.languageCode));
            try(var image=net.minecraft.client.Screenshot.takeScreenshot(m.getMainRenderTarget())){image.writeToFile(OUT.resolve(ROLE+"-interaction-frame-"+n+".png"));}
            captured=true;mark(ROLE+"-interaction-ack-"+n);
        }
    }
    @SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.HIGHEST) public static void nativeUse(net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickBlock event){
        if(event.getLevel().isClientSide()||server==null||current<0||current>=15||players(server).size()!=2||event.getEntity()!=players(server).get(phase.equals("observer_ack")?0:1))return;
        if(!event.getPos().equals(activeBlock))return;
        var observer=players(server).get(phase.equals("observer_ack")?1:0);observerStacksBefore=TimedInteractionWorkflow.inventorySnapshot(observer);observerBefore=privateState(observer);observerInventoryBefore=TimedInteractionWorkflow.inventory(observer);
        try{write("server-native-use-"+sequence+".json",obj("player",event.getEntity().getUUID().toString(),"block",event.getPos().toShortString(),"worldTick",event.getLevel().getGameTime(),"facing",event.getEntity().getDirection().getName(),"sneaking",event.getEntity().isShiftKeyDown(),"onGround",event.getEntity().onGround(),"observerBeforeNativeBlockUse",observerBefore,"observerInventoryBefore",observerInventoryBefore,"observerStacksBefore",observerStacksBefore,"event","Actual server PlayerInteractEvent.RightClickBlock"));}catch(Exception x){throw new RuntimeException(x);}
    }
    @SubscribeEvent public static void chat(ClientChatReceivedEvent.System event){
        String text=event.getMessage().getString();
        if(text.matches("\\[COD4_QA_TELEPORT_[0-9]+\\]")){
            String seq=text.substring("[COD4_QA_TELEPORT_".length(),text.length()-1);
            try{mark(ROLE+"-teleport-seen-"+seq);}catch(Exception x){throw new RuntimeException(x);}return;
        }
        if(localCase<0)return;
        NativeDialogueClientDriver.received(event.getMessage());
        messages.add(obj("resolved",event.getMessage().getString(),"component",net.minecraft.network.chat.Component.Serializer.toJson(event.getMessage()),"overlay",event.isOverlay()));
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event){
        if(!"interaction".equals(System.getProperty("dynasty.armorqa.suite"))||!HOST||event.phase!=TickEvent.Phase.END||server==null||players(server).size()!=2||!has("peer-world-ready")||finished)return;
        try{
            if(current<0){var ps=players(server);require(ps.get(1).connection.connection.getRemoteAddress() instanceof java.net.InetSocketAddress,"Require actual TCP peer");write("connections.json",ps.stream().map(p->obj("name",p.getGameProfile().getName(),"uuid",p.getUUID().toString(),"remote",p.connection.connection.getRemoteAddress().toString())).toList());for(var p:ps)reset(p);server.overworld().setDayTime(18000);prepare(0);return;}
            if(TimedInteractionWorkflow.waiting){TimedInteractionWorkflow.schedule();return;}
            if(phase.equals("complete")&&SITES.get(current).getAsJsonObject().get("id").getAsString().equals("sword_scar_wall"))NativeSwordDanceDriver.observe();
            ticks++;
            if(ticks==3){
                // A teleport can be acknowledged within the same server tick, when firstGoodX/Y/Z
                // still describe the old location. Native PosRot may then create a corrective teleport.
                // Wait through subsequent native connection ticks before publishing client readiness;
                // any corrective teleport is earlier than this marker on the same outgoing stream.
                for(var player:players(server))player.sendSystemMessage(net.minecraft.network.chat.Component.literal("[COD4_QA_TELEPORT_"+sequence+"]"));
            }
            if(ticks>(phase.equals("complete")&&current==7?3000:500))throw new AssertionError("Bounded natural interaction command stalled "+sequence+" site="+current+" phase="+phase);
            if(has("host-interaction-ack-"+sequence)&&has("peer-interaction-ack-"+sequence)){
                var ps=players(server);var actor=ps.get(phase.equals("observer_ack")?0:1);var observer=ps.get(phase.equals("observer_ack")?1:0);var command=JsonParser.parseString(Files.readString(OUT.resolve("interaction-command.json"))).getAsJsonObject();
                require(has("server-native-use-"+sequence+".json"),"Actual server-native block-use event required");
                require(observerBefore.equals(privateState(observer)),"Actor use must not write observer private progress");
                require(observerStacksBefore.equals(TimedInteractionWorkflow.inventorySnapshot(observer)),"Actor use must preserve observer equipment/offhand/Curios and complete item data");
                require(observerInventoryBefore.equals(TimedInteractionWorkflow.inventory(observer)),"Actor use must not give observer rewards or charge observer items");
                rows.add(obj("case",sequence,"siteIndex",current,"phase",phase,"id",command.get("id").getAsString(),"observerPrivateUnchanged",true,"observerPrivateBefore",observerBefore,"observerPrivateAfter",privateState(observer),"observerStacksBefore",observerStacksBefore,"observerStacksAfter",TimedInteractionWorkflow.inventorySnapshot(observer),"actorBefore",command.get("actorBefore").getAsString(),"actorAfter",privateState(actor),"actorInventoryBefore",command.getAsJsonObject("actorInventoryBefore"),"actorInventoryAfter",TimedInteractionWorkflow.inventory(actor),"observerInventoryUnchanged",true,"observerFullStacksUnchanged",true,"actorStacksBefore",command.get("actorStacksBefore").getAsString(),"actorStacksAfter",TimedInteractionWorkflow.inventorySnapshot(actor),"nativeWorldTick",server.overworld().getGameTime()));write("interaction-results.json",rows);
                if(phase.equals("entry")){
                    TimedInteractionWorkflow.assertEntry(command,ps.get(1));
                    if(current<14){prepare(current+1);return;}
                    TimedInteractionWorkflow.begin();return;
                }
                TimedInteractionWorkflow.accept(command,actor);
            }
        }catch(Throwable x){try{Files.writeString(OUT.resolve("fatal.txt"),x.toString());}catch(Exception ignored){}finished=true;}
    }
}
