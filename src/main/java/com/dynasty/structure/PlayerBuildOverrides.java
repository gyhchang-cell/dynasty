package com.dynasty.structure;

import com.google.gson.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.block.state.BlockState;

/** Small, reviewed player-authored block deltas; never reads or modifies a live save. */
final class PlayerBuildOverrides {
    private record Edit(int x,int y,int z,BlockState state) {}
    private static final java.util.Map<String,java.util.List<Edit>> CACHE=new java.util.HashMap<>();
    static void apply(String name,DynastyStructurePiece piece,WorldGenLevel level,BoundingBox bounds) {
        if(Boolean.getBoolean("dynasty.baselineOnly"))return;
        for(Edit e:CACHE.computeIfAbsent(name,PlayerBuildOverrides::load))piece.set(level,bounds,e.x,e.y,e.z,e.state);
    }
    private static java.util.List<Edit> load(String name) {
        try(var input=PlayerBuildOverrides.class.getResourceAsStream("/data/dynasty/build_overrides/"+name+".json")) {
            if(input==null)throw new IllegalStateException("Missing build overrides: "+name);
            var rows=JsonParser.parseReader(new java.io.InputStreamReader(input,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonArray();
            var edits=new java.util.ArrayList<Edit>();
            for(var row:rows){var o=row.getAsJsonObject();var p=o.getAsJsonArray("pos");
                var block=BlockStateParser.parseForBlock(BuiltInRegistries.BLOCK.asLookup(),o.get("state").getAsString(),false).blockState();
                edits.add(new Edit(p.get(0).getAsInt(),p.get(1).getAsInt(),p.get(2).getAsInt(),block));}
            return java.util.List.copyOf(edits);
        }catch(Exception e){throw new IllegalStateException("Invalid player build delta "+name,e);}
    }
}
