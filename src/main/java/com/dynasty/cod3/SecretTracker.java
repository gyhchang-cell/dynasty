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
    private static final Map<UUID,BlockPos> TEA_BREAKS=new HashMap<>();
    public static boolean teaFlipBreak(net.minecraft.world.entity.player.Player p,BlockPos pos){return pos.equals(TEA_BREAKS.get(p.getUUID()));}
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
        boolean indexed=p.serverLevel().getBlockEntity(anchor) instanceof StoryAnchor.Anchor&&Objects.equals(nearby(p.blockPosition()).get(anchor),n);
        if(!indexed&&!verifiedSite(p,n,anchor))return false;
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
    /** Thin adapter for the registered COD4 well; rewards, scope and payment stay in this ledger. */
    public record WaterDelivery(boolean accepted,boolean claimed,int count) {}
    private static boolean siteContext(ServerPlayer p,BlockPos pos,String id){
        return p.isAlive()&&!p.isSpectator()&&p.serverLevel().hasChunkAt(pos)&&p.distanceToSqr(Vec3.atCenterOf(pos))<=36
                &&p.serverLevel().getBlockState(pos).is(com.dynasty.expansion.SmallInteractions.ENTRIES.get(id).get());
    }
    private static boolean verifiedSite(ServerPlayer p,int n,BlockPos pos){
        // A successful native table break has already removed the Site. Only its
        // same-tick, physical vendor-bound proof may reach the original ledger.
        if(n==19){
            var state=progress(p,19);var site=com.dynasty.expansion.EquipmentBehaviors.saved(p);
            if(!p.isAlive()||p.isSpectator()||!p.serverLevel().hasChunkAt(pos)||p.distanceToSqr(Vec3.atCenterOf(pos))>36||!p.serverLevel().getBlockState(pos).isAir()
                    ||!state.hasUUID("TeaVendor")||!state.getBoolean("NativeFlip")||!state.contains("FlipAt")||state.getLong("FlipAt")!=p.level().getGameTime())return false;
            var vendor=p.serverLevel().getEntity(state.getUUID("TeaVendor"));
            return vendor instanceof DynastyNpcEntity npc&&npc.isAlive()&&com.dynasty.expansion.SmallInteractions.isPoisonTea(npc)
                    &&npc.getUUID().equals(com.dynasty.expansion.SmallInteractions.poisonTeaVendorId(p.serverLevel(),pos))&&npc.distanceToSqr(Vec3.atCenterOf(pos))<=16
                    &&npc.getPersistentData().getLong("cod4_poison_tea_anchor")==pos.asLong()&&site.getBoolean("site_wayside_tea_stall_inspected")
                    &&state.contains("SiteReady")&&state.getLong("SiteReady")==pos.asLong()&&state.getString("SiteDimension").equals(p.level().dimension().location().toString())
                    &&site.contains("site_wayside_tea_stall_start")&&p.level().getGameTime()-site.getLong("site_wayside_tea_stall_start")>=2400;
        }
        if(n!=8&&n!=30&&n!=29&&n!=17&&n!=28)return false;String id=n==8?"ancient_well":n==30?"puzzle_box":n==17?"ghost_market_boat":n==28?"sword_scar_wall":"mortuary_room";
        if(!siteContext(p,pos,id))return false;var state=progress(p,n);var site=com.dynasty.expansion.EquipmentBehaviors.saved(p);
        if(n==28)return SwordDance.context(p,pos)&&p.onGround()&&p.swinging&&p.swingingArm==net.minecraft.world.InteractionHand.MAIN_HAND
                &&state.getInt("Count")>=3&&state.contains("Anchor")&&state.getLong("Anchor")==pos.asLong()
                &&state.getString("DanceDimension").equals(p.level().dimension().location().toString())&&state.contains("DanceReadyAt")&&state.getLong("DanceReadyAt")==p.level().getGameTime()
                &&site.contains("site_sword_scar_wall_start")&&p.level().getGameTime()-site.getLong("site_sword_scar_wall_start")>=2400;
        if(n==17){
            if(!state.hasUUID("Boatman"))return false;var entity=p.serverLevel().getEntity(state.getUUID("Boatman"));
            return entity instanceof DynastyNpcEntity npc&&com.dynasty.expansion.SmallInteractions.ghostBoatContext(p,npc)
                    &&npc.getPersistentData().getLong("cod4_ghost_boat_anchor")==pos.asLong()&&site.getBoolean("site_ghost_market_boat_talked")
                    &&state.contains("SiteReady")&&state.getLong("SiteReady")==pos.asLong()&&state.getString("SiteDimension").equals(p.level().dimension().location().toString())
                    &&site.contains("site_ghost_market_boat_start")&&p.level().getGameTime()-site.getLong("site_ghost_market_boat_start")>=2400
                    &&held(p,"dynasty:cinnabar");
        }
        if(n==29){
            if(!state.hasUUID("Victim"))return false;var victim=p.serverLevel().getEntity(state.getUUID("Victim"));
            return victim instanceof com.dynasty.cod3.DynastyNpcEntity npc&&npc.isAlive()&&npc.getPersistentData().hasUUID("cod4_mortuary_owner")&&npc.getPersistentData().getUUID("cod4_mortuary_owner").equals(p.getUUID())
                    &&npc.getPersistentData().getLong("cod4_mortuary_anchor")==pos.asLong()&&npc.distanceToSqr(Vec3.atCenterOf(pos))<=16&&npc.getHealth()>state.getFloat("HealthBefore")
                    &&state.contains("SiteReady")&&state.getLong("SiteReady")==pos.asLong()&&state.getString("SiteDimension").equals(p.level().dimension().location().toString())
                    &&site.contains("site_mortuary_room_start")&&p.level().getGameTime()-site.getLong("site_mortuary_room_start")>=2400;
        }
        return state.contains("SiteReady")&&state.getLong("SiteReady")==pos.asLong()&&state.getString("SiteDimension").equals(p.serverLevel().dimension().location().toString())
                &&state.getInt("Count")>=(n==8?7:4)&&site.contains("site_"+id+"_start")&&p.level().getGameTime()-site.getLong("site_"+id+"_start")>=(n==8?3600:2400);
    }
    public static boolean wellClaimed(ServerPlayer p){return !get(p.serverLevel()).available(p,8,SecretDefinition.of(8));}
    public static WaterDelivery deliverWellWater(ServerPlayer p,BlockPos pos){
        var state=progress(p,8);int before=state.getInt("Count");
        if(!siteContext(p,pos,"ancient_well"))return new WaterDelivery(false,false,before);
        if(wellClaimed(p))return new WaterDelivery(false,true,before);
        var site=com.dynasty.expansion.EquipmentBehaviors.saved(p);long now=p.level().getGameTime();
        if(!site.contains("site_ancient_well_start")||now<site.getLong("site_ancient_well_next")||!p.getMainHandItem().is(Items.WATER_BUCKET))return new WaterDelivery(false,false,before);
        String dimension=p.serverLevel().dimension().location().toString();
        // Existing pre-adapter progress survives. Crossing a recorded Site dimension
        // starts a different physical well, as the native Anchor check already does.
        if(state.contains("SiteDimension")&&!state.getString("SiteDimension").equals(dimension)){
            state.getAllKeys().stream().toList().forEach(state::remove);before=0;
        }
        // Native conditions can reset when changing physical anchors; use that reset
        // before testing the last delivery's original three-minute site deadline.
        if(state.contains("Anchor")&&state.getLong("Anchor")!=pos.asLong()){
            state.getAllKeys().stream().toList().forEach(state::remove);before=0;
        }
        state.putString("SiteDimension",dimension);
        if(before>=6&&now-site.getLong("site_ancient_well_start")<3600)return new WaterDelivery(false,false,before);
        boolean ready=conditions(p,8,pos,SecretDefinition.Trigger.COMBINATION);
        // conditions() establishes Anchor and may clear metadata on the first use.
        state.putString("SiteDimension",dimension);int delivered=state.getInt("Count");
        if(delivered<=before)return new WaterDelivery(false,false,delivered);
        if(ready)state.putLong("SiteReady",pos.asLong());
        boolean claimed=ready&&get(p.serverLevel()).claim(p,8,pos);
        return new WaterDelivery(true,claimed,delivered);
    }
    public record PuzzleStep(boolean accepted,boolean claimed,int count,boolean reset) {}
    public static boolean swordDanceClaimed(ServerPlayer p){return !get(p.serverLevel()).available(p,28,SecretDefinition.of(28));}
    public static boolean finishSwordDance(ServerPlayer p,BlockPos at){
        return !swordDanceClaimed(p)&&verifiedSite(p,28,at)&&conditions(p,28,at,SecretDefinition.Trigger.USE_ITEM_AT_POS)&&get(p.serverLevel()).claim(p,28,at);
    }
    public static boolean poisonTeaClaimed(ServerPlayer p){return !get(p.serverLevel()).available(p,19,SecretDefinition.of(19));}
    public static boolean flipPoisonTea(ServerPlayer p,BlockPos pos,DynastyNpcEntity npc){
        if(!siteContext(p,pos,"wayside_tea_stall")||poisonTeaClaimed(p)||!com.dynasty.expansion.SmallInteractions.poisonTeaContext(p,npc))return false;
        var site=com.dynasty.expansion.EquipmentBehaviors.saved(p);
        if(!site.getBoolean("site_wayside_tea_stall_inspected")||!site.contains("site_wayside_tea_stall_start")||p.level().getGameTime()-site.getLong("site_wayside_tea_stall_start")<2400
                ||npc.getPersistentData().getLong("cod4_poison_tea_anchor")!=pos.asLong()||!conditions(p,19,pos,SecretDefinition.Trigger.BREAK_BLOCK))return false;
        var original=p.serverLevel().getBlockState(pos);var state=progress(p,19);boolean claimed=false;
        TEA_BREAKS.put(p.getUUID(),pos.immutable());
        try{
            if(!p.gameMode.destroyBlock(pos)||!p.serverLevel().getBlockState(pos).isAir())return false;
            state.putUUID("TeaVendor",npc.getUUID());state.putBoolean("NativeFlip",true);state.putLong("FlipAt",p.level().getGameTime());state.putLong("SiteReady",pos.asLong());state.putString("SiteDimension",p.level().dimension().location().toString());
            claimed=get(p.serverLevel()).claim(p,19,pos);return claimed;
        }finally{
            state.remove("NativeFlip");TEA_BREAKS.remove(p.getUUID());
            // Keep the physical overturned table available to other personal
            // secret owners; the native flip drops no duplicate placeable Site.
            if(p.serverLevel().getBlockState(pos).isAir())p.serverLevel().setBlock(pos,claimed?original.setValue(net.minecraft.world.level.block.state.properties.BlockStateProperties.LIT,true):original,3);
        }
    }
    public static boolean ghostBoatClaimed(ServerPlayer p){return !get(p.serverLevel()).available(p,17,SecretDefinition.of(17));}
    /** Native secret 17 owns cinnabar payment, bamboo slip reward and player/dimension receipt. */
    public static boolean deliverGhostBoat(ServerPlayer p,BlockPos pos,DynastyNpcEntity npc){
        if(!siteContext(p,pos,"ghost_market_boat")||ghostBoatClaimed(p)||!com.dynasty.expansion.SmallInteractions.ghostBoatContext(p,npc))return false;
        var root=com.dynasty.expansion.EquipmentBehaviors.saved(p);
        if(!root.getBoolean("site_ghost_market_boat_talked")||!root.contains("site_ghost_market_boat_start")||p.level().getGameTime()-root.getLong("site_ghost_market_boat_start")<2400
                ||npc.getPersistentData().getLong("cod4_ghost_boat_anchor")!=pos.asLong()||!conditions(p,17,pos,SecretDefinition.Trigger.USE_ITEM_AT_POS))return false;
        var state=progress(p,17);state.putUUID("Boatman",npc.getUUID());state.putLong("SiteReady",pos.asLong());state.putString("SiteDimension",p.level().dimension().location().toString());
        return get(p.serverLevel()).claim(p,17,pos);
    }
    public static boolean mortuaryClaimed(ServerPlayer p){return !get(p.serverLevel()).available(p,29,SecretDefinition.of(29));}
    /** Native healing effect and original potion payment/claim; no item-only rescue. */
    public static boolean rescueMortuary(ServerPlayer p,BlockPos pos,com.dynasty.cod3.DynastyNpcEntity victim){
        if(!siteContext(p,pos,"mortuary_room")||mortuaryClaimed(p)||victim==null||victim.level()!=p.level()||!victim.isAlive()||victim.getHealth()>=victim.getMaxHealth()
                ||victim.distanceToSqr(Vec3.atCenterOf(pos))>16||!victim.getPersistentData().hasUUID("cod4_mortuary_owner")||!victim.getPersistentData().getUUID("cod4_mortuary_owner").equals(p.getUUID())
                ||victim.getPersistentData().getLong("cod4_mortuary_anchor")!=pos.asLong()||!victim.getPersistentData().getBoolean("cod4_mortuary_waiting"))return false;
        var site=com.dynasty.expansion.EquipmentBehaviors.saved(p);long now=p.level().getGameTime();
        if(!site.contains("site_mortuary_room_start")||(!site.getBoolean("site_mortuary_room_done")&&now<site.getLong("site_mortuary_room_next"))||now-site.getLong("site_mortuary_room_start")<2400||!conditions(p,29,pos,SecretDefinition.Trigger.USE_ITEM_AT_POS))return false;
        float before=victim.getHealth();net.minecraft.world.effect.MobEffects.HEAL.applyInstantenousEffect(p,p,victim,0,1);
        if(victim.getHealth()<=before)return false;
        var state=progress(p,29);state.putUUID("Victim",victim.getUUID());state.putFloat("HealthBefore",before);state.putLong("SiteReady",pos.asLong());state.putString("SiteDimension",p.level().dimension().location().toString());
        boolean claimed=get(p.serverLevel()).claim(p,29,pos);
        if(claimed){victim.getPersistentData().putBoolean("cod4_mortuary_waiting",false);victim.getPersistentData().remove("cod3_react_until");victim.setNoAi(false);victim.setInvulnerable(false);}
        return claimed;
    }
    public static boolean puzzleClaimed(ServerPlayer p){return !get(p.serverLevel()).available(p,30,SecretDefinition.of(30));}
    public static int puzzleCount(ServerPlayer p){return Math.min(4,Math.max(0,progress(p,30).getInt("Count")));}
    /** Four cardinal presses reuse secret 30; original stand/sneak alternation is retained. */
    public static PuzzleStep pressPuzzle(ServerPlayer p,BlockPos pos){
        var state=progress(p,30);int before=puzzleCount(p);
        if(!siteContext(p,pos,"puzzle_box"))return new PuzzleStep(false,false,before,false);
        if(puzzleClaimed(p))return new PuzzleStep(false,true,before,false);
        var site=com.dynasty.expansion.EquipmentBehaviors.saved(p);long now=p.level().getGameTime();
        if(!site.contains("site_puzzle_box_start")||now<site.getLong("site_puzzle_box_next"))return new PuzzleStep(false,false,before,false);
        String dimension=p.serverLevel().dimension().location().toString();
        if(state.contains("SiteDimension")&&!dimension.equals(state.getString("SiteDimension"))||state.contains("Anchor")&&state.getLong("Anchor")!=pos.asLong()){
            state.getAllKeys().stream().toList().forEach(state::remove);before=0;
        }
        if(p.isShiftKeyDown()!=(before%2==1)||state.contains("Last")&&now-state.getLong("Last")<10)return new PuzzleStep(false,false,before,false);
        if(before>=3&&now-site.getLong("site_puzzle_box_start")<2400)return new PuzzleStep(false,false,before,false);
        boolean ready=conditions(p,30,pos,SecretDefinition.Trigger.COMBINATION);int after=puzzleCount(p);
        state.putString("SiteDimension",dimension);state.putLong("Last",now);
        if(after<=before)return new PuzzleStep(false,false,after,true);
        if(ready)state.putLong("SiteReady",pos.asLong());
        return new PuzzleStep(true,ready&&get(p.serverLevel()).claim(p,30,pos),after,false);
    }
    private static int count(ServerPlayer p,Item item){int amount=0;for(var stack:p.getInventory().items)if(stack.is(item))amount+=stack.getCount();return amount;}
    private static void consume(ServerPlayer p,Item item,int amount){for(var stack:p.getInventory().items)if(stack.is(item)){int taken=Math.min(amount,stack.getCount());stack.shrink(taken);amount-=taken;if(amount==0)break;}p.getInventory().setChanged();}
    private static boolean payment(ServerPlayer p,int number){
        if(p.getAbilities().instabuild)return true;
        if(number==5){if(count(p,Items.COOKED_CHICKEN)<2||!held(p,"dynasty:baijiu"))return false;consume(p,Items.COOKED_CHICKEN,2);p.getMainHandItem().shrink(1);}
        if(number==15||number==17||number==22||number==23){int needed=number==22?3:1;if(p.getMainHandItem().getCount()<needed)return false;p.getMainHandItem().shrink(needed);}
        if(number==16){
            var jade=com.dynasty.expansion.ExpansionContent.MATERIALS.get("sprite_jade").get();
            var cinnabar=ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty:cinnabar"));
            // A carried sprite-jade offering can replace the original cinnabar;
            // the original brush gesture, anchor and personal receipt stay intact.
            var offering=count(p,jade)>0?jade:cinnabar;if(count(p,offering)<1)return false;consume(p,offering,1);
        }
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
            case 16->trigger==SecretDefinition.Trigger.USE_ITEM_AT_POS&&(count(p,ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty:cinnabar")))>=1||count(p,com.dynasty.expansion.ExpansionContent.MATERIALS.get("sprite_jade").get())>=1);
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
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;SwordDance.tick(p);if(p.tickCount%20!=0)return;trigger(p,p.blockPosition(),SecretDefinition.Trigger.ENTER_REGION);trigger(p,p.blockPosition(),SecretDefinition.Trigger.TIME_WINDOW);trigger(p,p.blockPosition(),SecretDefinition.Trigger.WEATHER_WINDOW);trigger(p,p.blockPosition(),SecretDefinition.Trigger.EQUIPMENT_CHECK);}
    @SubscribeEvent public static void projectile(net.minecraftforge.event.entity.ProjectileImpactEvent e){
        if(e.getEntity() instanceof net.minecraft.world.entity.projectile.AbstractArrow arrow&&arrow.getOwner() instanceof ServerPlayer p&&e.getRayTraceResult() instanceof net.minecraft.world.phys.BlockHitResult hit)
            trigger(p,hit.getBlockPos(),SecretDefinition.Trigger.HIT_TARGET);
    }
    @SubscribeEvent public static void clone(PlayerEvent.Clone e){
        var original=e.getOriginal().getPersistentData();var copied=e.getEntity().getPersistentData();
        copied.put(Player.PERSISTED_NBT_TAG,original.getCompound(Player.PERSISTED_NBT_TAG).copy());
        // Discrete paid deliveries and lock steps survive death. Continuous posture,
        // underwater and timed equipment challenges deliberately keep their reset.
        for(int n:new int[]{8,30}){String key="cod3_progress_"+n;if(original.contains(key))copied.put(key,original.getCompound(key).copy());}
    }
}
