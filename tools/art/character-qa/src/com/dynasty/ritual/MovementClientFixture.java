package com.dynasty.ritual;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

/** QA sources only. Enter through the production transition, not a test teleport shortcut. */
public final class MovementClientFixture {
    public static void enter(ServerPlayer p) {
        var data=ZhenyuanRitualSavedData.get(p.serverLevel());
        var s=new ZhenyuanRitualSavedData.Session(p.serverLevel().dimension().location().toString(),new BlockPos(80,-60,80));
        s.owner=p.getUUID();s.mask=31;s.phase="charging";s.chargeEnds=0;s.removed=true;data.sessions.put(s.key,s);
        ZhenyuanRitualService.advanceSession(p.server,s,data,p,0);
        if(!s.is("active")||!p.level().dimension().equals(ZhenyuanArena.DIMENSION))throw new AssertionError("Production arena entry failed");
        p.getInventory().setItem(0,new ItemStack(Items.BOW));p.getInventory().setItem(1,new ItemStack(Items.ARROW,64));p.getInventory().selected=0;p.getInventory().setChanged();
    }
}
