package com.dynasty.cod3;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.player.*;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;

/** Loaded-anchor chunk index: no global block/entity search, and at most nine chunks per trigger. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class SecretTracker extends SavedData {
    private final CompoundTag worldClaims=new CompoundTag();
    private final Map<Long,Map<BlockPos,Integer>> anchors=new HashMap<>();
    public static SecretTracker get(ServerLevel level){return level.getDataStorage().computeIfAbsent(SecretTracker::load,SecretTracker::new,"dynasty_cod3_secrets");}
    private static SecretTracker load(CompoundTag n){var d=new SecretTracker();d.worldClaims.merge(n.getCompound("Claims"));return d;}
    @Override public CompoundTag save(CompoundTag n){n.put("Claims",worldClaims.copy());return n;}
    public static void attach(ServerLevel l,BlockPos p,int n){get(l).anchors.computeIfAbsent(ChunkPos.asLong(p.getX()>>4,p.getZ()>>4),k->new HashMap<>()).put(p.immutable(),n);}
    public static void detach(ServerLevel l,BlockPos p){var data=get(l);long chunk=ChunkPos.asLong(p.getX()>>4,p.getZ()>>4);var map=data.anchors.get(chunk);if(map!=null){map.remove(p);if(map.isEmpty())data.anchors.remove(chunk);}}
    public Map<BlockPos,Integer> nearby(BlockPos p){var out=new HashMap<BlockPos,Integer>();int cx=p.getX()>>4,cz=p.getZ()>>4;for(int x=-1;x<=1;x++)for(int z=-1;z<=1;z++){var m=anchors.get(ChunkPos.asLong(cx+x,cz+z));if(m!=null)for(var a:m.entrySet())if(a.getKey().distSqr(p)<=144)out.put(a.getKey(),a.getValue());}return out;}
    private static String key(ServerPlayer p,int n){return p.level().dimension().location()+":secret_"+n;}
    private static CompoundTag progress(ServerPlayer p,int n){String k="cod3_progress_"+n;if(!p.getPersistentData().contains(k))p.getPersistentData().put(k,new CompoundTag());return p.getPersistentData().getCompound(k);}
    private boolean available(ServerPlayer p,int n,SecretDefinition d){
        var claims=d.scope()==SecretDefinition.Scope.WORLD?worldClaims:p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);String k=key(p,n);
        return !claims.contains(k)||!d.oneTime()&&p.level().getGameTime()-claims.getLong(k)>=d.cooldown();
    }
    public boolean claim(ServerPlayer p,int n,BlockPos anchor){
        if(!(p.serverLevel().getBlockEntity(anchor) instanceof StoryAnchor.Anchor)||!Objects.equals(nearby(p.blockPosition()).get(anchor),n))return false;
        var def=SecretDefinition.of(n);if(!def.enabled())return false;
        var personal=p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        if(!p.getPersistentData().contains(Player.PERSISTED_NBT_TAG))p.getPersistentData().put(Player.PERSISTED_NBT_TAG,personal);
        var claims=def.scope()==SecretDefinition.Scope.WORLD?worldClaims:personal;
        String key=key(p,n);long now=p.level().getGameTime();if(claims.contains(key)&&(def.oneTime()||now-claims.getLong(key)<def.cooldown()))return false;
        var item=ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation(def.rewardItem()));if(item==null||item==Items.AIR)return false;
        if(!payment(p,n))return false;
        claims.putLong(key,now);setDirty();var reward=new ItemStack(item);if(!p.getInventory().add(reward))p.drop(reward,false);
        p.displayClientMessage(Component.translatable("cod3.dynasty.secret.success"),true);Cod3Vfx.send(p.serverLevel(),15,Vec3.atCenterOf(anchor),p.getLookAngle(),24,.5);
        return true;
    }
    private static int count(ServerPlayer p,Item item){int amount=0;for(var stack:p.getInventory().items)if(stack.is(item))amount+=stack.getCount();return amount;}
    private static void consume(ServerPlayer p,Item item,int amount){for(var stack:p.getInventory().items)if(stack.is(item)){int taken=Math.min(amount,stack.getCount());stack.shrink(taken);amount-=taken;if(amount==0)break;}p.getInventory().setChanged();}
    private static boolean payment(ServerPlayer p,int number){
        if(p.getAbilities().instabuild)return true;
        if(number==5){if(count(p,Items.COOKED_CHICKEN)<2||!held(p,"dynasty:baijiu"))return false;consume(p,Items.COOKED_CHICKEN,2);p.getMainHandItem().shrink(1);}
        if(number==15||number==17||number==22||number==23){int needed=number==22?3:1;if(p.getMainHandItem().getCount()<needed)return false;p.getMainHandItem().shrink(needed);}
        if(number==16){var cinnabar=ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty:cinnabar"));if(count(p,cinnabar)<1)return false;consume(p,cinnabar,1);}
        if(number==29){if(!held(p,"minecraft:potion"))return false;p.getMainHandItem().shrink(1);var bottle=new ItemStack(Items.GLASS_BOTTLE);if(!p.getInventory().add(bottle))p.drop(bottle,false);}
        return true;
    }
    private static boolean held(ServerPlayer p,String id){return id.isEmpty()||ForgeRegistries.ITEMS.getKey(p.getMainHandItem().getItem()).toString().equals(id);}
    private static boolean conditions(ServerPlayer p,int n,BlockPos pos,SecretDefinition.Trigger trigger){
        var l=p.serverLevel();var def=SecretDefinition.of(n);long day=Math.floorMod(l.getDayTime(),24000);var progress=progress(p,n);
        if(!held(p,def.requiredItem())){progress.remove("Since");return false;}
        if(!progress.contains("Anchor")||progress.getLong("Anchor")!=pos.asLong()){progress.getAllKeys().stream().toList().forEach(progress::remove);progress.putLong("Anchor",pos.asLong());}
        return switch(n){
            case 1->trigger==SecretDefinition.Trigger.PLAY_INSTRUMENT&&l.isRaining()&&l.isNight();
            case 2->trigger==SecretDefinition.Trigger.TIME_WINDOW&&day>=17000&&day<=19000&&l.getMoonPhase()==0&&p.getY()>=120;
            case 3->{if(!p.isShiftKeyDown()){progress.remove("Since");yield false;}if(!progress.contains("Since"))progress.putLong("Since",l.getGameTime());yield l.getGameTime()-progress.getLong("Since")>=20;}
            case 4->trigger==SecretDefinition.Trigger.KILL_ENTITY_AT_REGION;
            case 5->day>=17000&&day<=19000&&count(p,Items.COOKED_CHICKEN)>=2;
            case 6,13,19->trigger==SecretDefinition.Trigger.BREAK_BLOCK;
            case 7->trigger==SecretDefinition.Trigger.WEATHER_WINDOW&&l.isThundering()&&p.isShiftKeyDown();
            case 8->{if(trigger!=SecretDefinition.Trigger.COMBINATION)yield false;long last=progress.getLong("Last");if(progress.contains("Last")&&l.getGameTime()-last<10)yield false;int c=progress.getInt("Count")+1;progress.putLong("Last",l.getGameTime());progress.putInt("Count",c);if(!p.getAbilities().instabuild)p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(Items.BUCKET));yield c>=7;}
            case 9->{var s=p.getMainHandItem();if(!s.isDamageableItem()||s.getMaxDamage()-s.getDamageValue()!=1||!p.isInWater()){progress.remove("Since");yield false;}long since=progress.getLong("Since");if(!progress.contains("Since")){progress.putLong("Since",l.getGameTime());yield false;}yield l.getGameTime()-since>=24000;}
            case 10->{yield Cod3WorldState.get(l).unlocked("world_08")&&p.getInventory().contains(new ItemStack(ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty:zhuque_feather"))));}
            case 11->{if(trigger!=SecretDefinition.Trigger.COMBINATION)yield false;int c=progress.getInt("Count");int expected=c%2;if((p.isShiftKeyDown()?1:0)!=expected){progress.putInt("Count",0);yield false;}progress.putInt("Count",c+1);yield c>=7;}
            case 12->{if(!p.isShiftKeyDown()){progress.remove("Since");yield false;}if(!progress.contains("Since"))progress.putLong("Since",l.getGameTime());yield l.getGameTime()-progress.getLong("Since")>=6000;}
            case 14->l.isThundering()&&day>=11000&&day<=13000&&trigger==SecretDefinition.Trigger.WEATHER_WINDOW;
            case 15,17,23->trigger==SecretDefinition.Trigger.USE_ITEM_AT_POS;
            case 16->trigger==SecretDefinition.Trigger.USE_ITEM_AT_POS&&count(p,ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty:cinnabar")))>=1;
            case 22->trigger==SecretDefinition.Trigger.USE_ITEM_AT_POS&&p.getMainHandItem().getCount()>=3;
            case 18->p.getY()>pos.getY()+1;
            case 20->l.isNight()&&trigger==SecretDefinition.Trigger.HIT_TARGET;
            case 21->p.getY()<pos.getY();
            case 24->{if(trigger!=SecretDefinition.Trigger.HIT_TARGET)yield false;int c=progress.getInt("Count")+1;progress.putInt("Count",c);yield c>=4;}
            case 25->day>=5500&&day<=6500&&p.getY()<pos.getY()-3;
            case 26->{if(trigger!=SecretDefinition.Trigger.PLAY_INSTRUMENT)yield false;long last=progress.getLong("Last");int c=progress.getInt("Count");long gap=l.getGameTime()-last;if(c>0&&(gap<8||gap>80)){progress.putInt("Count",0);yield false;}progress.putLong("Last",l.getGameTime());progress.putInt("Count",c+1);yield c>=4;}
            case 27->p.isUnderWater();
            case 28->l.isNight()&&p.getMainHandItem().getItem() instanceof SwordItem;
            case 29->net.minecraft.world.item.alchemy.PotionUtils.getPotion(p.getMainHandItem())==net.minecraft.world.item.alchemy.Potions.HEALING;
            case 30->{if(trigger!=SecretDefinition.Trigger.COMBINATION)yield false;String facing=p.getDirection().getName();String[] order={"north","east","south","west"};int c=progress.getInt("Count");if(!facing.equals(order[c%4])){progress.putInt("Count",0);yield false;}progress.putInt("Count",c+1);yield c>=3;}
            default->false;
        };
    }
    public static boolean trigger(ServerPlayer p,BlockPos clicked,SecretDefinition.Trigger type){
        var data=get(p.serverLevel());boolean matched=false;
        for(var a:data.nearby(clicked).entrySet()){
            int n=a.getValue();var d=SecretDefinition.of(n);if(!d.enabled()||d.trigger()!=type)continue;
            if(EnumSet.of(SecretDefinition.Trigger.USE_ITEM_AT_POS,SecretDefinition.Trigger.COMBINATION,SecretDefinition.Trigger.BREAK_BLOCK,SecretDefinition.Trigger.HIT_TARGET).contains(type)&&!a.getKey().equals(clicked)&&!(n==24&&clicked.distSqr(a.getKey())<=9))continue;
            matched=true;
            if(!data.available(p,n,d))continue;
            if(conditions(p,n,a.getKey(),type))data.claim(p,n,a.getKey());
            else if(type!=SecretDefinition.Trigger.ENTER_REGION&&type!=SecretDefinition.Trigger.TIME_WINDOW&&type!=SecretDefinition.Trigger.WEATHER_WINDOW)p.displayClientMessage(Component.translatable("cod3.dynasty.secret.failure"),true);
        }
        return matched;
    }
    @SubscribeEvent public static void interact(PlayerInteractEvent.RightClickBlock e){if(e.getEntity() instanceof ServerPlayer p&&e.getHand()==net.minecraft.world.InteractionHand.MAIN_HAND){trigger(p,e.getPos(),SecretDefinition.Trigger.USE_ITEM_AT_POS);trigger(p,e.getPos(),SecretDefinition.Trigger.COMBINATION);}}
    @SubscribeEvent public static void breaking(BlockEvent.BreakEvent e){if(e.getPlayer() instanceof ServerPlayer p)trigger(p,e.getPos(),SecretDefinition.Trigger.BREAK_BLOCK);}
    @SubscribeEvent public static void kill(LivingDeathEvent e){if(e.getEntity().getKillCredit() instanceof ServerPlayer p)trigger(p,e.getEntity().blockPosition(),SecretDefinition.Trigger.KILL_ENTITY_AT_REGION);}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%20!=0)return;trigger(p,p.blockPosition(),SecretDefinition.Trigger.ENTER_REGION);trigger(p,p.blockPosition(),SecretDefinition.Trigger.TIME_WINDOW);trigger(p,p.blockPosition(),SecretDefinition.Trigger.WEATHER_WINDOW);trigger(p,p.blockPosition(),SecretDefinition.Trigger.EQUIPMENT_CHECK);}
    @SubscribeEvent public static void projectile(net.minecraftforge.event.entity.ProjectileImpactEvent e){
        if(e.getEntity() instanceof net.minecraft.world.entity.projectile.AbstractArrow arrow&&arrow.getOwner() instanceof ServerPlayer p&&e.getRayTraceResult() instanceof net.minecraft.world.phys.BlockHitResult hit)
            trigger(p,hit.getBlockPos(),SecretDefinition.Trigger.HIT_TARGET);
    }
    @SubscribeEvent public static void clone(PlayerEvent.Clone e){var stored=e.getOriginal().getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);e.getEntity().getPersistentData().put(Player.PERSISTED_NBT_TAG,stored.copy());}
}
