package com.dynasty.blueprint.artifact;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;

/** Vanilla right-click/release are use requests; the server computes elapsed charging time. */
public final class ArtifactItem extends SwordItem {
    private final ArtifactAbility ability;
    public ArtifactItem(Tier tier,int damage,float speed,ArtifactAbility ability,Properties properties){super(tier,damage,speed,properties);this.ability=ability;}
    public ArtifactAbility ability(){return ability;}
    @Override public InteractionResultHolder<ItemStack> use(Level level,Player player,InteractionHand hand){
        var stack=player.getItemInHand(hand);if(hand!=InteractionHand.MAIN_HAND)return InteractionResultHolder.fail(stack);
        if(level.isClientSide){if(player.getCooldowns().isOnCooldown(this))return InteractionResultHolder.fail(stack);player.startUsingItem(hand);return InteractionResultHolder.consume(stack);}
        if(player instanceof ServerPlayer p&&ArtifactCombat.counterReady(p,stack)&&ability.release(p,stack,40))return InteractionResultHolder.success(stack);
        if(player instanceof ServerPlayer p&&ArtifactAbility.begin(p,stack)){player.startUsingItem(hand);return InteractionResultHolder.consume(stack);}return InteractionResultHolder.fail(stack);
    }
    @Override public void releaseUsing(ItemStack stack,Level level,LivingEntity user,int remaining){if(user instanceof ServerPlayer p)ArtifactAbility.finish(p,stack);}
    @Override public void onUseTick(Level level,LivingEntity user,ItemStack stack,int remaining){if(user instanceof ServerPlayer p){var session=ArtifactAbility.USES.get(p.getUUID());if(session!=null&&session.stack()==stack&&p.getMainHandItem()==stack&&p.isAlive()&&session.dimension()==p.level().dimension()){long elapsed=p.serverLevel().getGameTime()-session.born();if(elapsed>=0&&elapsed<=72000)ability.tickUse(p,stack,(int)elapsed);}}}
    @Override public int getUseDuration(ItemStack stack){return 72000;}
    @Override public UseAnim getUseAnimation(ItemStack stack){return ability.useAnimation();}
    @Override public boolean shouldCauseReequipAnimation(ItemStack previous,ItemStack next,boolean slotChanged){return slotChanged||!ItemStack.isSameItem(previous,next);}
    @Override public void appendHoverText(ItemStack stack,Level level,java.util.List<net.minecraft.network.chat.Component> lines,TooltipFlag flag){super.appendHoverText(stack,level,lines,flag);var id=net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(this);if(id!=null)lines.add(net.minecraft.network.chat.Component.translatable("tooltip.dynasty."+id.getPath()+"_controls"));}
    @Override public void initializeClient(java.util.function.Consumer<net.minecraftforge.client.extensions.common.IClientItemExtensions> consumer){
        consumer.accept(new net.minecraftforge.client.extensions.common.IClientItemExtensions(){
            private com.dynasty.blueprint.artifact.client.ArtifactItemRenderer renderer;
            @Override public net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer getCustomRenderer(){if(renderer==null)renderer=new com.dynasty.blueprint.artifact.client.ArtifactItemRenderer();return renderer;}
        });
    }
}
