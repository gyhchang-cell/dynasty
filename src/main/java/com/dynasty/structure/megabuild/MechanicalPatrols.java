package com.dynasty.structure.megabuild;

import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.levelgen.structure.StructurePiece;

/** Query authored, rotated sites without generating geometry or loading a neighbouring chunk. */
public final class MechanicalPatrols {
    private MechanicalPatrols(){}
    public static List<BlockPos> spiderPositions(StructurePiece piece){return piece instanceof MegabuildPiece mine?mine.miningSpiderPositions():List.of();}
    public static List<BlockPos> snakePositions(StructurePiece piece){return piece instanceof MegabuildPiece city?city.bronzeSnakePositions():List.of();}
    public static List<BlockPos> mechanistPositions(StructurePiece piece){return piece instanceof MegabuildPiece site?site.mechanistPositions():List.of();}
    public static List<BlockPos> spiderWomanPositions(StructurePiece piece){return piece instanceof MegabuildPiece site?site.spiderWomanPositions():List.of();}
    public static List<BlockPos> inkAssassinPositions(StructurePiece piece){return piece instanceof MegabuildPiece site?site.inkAssassinPositions():List.of();}
    public static List<BlockPos> dogPositions(StructurePiece piece){
        return piece instanceof MegabuildPiece city?city.clockworkPatrols():List.of();
    }
}
