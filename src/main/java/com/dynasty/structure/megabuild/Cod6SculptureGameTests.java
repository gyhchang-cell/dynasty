package com.dynasty.structure.megabuild;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.gametest.*;
@GameTestHolder("dynasty_cod6") @PrefixGameTestTemplate(false)
public final class Cod6SculptureGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void compassGroupsAndRoofMask(GameTestHelper h) throws Exception {
        var registry=h.getLevel().registryAccess().registryOrThrow(Registries.STRUCTURE_SET);
        for(String name:new String[]{"sculpture_tiles","yunqi_manor"}) {
            var set=registry.get(new ResourceLocation("dynasty",name));
            h.assertTrue(set!=null&&set.structures().size()==1,"Compass group mixes distinct landmarks");
            h.assertTrue(set.placement() instanceof NaturalSculptures.Placement,"Lost chunk-local rare placement");
        }
        var b=SculptureBlueprint.load(h.getLevel().getServer().getResourceManager(),"yunqi_manor");
        int overhangs=0;
        for(int x=0;x<b.width;x++)for(int z=0;z<b.length;z++) {
            int top=b.columnTop(x,z);
            if(top>=4&&b.at(x,3,z)==0){overhangs++;h.assertTrue(b.clearTop(x,z)>=top+5,"Overhanging roof not cleared");}
            if(top<0)h.assertTrue(b.clearTop(x,z)==-1,"Outside silhouette cleared");
        }
        System.out.println("COD6 manor roof columns missed by old y=3 mask="+overhangs);
        h.assertTrue(b.clearTop(b.width/2,b.length/2)>=b.columnTop(b.width/2,b.length/2)+5,"Roof lacks bounded overhead clearance");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=1200)
    public static void normalTerrainSeed42(GameTestHelper h){probe(h,42L);}
    @GameTest(template="bow_ritual_test",timeoutTicks=1200)
    public static void normalTerrainSeed2026(GameTestHelper h){probe(h,2026L);}
    @GameTest(template="bow_ritual_test",timeoutTicks=1200)
    public static void normalTerrainSeedNegative(GameTestHelper h){probe(h,-731985L);}
    private static void probe(GameTestHelper h,long seed) {
        var access=h.getLevel().registryAccess();
        var generator=(net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator)access.registryOrThrow(Registries.WORLD_PRESET)
                .getOrThrow(net.minecraft.world.level.levelgen.presets.WorldPresets.NORMAL).createWorldDimensions().overworld();
        var random=net.minecraft.world.level.levelgen.RandomState.create(generator.generatorSettings().value(),access.lookupOrThrow(Registries.NOISE),seed);
        var structure=access.registryOrThrow(Registries.STRUCTURE).get(new ResourceLocation("dynasty","yunqi_manor"));
        var regions=new java.util.ArrayList<net.minecraft.world.level.ChunkPos>();
        for(int x=-12;x<=12;x++)for(int z=-12;z<=12;z++)regions.add(new net.minecraft.world.level.ChunkPos(x,z));
        regions.sort(java.util.Comparator.comparingInt(c->c.x*c.x+c.z*c.z));
        int[] index={0};
        Runnable search=new Runnable(){public void run(){
            for(int tries=0;tries<8&&index[0]<625;tries++) {
                var region=regions.get(index[0]++);
                var site=NaturalSculptures.site(seed,region.x*625,region.z*625);if(!site.id().equals("yunqi_manor"))continue;
                var start=structure.generate(access,generator,generator.getBiomeSource(),random,h.getLevel().getStructureManager(),seed,
                    new net.minecraft.world.level.ChunkPos(site.x()>>4,site.z()>>4),0,h.getLevel(),structure.biomes()::contains);
                if(start.isValid()) {
                    System.out.println("COD6 NORMAL worldgen seed="+seed+" manor="+site.x()+","+site.z()+" tile="+start.getBoundingBox());h.succeed();return;
                }
            }
            h.assertTrue(index[0]<625,"No valid manor among 625 normal terrain regions for seed "+seed);
            h.runAfterDelay(1,()->this.run());
        }};search.run();
    }
}
