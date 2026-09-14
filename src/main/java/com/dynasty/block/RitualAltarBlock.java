package com.dynasty.block;

import com.dynasty.Dynasty;
import com.dynasty.DynastyBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * 法阵·祭坛：用「Boss 掉落信物」对着祭坛使法，召唤对应 Boss。
 *
 * 条件：手持对应信物 + 祭坛四周 3×3 环里至少 4 块玉石块（法阵成形）+ 附近无同种 Boss。
 * 信物来自击败 Boss 本身，所以每个 Boss 都能反复挑战。
 *
 * Ritual altar: right-click with a boss token to summon that boss (needs 4 jade blocks around it).
 */
@SuppressWarnings({"null", "removal"})
public class RitualAltarBlock extends Block {

    /** 法阵成形需要几块玉石块 / jade blocks required around the altar */
    public static final int REQUIRED_JADE = 4;

    public RitualAltarBlock(Properties props) {
        super(props);
    }

    /** 信物 → Boss / catalyst item to boss */
    public static EntityType<? extends Mob> bossFor(ItemStack stack) {
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(stack.getItem());
        if (id == null || !id.getNamespace().equals(Dynasty.MODID)) {
            return null;
        }
        return switch (id.getPath()) {
            case "dragon_emperor_seal" -> com.dynasty.entity.DynastyEntities.DRAGON_EMPEROR.get();
            case "rebel_head" -> com.dynasty.entity.DynastyEntities.REBEL_GENERAL.get();
            case "eunuch_token" -> com.dynasty.entity.DynastyEntities.EUNUCH_MASTERMIND.get();
            case "emperor_bone" -> com.dynasty.entity.DynastyEntities.UNDEAD_FIRST_EMPEROR.get();
            case "sky_token" -> com.dynasty.entity.DynastyEntities.NINE_HEAVEN_GENERAL.get();
            case "sea_token" -> com.dynasty.entity.DynastyEntities.DRAGON_KING.get();
            default -> null;
        };
    }

    private static int countJade(Level level, BlockPos pos) {
        int found = 0;
        for (int dx = -1; dx <= 1; dx++) {
            for (int dz = -1; dz <= 1; dz++) {
                if (dx == 0 && dz == 0) {
                    continue;
                }
                if (level.getBlockState(pos.offset(dx, 0, dz)).is(DynastyBlocks.JADE_BLOCK.get())) {
                    found++;
                }
            }
        }
        return found;
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player,
                                 InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide() || !(level instanceof ServerLevel server)) {
            return InteractionResult.SUCCESS;
        }
        ItemStack stack = player.getItemInHand(hand);
        EntityType<? extends Mob> type = bossFor(stack);
        if (type == null) {
            player.displayClientMessage(Component.literal(
                    "§7法阵沉寂。手持 Boss 信物（龙帝玉玺 / 叛将首级 / 内廷令牌 / 帝骸骨）才能唤醒。"), true);
            return InteractionResult.SUCCESS;
        }
        int jade = countJade(level, pos);
        if (jade < REQUIRED_JADE) {
            player.displayClientMessage(Component.literal(
                    "§c法阵未成形：祭坛四周需 " + REQUIRED_JADE + " 块玉石块（当前 " + jade + " 块）。"), true);
            return InteractionResult.SUCCESS;
        }
        for (Mob existing : level.getEntitiesOfClass(Mob.class, player.getBoundingBox().inflate(80.0D),
                m -> m.getType() == type)) {
            if (existing.isAlive()) {
                player.displayClientMessage(Component.literal("§e法阵已锁定一位主祭：先击败它再来。"), true);
                return InteractionResult.SUCCESS;
            }
        }
        Mob boss = type.create(level);
        if (boss == null) {
            return InteractionResult.SUCCESS;
        }
        if (!player.getAbilities().instabuild) {
            stack.shrink(1);
        }
        boss.moveTo(pos.getX() + 0.5D, pos.getY() + 1.2D, pos.getZ() + 0.5D,
                player.getYRot() + 180.0F, 0.0F);
        boss.addEffect(new net.minecraft.world.effect.MobEffectInstance(
                net.minecraft.world.effect.MobEffects.DAMAGE_RESISTANCE, 200, 1, false, false));
        level.addFreshEntity(boss);
        summonEffects(server, pos, player);
        for (Player nearby : server.getEntitiesOfClass(Player.class, player.getBoundingBox().inflate(48.0D))) {
            nearby.displayClientMessage(Component.literal("§6[法阵] §r" + boss.getDisplayName().getString()
                    + " §r被信物唤醒，降临此间！"), false);
        }
        return InteractionResult.SUCCESS;
    }

    /** 召唤特效：三雷 + 灵火 + 轰鸣 / summoning effects */
    private void summonEffects(ServerLevel server, BlockPos pos, Player player) {
        for (int i = 0; i < 3; i++) {
            net.minecraft.world.entity.LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(server);
            if (bolt != null) {
                bolt.moveTo(net.minecraft.world.phys.Vec3.atBottomCenterOf(
                        pos.offset(server.random.nextInt(5) - 2, 0, server.random.nextInt(5) - 2)));
                bolt.setVisualOnly(true);
                server.addFreshEntity(bolt);
            }
        }
        server.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, pos.getX() + 0.5D, pos.getY() + 1.2D,
                pos.getZ() + 0.5D, 90, 1.5D, 1.2D, 1.5D, 0.02D);
        server.sendParticles(ParticleTypes.ENCHANT, pos.getX() + 0.5D, pos.getY() + 1.0D,
                pos.getZ() + 0.5D, 60, 1.2D, 1.0D, 1.2D, 0.4D);
        server.playSound(null, pos, SoundEvents.LIGHTNING_BOLT_THUNDER, SoundSource.BLOCKS, 2.0F, 0.8F);
        server.playSound(null, pos, SoundEvents.BEACON_ACTIVATE, SoundSource.BLOCKS, 1.5F, 1.2F);
    }
}
