package com.dynasty.structure.megabuild;
import net.minecraft.nbt.*;
import net.minecraft.SharedConstants;
import net.minecraft.world.level.block.Blocks;
import java.nio.file.*;
/** Deterministic templates for the user's flat creative workshop; natural terrain checks do not apply. */
final class MegabuildTemplateExport {
    static ListTag ints(int... v){var list=new ListTag();for(int n:v)list.add(IntTag.valueOf(n));return list;}
    static void write(Blueprint b,Path path)throws Exception{
        var root=new CompoundTag();root.putInt("DataVersion",SharedConstants.getCurrentVersion().getDataVersion().getVersion());
        root.put("size",ints(b.sizeX,b.sizeY,b.sizeZ));root.put("entities",new ListTag());
        var palette=new ListTag();
        for(var k:Blueprint.Kind.values())palette.add(NbtUtils.writeBlockState(k==Blueprint.Kind.CHEST||k==Blueprint.Kind.RICH_CHEST?Blocks.CHEST.defaultBlockState():MegabuildPiece.blockState(k)));
        root.put("palette",palette);
        var blocks=new ListTag();
        for(int y=0;y<b.sizeY;y++)for(int x=0;x<b.sizeX;x++)for(int z=0;z<b.sizeZ;z++){
            var k=b.at(x,y,z);if(k==Blueprint.Kind.AIR)continue;
            var block=new CompoundTag();block.put("pos",ints(x,y,z));block.putInt("state",k.ordinal());
            if(k==Blueprint.Kind.CHEST||k==Blueprint.Kind.RICH_CHEST){
                var nbt=new CompoundTag();nbt.putString("id","minecraft:chest");
                nbt.putString("LootTable","dynasty:chests/"+(k==Blueprint.Kind.RICH_CHEST?"tiangong_rich":"tiangong_common"));
                block.put("nbt",nbt);
            }
            if(k==Blueprint.Kind.SPAWNER_ZOMBIE||k==Blueprint.Kind.SPAWNER_SKELETON)block.put("nbt",CityEncounters.spawnerTag(k));
            blocks.add(block);
        }
        root.put("blocks",blocks);Files.createDirectories(path.getParent());NbtIo.writeCompressed(root,path.toFile());
        var loaded=NbtIo.readCompressed(path.toFile());
        if(loaded.getList("blocks",10).size()!=b.solidCount()+b.lightCount())throw new AssertionError("Template blocks lost");
    }
}
