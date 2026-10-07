package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.Combatant;
import com.dynasty.blueprint.combat.Faction;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.entity.living.MobSpawnEvent;
import net.minecraftforge.eventbus.api.Event;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;

/** Extra conditions and bounded idle ecology, never a replacement world spawn loop. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class EcologyManager {
    private static final String FACTION="DynastyEcologyFaction";
    private static final UUID CHARGE=UUID.fromString("7e3325ef-d01c-47af-8549-e4bdc09152aa");
    private static final UUID DARK=UUID.fromString("703fbe19-c15d-4345-b7fc-e4e47324906f");
    private static final Map<TemplateMob,Cache> CACHE=new WeakHashMap<>();
    private record Cache(long until,BlockPos pos,EcologyRule rule){}
    public static boolean dimensionMatches(ServerLevel level,EcologyRule rule){
        return level.dimensionTypeRegistration().is(TagKey.create(Registries.DIMENSION_TYPE,rule.dimensionTag()));
    }
    public static boolean regionMatches(ServerLevel level,BlockPos pos,EcologyRule rule){
        return dimensionMatches(level,rule)&&pos.getY()>=rule.minY()&&pos.getY()<=rule.maxY()
                &&level.hasChunkAt(pos)&&(rule.biomeTag()==null||level.getBiome(pos).is(TagKey.create(Registries.BIOME,rule.biomeTag())))
                &&LoadedStructureRegions.contains(level,pos,rule.structureTag(),rule.structureRadius());
    }
    public static boolean conditions(ServerLevel level,BlockPos pos,EcologyRule rule){
        long time=Math.floorMod(level.getDayTime(),24000L);
        boolean clock=switch(rule.timeWindow()){case ALL->true;case NIGHT->time>=13000&&time<=23000;
            case DUSK->time>=11500&&time<=13500;case OUTSIDE_NOON->time<5000||time>7000;};
        return clock&&level.getMaxLocalRawBrightness(pos)<=rule.maxLight()
                &&switch(rule.weather()){case ANY->true;case RAIN->level.isRaining();case THUNDER->level.isThundering();}
                &&(!rule.nearWater()||connectedWater(level,pos));
    }
    /** Local 7x7x3 loaded water check, requiring connected water in at least nine columns. */
    public static boolean connectedWater(ServerLevel level,BlockPos pos){
        var wet=new HashSet<BlockPos>();
        for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)for(int y=-1;y<=1;y++){
            var p=pos.offset(x,y,z);if(level.hasChunkAt(p)&&level.getFluidState(p).is(net.minecraft.tags.FluidTags.WATER))wet.add(p);
        }
        while(!wet.isEmpty()){
            var queue=new ArrayDeque<BlockPos>();var p=wet.iterator().next();queue.add(p);wet.remove(p);int count=0;var columns=new HashSet<Long>();
            while(!queue.isEmpty()){
                var q=queue.remove();count++;columns.add(BlockPos.asLong(q.getX(),0,q.getZ()));
                if(count>=12&&columns.size()>=9)return true;
                for(var direction:net.minecraft.core.Direction.values())if(wet.remove(q.relative(direction)))queue.add(q.relative(direction));
            }
        }
        return false;
    }
    public static Faction faction(TemplateMob mob,Faction defaultFaction){
        String value=mob.getPersistentData().getString(FACTION);
        // Only encounter-authored allegiance is accepted. Global species allegiance stays with cod1.
        return value.equals("REBELS")?Faction.REBELS:value.equals("DYNASTY_ARMY")?Faction.DYNASTY_ARMY:value.equals("SPIRITS")?Faction.SPIRITS:defaultFaction;
    }
    public static void assignBattlefield(TemplateMob mob){
        mob.getPersistentData().putString(FACTION,switch(mob.kind()){case POWDER,SCOUT,AXE_GUARD->"REBELS";default->"DYNASTY_ARMY";});
    }
    public static void assignFaction(TemplateMob mob,Faction faction){
        if(faction!=Faction.REBELS&&faction!=Faction.DYNASTY_ARMY&&faction!=Faction.SPIRITS)throw new IllegalArgumentException("Unsupported authored allegiance");
        mob.getPersistentData().putString(FACTION,faction.name());
    }
    private static EcologyRule region(TemplateMob mob,ServerLevel level){
        var old=CACHE.get(mob);long now=level.getGameTime();var pos=mob.blockPosition();
        if(old!=null&&old.until()>now&&old.pos().distSqr(pos)<64)return old.rule();
        var type=ForgeRegistries.ENTITY_TYPES.getKey(mob.getType());EcologyRule result=null;
        for(var rule:EcologyRules.ALL)if(rule.members().stream().anyMatch(m->m.mobType().equals(type))&&regionMatches(level,pos,rule)){result=rule;break;}
        CACHE.put(mob,new Cache(now+40,pos,result));return result;
    }
    /** Called before advancing any server damage frame. NoAI test/operator actions remain independent. */
    public static boolean pauseCombat(TemplateMob mob){
        if(mob.isNoAi()||!(mob.level() instanceof ServerLevel level))return false;
        var rule=region(mob,level);if(rule==null)return false;
        long time=Math.floorMod(level.getDayTime(),24000L);
        boolean howl=rule.id().getPath().equals("deep_forest")&&mob.kind()==TemplateMob.Kind.BEAST&&time>=17800&&time<=18200;
        if(howl&&time>=18000)howlTowardLoadedPeak(mob,level);
        return howl
                ||rule.id().getPath().equals("ruined_village")&&level.isDay()
                ||rule.id().getPath().equals("toxic_miao")&&time>=5000&&time<=7000;
    }
    public static void tickIdle(TemplateMob mob){
        if(mob.isNoAi()||!mob.isAlive()||!(mob.level() instanceof ServerLevel level)
                ||Math.floorMod(level.getGameTime()+mob.getUUID().hashCode(),32)!=0)return;
        var rule=region(mob,level);
        modifier(mob,Attributes.MOVEMENT_SPEED,CHARGE,"Tomb thunder charge",rule!=null&&rule.id().getPath().equals("underground_tomb")
                &&mob.faction()==Faction.CONSTRUCT&&level.isThundering(),.3);
        modifier(mob,Attributes.FOLLOW_RANGE,DARK,"Cave dark perception",rule!=null&&rule.id().getPath().equals("cave_rift")
                &&level.getMaxLocalRawBrightness(mob.blockPosition())==0,1);
        if(rule==null||pauseCombat(mob)||mob.getTarget() instanceof Player||mob.attack().current()!=null)return;
        if(mob.getTarget()!=null&&mob.getTarget().isAlive())return;
        if(rule.id().getPath().equals("deep_forest")){
            if(mob.kind()==TemplateMob.Kind.TREE&&mob.treeAwake()&&level.random.nextInt(level.isRaining()?4:8)==0){mob.setTreeAwake(false);mob.getNavigation().stop();}
            if(mob.kind()==TemplateMob.Kind.TOAD&&level.isRaining())migrateToMud(mob,level);
        }
        var candidates=level.getEntitiesOfClass(LivingEntity.class,mob.getBoundingBox().inflate(12),e->e!=mob&&e.isAlive()
                &&!(e instanceof Player)&&!e.isSpectator()&&mob.hasLineOfSight(e)
                &&(EcologyRules.predates(mob,e)||enemyFaction(mob,e,rule)));
        candidates.stream().min(Comparator.comparingDouble(mob::distanceToSqr)).ifPresent(mob::setTarget);
    }
    private static void howlTowardLoadedPeak(TemplateMob mob,ServerLevel level){
        long day=Math.floorDiv(level.getDayTime(),24000L);var data=mob.getPersistentData();
        if(data.contains("DynastyEcologyHowlDay")&&data.getLong("DynastyEcologyHowlDay")==day)return;
        data.putLong("DynastyEcologyHowlDay",day);var peak=mob.blockPosition();
        // Sixteen loaded heightmap samples, once per night; no claim of a global world maximum.
        for(int dx:new int[]{-48,-16,16,48})for(int dz:new int[]{-48,-16,16,48}){
            int x=mob.getBlockX()+dx,z=mob.getBlockZ()+dz;var chunk=level.getChunkSource().getChunkNow(x>>4,z>>4);if(chunk==null)continue;
            int y=chunk.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,x&15,z&15);
            if(y>peak.getY())peak=new BlockPos(x,y,z);
        }
        float yaw=(float)(Math.atan2(peak.getZ()-mob.getZ(),peak.getX()-mob.getX())*180/Math.PI)-90;
        mob.setYRot(yaw);mob.yHeadRot=yaw;mob.yBodyRot=yaw;
        mob.playSound(net.minecraft.sounds.SoundEvents.WOLF_HOWL,.8F,.8F);
    }
    private static void migrateToMud(TemplateMob mob,ServerLevel level){
        if(!mob.getNavigation().isDone())return;int cellX=Math.floorDiv(mob.getBlockX(),32)*32+16,cellZ=Math.floorDiv(mob.getBlockZ(),32)*32+16;
        var random=net.minecraft.util.RandomSource.create(level.getSeed()^BlockPos.asLong(cellX,0,cellZ)^Math.floorDiv(level.getDayTime(),24000));
        for(int n=0;n<8;n++){
            int x=cellX+random.nextInt(25)-12,z=cellZ+random.nextInt(25)-12;if(level.getChunkSource().getChunkNow(x>>4,z>>4)==null)continue;
            for(int dy=-3;dy<=3;dy++){
                var p=new BlockPos(x,mob.getBlockY()+dy,z);var soil=level.getBlockState(p.below());
                if((soil.is(net.minecraft.world.level.block.Blocks.MUD)||soil.is(net.minecraft.world.level.block.Blocks.CLAY))&&connectedWater(level,p)){
                    mob.getNavigation().moveTo(x+.5,p.getY(),z+.5,.65);return;
                }
            }
        }
    }
    private static boolean enemyFaction(TemplateMob mob,LivingEntity target,EcologyRule rule){
        if(!(target instanceof Combatant enemy)||Combatant.allied(mob,target))return false;
        return switch(rule.id().getPath()){
            case "ancient_battlefield"->(mob.faction()==Faction.DYNASTY_ARMY&&enemy.faction()==Faction.REBELS)
                    ||(mob.faction()==Faction.REBELS&&enemy.faction()==Faction.DYNASTY_ARMY);
            case "underground_tomb"->(mob.faction()==Faction.CONSTRUCT&&enemy.faction()==Faction.SPIRITS)
                    ||(mob.faction()==Faction.SPIRITS&&enemy.faction()==Faction.CONSTRUCT);
            case "deep_forest"->mob.faction()==Faction.WOODLAND&&rule.hostileFactions().contains(enemy.faction());
            default->false;
        };
    }
    private static void modifier(TemplateMob mob,net.minecraft.world.entity.ai.attributes.Attribute attribute,UUID id,String name,boolean enable,double amount){
        var value=mob.getAttribute(attribute);if(value==null)return;
        if(enable&&!value.hasModifier(new AttributeModifier(id,name,amount,AttributeModifier.Operation.MULTIPLY_TOTAL)))
            value.addTransientModifier(new AttributeModifier(id,name,amount,AttributeModifier.Operation.MULTIPLY_TOTAL));
        else if(!enable&&value.getModifier(id)!=null)value.removeModifier(id);
    }
    public static boolean capAllows(ServerLevel level,BlockPos pos,EcologyRule rule,EcologyRule.Member member){
        var nearby=level.getEntitiesOfClass(net.minecraft.world.entity.Mob.class,new net.minecraft.world.phys.AABB(pos).inflate(32),LivingEntity::isAlive);
        int same=0,ordinary=0,flying=0,elite=0;
        for(var mob:nearby){var id=ForgeRegistries.ENTITY_TYPES.getKey(mob.getType());
            var entry=rule.members().stream().filter(m->m.mobType().equals(id)).findFirst();if(entry.isEmpty())continue;
            if(member.mobType().equals(id))same++;
            if(entry.get().elite())elite++;else if(entry.get().flying())flying++;else ordinary++;
        }
        return same<member.localCap()&&(member.elite()?elite<rule.caps().elite():member.flying()?flying<rule.caps().flying():ordinary<rule.caps().ordinary());
    }
    @SubscribeEvent public static void checkSpawn(MobSpawnEvent.PositionCheck event){
        if(event.getSpawnType()!=MobSpawnType.NATURAL||!(event.getEntity().level() instanceof ServerLevel level))return;
        var pos=event.getEntity().blockPosition();var id=ForgeRegistries.ENTITY_TYPES.getKey(event.getEntity().getType());
        if(level.dimension().location().equals(new ResourceLocation("dynasty:zhenyuan_arena"))&&id!=null&&id.getNamespace().equals("dynasty")){
            event.setResult(Event.Result.DENY);return;
        }
        for(var rule:EcologyRules.ALL)for(var member:rule.members())if(member.mobType().equals(id)&&regionMatches(level,pos,rule)
                &&(member.elite()||!rule.naturalSpawning()||!conditions(level,pos,rule)||!capAllows(level,pos,rule,member))){event.setResult(Event.Result.DENY);return;}
    }
    private EcologyManager(){}
}
