package com.dynasty.structure.megabuild;
import com.dynasty.Dynasty;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
/** Explicit two-step repair of a selected saved sculpture, never a world scan or automatic old-save rewrite. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class RoofRepair {
    private record Plan(ResourceKey<Level> dimension,long expires,Map<BlockPos,BlockState> cells){}
    private static final Map<UUID,Plan> PLANS=new HashMap<>();
    static boolean terrain(BlockState s){return s.is(BlockTags.DIRT)||s.is(BlockTags.LEAVES)||s.is(BlockTags.LOGS)||s.is(Blocks.STONE)||s.is(Blocks.DEEPSLATE)||s.is(Blocks.GRAVEL)||s.is(Blocks.SAND)||s.is(Blocks.SNOW)||s.is(Blocks.SNOW_BLOCK);}
    @SubscribeEvent public static void commands(RegisterCommandsEvent e) {
        e.getDispatcher().register(Commands.literal("dynasty").then(Commands.literal("repair_roof").requires(s->s.hasPermission(2))
            .then(Commands.literal("preview").executes(c->preview(c.getSource().getPlayerOrException())))
            .then(Commands.literal("confirm").executes(c->confirm(c.getSource().getPlayerOrException())))));
    }
    private static int preview(ServerPlayer p) {
        var cells=NaturalSculptures.roofPreview(p);
        if(cells.isEmpty()){p.sendSystemMessage(Component.literal("未找到可修屋顶：请站在已生成的云栖庄园/龙阙结构内；改建屋顶和未加载区块不会处理。"));return 0;}
        PLANS.put(p.getUUID(),new Plan(p.level().dimension(),p.server.overworld().getGameTime()+1200,Map.copyOf(cells)));
        int minY=cells.keySet().stream().mapToInt(BlockPos::getY).min().orElse(0),maxY=cells.keySet().stream().mapToInt(BlockPos::getY).max().orElse(0);
        p.sendSystemMessage(Component.literal("预览：当前脚下已存结构，水平半径24格，屋顶上方至多5格；Y="+minY+".."+maxY+"，将清除 "+cells.size()+" 个天然材质方块。箱子/方块实体与已改屋顶保留。天然材质也可能由玩家放置，请检查范围后在60秒内执行 /dynasty repair_roof confirm；不确认不改动。"));return cells.size();
    }
    private static int confirm(ServerPlayer p) {
        var plan=PLANS.remove(p.getUUID());
        if(plan==null||plan.dimension!=p.level().dimension()||p.server.overworld().getGameTime()>plan.expires)return 0;
        for(var entry:plan.cells.entrySet())if(!p.level().hasChunkAt(entry.getKey())||p.level().getBlockEntity(entry.getKey())!=null||!p.level().getBlockState(entry.getKey()).equals(entry.getValue())) {
            p.sendSystemMessage(Component.literal("范围已变化，本次未清理；请重新预览。"));return 0;
        }
        plan.cells.keySet().forEach(pos->p.level().setBlock(pos,Blocks.AIR.defaultBlockState(),3));
        p.sendSystemMessage(Component.literal("已清理选中屋顶上方 "+plan.cells.size()+" 格。"));return plan.cells.size();
    }
    @SubscribeEvent public static void stopped(net.minecraftforge.event.server.ServerStoppedEvent e){PLANS.clear();}
    private RoofRepair(){}
}
