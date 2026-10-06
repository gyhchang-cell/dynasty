package com.dynasty.infusion;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.common.extensions.IForgeMenuType;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.network.NetworkHooks;
import net.minecraftforge.registries.*;

public final class InfusionContent {
    public static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,Dynasty.MODID);
    public static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,Dynasty.MODID);
    public static final DeferredRegister<MenuType<?>> MENUS=DeferredRegister.create(ForgeRegistries.MENU_TYPES,Dynasty.MODID);
    public static final RegistryObject<Block> TABLE=BLOCKS.register("infusion_table",Table::new);
    public static final RegistryObject<Item> TABLE_ITEM=ITEMS.register("infusion_table",()->new BlockItem(TABLE.get(),new Item.Properties()));
    public static final RegistryObject<MenuType<InfusionMenu>> MENU=MENUS.register("infusion",()->IForgeMenuType.create((id,inv,buf)->new InfusionMenu(id,inv,buf.readBlockPos())));
    public static void register(IEventBus bus){BLOCKS.register(bus);ITEMS.register(bus);MENUS.register(bus);}
    private static final class Table extends Block {
        Table(){super(Properties.copy(Blocks.SMITHING_TABLE).noOcclusion());}
        @Override public InteractionResult use(BlockState state,Level level,BlockPos pos,Player p,InteractionHand hand,BlockHitResult hit){
            if(hand!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
            if(p instanceof ServerPlayer sp)NetworkHooks.openScreen(sp,new SimpleMenuProvider((id,inv,who)->new InfusionMenu(id,inv,pos),Component.translatable("block.dynasty.infusion_table")),pos);
            return InteractionResult.sidedSuccess(level.isClientSide);
        }
    }
    private InfusionContent(){}
}
