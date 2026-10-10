package com.dynasty.structure.megabuild;

import com.dynasty.Dynasty;
import java.util.*;
import net.minecraft.commands.Commands;
import net.minecraft.core.*;
import net.minecraft.core.registries.*;
import net.minecraft.nbt.*;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.*;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Explicit operator upgrade of ONE loaded, unchanged native legacy instance. Never scans saves. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class MiningUpgrade {
    static final int MAX_CELLS=65536;
    private static final Map<UUID,Plan> PLANS=new HashMap<>();
    record Change(BlockState before,BlockState after,boolean newChest){}
    record Selection(StructureStart start,MegabuildPiece piece,ChunkPos owner){}
    record Survey(Selection selection,Map<BlockPos,Change> changes,Map<BlockPos,CompoundTag> containers,BitSet columns,String refusal){}
    private record Plan(String dimension,long expires,BlockPos anchor,Survey survey){}
    record Receipt(String dimension,CompoundTag originalPiece,Map<BlockPos,Change> changes,Map<BlockPos,CompoundTag> containers){}

    /** Bounded original native block states and container NBT; eligibility lives in the original piece. */
    static final class History extends SavedData {
        static final String KEY="dynasty_mine_upgrades";
        final LinkedHashMap<UUID,Receipt> receipts=new LinkedHashMap<>();
        static History get(net.minecraft.server.MinecraftServer server){return server.overworld().getDataStorage().computeIfAbsent(History::load,History::new,KEY);}
        void record(UUID owner,Receipt value){receipts.remove(owner);receipts.put(owner,value);while(receipts.size()>8)receipts.remove(receipts.keySet().iterator().next());setDirty();}
        static History load(CompoundTag tag){
            var h=new History();if(tag.getInt("Version")!=1)return h;var rows=tag.getList("Upgrades",Tag.TAG_COMPOUND);
            for(int i=0;i<Math.min(8,rows.size());i++){
                var row=rows.getCompound(i);if(!row.hasUUID("Owner")||ResourceLocation.tryParse(row.getString("Dimension"))==null)continue;
                var cells=new LinkedHashMap<BlockPos,Change>();var values=row.getList("Cells",Tag.TAG_COMPOUND);
                for(int j=0;j<Math.min(MAX_CELLS,values.size());j++){var cell=values.getCompound(j);cells.put(BlockPos.of(cell.getLong("Pos")),new Change(NbtUtils.readBlockState(BuiltInRegistries.BLOCK.asLookup(),cell.getCompound("Before")),NbtUtils.readBlockState(BuiltInRegistries.BLOCK.asLookup(),cell.getCompound("After")),cell.getBoolean("NewChest")));}
                var containers=new LinkedHashMap<BlockPos,CompoundTag>();var saved=row.getList("Containers",Tag.TAG_COMPOUND);
                for(int j=0;j<Math.min(MiningEstate.SIZE*MiningEstate.SIZE,saved.size());j++){var cell=saved.getCompound(j);containers.put(BlockPos.of(cell.getLong("Pos")),cell.getCompound("Nbt").copy());}
                if(!cells.isEmpty())h.receipts.put(row.getUUID("Owner"),new Receipt(row.getString("Dimension"),row.getCompound("OriginalPiece").copy(),Map.copyOf(cells),Map.copyOf(containers)));
            }return h;
        }
        @Override public CompoundTag save(CompoundTag tag){
            tag.putInt("Version",1);var rows=new ListTag();receipts.forEach((owner,r)->{
                var row=new CompoundTag();row.putUUID("Owner",owner);row.putString("Dimension",r.dimension);row.put("OriginalPiece",r.originalPiece.copy());
                var cells=new ListTag();r.changes.forEach((pos,c)->{var cell=new CompoundTag();cell.putLong("Pos",pos.asLong());cell.put("Before",NbtUtils.writeBlockState(c.before));cell.put("After",NbtUtils.writeBlockState(c.after));cell.putBoolean("NewChest",c.newChest);cells.add(cell);});row.put("Cells",cells);
                var containers=new ListTag();r.containers.forEach((pos,nbt)->{var cell=new CompoundTag();cell.putLong("Pos",pos.asLong());cell.put("Nbt",nbt.copy());containers.add(cell);});row.put("Containers",containers);rows.add(row);
            });tag.put("Upgrades",rows);return tag;
        }
    }

    private static Survey refused(Selection selected,String reason){return new Survey(selected,Map.of(),Map.of(),new BitSet(),reason);}
    static Selection selected(ServerPlayer p){
        var level=p.serverLevel();var structure=level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(new ResourceLocation("dynasty","tiangong_mining_estate"));
        if(structure==null)return null;var current=level.getChunkSource().getChunkNow(p.getBlockX()>>4,p.getBlockZ()>>4);if(current==null)return null;
        var refs=new it.unimi.dsi.fastutil.longs.LongOpenHashSet(current.getReferencesForStructure(structure));refs.add(current.getPos().toLong());
        for(long ref:refs){var cp=new ChunkPos(ref);var chunk=level.getChunkSource().getChunkNow(cp.x,cp.z);if(chunk==null)continue;var start=chunk.getStartForStructure(structure);
            if(start==null||!start.isValid()||start.getPieces().size()!=1||!(start.getPieces().get(0) instanceof MegabuildPiece piece)||!piece.getBoundingBox().isInside(p.blockPosition()))continue;
            var b=piece.getBoundingBox();if(b.getXSpan()!=MiningEstate.SIZE||b.getZSpan()!=MiningEstate.SIZE||b.getYSpan()!=MiningEstate.HEIGHT)return null;
            return new Selection(start,piece,cp);
        }return null;
    }

    static Survey survey(ServerPlayer p){
        var selected=selected(p);if(selected==null)return refused(null,"请站在已经保存的原生采矿庄园实例内；手动模板没有原结构版本，不能据此安全升级。");
        var piece=selected.piece;if(!piece.legacyMine())return refused(selected,"该实例已经升级或为当前版本；不能重复生成矿物和箱子。");
        var level=p.serverLevel();var box=piece.getBoundingBox();var chunks=new ArrayList<net.minecraft.world.level.chunk.LevelChunk>();
        // Verify every source/halo chunk first. No survey read can force a neighboring load.
        for(int x=(box.minX()-1)>>4;x<=(box.maxX()+1)>>4;x++)for(int z=(box.minZ()-1)>>4;z<=(box.maxZ()+1)>>4;z++){
            var chunk=level.getChunkSource().getChunkNow(x,z);if(chunk==null)return refused(selected,"范围或支撑边界含未加载区块，全部保留；请实际走访该庄园后重新预览。");chunks.add(chunk);
        }
        for(var chunk:chunks)for(var entry:chunk.getAllReferences().entrySet())for(long reference:entry.getValue()){
            var key=new ChunkPos(reference);var owner=level.getChunkSource().getChunkNow(key.x,key.z);if(owner==null)return refused(selected,"存在无法核对的其他结构引用，全部保留。");
            var other=owner.getStartForStructure(entry.getKey());if(other==null||!other.isValid()||other==selected.start)continue;
            for(var part:other.getPieces())if(part.getBoundingBox().intersects(box))return refused(selected,"另一个已存结构与选中范围相交，全部保留。");
        }
        var source=piece.miningSource();var target=new MiningEstate(piece.miningSeed()).blueprint().rotate(piece.miningRotation());
        var oldStates=new EnumMap<Blueprint.Kind,BlockState>(Blueprint.Kind.class);var newStates=new EnumMap<Blueprint.Kind,BlockState>(Blueprint.Kind.class);
        for(var kind:Blueprint.Kind.values()){oldStates.put(kind,piece.miningState(kind,false));newStates.put(kind,piece.miningState(kind,true));}
        var containers=new LinkedHashMap<BlockPos,CompoundTag>();var columns=new BitSet(MiningEstate.SIZE*MiningEstate.SIZE);
        for(int x=0;x<MiningEstate.SIZE;x++)for(int z=0;z<MiningEstate.SIZE;z++)for(int y=0;y<MiningEstate.HEIGHT;y++){
            var at=piece.miningWorld(x,y,z);var actual=level.getBlockState(at);var expected=oldStates.get(source.at(x,y,z));
            if(actual.hasBlockEntity()){
                var be=level.getBlockEntity(at);if(be==null||!actual.is(expected.getBlock()))return refused(selected,"容器或功能方块与原版本不一致，整座保留："+at.toShortString());
                containers.put(at,be.saveWithFullMetadata().copy());reserve(columns,x,z);
            }else if(!actual.equals(expected))return refused(selected,"发现改建、开采或无法确认的原方块，整座保留："+at.toShortString());
            if(x==0||z==0||x==MiningEstate.SIZE-1||z==MiningEstate.SIZE-1)for(var direction:Direction.Plane.HORIZONTAL){
                var beside=at.relative(direction);if(box.isInside(beside))continue;var state=level.getBlockState(beside);
                if(!state.isAir()&&!RoofRepair.terrain(state))reserve(columns,x,z);
            }
        }
        var changes=new LinkedHashMap<BlockPos,Change>();
        for(int x=0;x<MiningEstate.SIZE;x++)for(int z=0;z<MiningEstate.SIZE;z++)if(!columns.get(x*MiningEstate.SIZE+z))for(int y=0;y<MiningEstate.HEIGHT;y++){
            var old=oldStates.get(source.at(x,y,z));var next=newStates.get(target.at(x,y,z));if(old.equals(next))continue;
            if(changes.size()==MAX_CELLS)return refused(selected,"变化超过安全上限，全部保留。");
            changes.put(piece.miningWorld(x,y,z),new Change(old,next,target.at(x,y,z)==Blueprint.Kind.MINING_CHEST));
        }
        if(changes.isEmpty())return refused(selected,"没有可安全升级的差异，全部保留。");
        if(obstructed(p,changes,box))return refused(selected,"升级将阻挡现有玩家、生物或物品；全部保留，请先离开候选填矿位置。");
        return new Survey(selected,Map.copyOf(changes),Map.copyOf(containers),columns,"");
    }
    private static void reserve(BitSet columns,int x,int z){for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++){int nx=x+dx,nz=z+dz;if(nx>=0&&nz>=0&&nx<MiningEstate.SIZE&&nz<MiningEstate.SIZE)columns.set(nx*MiningEstate.SIZE+nz);}}
    private static boolean obstructed(ServerPlayer p,Map<BlockPos,Change> changes,BoundingBox bounds){
        var region=new AABB(bounds.minX(),bounds.minY(),bounds.minZ(),bounds.maxX()+1,bounds.maxY()+1,bounds.maxZ()+1);
        var entities=new ArrayList<Entity>(p.serverLevel().getEntities((Entity)null,region.inflate(1),e->!e.isRemoved()));entities.add(p);
        for(var entity:entities){var bb=entity.getBoundingBox();for(var pos:BlockPos.betweenClosed(net.minecraft.util.Mth.floor(bb.minX),net.minecraft.util.Mth.floor(bb.minY),net.minecraft.util.Mth.floor(bb.minZ),net.minecraft.util.Mth.floor(bb.maxX),net.minecraft.util.Mth.floor(bb.maxY),net.minecraft.util.Mth.floor(bb.maxZ))){
            var c=changes.get(pos);if(c==null||c.after.isAir())continue;
            for(var shape:c.after.getCollisionShape(p.level(),pos).toAabbs())if(shape.move(pos.getX(),pos.getY(),pos.getZ()).intersects(bb))return true;
        }}return false;
    }

    @SubscribeEvent public static void commands(RegisterCommandsEvent e){
        e.getDispatcher().register(Commands.literal("dynasty").then(Commands.literal("upgrade_mine").requires(s->s.hasPermission(2))
            .then(Commands.literal("preview").executes(c->preview(c.getSource().getPlayerOrException())))
            .then(Commands.literal("confirm").executes(c->confirm(c.getSource().getPlayerOrException())))));
    }
    private static int preview(ServerPlayer p){
        PLANS.remove(p.getUUID());var survey=survey(p);if(!survey.refusal.isEmpty()){p.sendSystemMessage(Component.literal(survey.refusal+" 旧预览已作废；本次没有修改世界。"));return 0;}
        var b=survey.selection.piece.getBoundingBox();long added=survey.changes.values().stream().filter(Change::newChest).count();
        PLANS.put(p.getUUID(),new Plan(p.level().dimension().location().toString(),p.server.overworld().getGameTime()+1200,p.blockPosition(),survey));
        p.sendSystemMessage(Component.literal("旧矿庄升级预览：原版本 "+survey.selection.piece.miningLayout()+" → 6；范围 "+b.minX()+","+b.minY()+","+b.minZ()+" 至 "+b.maxX()+","+b.maxY()+","+b.maxZ()+"；候选 "+survey.changes.size()+" 格，新增矿箱 "+added+" 个；原容器 "+survey.containers.size()+" 个及周围 "+survey.columns.cardinality()+" 整列保留，不搬移或补货。材质符合原版本不能证明从未改建；无法确认请不要升级。确认前会再核对全部方块和容器NBT。请在60秒内、原位置8格内执行 /dynasty upgrade_mine confirm；预览不改世界。"));
        return survey.changes.size();
    }
    private static boolean same(Survey before,Survey after){
        return after.refusal.isEmpty()&&before.selection.start==after.selection.start&&before.selection.piece==after.selection.piece&&before.changes.equals(after.changes)&&before.containers.equals(after.containers)&&before.columns.equals(after.columns);
    }
    private static int confirm(ServerPlayer p){
        var plan=PLANS.remove(p.getUUID());if(plan==null||!plan.dimension.equals(p.level().dimension().location().toString())||p.server.overworld().getGameTime()>plan.expires||p.blockPosition().distSqr(plan.anchor)>64)return 0;
        var before=plan.survey;if(!same(before,survey(p))){p.sendSystemMessage(Component.literal("选中实例、方块、容器或实体已变化，本次没有升级；请重新预览。"));return 0;}
        for(var entry:before.changes.entrySet())if(net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.level.BlockEvent.BreakEvent(p.level(),entry.getKey(),entry.getValue().before,p))){p.sendSystemMessage(Component.literal("范围内有保护方块，本次没有升级；旧预览已作废。"));return 0;}
        // Protection listeners are arbitrary code; re-read the full native snapshot after all vetoes.
        if(!same(before,survey(p)))return 0;
        var original=before.selection.piece.createTag(StructurePieceSerializationContext.fromLevel(p.serverLevel()));
        var owner=p.serverLevel().getChunkSource().getChunkNow(before.selection.owner.x,before.selection.owner.z);if(owner==null)return 0;
        try{
            for(var entry:before.changes.entrySet()){
                // The whole final layout is known: suppress intermediate support/shape destruction.
                // Otherwise removing a room's floor can pop its lantern before that planned removal.
                var pos=entry.getKey();var c=entry.getValue();if(!p.level().setBlock(pos,c.after,18))throw new IllegalStateException("Rejected block write at "+pos.toShortString()+"; actual="+p.level().getBlockState(pos)+", expected="+c.before+", target="+c.after);
                if(c.newChest){
                    if(!(p.level().getBlockEntity(pos) instanceof net.minecraft.world.level.block.entity.ChestBlockEntity chest))throw new IllegalStateException("New mine chest missing");
                    MiningRewards.fillNew(chest,before.selection.piece.miningSeed()^pos.asLong());
                }
            }
        }catch(RuntimeException failure){
            // All prior block entities were excluded. Only our just-created chests can be cleared here.
            before.changes.forEach((pos,c)->{if(c.newChest&&p.level().getBlockEntity(pos) instanceof net.minecraft.world.level.block.entity.ChestBlockEntity chest)chest.clearContent();p.level().setBlock(pos,c.before,18);});
            com.mojang.logging.LogUtils.getLogger().warn("Selected native mine upgrade rolled back",failure);
            p.sendSystemMessage(Component.literal("升级写入失败，原候选方块已回退；未记录成功版本。"));return 0;
        }
        before.selection.piece.upgradeMining(before.columns);owner.setUnsaved(true);
        History.get(p.server).record(p.getUUID(),new Receipt(p.level().dimension().location().toString(),original, before.changes,before.containers));
        p.sendSystemMessage(Component.literal("已升级选中旧矿庄 "+before.changes.size()+" 格；原容器与支撑保留，实例内一次性版本和原状态回执已保存。该实例不能重复升级或补货。"));return before.changes.size();
    }
    @SubscribeEvent public static void logout(net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent e){PLANS.remove(e.getEntity().getUUID());}
    @SubscribeEvent public static void stopped(net.minecraftforge.event.server.ServerStoppedEvent e){PLANS.clear();}
    private MiningUpgrade(){}
}
