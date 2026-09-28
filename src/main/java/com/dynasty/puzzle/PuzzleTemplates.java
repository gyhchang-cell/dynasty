package com.dynasty.puzzle;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import java.util.List;

/** Administrator previews use exactly the same enclosed shell as natural ruins. */
public final class PuzzleTemplates {
    private PuzzleTemplates() {}
    public enum Room {
        STAR("star_room",PuzzleRules.Kind.STAR,0), BELL("bell_room",PuzzleRules.Kind.BELL,1), LAMP("lamp_room",PuzzleRules.Kind.ELEMENTS,2);
        public final String id;
        public final PuzzleRules.Kind kind;
        public final int defaultVariant;
        Room(String id,PuzzleRules.Kind kind,int variant){this.id=id;this.kind=kind;this.defaultVariant=variant;}
        public static Room byId(String id){for(Room r:values())if(r.id.equalsIgnoreCase(id))return r;return null;}
    }
    public static void build(ServerLevel level,BlockPos origin,Room room,int variant){
        for(var cell:RuinLayout.shell(RuinLayout.TREASURY_VERSION)) {
            level.setBlock(origin.offset(cell.x(),cell.y(),cell.z()),PuzzleRuinPiece.shellState(cell.role()),2);
            if(cell.role()==RuinLayout.Role.TREASURE && level.getBlockEntity(origin.offset(cell.x(),cell.y(),cell.z()))
                    instanceof net.minecraft.world.level.block.entity.ChestBlockEntity chest)
                chest.setLootTable(PuzzleRuinPiece.TREASURE_LOOT,origin.asLong()+cell.x());
        }
        int[][] offsets=RuinLayout.partOffsets(room.kind);
        int[] ranks=RuinLayout.runtimeOrder(offsets);
        int[] ring=room.kind==PuzzleRules.Kind.ELEMENTS?PuzzleRuinPiece.ringOrder(offsets):null;
        for(int i=0;i<offsets.length;i++){
            var p=origin.offset(offsets[i][0],offsets[i][1],offsets[i][2]);
            var state=PuzzleBlocks.partFor(room.kind).defaultBlockState();
            if(room.kind==PuzzleRules.Kind.STAR)
                state=state.setValue(PuzzleBlocks.FACING,PuzzleRuinPiece.facingOf(PuzzleRules.starInitial(variant)[ranks[i]]));
            if(room.kind==PuzzleRules.Kind.ELEMENTS)
                state=state.setValue(PuzzleBlocks.SYMBOL,ranks[i]).setValue(PuzzleBlocks.LIT,
                        PuzzleRules.lampInitial(variant)[PuzzleRuinPiece.indexOf(ring,i)]==1);
            level.setBlock(p,state,3);
            level.setBlock(p.above(),PuzzleBlocks.CLUE_TABLET.get().defaultBlockState(),3);
        }
        level.setBlock(origin,PuzzleBlocks.RUIN_CONTROLLER.get().defaultBlockState()
                .setValue(PuzzleBlocks.KIND,room.kind.ordinal()).setValue(PuzzleBlocks.VARIANT,PuzzleRules.wrap(variant)),3);
    }
    public static List<String> ids(){return List.of(Room.STAR.id,Room.BELL.id,Room.LAMP.id);}
}
