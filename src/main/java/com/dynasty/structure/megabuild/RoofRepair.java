package com.dynasty.structure.megabuild;
import com.dynasty.Dynasty;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.*;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
/** Explicit local preview/confirm, with bounded receipts. No automatic old-save rewrite. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class RoofRepair {
    private record Plan(ResourceKey<Level> dimension,long expires,BlockPos anchor,Map<BlockPos,BlockState> cells){}
    private static final Map<UUID,Plan> PLANS=new HashMap<>();
    static boolean terrain(BlockState s){return s.is(BlockTags.DIRT)||s.is(BlockTags.LEAVES)||s.is(BlockTags.LOGS)||s.is(Blocks.STONE)||s.is(Blocks.DEEPSLATE)||s.is(Blocks.GRAVEL)||s.is(Blocks.SAND)||s.is(Blocks.SNOW)||s.is(Blocks.SNOW_BLOCK);}
    record Receipt(String dimension,BlockPos anchor,Map<BlockPos,BlockState> cells){}
    /** Last repair per operator, maximum16 receipts of8192 cells, written only by explicit confirmation. */
    static final class History extends SavedData {
        static final String KEY="dynasty_roof_repairs";final LinkedHashMap<UUID,Receipt> receipts=new LinkedHashMap<>();
        static History get(MinecraftServer server){return server.overworld().getDataStorage().computeIfAbsent(History::load,History::new,KEY);}
        void record(UUID owner,Receipt receipt){receipts.remove(owner);receipts.put(owner,receipt);while(receipts.size()>16)receipts.remove(receipts.keySet().iterator().next());setDirty();}
        static History load(CompoundTag tag){
            var h=new History();var rows=tag.getList("Repairs",Tag.TAG_COMPOUND);
            for(int i=0;i<Math.min(16,rows.size());i++){
                var row=rows.getCompound(i);if(!row.hasUUID("Owner")||net.minecraft.resources.ResourceLocation.tryParse(row.getString("Dimension"))==null)continue;
                var cells=new LinkedHashMap<BlockPos,BlockState>();var values=row.getList("Cells",Tag.TAG_COMPOUND);
                for(int j=0;j<Math.min(8192,values.size());j++){var cell=values.getCompound(j);var state=NbtUtils.readBlockState(BuiltInRegistries.BLOCK.asLookup(),cell.getCompound("State"));if(terrain(state))cells.put(BlockPos.of(cell.getLong("Pos")),state);}
                if(!cells.isEmpty())h.receipts.put(row.getUUID("Owner"),new Receipt(row.getString("Dimension"),BlockPos.of(row.getLong("Anchor")),Map.copyOf(cells)));
            }return h;
        }
        @Override public CompoundTag save(CompoundTag tag){
            tag.putInt("Version",1);var rows=new ListTag();
            receipts.forEach((owner,receipt)->{var row=new CompoundTag();row.putUUID("Owner",owner);row.putString("Dimension",receipt.dimension);row.putLong("Anchor",receipt.anchor.asLong());var values=new ListTag();receipt.cells.forEach((pos,state)->{var cell=new CompoundTag();cell.putLong("Pos",pos.asLong());cell.put("State",NbtUtils.writeBlockState(state));values.add(cell);});row.put("Cells",values);rows.add(row);});tag.put("Repairs",rows);return tag;
        }
    }
    @SubscribeEvent public static void commands(RegisterCommandsEvent e) {
        e.getDispatcher().register(Commands.literal("dynasty").then(Commands.literal("repair_roof").requires(s->s.hasPermission(2))
            .then(Commands.literal("preview").executes(c->preview(c.getSource().getPlayerOrException())))
            .then(Commands.literal("confirm").executes(c->confirm(c.getSource().getPlayerOrException())))));
    }
    private static int preview(ServerPlayer p) {
        PLANS.remove(p.getUUID());var survey=NaturalSculptures.roofSurvey(p);var cells=survey.cells();
        if(cells.isEmpty()){p.sendSystemMessage(Component.literal("未找到可修屋顶：请站在已生成的云栖庄园/龙阙结构内；改建屋顶、其他建筑与未加载区块保留。旧预览已作废。"));return 0;}
        PLANS.put(p.getUUID(),new Plan(p.level().dimension(),p.server.overworld().getGameTime()+1200,p.blockPosition(),cells));
        int minY=cells.keySet().stream().mapToInt(BlockPos::getY).min().orElse(0),maxY=cells.keySet().stream().mapToInt(BlockPos::getY).max().orElse(0);
        p.sendSystemMessage(Component.literal("预览：当前已存结构，水平半径24格，屋顶上方至多5格；Y="+minY+".."+maxY+"，候选 "+cells.size()+" 格；保留方块实体 "+survey.containers()+" 格、改建屋顶 "+survey.alteredRoofs()+" 列、其他建筑 "+survey.reserved()+" 格。候选天然材质可能由玩家放置，无法可靠区分，请检查后在60秒内、原位置8格内执行 /dynasty repair_roof confirm；预览不改世界。"));return cells.size();
    }
    private static int confirm(ServerPlayer p) {
        var plan=PLANS.remove(p.getUUID());
        if(plan==null||!plan.dimension.equals(p.level().dimension())||p.server.overworld().getGameTime()>plan.expires||p.blockPosition().distSqr(plan.anchor)>64)return 0;
        // A new/edited roof, changed reservation or different selection invalidates the whole preview.
        if(!NaturalSculptures.roofPreview(p).equals(plan.cells)){
            p.sendSystemMessage(Component.literal("屋顶或选中范围已变化，本次未清理；请重新预览。"));return 0;
        }
        for(var entry:plan.cells.entrySet())if(!p.level().hasChunkAt(entry.getKey())||p.level().getBlockEntity(entry.getKey())!=null||!p.level().getBlockState(entry.getKey()).equals(entry.getValue())) {
            p.sendSystemMessage(Component.literal("范围已变化，本次未清理；请重新预览。"));return 0;
        }
        // Claim/protection mods can veto through the original Forge block-break contract, before any write.
        for(var entry:plan.cells.entrySet())if(net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.level.BlockEvent.BreakEvent(p.level(),entry.getKey(),entry.getValue(),p))){
            p.sendSystemMessage(Component.literal("范围内有保护方块，本次未清理。"));return 0;
        }
        // Veto listeners may change the world: never trust the snapshot after dispatching arbitrary listeners.
        if(!NaturalSculptures.roofPreview(p).equals(plan.cells))return 0;
        History.get(p.server).record(p.getUUID(),new Receipt(p.level().dimension().location().toString(),plan.anchor,plan.cells));
        plan.cells.keySet().forEach(pos->p.level().setBlock(pos,Blocks.AIR.defaultBlockState(),3));
        p.sendSystemMessage(Component.literal("已清理选中屋顶上方 "+plan.cells.size()+" 格；原方块、范围和版本已记入 dynasty_roof_repairs 存档。"));return plan.cells.size();
    }
    @SubscribeEvent public static void logout(net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent e){PLANS.remove(e.getEntity().getUUID());}
    @SubscribeEvent public static void stopped(net.minecraftforge.event.server.ServerStoppedEvent e){PLANS.clear();}
    private RoofRepair(){}
}
