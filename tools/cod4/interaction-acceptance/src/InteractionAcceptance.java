package com.dynasty.structure;

import com.dynasty.expansion.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.*;
import net.minecraft.world.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.phys.*;
import net.minecraft.util.RandomSource;
import net.minecraftforge.gametest.*;
import java.util.*;
import java.nio.file.*;

@GameTestHolder("dynasty_interaction_qa") @PrefixGameTestTemplate(false)
public final class InteractionAcceptance {
    static final String[][] IDS={{"wayside_shrine","old_weapon_rack","puzzle_box","wayside_tea_stall","broken_stele"},{"herb_spot","nameless_tomb","sword_scar_wall","mortuary_room","broken_waterwheel"},{"abandoned_armory","battlefield_remnant","ghost_market_boat","old_bellows","ancient_well"}};
    static final List<Map<String,Object>> ROWS=new ArrayList<>();
    public static void evidence(String kind, Object... fields){
        var row=new LinkedHashMap<String,Object>();row.put("kind",kind);
        for(int i=0;i<fields.length;i+=2)row.put(fields[i].toString(),fields[i+1]);ROWS.add(row);
        try{Path f=Path.of(System.getProperty("interaction.evidence"));Files.createDirectories(f.getParent());Files.writeString(f,new com.google.gson.GsonBuilder().setPrettyPrinting().create().toJson(ROWS));}catch(Exception e){throw new RuntimeException(e);}
    }
    public static final class Piece extends TravelSitePiece {
        Piece(BlockPos at,int style,Direction orientation){super(at,style);setOrientation(orientation);}
        public BlockPos point(int x,int y,int z){return world(x,y,z);}
    }
    public static Piece build(GameTestHelper h,int style,Direction facing,BlockPos origin){
        var l=h.getLevel();var p=new Piece(origin,style,facing);var box=p.getBoundingBox();
        // Each chunk receives the real production postProcess with its own clip.
        for(int x=box.minX()>>4;x<=box.maxX()>>4;x++)for(int z=box.minZ()>>4;z<=box.maxZ()>>4;z++){
            l.setChunkForced(x,z,true);l.getChunk(x,z);var cp=new ChunkPos(x,z);var clip=new BoundingBox(x*16,l.getMinBuildHeight(),z*16,x*16+15,l.getMaxBuildHeight()-1,z*16+15);
            p.postProcess(l,l.structureManager(),l.getChunkSource().getGenerator(),RandomSource.create(42000+style),clip,cp,origin);
        }return p;
    }
    public static ServerPlayer player(GameTestHelper h,BlockPos at){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"InteractionQA"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(at));return p;
    }
    public static void use(GameTestHelper h,ServerPlayer p,BlockPos at){h.getLevel().getBlockState(at).use(h.getLevel(),p,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(at),Direction.UP,at,false));}
    public static ItemStack offering(String id){return switch(id){
        case "wayside_shrine","ghost_market_boat"->new ItemStack(ExpansionContent.SUPPLIES.get("soul_incense").get(),2);
        case "nameless_tomb"->new ItemStack(Items.POPPY,2);
        case "broken_stele"->new ItemStack(Items.PAPER,2);
        case "broken_waterwheel"->new ItemStack(ExpansionContent.MATERIALS.get("qimen_cable").get(),2);
        case "old_bellows"->new ItemStack(Items.CHARCOAL,2);
        case "ancient_well"->new ItemStack(Items.WATER_BUCKET);
        case "sword_scar_wall"->new ItemStack(Items.IRON_SWORD);
        default->ItemStack.EMPTY;};}
    @GameTest(template="bow_ritual_test",batch="interaction_placement",timeoutTicks=400)
    public static void allFifteenProductionPlacementsFourOrientationsAndBothPhysicalStates(GameTestHelper h){
        h.assertTrue(SmallInteractions.IDS.size()==15&&new HashSet<>(SmallInteractions.IDS).size()==15,"Actual fifteen distinct registered Site IDs");
        var observed=new HashSet<String>();var l=h.getLevel();int checks=0;
        for(int style=0;style<3;style++)for(var facing:Direction.Plane.HORIZONTAL){
            var piece=build(h,style,facing,new BlockPos(1024,80,1024));
            for(int i=0;i<5;i++){
                String id=IDS[style][i];var at=piece.point(5+i*4,1,28);var approach=piece.point(5+i*4,1,27);var state=l.getBlockState(at);observed.add(id);
                h.assertTrue(state.is(SmallInteractions.ENTRIES.get(id).get()),"Production chunk-clipped placement "+id+" / "+facing+" at "+at);
                var p=player(h,approach);boolean support=l.getBlockState(approach.below()).isFaceSturdy(l,approach.below(),Direction.UP);
                boolean clear=l.noCollision(p,p.getBoundingBox());double distance=p.distanceToSqr(Vec3.atCenterOf(at));
                var ray=l.clip(new ClipContext(p.getEyePosition(),Vec3.atBottomCenterOf(at).add(0,.15,0),ClipContext.Block.OUTLINE,ClipContext.Fluid.NONE,p));
                h.assertTrue(support&&clear&&distance<36&&ray.getBlockPos().equals(at),"Supported unobstructed actual transformed approach/raycast "+id+" / "+facing);
                for(boolean lit:new boolean[]{false,true}){
                    var s=state.setValue(BlockStateProperties.LIT,lit);l.setBlock(at,s,2);
                    var outline=s.getShape(l,at);var collision=s.getCollisionShape(l,at);
                    h.assertTrue(!outline.isEmpty()&&!collision.isEmpty(),"Native collision is nonempty even with noOcclusion "+id);
                    double top=id.equals("herb_spot")?5./16:13./16;
                    h.assertTrue(Math.abs(collision.bounds().maxY-top)<1e-8,"Actual collision height "+id);
                    var overlap=p.getBoundingBox().move(Vec3.atBottomCenterOf(at).subtract(p.position()));
                    h.assertTrue(!l.noCollision(p,overlap),"Native player body cannot pass through Site solid core "+id);
                    evidence("placement","id",id,"style",style,"orientation",facing.toString(),"world",at.toShortString(),"approach",approach.toShortString(),"supported",support,"approach_no_collision",clear,"distance_squared",distance,"ray_hit",ray.getBlockPos().toShortString(),"lit",lit,"outline",outline.bounds().toString(),"collision",collision.bounds().toString(),"body_core_blocked",true);checks++;
                }p.discard();
            }
        }
        h.assertTrue(observed.equals(new HashSet<>(SmallInteractions.IDS))&&checks==120,"All15 x4 orientations x2 physical states");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="interaction_range",timeoutTicks=60)
    public static void actualUsePacketRejectsRemoteForEveryRegisteredSite(GameTestHelper h){
        var at=h.absolutePos(new BlockPos(3,2,3));var errors=new ArrayList<String>();
        for(String id:SmallInteractions.IDS){
            h.getLevel().setBlock(at,SmallInteractions.ENTRIES.get(id).get().defaultBlockState(),3);
            var p=player(h,at.offset(30,0,0));p.setItemInHand(InteractionHand.MAIN_HAND,offering(id));
            var before=p.getPersistentData().copy();var held=p.getMainHandItem().copy();
            p.connection.handleUseItemOn(new net.minecraft.network.protocol.game.ServerboundUseItemOnPacket(InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(at),Direction.UP,at,false),0));
            boolean unchanged=p.getPersistentData().equals(before)&&ItemStack.matches(held,p.getMainHandItem());
            evidence("packet_range","id",id,"distance_squared",p.distanceToSqr(Vec3.atCenterOf(at)),"unchanged",unchanged);
            if(!unchanged)errors.add(id);p.discard();
        }h.assertTrue(errors.isEmpty(),"Actual native packet remote guard: "+errors);h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="interaction_range",timeoutTicks=60)
    public static void internalBlockUseFarDistanceAuditReportsAnyMissingDefenseInDepth(GameTestHelper h){
        var at=h.absolutePos(new BlockPos(3,2,3));var failures=new ArrayList<String>();
        for(String id:SmallInteractions.IDS){
            h.getLevel().setBlock(at,SmallInteractions.ENTRIES.get(id).get().defaultBlockState(),3);
            var p=player(h,at.offset(30,0,0));p.setItemInHand(InteractionHand.MAIN_HAND,offering(id));
            var before=EquipmentBehaviors.saved(p).copy();use(h,p,at);boolean changed=!before.equals(EquipmentBehaviors.saved(p));
            evidence("internal_direct_use_range","id",id,"changed",changed,"after",EquipmentBehaviors.saved(p).toString(),"scope","direct BlockState.use; distinguish from guarded network packet");if(changed)failures.add(id);p.discard();
        }h.assertTrue(failures.isEmpty(),"Missing direct-use range defense (network independently tested): "+failures);h.succeed();
    }
}
