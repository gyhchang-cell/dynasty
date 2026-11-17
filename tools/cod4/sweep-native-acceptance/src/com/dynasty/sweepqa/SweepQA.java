package com.dynasty.sweepqa;

import com.google.gson.GsonBuilder;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.storage.LevelResource;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import java.nio.file.*;
import java.util.*;

/** Private fixtures only after explicit operator command. No launch, world creation or cue generation. */
@Mod("dynastysweepqa")
@Mod.EventBusSubscriber(modid="dynastysweepqa")
public final class SweepQA {
 public static final Path OUT=Path.of(System.getProperty("dynasty.sweepqa.output", ".sweepqa-disabled"));
 static UUID actor; static String mode=""; static long armed;
 static final List<LivingEntity> targets=new ArrayList<>();
 public SweepQA(){if(!OUT.isAbsolute()||System.getProperty("dynasty.sweepqa.instance")==null||!Boolean.getBoolean("dynasty.sweepqa.enabled"))throw new IllegalStateException("Private sweep QA requires explicit opt-in");CaseLog.installArtifact(net.minecraftforge.fml.ModList.get().getModFileById("dynastysweepqa").getFile().getFilePath());}
 public static Path real(Path p){try{return p.toRealPath();}catch(java.io.IOException ex){throw new IllegalStateException(ex);}}
 public static synchronized void write(String name,Object data){try{Files.createDirectories(OUT);Files.writeString(OUT.resolve(name),new GsonBuilder().setPrettyPrinting().create().toJson(data));}catch(Exception ex){throw new IllegalStateException(ex);}}
 public static long cycle(){var s=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();return s==null?-1:s.getTickCount();}
 public static long actorTick(){var s=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();var p=s==null||actor==null?null:s.getPlayerList().getPlayer(actor);return p==null?-1:p.level().getGameTime();}
 public static Object entity(Entity e){if(e==null)return Map.of();var m=new LinkedHashMap<String,Object>();m.put("id",e.getId());m.put("uuid",e.getUUID().toString());m.put("dimension",e.level().dimension().location().toString());m.put("tick",e.level().getGameTime());m.put("alive",e.isAlive());m.put("invulnerable",e.isInvulnerable());m.put("removed",e.isRemoved());m.put("pos",Probe.v(e.position()));if(e instanceof LivingEntity l)m.put("health",l.getHealth());return m;}
 static boolean scoped(Entity e){return actor!=null&&targets.contains(e);}
 static void cleanup(){for(var t:targets)if(!t.isRemoved())t.discard();targets.clear();actor=null;mode="";Probe.SERVER.close();}
 @SubscribeEvent public static void commands(RegisterCommandsEvent e){
  e.getDispatcher().register(Commands.literal("sweepqa").requires(s->s.hasPermission(2))
   .then(Commands.literal("arm").then(Commands.argument("case",StringArgumentType.word()).then(Commands.argument("mode",StringArgumentType.word()).executes(c->{
    var p=c.getSource().getPlayerOrException();String name=StringArgumentType.getString(c,"case"),which=StringArgumentType.getString(c,"mode");
    if(!name.matches("[a-zA-Z0-9_-]{1,70}")||!Set.of("success","cancel-attack","cancel-damage","invulnerable").contains(which))throw new IllegalArgumentException("case or mode");
    var instance=real(Path.of(Objects.requireNonNull(System.getProperty("dynasty.sweepqa.instance"))));
    if(!real(p.server.getWorldPath(LevelResource.ROOT)).startsWith(instance))throw new IllegalStateException("Not the explicitly selected private world");
    if(Files.exists(OUT.resolve(name+"-fixture.json")))throw new IllegalStateException("Case already exists; choose a new case ID");
    if(!Probe.SERVER.current().isEmpty())throw new IllegalStateException("Dump/clear existing server case first");
    cleanup();actor=p.getUUID();mode=which;armed=p.level().getGameTime();Probe.SERVER.begin(name,UUID.randomUUID().toString(),which);
    var weapon=Objects.requireNonNull(ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty:halberd_fangtian")));
    p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(weapon));
    // No player health, armor, skills, cooldown, world time or damage coefficient mutation.
    Vec3 forward=p.getLookAngle().multiply(1,0,1).normalize(),side=new Vec3(-forward.z,0,forward.x);
    for(int i=0;i<2;i++){var cow=EntityType.COW.create(p.serverLevel());if(cow==null)throw new IllegalStateException("cow");cow.setNoAi(true);cow.setPersistenceRequired();cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000000);cow.setHealth(cow.getMaxHealth());cow.setInvulnerable(which.equals("invulnerable"));cow.setPos(p.position().add(forward.scale(2.1)).add(side.scale(i==0?0:1.1)));if(!p.serverLevel().addFreshEntity(cow))throw new IllegalStateException("spawn failed");targets.add(cow);}
    var fixture=Map.of("case",name,"mode",mode,"actor",entity(p),"identity",Probe.SERVER.stamp(),"targets",targets.stream().map(SweepQA::entity).toList());write(name+"-fixture.json",fixture);Probe.SERVER.event("fixture-ready",fixture);
    c.getSource().sendSuccess(()->Component.literal("sweepqa target="+targets.get(0).getId()+"; wait for full native cooldown then /sweepqa-client "+name+" "+targets.get(0).getId()+" first (or third)"),false);return 1;
   }))))
   .then(Commands.literal("dump").executes(c->{if(!Probe.SERVER.current().isEmpty()){Probe.SERVER.event("server-final-targets",targets.stream().map(SweepQA::entity).toList());write(Probe.SERVER.current()+"-server-events.json",Probe.SERVER.snapshot());}return 1;}))
   .then(Commands.literal("clear").executes(c->{if(!Probe.SERVER.current().isEmpty()){Probe.SERVER.event("server-final-targets",targets.stream().map(SweepQA::entity).toList());write(Probe.SERVER.current()+"-server-events.json",Probe.SERVER.snapshot());}cleanup();Probe.SERVER.close();return 1;})));
 }
 @SubscribeEvent(priority=EventPriority.HIGHEST) public static void cancelAttack(AttackEntityEvent e){if(!e.getEntity().level().isClientSide&&Objects.equals(actor,e.getEntity().getUUID())&&scoped(e.getTarget())&&mode.equals("cancel-attack"))e.setCanceled(true);}
 @SubscribeEvent(priority=EventPriority.LOWEST,receiveCanceled=true) public static void attack(AttackEntityEvent e){if(!e.getEntity().level().isClientSide&&Objects.equals(actor,e.getEntity().getUUID()))Probe.SERVER.event("server-native-attack",Map.of("actor",entity(e.getEntity()),"target",entity(e.getTarget()),"cancelled",e.isCanceled(),"cycle",e.getEntity().getServer().getTickCount()));}
 @SubscribeEvent(priority=EventPriority.HIGHEST) public static void cancelDamage(LivingDamageEvent e){if(!e.getEntity().level().isClientSide&&scoped(e.getEntity())&&mode.equals("cancel-damage")&&Objects.equals(actor,e.getSource().getEntity()==null?null:e.getSource().getEntity().getUUID()))e.setCanceled(true);}
 @SubscribeEvent(priority=EventPriority.LOWEST,receiveCanceled=true) public static void damage(LivingDamageEvent e){if(!e.getEntity().level().isClientSide&&scoped(e.getEntity()))Probe.SERVER.event("server-damage-event-not-final-hp",Map.of("target",entity(e.getEntity()),"amount",e.getAmount(),"source",e.getSource().getMsgId(),"direct",entity(e.getSource().getDirectEntity()),"owner",entity(e.getSource().getEntity()),"cancelled",e.isCanceled()));}
 @SubscribeEvent public static void timeout(TickEvent.ServerTickEvent e){if(e.phase!=TickEvent.Phase.END||actor==null)return;var s=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();if(s==null)return;var p=s.getPlayerList().getPlayer(actor);if(p==null||p.level().getGameTime()-armed>600){if(!Probe.SERVER.current().isEmpty())write(Probe.SERVER.current()+"-timeout-server-events.json",Probe.SERVER.snapshot());cleanup();Probe.SERVER.close();}}
}
