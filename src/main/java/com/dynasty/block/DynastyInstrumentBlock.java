package com.dynasty.block;

import com.dynasty.DynastyStats;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;

/**
 * 宫廷乐器方块：编钟（钟声安民）与太鼓（鼓声振奋士气）。
 * Palace instruments: the chime bell (calms the people) and the taiko drum (inspires the troops).
 */
@SuppressWarnings("null")
public class DynastyInstrumentBlock extends Block {

    private final boolean bell;

    public DynastyInstrumentBlock(Properties props, boolean bell) {
        super(props);
        this.bell = bell;
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player,
                                 InteractionHand hand, BlockHitResult hit) {
        if (!(level instanceof ServerLevel serverLevel)) {
            return InteractionResult.SUCCESS;
        }
        long now = level.getGameTime();
        String key = this.bell ? "dynasty_bell_use" : "dynasty_drum_use";
        if (now - player.getPersistentData().getLong(key) < 40L) {
            return InteractionResult.CONSUME;
        }
        player.getPersistentData().putLong(key, now);

        double radius = this.bell ? 12.0D : 10.0D;
        for (ServerPlayer target : level.getEntitiesOfClass(ServerPlayer.class, new AABB(pos).inflate(radius))) {
            if (this.bell) {
                target.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 20 * 8, 0));
                DynastyStats.addLoyalty(target, 1);
                target.sendSystemMessage(Component.literal("§e[编钟] §r钟声悠扬，民心安定（忠诚 +1）"));
            } else {
                target.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 20 * 30, 0));
                target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 20 * 30, 0));
                target.sendSystemMessage(Component.literal("§c[太鼓] §r鼓声雷动，士气大振！"));
            }
        }
        level.playSound(null, pos, this.bell
                        ? SoundEvents.BELL_BLOCK
                        : SoundEvents.NOTE_BLOCK_BASEDRUM.value(),
                SoundSource.BLOCKS, 2.0F, this.bell ? 1.0F : 0.8F);
        serverLevel.sendParticles(this.bell ? ParticleTypes.NOTE : ParticleTypes.CRIT,
                pos.getX() + 0.5D, pos.getY() + 1.2D, pos.getZ() + 0.5D,
                12, 0.6D, 0.2D, 0.6D, 0.1D);
        return InteractionResult.CONSUME;
    }
}
