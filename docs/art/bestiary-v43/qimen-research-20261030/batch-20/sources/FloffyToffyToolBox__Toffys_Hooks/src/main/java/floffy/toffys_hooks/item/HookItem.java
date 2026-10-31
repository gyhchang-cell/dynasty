//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by FernFlower decompiler)
//

package floffy.toffys_hooks.item;

import floffy.toffys_hooks.entity.HookEntity;
import floffy.toffys_hooks.register.ModSoundEvents;
import floffy.toffys_hooks.util.PlayerWithHookData;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.sound.SoundCategory;
import net.minecraft.sound.SoundEvents;
import net.minecraft.stat.Stats;
import net.minecraft.util.Hand;
import net.minecraft.util.TypedActionResult;
import net.minecraft.world.World;
import net.minecraft.world.event.GameEvent;

public class HookItem extends Item {
    public HookItem(Item.Settings settings) {
        super(settings);
    }


    @Override
    public TypedActionResult<ItemStack> use(World world, PlayerEntity player, Hand hand) {
        ItemStack itemStack = player.getStackInHand(hand);
        HookEntity hookEntity = ((PlayerWithHookData)player).getHook();
        if (hookEntity != null) {
            HookItem.discard(world, player, hookEntity);
        } else {
            if (!world.isClient) {
                itemStack.damage(1, player, (p) -> {
                p.sendToolBreakStatus(hand);
            });
            }
            this.fire(world, player);
        }
        player.getItemCooldownManager().set(this, 3);
        return TypedActionResult.success(itemStack, world.isClient);
    }

    private void fire(World world, PlayerEntity player) {
        if (!world.isClient) {
            world.spawnEntity(new HookEntity(player,world));
        }

        player.incrementStat(Stats.USED.getOrCreateStat(this));
        world.playSound(null, player.getX(), player.getY(), player.getZ(), ModSoundEvents.GRAPPLING_HOOK_FIRE, SoundCategory.NEUTRAL, .25f, 1F / (world.getRandom().nextFloat() * 0.4F + 0.8F));
        player.emitGameEvent(GameEvent.ITEM_INTERACT_START);
    }

    private static void discard(World world, PlayerEntity player, HookEntity hookEntity) {
        if (!world.isClient()) {
            hookEntity.discard();
            ((PlayerWithHookData)player).setHook(null);
        }
        world.playSound(null, player.getX(), player.getY(), player.getZ(), ModSoundEvents.RETRIEVE_HOOK, SoundCategory.NEUTRAL, .25f, 1f / (world.getRandom().nextFloat() * 0.4f + 0.8f));
        player.emitGameEvent(GameEvent.ITEM_INTERACT_FINISH);
    }
}
