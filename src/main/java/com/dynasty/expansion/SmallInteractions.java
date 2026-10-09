package com.dynasty.expansion;

import net.minecraft.core.BlockPos;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.*;
import net.minecraft.world.effect.*;
import net.minecraft.network.chat.Component;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.*;
import java.util.*;

/** Small, persistent, per-player interactions; no second event/quest engine and no ticker entities. */
public final class SmallInteractions {
    public static final List<String> IDS=List.of("wayside_shrine","nameless_tomb","old_weapon_rack","sword_scar_wall","herb_spot","abandoned_armory","puzzle_box","battlefield_remnant","broken_stele","mortuary_room","ghost_market_boat","wayside_tea_stall","old_bellows","broken_waterwheel","ancient_well");
    public static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,"dynasty");
    public static final Map<String,RegistryObject<Block>> ENTRIES=new LinkedHashMap<>();
    static {for(String id:IDS){RegistryObject<Block> block=BLOCKS.register(id,()->new Site(id));ENTRIES.put(id,block);ExpansionContent.ITEMS.register(id,()->new BlockItem(block.get(),new Item.Properties()));}}
    public static void bootstrap(IEventBus bus) {BLOCKS.register(bus);}
    private static final class Site extends Block {
        private final String id;
        private static final net.minecraft.world.level.block.state.properties.BooleanProperty REPAIRED=net.minecraft.world.level.block.state.properties.BlockStateProperties.LIT;
        Site(String id) {super(Properties.copy(Blocks.STONE).strength(2).noOcclusion());this.id=id;registerDefaultState(stateDefinition.any().setValue(REPAIRED,false));}
        @Override protected void createBlockStateDefinition(net.minecraft.world.level.block.state.StateDefinition.Builder<Block,BlockState> builder){builder.add(REPAIRED);}
        @Override public VoxelShape getShape(BlockState state,BlockGetter level,BlockPos pos,CollisionContext context){return Block.box(2,0,2,14,id.equals("herb_spot")?5:13,14);}
        @Override public InteractionResult use(BlockState state,Level level,BlockPos pos,Player player,InteractionHand hand,BlockHitResult hit) {
            if(hand!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
            if(!(player instanceof ServerPlayer p))return InteractionResult.SUCCESS;
            var root=EquipmentBehaviors.saved(p);String key="site_"+id;
            if(id.equals("ancient_well"))return useWell((net.minecraft.server.level.ServerLevel)level,pos,p);
            if(id.equals("broken_waterwheel")&&state.getValue(REPAIRED)){
                root.putBoolean(key+"_done",true);
                com.dynasty.cod3.Cod3WorldState.get((net.minecraft.server.level.ServerLevel)level).unlock((net.minecraft.server.level.ServerLevel)level,"world_02");
                com.dynasty.DynastyAdvancements.award(p,"cod4_"+id);
                p.displayClientMessage(Component.translatable("message.dynasty.cod4.site_done"),true);return InteractionResult.CONSUME;
            }
            // Completed legacy repairs retain their payment/reward history and migrate only missing behavior.
            if(root.getBoolean(key+"_done")&&id.equals("broken_waterwheel")){
                level.setBlock(pos,state.setValue(REPAIRED,true),3);
                com.dynasty.cod3.Cod3WorldState.get((net.minecraft.server.level.ServerLevel)level).unlock((net.minecraft.server.level.ServerLevel)level,"world_02");
            }
            if(root.getBoolean(key+"_done")&&id.equals("old_bellows")&&!root.getBoolean(key+"_assisted")){
                if(!assistFurnace((net.minecraft.server.level.ServerLevel)level,pos)){
                    p.displayClientMessage(Component.translatable("message.dynasty.cod4.bellows_needs_furnace"),true);return InteractionResult.CONSUME;
                }
                root.putBoolean(key+"_assisted",true);feedback((net.minecraft.server.level.ServerLevel)level,pos,"site_bellows",0xe6a04b);
            }
            if(root.getBoolean(key+"_done")){p.displayClientMessage(Component.translatable("message.dynasty.cod4.site_done"),true);return InteractionResult.CONSUME;}
            ItemStack held=p.getItemInHand(hand);long now=level.getGameTime();
            if(root.contains(key+"_start") && now<root.getLong(key+"_next")){p.displayClientMessage(Component.translatable("message.dynasty.cod4.wait",(root.getLong(key+"_next")-now+19)/20),true);return InteractionResult.CONSUME;}
            boolean valid=switch(id) {
                case "wayside_shrine","ghost_market_boat"->held.is(ExpansionContent.SUPPLIES.get("soul_incense").get());
                case "nameless_tomb"->held.is(net.minecraft.tags.ItemTags.FLOWERS);
                case "sword_scar_wall"->held.getItem() instanceof SwordItem && !level.isDay();
                case "broken_stele"->held.is(Items.PAPER);
                case "mortuary_room","wayside_tea_stall"->held.is(Items.MILK_BUCKET);
                case "broken_waterwheel"->held.is(ExpansionContent.MATERIALS.get("qimen_cable").get());
                case "old_bellows"->held.is(Items.CHARCOAL);
                case "ancient_well"->held.is(Items.BUCKET) || held.is(Items.WATER_BUCKET);
                case "puzzle_box"->p.isShiftKeyDown()==(root.getInt(key+"_count")%2==1);
                default->true;
            };
            if(!valid){p.displayClientMessage(Component.translatable("interaction.dynasty."+id),false);return InteractionResult.CONSUME;}
            int needed=id.equals("ancient_well")?7:Set.of("puzzle_box","sword_scar_wall","battlefield_remnant").contains(id)?3:1;
            int duration=switch(id){case "abandoned_armory","ancient_well"->3600;case "sword_scar_wall","puzzle_box","mortuary_room","ghost_market_boat","wayside_tea_stall"->2400;case "nameless_tomb","herb_spot","battlefield_remnant","broken_waterwheel"->1200;default->600;};
            int interval=(duration+needed-1)/needed;
            if(!root.contains(key+"_start")) {root.putLong(key+"_start",now);root.putLong(key+"_next",now+interval);p.displayClientMessage(Component.translatable("message.dynasty.cod4.wait",(interval+19)/20),true);return InteractionResult.CONSUME;}
            if(id.equals("old_bellows")&&!assistFurnace((net.minecraft.server.level.ServerLevel)level,pos)){
                p.displayClientMessage(Component.translatable("message.dynasty.cod4.bellows_needs_furnace"),true);return InteractionResult.CONSUME;
            }
            int count=root.getInt(key+"_count")+1;
            if(id.equals("battlefield_remnant")) {
                String place=level.dimension().location()+"/"+pos.asLong();var visited=root.getCompound("cod4Battlefields");
                if(visited.getBoolean(place))return InteractionResult.CONSUME;
                visited.putBoolean(place,true);root.put("cod4Battlefields",visited);needed=3;
            }
            root.putInt(key+"_count",count);root.putLong(key+"_next",now+interval);
            if(count<needed){p.displayClientMessage(Component.translatable("message.dynasty.cod4.site_progress",count,needed),true);return InteractionResult.CONSUME;}
            if(!p.getAbilities().instabuild && Set.of("wayside_shrine","nameless_tomb","ghost_market_boat","broken_stele","broken_waterwheel","old_bellows").contains(id))held.shrink(1);
            root.putBoolean(key+"_done",true);
            if(id.equals("old_bellows"))root.putBoolean(key+"_assisted",true);
            switch(id) {
                case "wayside_shrine","nameless_tomb"->p.addEffect(new MobEffectInstance(MobEffects.LUCK,2400));
                case "old_weapon_rack"->{
                    ItemStack weapon=new ItemStack(ExpansionContent.item("tie_jian"));
                    if(weapon.isDamageableItem())weapon.setDamageValue(weapon.getMaxDamage()*3/4);
                    give(p,weapon);
                    level.playSound(null,pos,net.minecraft.sounds.SoundEvents.ARMOR_EQUIP_IRON,net.minecraft.sounds.SoundSource.BLOCKS,.6F,.75F);
                }
                case "abandoned_armory"->give(p,new ItemStack(ExpansionContent.MATERIALS.get("qimen_gear").get()));
                case "herb_spot"->{
                    give(p,new ItemStack(com.dynasty.DynastyItems.TEA.get(),2));
                    p.displayClientMessage(Component.translatable("message.dynasty.cod4.herbs"),true);
                    ((net.minecraft.server.level.ServerLevel)level).sendParticles(new net.minecraft.core.particles.BlockParticleOption(net.minecraft.core.particles.ParticleTypes.BLOCK,Blocks.FERN.defaultBlockState()),pos.getX()+.5,pos.getY()+.3,pos.getZ()+.5,12,.25,.15,.25,.02);
                    level.playSound(null,pos,net.minecraft.sounds.SoundEvents.CROP_BREAK,net.minecraft.sounds.SoundSource.BLOCKS,.7F,1F);
                }
                case "ancient_well","mortuary_room"->{p.removeEffect(ExpansionEffects.YIN.get());p.removeEffect(ExpansionEffects.SOUL.get());}
                case "wayside_tea_stall"->p.removeEffect(MobEffects.POISON);
                case "old_bellows"->{
                    give(p,new ItemStack(Items.IRON_NUGGET,3));
                    feedback((net.minecraft.server.level.ServerLevel)level,pos,"site_bellows",0xe6a04b);
                    level.playSound(null,pos,net.minecraft.sounds.SoundEvents.FIRE_AMBIENT,net.minecraft.sounds.SoundSource.BLOCKS,.5F,1.3F);
                }
                case "broken_waterwheel"->{
                    level.setBlock(pos,state.setValue(REPAIRED,true),3);
                    com.dynasty.cod3.Cod3WorldState.get((net.minecraft.server.level.ServerLevel)level).unlock((net.minecraft.server.level.ServerLevel)level,"world_02");
                    give(p,new ItemStack(ExpansionContent.item("copper_coin"),2));
                    feedback((net.minecraft.server.level.ServerLevel)level,pos,"site_waterwheel",0x85c3c9);
                    level.playSound(null,pos,net.minecraft.sounds.SoundEvents.WOOD_PLACE,net.minecraft.sounds.SoundSource.BLOCKS,.8F,.6F);
                }
                default->give(p,new ItemStack(ExpansionContent.item("copper_coin"),2));
            }
            com.dynasty.DynastyAdvancements.award(p,"cod4_"+id);
            CombatFeedback.send(p,CombatFeedback.HEAL);return InteractionResult.CONSUME;
        }
    }
    /** Retain old site timers/completion and use the native secret's real water counter. */
    private static InteractionResult useWell(net.minecraft.server.level.ServerLevel level,BlockPos pos,ServerPlayer p){
        var root=EquipmentBehaviors.saved(p);String key="site_ancient_well";long now=level.getGameTime();
        if(!p.isAlive()||p.isSpectator()||!level.hasChunkAt(pos)||p.distanceToSqr(net.minecraft.world.phys.Vec3.atCenterOf(pos))>36)return InteractionResult.PASS;
        if(com.dynasty.cod3.SecretTracker.wellClaimed(p)){
            root.putBoolean(key+"_done",true);com.dynasty.DynastyAdvancements.award(p,"cod4_ancient_well");
            p.displayClientMessage(Component.translatable("message.dynasty.cod4.site_done"),true);return InteractionResult.CONSUME;
        }
        // A legacy completed Site may still lack native secret 8. Keep its paid
        // completion/reward flag; only the missing secret uses seven real deliveries.
        if(!p.getMainHandItem().is(Items.WATER_BUCKET)){
            p.displayClientMessage(Component.translatable("interaction.dynasty.ancient_well"),false);return InteractionResult.CONSUME;
        }
        int interval=(3600+6)/7;
        if(!root.contains(key+"_start")){
            root.putLong(key+"_start",now);root.putLong(key+"_next",now+interval);
            p.displayClientMessage(Component.translatable("message.dynasty.cod4.wait",(interval+19)/20),true);return InteractionResult.CONSUME;
        }
        if(now<root.getLong(key+"_next")){
            p.displayClientMessage(Component.translatable("message.dynasty.cod4.wait",(root.getLong(key+"_next")-now+19)/20),true);return InteractionResult.CONSUME;
        }
        var delivery=com.dynasty.cod3.SecretTracker.deliverWellWater(p,pos);
        if(!delivery.accepted()){
            p.displayClientMessage(Component.translatable("message.dynasty.cod4.wait",Math.max(1,(3600-(now-root.getLong(key+"_start"))+19)/20)),true);return InteractionResult.CONSUME;
        }
        root.putInt(key+"_count",Math.max(root.getInt(key+"_count"),delivery.count()));root.putLong(key+"_next",now+interval);
        level.sendParticles(net.minecraft.core.particles.ParticleTypes.SPLASH,pos.getX()+.5,pos.getY()+.6,pos.getZ()+.5,8,.15,.1,.15,.03);
        level.playSound(null,pos,net.minecraft.sounds.SoundEvents.BUCKET_EMPTY,net.minecraft.sounds.SoundSource.BLOCKS,.5F,.8F);
        if(!delivery.claimed()){
            p.displayClientMessage(Component.translatable("message.dynasty.cod4.site_progress",delivery.count(),7),true);return InteractionResult.CONSUME;
        }
        boolean oldDone=root.getBoolean(key+"_done");root.putBoolean(key+"_done",true);
        if(!oldDone){p.removeEffect(ExpansionEffects.YIN.get());p.removeEffect(ExpansionEffects.SOUL.get());}
        com.dynasty.DynastyAdvancements.award(p,"cod4_ancient_well");
        p.displayClientMessage(Component.translatable("message.dynasty.cod4.well_released"),false);
        level.sendParticles(net.minecraft.core.particles.ParticleTypes.SOUL,pos.getX()+.5,pos.getY()+.8,pos.getZ()+.5,12,.3,.4,.3,.02);
        return InteractionResult.CONSUME;
    }
    /** Consume the site's charcoal through the existing use transaction, never create smelted output. */
    private static boolean assistFurnace(net.minecraft.server.level.ServerLevel level,BlockPos site){
        for(BlockPos cursor:BlockPos.betweenClosed(site.offset(-3,-1,-3),site.offset(3,2,3))){
            if(!level.hasChunkAt(cursor)||!(level.getBlockEntity(cursor) instanceof net.minecraft.world.level.block.entity.AbstractFurnaceBlockEntity furnace))continue;
            var kind=furnace instanceof net.minecraft.world.level.block.entity.SmokerBlockEntity?net.minecraft.world.item.crafting.RecipeType.SMOKING:
                    furnace instanceof net.minecraft.world.level.block.entity.BlastFurnaceBlockEntity?net.minecraft.world.item.crafting.RecipeType.BLASTING:net.minecraft.world.item.crafting.RecipeType.SMELTING;
            var recipe=level.getRecipeManager().getRecipeFor(kind,furnace,level).orElse(null);
            if(recipe==null||furnace.getItem(0).isEmpty())continue;
            ItemStack result=recipe.getResultItem(level.registryAccess()),output=furnace.getItem(2);
            if(result.isEmpty()||!output.isEmpty()&&(!ItemStack.isSameItemSameTags(result,output)||output.getCount()+result.getCount()>Math.min(furnace.getMaxStackSize(),output.getMaxStackSize())))continue;
            var data=furnace.saveWithoutMetadata();int burn=Math.max(0,data.getInt("BurnTime"));
            if(burn>1600)continue; // A whole charcoal's fuel fits; do not waste it on an already full fire.
            int total=Math.max(1,recipe.getCookingTime());
            data.putInt("BurnTime",burn+1600);data.putInt("CookTimeTotal",total);
            data.putInt("CookTime",Math.min(total-1,Math.max(0,data.getInt("CookTime"))+20));
            furnace.load(data);furnace.setChanged();
            BlockState state=level.getBlockState(cursor);
            if(state.hasProperty(net.minecraft.world.level.block.state.properties.BlockStateProperties.LIT))level.setBlock(cursor,state.setValue(net.minecraft.world.level.block.state.properties.BlockStateProperties.LIT,true),3);
            return true;
        }
        return false;
    }
    private static void feedback(net.minecraft.server.level.ServerLevel level,BlockPos pos,String sequence,int tint){
        var origin=net.minecraft.world.phys.Vec3.atCenterOf(pos);
        var packet=new com.dynasty.cod3.Cod3VisualPacket(level.dimension().location().toString(),26,-1,level.random.nextLong(),level.getGameTime(),30,1,origin,new net.minecraft.world.phys.Vec3(0,0,1),sequence,0,tint);
        com.dynasty.network.DynastyNetwork.CHANNEL.send(net.minecraftforge.network.PacketDistributor.NEAR.with(()->new net.minecraftforge.network.PacketDistributor.TargetPoint(origin.x,origin.y,origin.z,32,level.dimension())),packet);
    }
    private static void give(Player p,ItemStack s) {if(!p.getInventory().add(s))p.drop(s,false);}
    private SmallInteractions() { }
}
