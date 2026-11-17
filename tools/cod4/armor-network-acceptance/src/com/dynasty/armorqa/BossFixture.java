package com.dynasty.armorqa;
import com.dynasty.ritual.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.block.Blocks;
import java.util.Map;
import static com.dynasty.armorqa.ArmorNetworkQa.*;

/** QA encounter ledger and plain collision platform; original 280-tick intro/gate still runs. */
final class BossFixture {
 static ZhenyuanRitualSavedData.Session session;
 @SuppressWarnings("unchecked") static Map<String,ZhenyuanRitualSavedData.Session> ledger()throws Exception{var d=ZhenyuanRitualSavedData.get(server.overworld());var f=d.getClass().getDeclaredField("sessions");f.setAccessible(true);return (Map<String,ZhenyuanRitualSavedData.Session>)f.get(d);}
 static void travel(ServerPlayer p,net.minecraft.server.level.ServerLevel level,BlockPos pos)throws Exception{var m=ZhenyuanRitualService.class.getDeclaredMethod("teleport",ServerPlayer.class,net.minecraft.server.level.ServerLevel.class,BlockPos.class,float.class);m.setAccessible(true);require((Boolean)m.invoke(null,p,level,pos,0F),"QA authorized native cross-dimension travel");}
 static void cleanup()throws Exception{if(session==null)return;session.phase="paused";for(var p:players(server))travel(p,server.overworld(),new BlockPos(p==players(server).get(0)?4:0,-60,0));ledger().remove(session.key);session=null;}
 static void setup(ServerPlayer peer)throws Exception{
  target.discard();var arena=server.getLevel(ZhenyuanArena.DIMENSION);require(arena!=null,"existing arena dimension");
  for(int x=-5;x<=5;x++)for(int z=-5;z<=5;z++)arena.setBlockAndUpdate(new BlockPos(x,64,z),Blocks.STONE.defaultBlockState());
  net.minecraft.world.entity.LivingEntity boss=ZhenyuanBosses.FINAL_BOSS.get().create(arena);require(boss!=null,"original sovereign type");boss.moveTo(.5,65,2.5,180,0);boss.getAttribute(Attributes.MAX_HEALTH).setBaseValue(100000);boss.setHealth(100000);boss.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(0);boss.getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(0);
  session=new ZhenyuanRitualSavedData.Session("minecraft:overworld",new BlockPos(500,-60,500));session.owner=peer.getUUID();for(var p:players(server))session.participants.add(p.getUUID());session.boss=boss.getUUID();session.phase="active";session.arenaIndex=0;session.arenaReady=true;session.removed=true;session.bossIntroTick=0;
  ledger().put(session.key,session);arena.addFreshEntity(boss);for(var p:players(server))travel(p,arena,new BlockPos(p==peer?0:4,65,0));target=boss;
  write("command.json",Map.of("case",active,"set",set(active),"pieces",count(active),"target",target.getUUID().toString(),"peer",peer.getUUID().toString()));
  event("native-boss-intro-start",peer,Map.of("introTick",session.bossIntroTick,"fixture","QA ledger and plain stone platform, HP/damage/movement attributes supplied; original native intro and hurt gate; not ritual acquisition or whole AI battle"));
 }
}
