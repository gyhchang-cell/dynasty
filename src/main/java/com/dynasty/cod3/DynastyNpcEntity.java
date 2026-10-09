package com.dynasty.cod3;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;

/** Fifteen identities share weather/danger logic, but keep their own anatomy and work gestures. */
public final class DynastyNpcEntity extends AbstractVillager implements software.bernie.geckolib.animatable.GeoEntity {
    public enum State {IDLE,WALK,TURN,TALK,WORK,REACT,RAIN,NIGHT,DANGER,PLAYER_NEAR,PLAYER_HOLDS_SPECIAL}
    private static final EntityDataAccessor<Integer> STATE=SynchedEntityData.defineId(DynastyNpcEntity.class,EntityDataSerializers.INT);
    public final String role;
    private final software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache animationCache=software.bernie.geckolib.util.GeckoLibUtil.createInstanceCache(this);
    @Override public software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache getAnimatableInstanceCache(){return animationCache;}
    @Override public void registerControllers(software.bernie.geckolib.core.animation.AnimatableManager.ControllerRegistrar controllers){
        controllers.add(new software.bernie.geckolib.core.animation.AnimationController<>(this,"npc",5,event->{
            event.getController().setAnimation(software.bernie.geckolib.core.animation.RawAnimation.begin().thenLoop("animation.npc."+state().name().toLowerCase(java.util.Locale.ROOT)));
            return software.bernie.geckolib.core.object.PlayState.CONTINUE;
        }));
    }
    @Override public net.minecraft.world.entity.AgeableMob getBreedOffspring(net.minecraft.server.level.ServerLevel level,net.minecraft.world.entity.AgeableMob other){return null;}
    private BlockPos home;
    private long talkingUntil;
    public boolean worldChanged(){
        if(!(level() instanceof net.minecraft.server.level.ServerLevel server))return false;
        String flag=switch(role){case "lao_chen","mo_jizi"->"world_02";case "han_chong"->"world_01";case "qingxuanzi"->"world_08";case "baibao_jin","cao_chengfu"->"world_09";case "a_ji"->"world_04";case "hei_po","xiaoyuanzi"->"world_03";case "chu_nongyu","yan_chifeng"->"world_07";case "ba_tu"->"world_06";default->"world_10";};
        return Cod3WorldState.get(server).unlocked(flag);
    }
    public DynastyNpcEntity(EntityType<? extends DynastyNpcEntity> type,Level level,String role){super(type,level);this.role=role;setPersistenceRequired();}
    public static AttributeSupplier.Builder attributes(){return createMobAttributes().add(Attributes.MAX_HEALTH,40).add(Attributes.MOVEMENT_SPEED,.24).add(Attributes.FOLLOW_RANGE,24);}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(STATE,0);}
    public State state(){return State.values()[Math.floorMod(entityData.get(STATE),State.values().length)];}
    public BlockPos home(){return home==null?blockPosition():home;}
    public void home(BlockPos pos){home=pos.immutable();restrictTo(home,12);}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new AvoidEntityGoal<>(this,Monster.class,10,1,1.25));
        goalSelector.addGoal(3,new MoveTowardsRestrictionGoal(this,.8));goalSelector.addGoal(6,new RandomStrollGoal(this,.6,120));
        goalSelector.addGoal(8,new LookAtPlayerGoal(this,Player.class,6));goalSelector.addGoal(9,new RandomLookAroundGoal(this));
    }
    @Override public boolean hurt(net.minecraft.world.damagesource.DamageSource source,float amount){
        if(java.util.Set.of("lao_chen","han_chong","qingxuanzi","hei_po","xiaoyuanzi","huang_laohan").contains(role))return false;
        boolean hurt=super.hurt(source,amount);if(hurt)getPersistentData().putLong("cod3_react_until",level().getGameTime()+40);return hurt;
    }
    @Override public void tick(){
        super.tick();if(level().isClientSide)return;
        var customer=getTradingPlayer();
        if(customer!=null&&(!customer.isAlive()||customer.isSpectator()||customer.level()!=level()||customer.distanceToSqr(this)>36
                ||com.dynasty.expansion.SmallInteractions.isGhostBoat(this)&&(!(customer instanceof net.minecraft.server.level.ServerPlayer sp)||!com.dynasty.expansion.SmallInteractions.ghostBoatContext(sp,this))))setTradingPlayer(null);
        if(tickCount%20!=0)return;
        ensureContentTrades();
        State next;
        Player near=level().getNearestPlayer(this,6);
        if(level().getGameTime()<getPersistentData().getLong("cod3_react_until"))next=State.REACT;
        else if(level().getGameTime()<talkingUntil||isTrading())next=State.TALK;
        else if(!level().getEntitiesOfClass(Monster.class,getBoundingBox().inflate(10),Mob::isAlive).isEmpty())next=State.DANGER;
        else if(level().isRainingAt(blockPosition())){next=State.RAIN;getNavigation().moveTo(home().getX()+.5,home().getY(),home().getZ()+.5,1);}
        else if(level().isNight()){next=State.NIGHT;if(distanceToSqr(Vec3.atCenterOf(home()))>9)getNavigation().moveTo(home().getX()+.5,home().getY(),home().getZ()+.5,.8);}
        else if(near!=null){var id=ForgeRegistries.ITEMS.getKey(near.getMainHandItem().getItem());next=id!=null&&id.getNamespace().equals(Dynasty.MODID)&&id.getPath().matches(".*(token|seal|scale|feather|qinglong_dao|tianzi_sword).*")?State.PLAYER_HOLDS_SPECIAL:State.PLAYER_NEAR;getLookControl().setLookAt(near,25,25);}
        else if(state()==State.PLAYER_NEAR||state()==State.PLAYER_HOLDS_SPECIAL){next=State.TURN;getLookControl().setLookAt(home().getX()+.5,home().getY()+1,home().getZ()+.5);}
        else if(getNavigation().isDone())next=level().getGameTime()%200<140?State.WORK:State.IDLE;
        else next=State.WALK;
        entityData.set(STATE,next.ordinal());
        if(worldChanged()&&!getPersistentData().getBoolean("cod3_changed_trade")){
            Item reward=item(switch(role){case "lao_chen","mo_jizi"->"blueprint";case "han_chong"->"refined_steel";case "baibao_jin"->"silver_ingot";case "hei_po","xiaoyuanzi"->"healing_salve";default->"tea";});
            if(reward!=null&&reward!=Items.AIR)getOffers().add(new MerchantOffer(new ItemStack(item("copper_coin"),12),new ItemStack(reward),8,1,.05f));
            getPersistentData().putBoolean("cod3_changed_trade",true);
        }
    }
    @Override public InteractionResult mobInteract(Player p,InteractionHand hand){
        if(hand!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
        if(p instanceof net.minecraft.server.level.ServerPlayer sp){
            beginConversation(p);
            if(p.isShiftKeyDown())trade(sp);else NpcDialogue.open(sp,this);
        }
        return InteractionResult.sidedSuccess(level().isClientSide);
    }
    public void beginConversation(Player p){talkingUntil=level().getGameTime()+80;getNavigation().stop();getLookControl().setLookAt(p,30,30);}
    public boolean trade(net.minecraft.server.level.ServerPlayer p){
        if(p.level()!=level()||!p.isAlive()||p.isSpectator()||!isAlive()||p.distanceToSqr(this)>36
                ||getTradingPlayer()!=null&&getTradingPlayer()!=p
                ||com.dynasty.expansion.SmallInteractions.isGhostBoat(this)&&(!com.dynasty.expansion.SmallInteractions.ghostBoatContext(p,this)
                ||!com.dynasty.expansion.EquipmentBehaviors.saved(p).getBoolean("site_ghost_market_boat_talked")))return false;
        ensureContentTrades();
        if(getOffers().isEmpty())return false;
        if(role.equals("huang_laohan")&&level().dimension().equals(com.dynasty.block.DynastyPortalBlock.DRAGON_PALACE))com.dynasty.DynastyAdvancements.award(p,"entered_dragon_palace");
        setTradingPlayer(p);openTradingScreen(p,getDisplayName(),1);return true;
    }
    /** Upgrade native merchant offers in place, retaining their stock and NBT on old saves. */
    public void ensureContentTrades(){
        if(level().isClientSide)return;
        switch(role){
            case "baibao_jin"->buy("fox_pelt",2,6);
            case "ba_tu"->buy("wolf_fang",2,5);
            case "hei_po"->{
                exchange("python_gall",1,"healing_salve",2,8);
                exchange("locust_dust",2,"healing_salve",1,8);
            }
            case "huang_laohan"->{
                buy("crab_shell",2,6);buy("kappa_scale",2,8);
                if(level().dimension().equals(com.dynasty.block.DynastyPortalBlock.DRAGON_PALACE))exchange("copper_coin",48,"sea_pearl",1,8);
            }
        }
    }
    private void buy(String material,int count,int coins){exchange(material,count,"copper_coin",coins,16);}
    private void exchange(String from,int amount,String to,int result,int stock){
        Item input=item(from),output=item(to);if(input==null||output==null||input==Items.AIR||output==Items.AIR)return;
        if(getOffers().stream().anyMatch(o->o.getBaseCostA().is(input)&&o.getBaseCostA().getCount()==amount&&o.getResult().is(output)))return;
        getOffers().add(new MerchantOffer(new ItemStack(input,amount),new ItemStack(output,result),stock,0,0));
    }
    private Item item(String name){return ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty",name));}
    @Override protected void updateTrades(){
        String[] goods=switch(role){case "lao_chen"->new String[]{"blueprint","refined_steel"};case "han_chong"->new String[]{"mu_mao","bamboo_slip"};case "baibao_jin"->new String[]{"tea","silk","jade"};case "hei_po","xiaoyuanzi"->new String[]{"healing_salve","tea"};default->new String[]{"tea"};};
        for(int i=0;i<goods.length;i++){Item reward=item(goods[i]);if(reward!=null&&reward!=Items.AIR)getOffers().add(new MerchantOffer(new ItemStack(item("copper_coin"),8+i*4),new ItemStack(reward),8,1,.05f));}
    }
    @Override protected void rewardTradeXp(MerchantOffer offer){if(level() instanceof net.minecraft.server.level.ServerLevel l)ExperienceOrb.award(l,position(),1);}
    @Override public void addAdditionalSaveData(CompoundTag n){super.addAdditionalSaveData(n);n.putLong("Home",home().asLong());n.putString("Faction",role);}
    @Override public void readAdditionalSaveData(CompoundTag n){super.readAdditionalSaveData(n);if(n.contains("Home"))home(BlockPos.of(n.getLong("Home")));}
}
