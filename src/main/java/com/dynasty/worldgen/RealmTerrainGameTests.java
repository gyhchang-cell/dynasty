package com.dynasty.worldgen;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import net.minecraftforge.registries.ForgeRegistries;

/** Exercises actual isolated server chunks, not just JSON strings. */
@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class RealmTerrainGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=1200)
    public static void fourRealmsGenerateTheirOwnRockAndSoil(GameTestHelper h) {
        String[][] realms={{"celestial_dynasty","celestial_stone","jade_soil"},
                {"underworld","underworld_stone","spirit_soil"},{"jiuxiao","cloud_stone","star_soil"},
                {"dragon_palace","tidal_stone","pearl_sand"}};
        for(String[] row:realms) {
            var level=h.getLevel().getServer().getLevel(ResourceKey.create(Registries.DIMENSION,new ResourceLocation("dynasty",row[0])));
            h.assertTrue(level!=null,"Realm loaded: "+row[0]);
            var stone=ForgeRegistries.BLOCKS.getValue(new ResourceLocation("dynasty",row[1]));
            var soil=ForgeRegistries.BLOCKS.getValue(new ResourceLocation("dynasty",row[2]));
            var chunk=level.getChunk(1001,1001);
            int stones=0,soils=0;
            var pos=new BlockPos.MutableBlockPos();
            for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=level.getMinBuildHeight()+6;y<level.getMaxBuildHeight();y++) {
                var state=chunk.getBlockState(pos.set(1001*16+x,y,1001*16+z));
                if(state.is(stone))stones++;
                if(state.is(soil))soils++;
            }
            h.assertTrue(stones>100&&soils>10,"Original rock/soil actually generated in "+row[0]+": "+stones+"/"+soils);
        }
        var biomes=h.getLevel().registryAccess().registryOrThrow(Registries.BIOME);
        var tag=TagKey.create(Registries.BIOME,new ResourceLocation("dynasty","imperial_settlements"));
        h.assertTrue(biomes.getHolderOrThrow(net.minecraft.world.level.biome.Biomes.PLAINS).is(tag),
                "Overworld plains accepts Dynasty settlement structures");
        h.succeed();
    }
}
