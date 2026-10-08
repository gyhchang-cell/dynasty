package com.dynasty.ritual;
import com.dynasty.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.gametest.*;
import java.util.UUID;
@GameTestHolder("dynasty_cod6") @PrefixGameTestTemplate(false)
public final class Cod6DamageGameTests {
    @GameTest(template="bow_ritual_test")
    public static void cleanTianziDamageChain(GameTestHelper h) {
        var level=h.getLevel();var data=ZhenyuanRitualSavedData.get(level);
        var boss=ZhenyuanBosses.FINAL_BOSS.get().create(level);
        var player=new net.minecraftforge.common.util.FakePlayer(level,new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod6-damage"));
        player.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.TIANZI_SWORD.get()));
        var session=new ZhenyuanRitualSavedData.Session(level.dimension().location().toString(),h.absolutePos(BlockPos.ZERO));
        session.owner=player.getUUID();session.boss=boss.getUUID();session.phase="active";session.bossIntroTick=280;data.sessions.put(session.key,session);
        try {
            boss.applyEncounterGate(true);boss.setHealth(boss.getMaxHealth());
            float before=boss.getHealth();
            double damage=1;
            for(var modifier:player.getMainHandItem().getAttributeModifiers(net.minecraft.world.entity.EquipmentSlot.MAINHAND).get(net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_DAMAGE))
                if(modifier.getOperation()==net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADDITION)damage+=modifier.getAmount();
            for(int i=0;i<4;i++){boss.invulnerableTime=0;boss.hurt(player.damageSources().playerAttack(player),(float)damage);}
            System.out.println("COD6 clean Tianzi input="+damage+", formal gated sovereign MAX="+before+", four actual hurt-pipeline hits remaining="+boss.getHealth());
            h.assertTrue(boss.isAlive()&&boss.getHealth()>before*.5,"Four clean hits skip the final encounter");
        } finally { data.sessions.remove(session.key);data.setDirty();boss.discard();player.discard(); }
        h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void arrowCannotBorrowTianziAfterRelease(GameTestHelper h) {
        var player=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod6-arrow"));
        player.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.HOUYI_BOW.get()));
        var arrow=new net.minecraft.world.entity.projectile.Arrow(h.getLevel(),player);
        DynastyWeaponProgression.onArrow(new net.minecraftforge.event.entity.EntityJoinLevelEvent(arrow,h.getLevel()));
        player.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.TIANZI_SWORD.get()));
        var source=player.damageSources().arrow(arrow,player);
        h.assertTrue(DynastySchoolCombat.firingWeapon(source,player.getMainHandItem()).is(DynastyWeapons.HOUYI_BOW.get()),"Arrow borrowed newly held sword");
        arrow.discard();player.discard();h.succeed();
    }
}
