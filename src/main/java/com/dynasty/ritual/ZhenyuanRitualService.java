package com.dynasty.ritual;

import com.google.gson.JsonParser;
import com.mojang.logging.LogUtils;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.BucketItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ChestBlock;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityTeleportEvent;
import net.minecraftforge.event.entity.EntityTravelToDimensionEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.server.ServerLifecycleHooks;
import org.slf4j.Logger;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import static com.dynasty.ritual.ZhenyuanRitualSavedData.Session;

/** Server-authoritative offering, arena and one-time reward lifecycle. Never edits an existing save offline. */
@Mod.EventBusSubscriber(modid = "dynasty")
public final class ZhenyuanRitualService {
    private static final Logger LOG = LogUtils.getLogger();
    private static final Set<UUID> AUTHORIZED_TRAVEL = new HashSet<>();
    private static final ResourceLocation BLUEPRINT = new ResourceLocation("dynasty", "ritual/zhenyuan_altar.json");
    private static final String RECEIPT = "DynastyZhenyuanReward";
    private ZhenyuanRitualService() {}

    public static InteractionResult interact(ServerPlayer player, ZhenyuanNodeBlockEntity node) {
        ServerLevel level = player.serverLevel();
        if(player.isSpectator()) return InteractionResult.FAIL;
        if (node.getLevel() != level || player.distanceToSqr(Vec3.atCenterOf(node.getBlockPos())) > 36)
            return InteractionResult.FAIL;
        var data = ZhenyuanRitualSavedData.get(level);
        Session s = data.at(level, node.getCorePos());
        if (s == null || !node.getBlockPos().equals(s.nodes.get(node.getSlot()))) {
            hint(player, "这座供台尚未绑定。完整祭坛请由管理员使用 /dynasty_ritual place 安装。");
            return InteractionResult.CONSUME;
        }
        if(s.phaseOne && s.is("idle")) return ZhenyuanPhaseOne.interact(player,node,s,data);
        if (!s.is("idle")) { hint(player, s.is("charging") ? "四象已齐，金球正在聚能……" : "此坛的镇渊仪式已启动。"); return InteractionResult.CONSUME; }
        if (s.owner != null && !s.owner.equals(player.getUUID())) {
            hint(player, "这座祭坛已由另一位挑战者绑定，不能重复投放或代领奖励。"); return InteractionResult.CONSUME;
        }
        Session current = data.forOwner(player.getUUID());
        if (current != null && current != s) { hint(player, "你已有未结束的镇渊挑战。使用 /dynasty_ritual resume 或 status。"); return InteractionResult.CONSUME; }
        ItemStack held = player.getMainHandItem();
        String item = String.valueOf(ForgeRegistries.ITEMS.getKey(held.getItem()));
        var result = ZhenyuanRitualRules.offer(s.mask, node.getSlot(), item);
        if (result != ZhenyuanRitualRules.OfferResult.ACCEPTED) {
            hint(player, switch (result) {
                case ALREADY_OFFERED -> "此处已经供奉，不会再次消耗物品。";
                case FOUR_SIGILS_REQUIRED -> "先点亮东青龙、西白虎、南朱雀、北玄武四座供台，再向中央供奉混元珠。";
                default -> "此透明球中需要：" + ZhenyuanRitualRules.NAMES[node.getSlot()] + " ×1，手持后右键底座。";
            });
            return InteractionResult.CONSUME;
        }
        if (player.server.getLevel(ZhenyuanArena.DIMENSION) == null) {
            hint(player, "镇渊维度未加载，祭品未消耗。请确认整合包更新并重启服务器。"); return InteractionResult.CONSUME;
        }
        // All checks precede inventory mutation; server main-thread execution serializes competing clicks.
        s.owner = player.getUUID(); s.yaw = player.getYRot();
        s.mask |= 1 << node.getSlot();
        if (!player.getAbilities().instabuild) held.shrink(1);
        if (s.mask == ZhenyuanRitualRules.ALL) {
            s.phase = "charging"; s.chargeEnds = level.getServer().overworld().getGameTime() + ZhenyuanRitualRules.CHARGE_TICKS;
            hint(player, "五件祭品已齐：五秒后祭坛隐去，你将进入镇渊终战。紧急撤离：/dynasty_ritual escape。");
        } else hint(player, ZhenyuanRitualRules.NAMES[node.getSlot()] + " 已归位，金球获得第 " + Integer.bitCount(s.mask) + " 道灵环。");
        syncNodes(level, s); data.setDirty();
        level.sendParticles(ParticleTypes.ENCHANT, node.getBlockPos().getX()+.5, node.getBlockPos().getY()+1.2,
                node.getBlockPos().getZ()+.5, 50, .45, .5, .45, .08);
        level.playSound(null, node.getBlockPos(), SoundEvents.BEACON_ACTIVATE, SoundSource.BLOCKS, .8f, 1.1f);
        return InteractionResult.CONSUME;
    }

