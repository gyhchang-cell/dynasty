package com.dynasty.structure.megabuild;
import net.minecraft.nbt.CompoundTag;
/** Ordinary darkness-sensitive cages, reduced radius and population budget. */
final class CityEncounters {
    static CompoundTag spawnerTag(Blueprint.Kind kind){
        var tag=new CompoundTag();tag.putString("id","minecraft:mob_spawner");
        tag.putShort("Delay",(short)60);tag.putShort("MinSpawnDelay",(short)300);tag.putShort("MaxSpawnDelay",(short)600);
        tag.putShort("SpawnCount",(short)2);tag.putShort("MaxNearbyEntities",(short)4);
        tag.putShort("RequiredPlayerRange",(short)12);tag.putShort("SpawnRange",(short)2);
        var data=new CompoundTag();var entity=new CompoundTag();
        entity.putString("id",kind==Blueprint.Kind.SPAWNER_SKELETON?"minecraft:skeleton":"minecraft:zombie");
        data.put("entity",entity);tag.put("SpawnData",data);return tag;
    }
}
