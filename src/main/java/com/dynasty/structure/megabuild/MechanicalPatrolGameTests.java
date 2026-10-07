package com.dynasty.structure.megabuild;

import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class MechanicalPatrolGameTests {
    private static boolean clear(Blueprint.Kind kind){return kind==Blueprint.Kind.AIR||kind==Blueprint.Kind.LIGHT;}
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="mechanical_sites")
    public static void authoredPatrolAndSnakeRoomsRemainClearAcrossFourRotationsAndReload(GameTestHelper h){
        var origin=h.absolutePos(new BlockPos(32,0,32));var original=new TiangongCitadel(42).blueprint();
        var context=net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext.fromLevel(h.getLevel());
        for(int rotation=0;rotation<4;rotation++){
            var rotated=original.rotate(rotation);
            var piece=new MegabuildPiece(MegabuildStructures.CITADEL_PIECE.get(),0,origin,seed->original,42,rotation,176,56);
            var restored=MegabuildStructures.CITADEL_PIECE.get().load(context,piece.createTag(context));
            h.assertTrue(MechanicalPatrols.dogPositions(piece).equals(MechanicalPatrols.dogPositions(restored))&&MechanicalPatrols.snakePositions(piece).equals(MechanicalPatrols.snakePositions(restored)),"Saved orientation preserves authored mechanical positions");
            var positions=new java.util.ArrayList<>(MechanicalPatrols.dogPositions(piece));positions.addAll(MechanicalPatrols.snakePositions(piece));
            for(var world:positions){
                var p=world.subtract(origin);
                h.assertTrue(rotated.at(p.getX(),p.getY()-1,p.getZ())!=Blueprint.Kind.AIR&&clear(rotated.at(p.getX(),p.getY(),p.getZ()))&&clear(rotated.at(p.getX(),p.getY()+1,p.getZ())),"Real city floor and headroom at "+p+" rotation "+rotation);
            }
        }
        var mine=new MiningEstate(42).blueprint();
        for(int rotation=0;rotation<4;rotation++){
            var rotated=mine.rotate(rotation);var piece=new MegabuildPiece(MegabuildStructures.MINING_PIECE.get(),0,origin,seed->mine,42,rotation,96,36);
            for(var world:MechanicalPatrols.spiderPositions(piece)){
                var p=world.subtract(origin);
                for(int x=-1;x<=1;x++)for(int z=-1;z<=1;z++)h.assertTrue(clear(rotated.at(p.getX()+x,4,p.getZ()+z))&&clear(rotated.at(p.getX()+x,5,p.getZ()+z))&&!clear(rotated.at(p.getX()+x,6,p.getZ()+z)),"Real quarry ceiling supports full spider footprint");
            }
        }
        h.assertTrue(mine.walkable(new int[]{47,1,4},new int[]{31,1,45}),"Quarry route reaches the existing under-bench encounter through new east opening");
        h.succeed();
    }
}