    /** Administrative installation is all-or-nothing for occupied space and records only our new blocks. */
    public static int install(ServerPlayer player, BlockPos core) {
        ServerLevel level = player.serverLevel();
        if (level.dimension().equals(ZhenyuanArena.DIMENSION)) { hint(player, "终战维度内不能安装祭坛。"); return 0; }
        var data = ZhenyuanRitualSavedData.get(level);
        Session existingSession=data.at(level,core);
        if(existingSession!=null&&existingSession.is("installing")) {
            removeOwnedAltar(level,existingSession); data.sessions.remove(existingSession.key); data.setDirty();
        } else if (existingSession != null) { hint(player, "此处已有仪式记录；不会覆盖或重置奖励。"); return 0; }
        Session pending=null;
        Map<BlockPos,BlockState> actualWrites=new LinkedHashMap<>();
        try (var reader = new InputStreamReader(level.getServer().getResourceManager().getResourceOrThrow(BLUEPRINT).open(), StandardCharsets.UTF_8)) {
            var root = JsonParser.parseReader(reader).getAsJsonObject();
            var rows = root.getAsJsonArray("blocks");
            if (rows.size() > 100_000) throw new IllegalArgumentException("Oversized altar blueprint");
            Map<BlockPos, BlockState> writes = new LinkedHashMap<>();
            Session s = new Session(level.dimension().location().toString(), core);
            pending=s; s.phase="installing"; s.phaseOne=true;
            for (var row : rows) {
                var o = row.getAsJsonObject();
                int x=o.get("x").getAsInt(), y=o.get("y").getAsInt(), z=o.get("z").getAsInt();
                if (Math.abs(x)>96 || Math.abs(z)>96 || y < -16 || y > 64) throw new IllegalArgumentException("Blueprint bounds");
                var state = BlockStateParser.parseForBlock(BuiltInRegistries.BLOCK.asLookup(), o.get("state").getAsString(), false).blockState();
                if (state.isAir()) continue;
                BlockPos p = core.offset(x,y,z);
                if (level.isOutsideBuildHeight(p)) throw new IllegalArgumentException("超出世界高度");
                if (!level.getWorldBorder().isWithinBounds(p)) throw new IllegalArgumentException("超出世界边界");
                BlockState existing = level.getBlockState(p);
                // Existing ground, dragon and mouth platform are never recorded or replaced.
                if (y < 0 && !existing.isAir()) continue;
                if (!existing.isAir()) { hint(player, "安装取消：" + p.toShortString() + " 已有方块，未改动建筑。请选空处。"); return 0; }
                writes.put(p, state);
                if (y >= 0) s.owned.put(p, BlockStateParser.serialize(state));
            }
            for (var n : root.getAsJsonArray("nodes")) {
                var o=n.getAsJsonObject(); int slot=o.get("slot").getAsInt();
                if (slot<0 || slot>4 || s.nodes.containsKey(slot)) throw new IllegalArgumentException("Duplicate/invalid node");
                int x=o.get("x").getAsInt(), y=o.get("y").getAsInt(), z=o.get("z").getAsInt();
                if(Math.abs(x)>96||Math.abs(z)>96||y<0||y>64) throw new IllegalArgumentException("Node bounds");
                BlockPos p=core.offset(x,y,z);
                if(level.isOutsideBuildHeight(p)||!level.getWorldBorder().isWithinBounds(p)||s.nodes.containsValue(p))
                    throw new IllegalArgumentException("Invalid/duplicate node position");
                if (!level.isEmptyBlock(p)) { hint(player, "供台位置有方块，安装已取消。"); return 0; }
                BlockState node=ZhenyuanRitualContent.NODE.get().defaultBlockState().setValue(ZhenyuanNodeBlock.SLOT,slot);
                writes.put(p,node); s.owned.put(p,BlockStateParser.serialize(node)); s.nodes.put(slot,p);
            }
            if (s.nodes.size()!=5) throw new IllegalArgumentException("Exactly five nodes required");
            // Record the ownership ledger before block writes; any interrupted installation is inspectable.
            data.sessions.put(s.key,s); data.setDirty();
            player.server.overworld().getDataStorage().save();
            for (var entry:writes.entrySet()) {
                if(!level.setBlock(entry.getKey(),entry.getValue(),3)) throw new IllegalStateException("方块放置被拒绝："+entry.getKey());
                actualWrites.put(entry.getKey(),entry.getValue());
            }
            for (var entry:s.nodes.entrySet()) {
                if (!(level.getBlockEntity(entry.getValue()) instanceof ZhenyuanNodeBlockEntity node)) throw new IllegalStateException("Missing altar node");
                node.configure(core,entry.getKey()); node.syncRitual(0,0);
            }
            level.getChunkSource().save(true);
            s.phase="idle"; data.setDirty(); player.server.overworld().getDataStorage().save();
            hint(player,"镇渊祭坛已安装："+core.toShortString()+"。只此新建祭坛会隐去，原地面和龙头保持不变。");
            return 1;
        } catch (Exception e) {
            // Roll back only blocks that this invocation placed and nobody subsequently replaced.
            for(var entry:actualWrites.entrySet()) if(level.getBlockState(entry.getKey()).equals(entry.getValue()))
                level.setBlock(entry.getKey(),Blocks.AIR.defaultBlockState(),3);
            if(pending!=null) data.sessions.remove(pending.key,pending);
            data.setDirty(); LOG.error("Cannot install Zhenyuan altar",e); hint(player,"安装失败，已回滚本次写入："+e.getMessage()); return 0;
        }
    }

