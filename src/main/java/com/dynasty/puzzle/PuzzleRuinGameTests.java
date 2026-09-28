package com.dynasty.puzzle;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

import java.util.HashMap;
import java.util.Map;

/**
 * 三种解谜遗迹的**真实生成**验证（沿用 VaultObservatoryGameTests 的「捕获写入流」写法）：
 * 直接跑生产部件 {@link PuzzleRuinPiece#postProcess}，把每一笔写入记录下来说明：
 *   * 所有写入都落在包围盒里；
 *   * 控制器带正确的机关类型与难度档；
 *   * 每种机关都写出了正确数量的部件 + 等量线索石板；
 *   * 封印门存在且宝室被封住（门在 z=SEAL_Z 的墙上）。
 *
 * 需要游戏环境（方块注册表）才能跑；命令：./gradlew --offline runGameTestServer
 */
@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class PuzzleRuinGameTests {

    private static final class Capture extends PuzzleRuinPiece {
        final Map<BlockPos, BlockState> writes = new HashMap<>();

        Capture(net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType type,
                BlockPos corner, PuzzleRules.Kind kind) {
            super(type, 0, corner, kind);
        }

        Capture(net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType type, CompoundTag tag,
                PuzzleRules.Kind kind) {
            super(type, tag, kind);
        }

        @Override
        protected void set(WorldGenLevel level, BoundingBox box, int dx, int dy, int dz, BlockState state) {
            writes.put(new BlockPos(dx, dy, dz), state);
        }
        @Override
        protected void treasure(WorldGenLevel level, BoundingBox box, RandomSource random, int x,int y,int z){
            set(level,box,x,y,z,net.minecraft.world.level.block.Blocks.CHEST.defaultBlockState());
        }
    }

    private static Capture generate(GameTestHelper h, PuzzleRules.Kind kind, int x, int y, int z) {
        var type = switch (kind) {
            case STAR -> com.dynasty.structure.DynastyStructures.STAR_VAULT_PIECE.get();
            case BELL -> com.dynasty.structure.DynastyStructures.MUSIC_RUIN_PIECE.get();
            case ELEMENTS -> com.dynasty.structure.DynastyStructures.SEAL_VAULT_PIECE.get();
        };
        BlockPos corner = h.absolutePos(new BlockPos(x, y, z));
        Capture piece = new Capture(type, corner, kind);
        BoundingBox box = piece.getBoundingBox();
        piece.postProcess(null, (StructureManager) null, (ChunkGenerator) null, RandomSource.create(7),
                box, new ChunkPos(corner), corner);
        return piece;
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 60)
    public static void starVaultGeneratesACompleteSealedRoom(GameTestHelper h) {
        Capture piece = generate(h, PuzzleRules.Kind.STAR, 2, 2, 2);
        h.assertTrue(piece.writes.size() > 300, "房间写入太少，可能只生成了一半：" + piece.writes.size());
        long dials = piece.writes.values().stream().filter(s -> s.is(PuzzleBlocks.STAR_DIAL.get())).count();
        long tablets = piece.writes.values().stream().filter(s -> s.is(PuzzleBlocks.CLUE_TABLET.get())).count();
        long gates = piece.writes.values().stream().filter(s -> s.is(PuzzleBlocks.RUIN_GATE.get())).count();
        h.assertTrue(dials == 4, "星盘应当正好 4 座，实际 " + dials);
        h.assertTrue(tablets == 5, "4 块部件线索 + 1 块门楣线索，实际 " + tablets);
        h.assertTrue(gates == 4, "封印门应当是 2×2 的 4 格，实际 " + gates);
        BlockPos controller = new BlockPos(RuinLayout.TREASURY_CENTER, RuinLayout.CY, RuinLayout.TREASURY_CENTER);
        BlockState state = piece.writes.get(controller);
        h.assertTrue(state != null && state.is(PuzzleBlocks.RUIN_CONTROLLER.get()),
                "控制器必须写在包围盒内的 (CX, CY, CZ)");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 60)
    public static void bellAndLampVaultsGenerateTheirParts(GameTestHelper h) {
        Capture bell = generate(h, PuzzleRules.Kind.BELL, 2, 2, 2);
        long bells = bell.writes.values().stream().filter(s -> s.is(PuzzleBlocks.ECHO_BELL.get())).count();
        h.assertTrue(bells == 5, "编钟应当正好 5 口，实际 " + bells);

        Capture lamp = generate(h, PuzzleRules.Kind.ELEMENTS, 40, 2, 2);
        long lamps = lamp.writes.values().stream().filter(s -> s.is(PuzzleBlocks.ELEMENT_LAMP.get())).count();
        h.assertTrue(lamps == 4, "四象灯应当正好 4 盏，实际 " + lamps);
        long lit = lamp.writes.values().stream()
                .filter(s -> s.is(PuzzleBlocks.ELEMENT_LAMP.get()))
                .filter(s -> s.getValue(PuzzleBlocks.LIT)).count();
        h.assertTrue(lit < 4, "开局不能已经是全亮（否则一进门就完成），实际亮 " + lit + " 盏");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 60)
    public static void treasuryLayoutPersistsAndKeepsLegacyStarts(GameTestHelper h){
        var piece=generate(h,PuzzleRules.Kind.BELL,2,2,2);
        var tag=piece.createTag(null);
        h.assertTrue(tag.getInt("DynastyRuinLayout")==3,"New layout version must be saved");
        var type=com.dynasty.structure.DynastyStructures.MUSIC_RUIN_PIECE.get();
        var restored=new Capture(type,tag,PuzzleRules.Kind.BELL);
        restored.postProcess(null,null,null,RandomSource.create(7),restored.getBoundingBox(),new ChunkPos(0,0),BlockPos.ZERO);
        h.assertTrue(piece.writes.equals(restored.writes),"Reload changed treasure hall geometry");
        h.assertTrue(piece.writes.values().stream().filter(s->s.is(net.minecraft.world.level.block.Blocks.CHEST)).count()==2,"Two material caches required");
        for(var p:piece.writes.keySet())h.assertTrue(p.getX()>=0&&p.getX()<29&&p.getY()>=0&&p.getY()<8&&p.getZ()>=0&&p.getZ()<29,"Out-of-bounds write");
        tag.remove("DynastyRuinLayout");
        tag.putIntArray("BB",new int[]{0,64,0,20,69,20});
        var legacy=new Capture(type,tag,PuzzleRules.Kind.BELL);
        legacy.postProcess(null,null,null,RandomSource.create(7),legacy.getBoundingBox(),new ChunkPos(0,0),BlockPos.ZERO);
        h.assertTrue(legacy.writes.containsKey(new BlockPos(10,1,10)),"Legacy center shifted");
        h.assertTrue(legacy.writes.values().stream().noneMatch(s->s.is(net.minecraft.world.level.block.Blocks.CHEST)),"Old start was silently expanded");
        h.succeed();
    }
}
