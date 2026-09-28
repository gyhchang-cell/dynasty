package com.dynasty.block;

import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.registries.ForgeRegistries;

/** Small server-authoritative workstations: no background ticks or world scanning. */
public final class LivingWorkshopBlock extends Block {
    public enum Kind { MARROW, ESSENCE, REPAIR, VITALITY, HIDE, HERBAL, LAPIDARY, EMBER }
    private record Cost(String id, int count) {}
    private final Kind kind;
    @Override public net.minecraft.world.phys.shapes.VoxelShape getShape(BlockState state,
            net.minecraft.world.level.BlockGetter level, BlockPos pos,
            net.minecraft.world.phys.shapes.CollisionContext context) {
        return WorkshopShapes.get(kind,state.getValue(BlockStateProperties.HORIZONTAL_FACING));
    }
    @Override public net.minecraft.world.phys.shapes.VoxelShape getCollisionShape(BlockState state,
            net.minecraft.world.level.BlockGetter level, BlockPos pos,
            net.minecraft.world.phys.shapes.CollisionContext context) {
        return getShape(state,level,pos,context);
    }
    @Override public BlockState getStateForPlacement(net.minecraft.world.item.context.BlockPlaceContext context) {
        return defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING,context.getHorizontalDirection().getOpposite());
    }
    @Override public BlockState rotate(BlockState state,net.minecraft.world.level.block.Rotation rotation) {
        return state.setValue(BlockStateProperties.HORIZONTAL_FACING,rotation.rotate(state.getValue(BlockStateProperties.HORIZONTAL_FACING)));
    }
    @Override public BlockState mirror(BlockState state,net.minecraft.world.level.block.Mirror mirror) {
        return state.rotate(mirror.getRotation(state.getValue(BlockStateProperties.HORIZONTAL_FACING)));
    }
    public LivingWorkshopBlock(Properties properties, Kind kind) {
        super(properties); this.kind=kind;
        registerDefaultState(stateDefinition.any().setValue(BlockStateProperties.LIT,false)
                .setValue(BlockStateProperties.HORIZONTAL_FACING,net.minecraft.core.Direction.NORTH));
    }
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> b) {
        b.add(BlockStateProperties.LIT,BlockStateProperties.HORIZONTAL_FACING);
    }
    private List<Cost> costs() {
        return switch(kind) {
            case MARROW -> List.of(new Cost("minecraft:rotten_flesh",8));
            case ESSENCE -> List.of(new Cost("minecraft:amethyst_shard",4),new Cost("minecraft:bone_meal",4));
            case REPAIR -> List.of(new Cost("dynasty:jade",2),new Cost("minecraft:iron_ingot",4));
            case VITALITY -> List.of(new Cost("minecraft:honey_bottle",1));
            case HIDE -> List.of(new Cost("minecraft:rotten_flesh",8),new Cost("minecraft:bone_meal",2));
            case HERBAL -> List.of(new Cost("minecraft:wheat",4),new Cost("minecraft:sugar",2),new Cost("minecraft:kelp",2));
            case LAPIDARY -> List.of(new Cost("minecraft:amethyst_shard",4),new Cost("minecraft:quartz",4));
            case EMBER -> List.of(new Cost("minecraft:charcoal",2),new Cost("minecraft:blaze_powder",1));
        };
    }
    private Item item(String id) { return ForgeRegistries.ITEMS.getValue(new ResourceLocation(id)); }
    private int count(Player p, Item item) {
        int n=0;
        for(int i=0;i<p.getInventory().getContainerSize();i++) {
            var s=p.getInventory().getItem(i); if(s.is(item))n+=s.getCount();
        }
        return n;
    }
    private void consume(Player p, Item item, int amount) {
        for(int i=0;i<p.getInventory().getContainerSize()&&amount>0;i++) {
            var s=p.getInventory().getItem(i);
            if(s.is(item)){int n=Math.min(amount,s.getCount());s.shrink(n);amount-=n;}
        }
    }
    private void give(Player p, String id,int n) {
        var stack=new ItemStack(item(id),n);
        if(!p.getInventory().add(stack))p.drop(stack,false);
    }
    @Override public InteractionResult use(BlockState state,Level level,BlockPos pos,Player p,
            InteractionHand hand,BlockHitResult hit) {
        if(hand!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
        if(!(level instanceof ServerLevel server))return InteractionResult.SUCCESS;
        String key=kind.name().toLowerCase(java.util.Locale.ROOT);
        if(p.isShiftKeyDown()) {
            p.displayClientMessage(Component.translatable("workshop.dynasty."+key+".guide"),false);
            return InteractionResult.CONSUME;
        }
        // One cooldown across every block of this type; moving/replacing a block cannot reset it.
        String timer="dynasty_workshop_"+key;
        long now=server.getServer().overworld().getGameTime();
        long until=p.getPersistentData().getLong(timer);
        if(until>now&&until-now<=600) {
            p.displayClientMessage(Component.translatable("workshop.dynasty.cooldown",(until-now+19)/20),true);
            return InteractionResult.CONSUME;
        }
        ItemStack held=p.getMainHandItem();
        if(kind==Kind.REPAIR&&(!held.isDamageableItem()||!held.isDamaged())) {
            p.displayClientMessage(Component.translatable("workshop.dynasty.repair.hold"),true);
            return InteractionResult.CONSUME;
        }
        if(kind==Kind.VITALITY&&p.getHealth()>=p.getMaxHealth()) {
            p.displayClientMessage(Component.translatable("workshop.dynasty.vitality.full"),true);
            return InteractionResult.CONSUME;
        }
        if(kind==Kind.HERBAL&&p.getHealth()>=p.getMaxHealth()&&!p.hasEffect(net.minecraft.world.effect.MobEffects.POISON)) {
            p.displayClientMessage(Component.translatable("workshop.dynasty.herbal.full"),true);
            return InteractionResult.CONSUME;
        }
        // Validate the entire transaction before consuming anything, including in creative.
        for(Cost c:costs()) if(count(p,item(c.id))<c.count) {
            p.displayClientMessage(Component.translatable("workshop.dynasty."+key+".guide"),false);
            return InteractionResult.CONSUME;
        }
        for(Cost c:costs())consume(p,item(c.id),c.count);
        switch(kind) {
            case MARROW -> give(p,"minecraft:bone_meal",4);
            case ESSENCE -> give(p,"minecraft:experience_bottle",1);
            case REPAIR -> held.setDamageValue(Math.max(0,held.getDamageValue()-Math.max(1,held.getMaxDamage()/4)));
            case VITALITY -> {p.heal(6);give(p,"minecraft:glass_bottle",1);}
            case HIDE -> give(p,"minecraft:leather",2);
            case HERBAL -> {
                p.removeEffect(net.minecraft.world.effect.MobEffects.POISON);
                p.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.REGENERATION,100,0));
            }
            case LAPIDARY -> give(p,"dynasty:jade",1);
            case EMBER -> p.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.FIRE_RESISTANCE,2400,0));
        }
        p.getInventory().setChanged();
        p.getPersistentData().putLong(timer,now+(kind==Kind.VITALITY||kind==Kind.HERBAL||kind==Kind.EMBER?600:20));
        server.setBlock(pos,state.setValue(BlockStateProperties.LIT,true),3);
        server.scheduleTick(pos,this,40);
        server.sendParticles(ParticleTypes.HAPPY_VILLAGER,pos.getX()+.5,pos.getY()+1,pos.getZ()+.5,8,.3,.2,.3,0);
        server.playSound(null,pos,SoundEvents.AMETHYST_BLOCK_CHIME,SoundSource.BLOCKS,.7f,1f);
        p.displayClientMessage(Component.translatable("workshop.dynasty."+key+".done"),true);
        return InteractionResult.CONSUME;
    }
    @Override public void tick(BlockState s,ServerLevel level,BlockPos pos,RandomSource random) {
        level.setBlock(pos,s.setValue(BlockStateProperties.LIT,false),3);
    }
    @Override public void appendHoverText(ItemStack stack,net.minecraft.world.level.BlockGetter level,
            List<Component> tips,net.minecraft.world.item.TooltipFlag flag) {
        tips.add(Component.translatable("workshop.dynasty."+kind.name().toLowerCase(java.util.Locale.ROOT)+".guide"));
    }
}