    /**
     * Trusted runtime importer hook. The caller must pass ONLY altar voxels its own placement job just
     * created in previously empty space, never the whole dragon/platform or pre-existing matches.
     * All coordinates are absolute. Core is the safe original ground-level return feet position.
     */
    public static boolean bindImportedAltar(ServerLevel level,BlockPos core,Map<BlockPos,BlockState> newlyPlacedAltar,
                                             Map<Integer,BlockPos> nodes) {
        if(level.dimension().equals(ZhenyuanArena.DIMENSION)||newlyPlacedAltar.isEmpty()||newlyPlacedAltar.size()>100_000
                ||nodes.size()!=5||new HashSet<>(nodes.values()).size()!=5) return false;
        var data=ZhenyuanRitualSavedData.get(level);
        Session s=new Session(level.dimension().location().toString(),core);
        s.phaseOne=true;
        for(var e:newlyPlacedAltar.entrySet()) {
            BlockPos p=e.getKey();
            if(Math.abs(p.getX()-core.getX())>96||Math.abs(p.getZ()-core.getZ())>96||p.getY()-core.getY()>64
                    ||level.isOutsideBuildHeight(p)||!level.getWorldBorder().isWithinBounds(p)||e.getValue().isAir()) return false;
            if(p.getY()>=core.getY()) s.owned.put(p.immutable(),BlockStateParser.serialize(e.getValue()));
        }
        for(int slot=0;slot<5;slot++) {
            BlockPos p=nodes.get(slot);
            if(p==null||!s.owned.containsKey(p)) return false;
            BlockState state=newlyPlacedAltar.get(p);
            if(!state.is(ZhenyuanRitualContent.NODE.get())||state.getValue(ZhenyuanNodeBlock.SLOT)!=slot) return false;
            s.nodes.put(slot,p.immutable());
        }
        Session previous=data.at(level,core);
        if(previous!=null) {
            // A builder may crash AFTER this durable bind but BEFORE its own final job checkpoint.
            // Acknowledge that exact immutable binding only. Never reset offerings, ownership, boss,
            // rewards, or live block states, even if gameplay progressed before the builder retries.
            return !previous.is("installing")&&previous.owned.equals(s.owned)&&previous.nodes.equals(s.nodes);
        }
        for(var e:newlyPlacedAltar.entrySet()) if(!level.getBlockState(e.getKey()).equals(e.getValue())) return false;
        for(BlockPos p:s.nodes.values()) if(!(level.getBlockEntity(p) instanceof ZhenyuanNodeBlockEntity)) return false;
        if(!level.getBlockState(core.below()).isFaceSturdy(level,core.below(),Direction.UP)) return false;
        for(var e:s.nodes.entrySet()) {
            var node=(ZhenyuanNodeBlockEntity)level.getBlockEntity(e.getValue()); node.configure(core,e.getKey()); node.syncRitual(0,0);
        }
        level.getChunkSource().save(true);
        data.sessions.put(s.key,s); data.setDirty(); level.getServer().overworld().getDataStorage().save();
        return true;
    }

    private static ServerLevel origin(MinecraftServer server, Session s) {
        ResourceLocation id=ResourceLocation.tryParse(s.dimension);
        return id==null?null:server.getLevel(ResourceKey.create(Registries.DIMENSION,id));
    }
    static void syncNodes(ServerLevel level,Session s) {
        for (var entry:s.nodes.entrySet()) if(level.getBlockEntity(entry.getValue()) instanceof ZhenyuanNodeBlockEntity node)
            if(node.getCorePos().equals(s.core)) { node.syncTimeline(s); node.syncRitual(s.mask,ZhenyuanRitualRules.visualStage(s.phase)); }
    }
    /** Never replaces arbitrary blocks with air: exact original owned state or the configured owned node only. */
    public static int removeOwnedAltar(ServerLevel level,Session s) {
        int removed=0;
        for(var entry:s.owned.entrySet()) {
            BlockPos p=entry.getKey();
            if(p.getY()<s.core.getY()) continue;
            BlockState at=level.getBlockState(p);
            boolean match=BlockStateParser.serialize(at).equals(entry.getValue());
            if(at.is(ZhenyuanRitualContent.NODE.get())&&!s.is("installing")) match=level.getBlockEntity(p) instanceof ZhenyuanNodeBlockEntity node
                    && node.getCorePos().equals(s.core) && p.equals(s.nodes.get(node.getSlot()));
            if(match) { level.setBlock(p,Blocks.AIR.defaultBlockState(),3); removed++; }
        }
        s.removed=true;
        return removed;
    }

