package com.dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;
import java.util.UUID;
@GameTestHolder("dynasty_cod6") @PrefixGameTestTemplate(false)
public final class Cod6EdictGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void remoteSpellAndReplayGate(GameTestHelper h) {
        var p=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod6-spell"));
        p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.CHILING_BRUSH.get()));
        var start=h.absoluteVec(new Vec3(2,2,2));p.moveTo(start.x,start.y,start.z,0,0);
        var target=net.minecraft.world.entity.EntityType.ZOMBIE.create(h.getLevel());target.setNoAi(true);target.setNoGravity(true);
        target.moveTo(start.x,start.y,start.z+10,0,0);h.getLevel().addFreshEntity(target);
        float before=target.getHealth();
        h.assertTrue(EdictSpells.cast(p,0),"Valid short spell rejected");
        h.assertTrue(!EdictSpells.cast(p,0),"Replay accepted during windup");
        h.runAfterDelay(10,()->{h.assertTrue(target.getHealth()<before,"Ranged spell did not hit at ten blocks");target.discard();p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test")
    public static void wallAndEachAreaCast(GameTestHelper h) {
        var p=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod6-wall"));
        p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.CHILING_BRUSH.get()));
        var start=h.absoluteVec(new Vec3(2,2,2));p.moveTo(start.x,start.y,start.z,0,0);
        var target=net.minecraft.world.entity.EntityType.HUSK.create(h.getLevel());target.setNoAi(true);target.setNoGravity(true);
        target.moveTo(start.x,start.y,start.z+6,0,0);h.getLevel().addFreshEntity(target);
        var center=target.getBoundingBox().getCenter();
        for(int x=-1;x<=1;x++)for(int y=0;y<4;y++)h.getLevel().setBlock(BlockPos.containing(start).offset(x,y,3),Blocks.STONE.defaultBlockState(),3);
        float before=target.getHealth();
        for(int kind:new int[]{0,1,2,3,5}){target.invulnerableTime=0;EdictSpells.resolve(p,kind,p.getEyePosition(),center);}
        h.assertTrue(target.getHealth()==before,"A spell crossed a solid wall");
        EdictSpells.resolve(p,4,p.getEyePosition(),p.position());h.assertTrue(p.hasEffect(DynastyEffects.IRON_WALL.get()),"Shield did not reuse Iron Wall");
        target.discard();p.discard();h.succeed();
    }
}
