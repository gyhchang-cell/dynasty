package com.dynasty.structure;
import com.dynasty.expansion.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
import static com.dynasty.structure.InteractionAcceptance.*;
@GameTestHolder("dynasty_interaction_extra_qa") @PrefixGameTestTemplate(false)
public final class InteractionPacketBoundaryAcceptance {
    @GameTest(template="bow_ritual_test",batch="interaction_packet_boundary",timeoutTicks=40)
    public static void nativePacketSixBlockEyeBoundaryAndForgedHitLocationCannotBypassReach(GameTestHelper h){
        var at=h.absolutePos(new BlockPos(3,2,3));int checked=0;
        for(String id:SmallInteractions.IDS){
            h.getLevel().setBlock(at,SmallInteractions.ENTRIES.get(id).get().defaultBlockState(),3);
            for(var d:Direction.Plane.HORIZONTAL)h.getLevel().setBlock(at.relative(d).below(),Blocks.STONE.defaultBlockState(),3);
            for(double distance:new double[]{6.01,5.99}){
                var p=player(h,at.north());p.setYRot(180);p.setItemInHand(InteractionHand.MAIN_HAND,offering(id));var center=Vec3.atCenterOf(at);
                double dy=p.getEyeY()-center.y;double horizontal=Math.sqrt(distance*distance-dy*dy);p.setPos(center.x+horizontal,p.getY(),center.z);
                var before=EquipmentBehaviors.saved(p).copy();p.connection.handleUseItemOn(new net.minecraft.network.protocol.game.ServerboundUseItemOnPacket(InteractionHand.MAIN_HAND,new BlockHitResult(center,Direction.UP,at,false),3));
                boolean changed=!before.equals(EquipmentBehaviors.saved(p));boolean expected=distance<6&&!id.equals("sword_scar_wall");
                // Moonlit sword-wall gating is tested separately with actual outdoor lighting.
                if(distance>6||!id.equals("sword_scar_wall"))h.assertTrue(changed==expected,"Native eye-distance boundary "+id+" distance="+distance+" changed="+changed);
                evidence("packet_boundary","id",id,"eye_distance",p.getEyePosition().distanceTo(center),"changed",changed,"inside_positive_applicable",!id.equals("sword_scar_wall"));p.discard();checked++;
            }
            var p=player(h,at.north());p.setYRot(180);p.setItemInHand(InteractionHand.MAIN_HAND,offering(id));var before=EquipmentBehaviors.saved(p).copy();
            p.connection.handleUseItemOn(new net.minecraft.network.protocol.game.ServerboundUseItemOnPacket(InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(at).add(2,0,0),Direction.UP,at,false),4));
            h.assertTrue(before.equals(EquipmentBehaviors.saved(p)),"Nearby player cannot forge a hit outside clicked block "+id);evidence("forged_hit_rejected","id",id,"unchanged",true);p.discard();checked++;
        }h.assertTrue(checked==45,"15sites x three actual packet checks");h.succeed();
    }
}
