package com.dynasty.structure;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
import java.util.*;
import static com.dynasty.structure.InteractionAcceptance.*;
@GameTestHolder("dynasty_interaction_extra_qa") @PrefixGameTestTemplate(false)
public final class InteractionWalkAcceptance {
    @GameTest(template="bow_ritual_test",batch="interaction_continuous_approach",timeoutTicks=500)
    public static void nativeCollisionWalkFromActualEntranceReachesAllFifteenAcrossFourOrientations(GameTestHelper h){
        record Case(int style,Direction facing,Piece piece){}
        var cases=new ArrayList<Case>();int r=0;
        for(var d:Direction.Plane.HORIZONTAL){for(int s=0;s<3;s++)cases.add(new Case(s,d,build(h,s,d,new BlockPos(4608+s*64,80,3072+r*64))));r++;}
        h.runAtTickTime(h.getTick()+80,()->{
            int checked=0;
            for(var c:cases){var piece=c.piece();var start=piece.point(15,1,30);var p=player(h,start);var parents=new HashMap<BlockPos,BlockPos>();var queue=new ArrayDeque<BlockPos>();parents.put(start,start);queue.add(start);var box=piece.getBoundingBox();
                while(!queue.isEmpty()){
                    var node=queue.remove();for(var d:Direction.Plane.HORIZONTAL){var n=node.relative(d);if(n.getX()<box.minX()||n.getX()>box.maxX()||n.getZ()<box.minZ()||n.getZ()>box.maxZ()||parents.containsKey(n))continue;
                        var center=Vec3.atBottomCenterOf(n);var body=new AABB(center.x-.3,center.y,center.z-.3,center.x+.3,center.y+1.8,center.z+.3);
                        if(h.getLevel().getBlockState(n.below()).isFaceSturdy(h.getLevel(),n.below(),Direction.UP)&&h.getLevel().noCollision(p,body)){parents.put(n,node);queue.add(n);}
                    }
                }
                for(int i=0;i<5;i++){
                    String id=IDS[c.style()][i];var goal=piece.point(5+i*4,1,27);h.assertTrue(parents.containsKey(goal),"Entrance grounded collision route exists "+id+" "+c.facing());
                    var route=new ArrayList<BlockPos>();for(var n=goal;!n.equals(start);n=parents.get(n))route.add(n);Collections.reverse(route);p.setPos(Vec3.atBottomCenterOf(start));
                    for(var node:route){var target=Vec3.atBottomCenterOf(node);var delta=target.subtract(p.position());p.move(MoverType.SELF,delta);h.assertTrue(p.position().distanceToSqr(target)<.000001,"Actual native movement cannot clip on route to "+id+" at "+node);}
                    evidence("entrance_walk","id",id,"style",c.style(),"orientation",c.facing().toString(),"entrance_world",start.toShortString(),"goal_world",goal.toShortString(),"steps",route.size(),"route_world",route.stream().map(BlockPos::toShortString).toList(),"actual_native_move",true);checked++;
                }p.discard();
            }h.assertTrue(checked==60,"15sites x four orientations continuous native entrance approaches");h.succeed();
        });
    }
}