    private static void begin(ServerPlayer player,Session s,ZhenyuanRitualSavedData data) {
        ServerLevel arena=player.server.getLevel(ZhenyuanArena.DIMENSION), home=origin(player.server,s);
        if(arena==null || home==null) { s.phase="paused"; data.setDirty(); if(home!=null)syncNodes(home,s); hint(player,"维度暂不可用，仪式已暂停，祭品保留。"); return; }
        try {
            if(s.arenaIndex<0) {
                if(data.nextArena>=1024*1024) throw new IllegalStateException("镇渊战场预留容量已满，请管理员检查");
                s.arenaIndex=data.nextArena++; data.setDirty();
                // Flush the monotonically increasing allocation before any cell is constructed.
                player.server.overworld().getDataStorage().save();
            }
            if(!s.arenaReady) {
                // A crash while building may only leave this session's reserved cell half-built.
                // Replaying this deterministic build is safe; no boss/player enters before the commit.
                ZhenyuanArena.build(arena,s.arenaIndex);
                arena.getChunkSource().save(true);
                s.arenaReady=true; data.setDirty(); player.server.overworld().getDataStorage().save();
            } else ZhenyuanArena.forceChunks(arena,s.arenaIndex,true);
            if(s.boss==null) {
                Mob boss=ZhenyuanBosses.FINAL_BOSS.get().create(arena);
                if(boss==null) throw new IllegalStateException("Boss type unavailable");
                BlockPos c=ZhenyuanArena.center(s.arenaIndex);
                boss.moveTo(c.getX()+.5,c.getY(),c.getZ()+.5,0,0); boss.setPersistenceRequired();
                boss.getPersistentData().putString("DynastyZhenyuanSession",s.key);
                if(!arena.addFreshEntity(boss)) throw new IllegalStateException("Boss spawn rejected");
                s.boss=boss.getUUID();
                snapshot(s,boss);
            }
            Mob prepared=resolveBoss(arena,s);
            if(prepared==null) throw new IllegalStateException("Boss实体尚未加载；请稍后resume，未发奖也未重新扣祭品");
            s.phase="active"; s.bossFightStarted=s.bossIntroTick>=280; data.setDirty();
            if(!s.removed) { removeOwnedAltar(home,s); home.getChunkSource().save(true); }
            player.server.overworld().getDataStorage().save();
            if(!enter(player,s)) throw new IllegalStateException("跨维度传送被其它保护规则取消，挑战已保留");
            hint(player,"镇渊终战已开启。红色法阵是攻击预警，离开标记再反击。紧急撤离 /dynasty_ritual escape。");
        } catch(Exception e) {
            LOG.error("Zhenyuan encounter preparation failed",e); pause(player.server,s,data);
            hint(player,"战场准备失败，挑战已暂停且祭品保留。可稍后 /dynasty_ritual resume。");
        }
    }
    private static boolean enter(ServerPlayer player,Session s) {
        ServerLevel arena=player.server.getLevel(ZhenyuanArena.DIMENSION);
        if(arena==null || s.arenaIndex<0) return false;
        ZhenyuanArena.forceChunks(arena,s.arenaIndex,true);
        BlockPos arrival=ZhenyuanArena.arrival(s.arenaIndex);
        if((player.serverLevel()!=arena || !ZhenyuanArena.interior(s.arenaIndex).contains(player.position()))
                && !teleport(player,arena,arrival,180)) return false;
        if(arena.getEntity(s.boss) instanceof ZhenyuanSovereign mob) { mob.applyEncounterGate(true); if(mob.combatReady())mob.setTarget(player); }
        return true;
    }
    private static void snapshot(Session s,Mob boss) {
        if(boss.isAlive()) s.bossSnapshot=boss.saveWithoutId(new CompoundTag());
    }
    private static Mob resolveBoss(ServerLevel arena,Session s) {
        if(s.boss==null) return null;
        BlockPos c=ZhenyuanArena.center(s.arenaIndex); arena.getChunkAt(c.offset(0,0,-13));
        if(arena.getEntity(s.boss) instanceof Mob mob) return mob;
        if(s.bossSnapshot.isEmpty()) return null;
        Mob restored=ZhenyuanBosses.FINAL_BOSS.get().create(arena);
        if(restored==null) return null;
        restored.load(s.bossSnapshot.copy()); restored.setUUID(s.boss); restored.setPersistenceRequired();
        // UUID uniqueness prevents a delayed chunk entity from creating a second copy of this boss.
        return arena.addFreshEntity(restored)?restored:null;
    }
    private static boolean teleport(ServerPlayer player,ServerLevel level,BlockPos p,float yaw) {
        AUTHORIZED_TRAVEL.add(player.getUUID());
        try {
            player.stopRiding(); player.setDeltaMovement(Vec3.ZERO); player.fallDistance=0; player.clearFire();
            player.teleportTo(level,p.getX()+.5,p.getY(),p.getZ()+.5,yaw,0); player.invulnerableTime=100;
            return player.serverLevel()==level&&player.distanceToSqr(Vec3.atBottomCenterOf(p))<.01;
        } finally { AUTHORIZED_TRAVEL.remove(player.getUUID()); }
    }
    public static boolean standable(ServerLevel level,BlockPos p) {
        return level.isEmptyBlock(p)&&level.isEmptyBlock(p.above())&&level.getFluidState(p).isEmpty()
                &&level.getBlockState(p.below()).isFaceSturdy(level,p.below(),Direction.UP);
    }
    private static BlockPos safeNear(ServerLevel level,BlockPos core) {
        level.getChunkAt(core);
        if(standable(level,core)) return core;
        for(int r=1;r<=12;r++) for(int y=-2;y<=5;y++) for(int x=-r;x<=r;x++) for(int z=-r;z<=r;z++)
            if((Math.abs(x)==r||Math.abs(z)==r)&&standable(level,core.offset(x,y,z))) return core.offset(x,y,z);
        return null;
    }
    private static boolean returnPlayer(ServerPlayer player,Session s) {
        ServerLevel home=origin(player.server,s);
        BlockPos target=home==null?null:safeNear(home,s.core);
        if(target==null) {
            home=player.server.overworld(); BlockPos spawn=home.getSharedSpawnPos();
            target=safeNear(home,home.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,spawn));
        }
        if(target==null) { hint(player,"返回点被堵住，未破坏任何方块；请管理员清空原祭坛中心或主世界出生点后重试 escape。"); return false; }
        if(teleport(player,home,target,s.yaw)) return true;
        hint(player,"传送被其它服务器保护规则拦截，未发放奖励；挑战记录保留，可修复规则后重试 escape。");
        return false;
    }
    public static int escape(ServerPlayer player) {
        var data=ZhenyuanRitualSavedData.get(player.serverLevel()); Session s=data.forOwner(player.getUUID());
        if(s==null) {
            if(player.level().dimension().equals(ZhenyuanArena.DIMENSION)) {
                var home=player.server.overworld(); var p=safeNear(home,home.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,home.getSharedSpawnPos()));
                if(p!=null) return teleport(player,home,p,0)?1:0;
            }
            hint(player,"你没有进行中的镇渊挑战。"); return 0;
        }
        if(s.is("victory")) return claim(player);
        if(s.is("idle")) { hint(player,"供奉尚未结束；已投放的祭品保留在祭坛。"); return 0; }
        pause(player.server,s,data);
        if(!returnPlayer(player,s)) return 0;
        hint(player,"已安全撤离，未发放通关奖励；挑战和 Boss 血量保留，使用 /dynasty_ritual resume 继续。"); return 1;
    }
    private static void pause(MinecraftServer server,Session s,ZhenyuanRitualSavedData data) {
        s.phase="paused"; data.setDirty();
        ServerLevel arena=server.getLevel(ZhenyuanArena.DIMENSION);
        if(arena!=null&&s.arenaIndex>=0) {
            if(s.boss!=null&&arena.getEntity(s.boss) instanceof Mob mob) {
                mob.setTarget(null); mob.setNoAi(true);
                if(mob instanceof ZhenyuanSovereign sovereign) sovereign.applyEncounterGate(false);
                snapshot(s,mob);
            }
            ZhenyuanArena.forceChunks(arena,s.arenaIndex,false);
        }
        ServerLevel home=origin(server,s); if(home!=null&&!s.removed) syncNodes(home,s);
    }
    public static int resume(ServerPlayer player) {
        var data=ZhenyuanRitualSavedData.get(player.serverLevel()); Session s=data.forOwner(player.getUUID());
        if(s==null) { hint(player,"没有待恢复的挑战。"); return 0; }
        if(s.phaseOne&&s.is("idle")) { hint(player,"献祭演出会在原祭坛附近自动继续；已接受的贡品不会再次扣除。"); return 1; }
        if(s.is("victory")) return claim(player);
        if(s.mask!=31) { hint(player,"祭品尚未齐全，请继续供奉四象与中央。"); return 0; }
        if(s.is("active")) return enter(player,s)?1:0;
        s.phase="charging"; s.chargeEnds=player.server.overworld().getGameTime()+ZhenyuanRitualRules.CHARGE_TICKS;
        ServerLevel arena=player.server.getLevel(ZhenyuanArena.DIMENSION);
        if(arena!=null&&s.arenaIndex>=0) ZhenyuanArena.forceChunks(arena,s.arenaIndex,true);
        ServerLevel home=origin(player.server,s); if(home!=null&&!s.removed) syncNodes(home,s);
        data.setDirty(); hint(player,"镇渊之门重新聚能，五秒后继续挑战；不会重复消耗祭品。"); return 1;
    }

    public static int claim(ServerPlayer player) {
        var data=ZhenyuanRitualSavedData.get(player.serverLevel()); Session s=data.forOwner(player.getUUID());
        if(s==null||!s.is("victory")) { hint(player,"只有已通关且未领宝箱的挑战可以领取。"); return 0; }
        if(!s.returnedToOrigin||player.level().dimension().equals(ZhenyuanArena.DIMENSION)) {
            if(!returnPlayer(player,s)) return 0;
            s.returnedToOrigin=true; data.setDirty();
        }
        boolean issued;
        try { issued=depositReward(player,s,data); }
        catch(Exception error) {
            LOG.error("Zhenyuan reward commit failed; pending chest stays sealed",error);
            hint(player,"宝箱正在等待安全落盘，已暂时封存，请修复磁盘问题后重试 claim；不会重填已领取奖励。");
            issued=false;
        }
        ServerLevel arena=player.server.getLevel(ZhenyuanArena.DIMENSION);
        if(arena!=null&&s.arenaIndex>=0) ZhenyuanArena.forceChunks(arena,s.arenaIndex,false);
        return issued?1:0;
    }

    /** Chest-only rewards. The receipt/ledger are never reset by looting, breaking, logout, or replaying a death event. */
    public static boolean depositReward(ServerPlayer player,Session s,ZhenyuanRitualSavedData data) {
        if(!s.is("victory")) return false;
        if(s.rewardIssued) {
            // The receipt may have been committed immediately before a process/power failure.
            // Fail closed rather than re-minting items after someone has already looted the chest.
            s.phase="returned"; data.setDirty();
            hint(player,"此挑战的宝箱奖励已有持久化发放记录，不会自动重填；若服务器异常中断，请管理员核对宝箱收据。");
            return false;
        }
        ServerLevel level=origin(player.server,s); if(level==null) return false;
        Direction forward=Direction.fromYRot(s.yaw);
        BlockPos p=s.rewardPos;
        if(p!=null&&level.getBlockEntity(p) instanceof ChestBlockEntity receipt && s.key.equals(receipt.getPersistentData().getString(RECEIPT))) {
            level.getChunkSource().save(true);
            s.rewardIssued=true; s.rewardPending=false; s.phase="returned"; data.setDirty();
            player.server.overworld().getDataStorage().save(); return false;
        }
        if(s.rewardPending && p!=null && !standable(level,p)) {
            hint(player,"奖励位置已有其他方块，未覆盖它；请清空 "+p.toShortString()+" 后使用 claim。"); return false;
        }
        if(p==null || !standable(level,p)) {
            p=null;
            for(int distance=3;distance<=10;distance++) {
                BlockPos candidate=s.core.relative(forward,distance);
                if(standable(level,candidate)&&!adjacentChest(level,candidate)) { p=candidate; break; }
            }
        }
        if(p==null) { hint(player,"已通关；前方宝箱位置被占用，奖励保留。清空前方3–10格后使用 /dynasty_ritual claim。"); return false; }
        s.rewardPos=p;
        // Prepare a fixed destination first. No network tick occurs between this and the final commit.
        // After a crash: a matching chest receipt is acknowledged without ever refilling its inventory.
        s.rewardPending=true; data.setDirty(); player.server.overworld().getDataStorage().save();
        if(!level.setBlock(p,Blocks.CHEST.defaultBlockState().setValue(ChestBlock.FACING,forward.getOpposite()),3)
                ||!(level.getBlockEntity(p) instanceof ChestBlockEntity chest)) {
            // No items were created. Safe to retry a rejected placement, without replacing the obstruction.
            data.setDirty(); return false;
        }
        chest.getPersistentData().putString(RECEIPT,s.key);
        chest.setCustomName(Component.literal("镇渊终战 · 天命宝匣"));
        int slot=0;
        for(ItemStack stack:new ItemStack[]{item("dynasty:dragon_emperor_seal",2),item("dynasty:xuantian_jade",32),
                item("dynasty:dragon_crystal",64),item("dynasty:gold_coin",32),new ItemStack(Items.NETHERITE_INGOT,8),
                new ItemStack(Items.ENCHANTED_GOLDEN_APPLE,4),new ItemStack(Items.NETHER_STAR,1)}) {
            if(!stack.isEmpty()) chest.setItem(slot++,stack);
        }
        chest.setChanged(); level.getChunkAt(p).setUnsaved(true);
        // Persist the real chest, then close the durable receipt. Recovery never refills an issued chest.
        level.getChunkSource().save(true);
        s.rewardIssued=true; s.rewardPending=false; s.phase="returned";
        data.setDirty(); player.server.overworld().getDataStorage().save();
        hint(player,"镇渊之主已伏诛。祭坛已消散，前方 "+p.toShortString()+" 的天命宝匣是本次唯一奖励。");
        return true;
    }
    private static boolean adjacentChest(ServerLevel level,BlockPos p) {
        for(Direction d:Direction.Plane.HORIZONTAL) if(level.getBlockState(p.relative(d)).is(Blocks.CHEST)) return true;
        return false;
    }
    private static ItemStack item(String id,int count) {
        var item=ForgeRegistries.ITEMS.getValue(new ResourceLocation(id));
        return item==null?ItemStack.EMPTY:new ItemStack(item,count);
    }
    public static boolean isEncounterActive(UUID bossId,ServerLevel level) {
        Session s=ZhenyuanRitualSavedData.get(level).forBoss(bossId);
        return s!=null&&s.is("active")&&participant(level,bossId)!=null;
    }
    public static ServerPlayer participant(ServerLevel level,UUID bossId) {
        Session s=ZhenyuanRitualSavedData.get(level).forBoss(bossId);
        if(s==null||s.owner==null) return null;
        for(ServerPlayer player:level.players())if(player.isAlive()&&!player.isSpectator()&&(player.getUUID().equals(s.owner)||s.participants.contains(player.getUUID()))
                &&s.arenaIndex>=0&&ZhenyuanArena.interior(s.arenaIndex).contains(player.position()))return player;
        return null;
    }
    public static int join(ServerPlayer player,ServerPlayer leader) {
        var data=ZhenyuanRitualSavedData.get(player.serverLevel());var s=data.forOwner(leader.getUUID());
        if(player.isSpectator()||s==null||!s.is("active")||data.forOwner(player.getUUID())!=null) {hint(player,"只能加入在线挑战者正在进行的镇渊挑战，且自己不能已有挑战。");return 0;}
        s.participants.add(player.getUUID());data.setDirty();
        if(!enter(player,s)){s.participants.remove(player.getUUID());data.setDirty();return 0;}
        hint(player,"已加入同一战场，共用同一 Boss 和演出进度；奖励为队伍共用宝箱。");return 1;
    }
    public static int status(ServerPlayer player) {
        Session s=ZhenyuanRitualSavedData.get(player.serverLevel()).forOwner(player.getUUID());
        if(s==null) { hint(player,"无进行中的挑战。管理员 /dynasty_ritual place 安装完整祭坛。"); return 0; }
        hint(player,"供奉 "+Integer.bitCount(s.mask)+"/5 · 状态 "+s.phase+" · 原祭坛 "+s.core.toShortString()
                +(s.phaseOne?" · 演出 "+s.ritualStage+" ("+s.ritualTicks+" tick)":"")
                +" · resume 继续 / escape 撤离 / claim 领取已通关宝箱"); return 1;
    }
    static void hint(ServerPlayer player,String text) { player.sendSystemMessage(Component.literal("§b[镇渊] §r"+text)); }

    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if(event.phase!=TickEvent.Phase.END) return;
        MinecraftServer server=ServerLifecycleHooks.getCurrentServer(); if(server==null) return;
        var data=ZhenyuanRitualSavedData.get(server.overworld()); long now=server.overworld().getGameTime();
        for(Session s:data.sessions()) {
            ServerPlayer player=s.owner==null?null:server.getPlayerList().getPlayer(s.owner);
            if(player==null)for(UUID member:s.participants){player=server.getPlayerList().getPlayer(member);if(player!=null)break;}
            if(s.phaseOne&&s.is("idle")||now%10==0) advanceSession(server,s,data,player,now);
        }
        // An orphaned arena player is never stranded because a session record went missing.
        for(ServerPlayer player:server.getPlayerList().getPlayers()) if(player.serverLevel().dimension().equals(ZhenyuanArena.DIMENSION)
                &&data.forOwner(player.getUUID())==null) escape(player);
    }

    /** Deterministic transition seam: production supplies the connected owner and world clock; tests use a real server FakePlayer. */
    static void advanceSession(MinecraftServer server,Session s,ZhenyuanRitualSavedData data,ServerPlayer player,long now) {
        if(s.phaseOne&&s.is("idle")) {
            ServerLevel home=origin(server,s);
            if(home!=null&&ZhenyuanPhaseOne.tick(home,s,data,player))begin(player,s,data);
            return;
        }
        if(player==null&&(s.is("active")||s.is("charging"))) { pause(server,s,data); return; }
        if(player==null&&s.is("victory")) {
            ServerLevel arena=server.getLevel(ZhenyuanArena.DIMENSION);
            if(arena!=null&&s.arenaIndex>=0) ZhenyuanArena.forceChunks(arena,s.arenaIndex,false);
            return;
        }
        if(s.is("charging")&&player!=null) {
            ServerLevel home=origin(server,s);
            if(home!=null&&!s.removed) home.sendParticles(ParticleTypes.END_ROD,s.core.getX()+.5,s.core.getY()+2.5,s.core.getZ()+.5,15,1.5,1,1.5,.03);
            if(now>=s.chargeEnds) begin(player,s,data);
        } else if(s.is("active")&&player!=null) {
            ServerLevel arena=server.getLevel(ZhenyuanArena.DIMENSION);
            if(arena==null) { pause(server,s,data); returnPlayer(player,s); return; }
            Mob boss=resolveBoss(arena,s);
            if(boss==null) { pause(server,s,data); returnPlayer(player,s); hint(player,"Boss数据尚未恢复，已安全暂停，可稍后resume。"); return; }
            if(boss instanceof ZhenyuanSovereign sovereign) sovereign.applyEncounterGate(true);
            if(!boss.isNoAi()) boss.setTarget(player);
            if(now%100==0) { snapshot(s,boss); data.setDirty(); }
            // Entry is the only placement operation. Never re-anchor a participant from
            // the encounter tick: feet on FLOOR_Y+1 were outside deflate(.4), causing
            // a position/velocity/look reset every ten ticks, including during INTRO.
            // The arena shell contains combat; explicit resume/escape handles travel.
            if(!s.removed) { ServerLevel home=origin(server,s); if(home!=null) { removeOwnedAltar(home,s); home.getChunkSource().save(true); data.setDirty(); } }
        } else if(s.is("victory")&&player!=null&&!s.returnedToOrigin&&now>=s.victoryAt+60) claim(player);
    }

    @SubscribeEvent(priority=EventPriority.HIGHEST) public static void death(LivingDeathEvent event) {
        if(!(event.getEntity().level() instanceof ServerLevel level)) return;
        var data=ZhenyuanRitualSavedData.get(level);
        if(event.getEntity() instanceof ServerPlayer player) {
            Session s=data.forOwner(player.getUUID());
            if(s!=null&&s.is("active")&&level.dimension().equals(ZhenyuanArena.DIMENSION)) {
                // Defeat, not a destructive death: do not scatter the player's inventory into an unloaded arena.
                event.setCanceled(true); player.setHealth(Math.max(1,player.getMaxHealth()*.25f));
                pause(player.server,s,data);
                boolean returned=returnPlayer(player,s);
                hint(player,returned?"本次挑战失利，已保留物品并撤离；没有奖励。/dynasty_ritual resume 可继续。"
                        :"本次挑战已安全暂停、Boss停止行动，物品保留且没有奖励；传送受阻，请修复保护规则后重试 escape。");
            }
            return;
        }
    }
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void bossDeath(LivingDeathEvent event) {
        if(event.isCanceled() || event.getEntity() instanceof ServerPlayer || !(event.getEntity().level() instanceof ServerLevel level)) return;
        var data=ZhenyuanRitualSavedData.get(level);
        Session s=data.forBoss(event.getEntity().getUUID());
        if(s!=null&&s.is("active")&&level.dimension().equals(ZhenyuanArena.DIMENSION)) {
            s.phase="victory"; s.victoryAt=level.getServer().overworld().getGameTime(); data.setDirty();
            s.bossDefeated=true;
            net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new ZhenyuanVictoryEvent(s.owner,s.key,s.dimension,s.core));
            ServerPlayer owner=s.owner==null?null:level.getServer().getPlayerList().getPlayer(s.owner);
            if(owner!=null) hint(owner,"终战已胜！三秒后回到龙嘴原祭坛中心，奖励只会存入前方宝箱。");
        }
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent event) {
        if(event.getEntity() instanceof ServerPlayer player) {
            var data=ZhenyuanRitualSavedData.get(player.serverLevel()); Session s=data.forOwner(player.getUUID());
            if(s!=null&&(s.is("active")||s.is("charging"))) {
                boolean other=player.server.getPlayerList().getPlayers().stream().anyMatch(p->p!=player&&p.isAlive()
                        &&(p.getUUID().equals(s.owner)||s.participants.contains(p.getUUID()))&&p.serverLevel().dimension().equals(ZhenyuanArena.DIMENSION));
                if(!other)pause(player.server,s,data);
            }
            else if(s!=null&&s.is("victory")&&s.arenaIndex>=0) {
                ServerLevel arena=player.server.getLevel(ZhenyuanArena.DIMENSION);
                if(arena!=null) ZhenyuanArena.forceChunks(arena,s.arenaIndex,false);
            }
        }
    }
    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent event) {
        if(event.getEntity() instanceof ServerPlayer player) player.server.execute(()->{
            var data=ZhenyuanRitualSavedData.get(player.serverLevel()); Session s=data.forOwner(player.getUUID());
            if(s!=null&&s.is("active")) {
                if(enter(player,s)) hint(player,"已恢复未结束的镇渊终战。");
                else {pause(player.server,s,data);hint(player,"恢复传送被保护规则拦截，挑战已暂停。");}
            }
            else if(s!=null&&s.is("paused")&&player.level().dimension().equals(ZhenyuanArena.DIMENSION)) returnPlayer(player,s);
            else if(s!=null&&s.is("charging")) { s.chargeEnds=player.server.overworld().getGameTime()+100; data.setDirty(); }
            else if(s==null&&player.level().dimension().equals(ZhenyuanArena.DIMENSION)) escape(player);
        });
    }
    @SubscribeEvent public static void respawn(PlayerEvent.PlayerRespawnEvent event) {
        if(event.getEntity() instanceof ServerPlayer player) {
            var data=ZhenyuanRitualSavedData.get(player.serverLevel()); Session s=data.forOwner(player.getUUID());
            if(s!=null&&s.is("active")) { pause(player.server,s,data); player.server.execute(()->returnPlayer(player,s)); }
        }
    }
    @SubscribeEvent public static void travel(EntityTravelToDimensionEvent event) {
        if(!(event.getEntity() instanceof ServerPlayer)&&event.getEntity().level().dimension().equals(ZhenyuanArena.DIMENSION)) {
            event.setCanceled(true);return;
        }
        if(event.getEntity() instanceof ServerPlayer player && !AUTHORIZED_TRAVEL.contains(player.getUUID())
                && (event.getDimension().equals(ZhenyuanArena.DIMENSION)||player.level().dimension().equals(ZhenyuanArena.DIMENSION))) {
            event.setCanceled(true); hint(player,"镇渊战场不能用传送道具离开；紧急撤离 /dynasty_ritual escape。");
        }
    }
    @SubscribeEvent public static void teleport(EntityTeleportEvent event) {
        if(event.getEntity().level().dimension().equals(ZhenyuanArena.DIMENSION)) event.setCanceled(true);
    }
    @SubscribeEvent public static void breakBlock(BlockEvent.BreakEvent event) {
        if(event.getLevel() instanceof ServerLevel level && (level.dimension().equals(ZhenyuanArena.DIMENSION)||pendingRewardAt(level,event.getPos()))) event.setCanceled(true);
    }
    @SubscribeEvent public static void placeBlock(BlockEvent.EntityPlaceEvent event) {
        if(event.getLevel() instanceof ServerLevel level && level.dimension().equals(ZhenyuanArena.DIMENSION)) event.setCanceled(true);
    }
    @SubscribeEvent public static void useBlock(PlayerInteractEvent.RightClickBlock event) {
        // Protect the scenery without swallowing food, bows or other held-item use
        // merely because the crosshair happens to point at the floor or wall.
        if(event.getLevel().dimension().equals(ZhenyuanArena.DIMENSION))
            event.setUseBlock(net.minecraftforge.eventbus.api.Event.Result.DENY);
        else if(event.getLevel() instanceof ServerLevel level&&pendingRewardAt(level,event.getPos())) event.setCanceled(true);
    }
    @SubscribeEvent public static void useItem(PlayerInteractEvent.RightClickItem event) {
        if(event.getLevel().dimension().equals(ZhenyuanArena.DIMENSION)
                &&(event.getItemStack().getItem() instanceof BlockItem || event.getItemStack().getItem() instanceof BucketItem)) event.setCanceled(true);
    }
    @SubscribeEvent public static void explosion(ExplosionEvent.Detonate event) {
        if(event.getLevel().dimension().equals(ZhenyuanArena.DIMENSION)) event.getAffectedBlocks().clear();
    }
    private static boolean pendingRewardAt(ServerLevel level,BlockPos pos) {
        return ZhenyuanRitualSavedData.get(level).sessions().stream().anyMatch(s->s.rewardPending&&!s.rewardIssued
                &&level.dimension().location().toString().equals(s.dimension)&&pos.equals(s.rewardPos));
    }
}
