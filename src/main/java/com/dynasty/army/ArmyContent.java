package com.dynasty.army;
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
public final class ArmyContent {
    public static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,Dynasty.MODID);
    public static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,Dynasty.MODID);
    public static final DeferredRegister<MenuType<?>> MENUS=DeferredRegister.create(ForgeRegistries.MENU_TYPES,Dynasty.MODID);
    public static final RegistryObject<Block> DESK=BLOCKS.register("recruitment_desk",Desk::new);
    public static final RegistryObject<Item> DESK_ITEM=ITEMS.register("recruitment_desk",()->new BlockItem(DESK.get(),new Item.Properties()));
    public static final RegistryObject<MenuType<ArmyMenu>> MENU=MENUS.register("army_roster",()->IForgeMenuType.create((id,inv,buf)->new ArmyMenu(id,inv,buf.readBoolean()?buf.readBlockPos():null)));
    public static void register(IEventBus bus){BLOCKS.register(bus);ITEMS.register(bus);MENUS.register(bus);}
    public static void open(ServerPlayer p,BlockPos desk) {
        NetworkHooks.openScreen(p,new SimpleMenuProvider((id,inv,who)->new ArmyMenu(id,inv,desk),Component.literal(desk==null?"虎符 · 兵册与军阵":"募兵台")),buf->{buf.writeBoolean(desk!=null);if(desk!=null)buf.writeBlockPos(desk);});
    }
    private static final class Desk extends Block {
        Desk(){super(Properties.copy(Blocks.SMITHING_TABLE));}
        @Override public InteractionResult use(BlockState state,Level level,BlockPos pos,Player p,InteractionHand hand,BlockHitResult hit) {
            if(p instanceof ServerPlayer sp)open(sp,pos);return InteractionResult.sidedSuccess(level.isClientSide);
        }
    }
    private ArmyContent(){}
}
