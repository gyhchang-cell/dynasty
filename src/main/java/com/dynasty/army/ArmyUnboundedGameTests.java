package com.dynasty.army;

import com.dynasty.DynastyItems;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import java.util.UUID;

@GameTestHolder("dynasty_army_unbounded") @PrefixGameTestTemplate(false)
public final class ArmyUnboundedGameTests {
    @GameTest(template="bow_ritual_test",batch="army_unbounded_v30",setupTicks=20,timeoutTicks=100)
    public static void paidRosterBeyond36PagesAndFormationBeyond9RemainAuthoritative(GameTestHelper h){
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"unbounded-army"));
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyItems.TIGER_TALLY.get()));
        p.moveTo(h.absolutePos(new BlockPos(8,52,2)),0,0);h.getLevel().addNewPlayer(p);
        try{
            for(int i=0;i<43;i++){
                p.getInventory().setItem(2,new ItemStack(DynastyItems.SILVER_COIN.get(),12));
                h.assertTrue(ArmyRoster.recruit(p,0)&&ArmyRoster.coins(p)==0,"Every soldier beyond36 still costs real silver");
            }
            var m=new ArmyMenu(92,p.getInventory(),null);
            h.assertTrue(m.total()==43&&m.window()==0,"Total count independent of fixed-size network page");
            int stale=(m.view.get(2)<<8)|81;
            h.assertTrue(m.clickMenuButton(p,stale)&&m.window()==1&&!m.clickMenuButton(p,stale),"Page switch is revision guarded");
            h.assertTrue(m.clickMenuButton(p,(m.view.get(2)<<8)|40),"Page2 first row can join formation");
            h.assertTrue(ArmyRoster.soldiers(p).getCompound(36).getInt("Slot")==0&&ArmyRoster.soldiers(p).getCompound(0).getInt("Slot")==-1,"Page action targets soldier37, never soldier1");
            h.assertTrue(m.clickMenuButton(p,(m.view.get(2)<<8)|13),"Quick formation includes all reserves");
            for(int i=0;i<43;i++)h.assertTrue(ArmyRoster.soldiers(p).getCompound(i).getInt("Slot")==i,"No nine-slot truncation");
            for(int preset=0;preset<3;preset++)h.assertTrue(m.clickMenuButton(p,(m.view.get(2)<<8)|(100+preset)),"All three large formation presets save");
            ArmyRoster.soldiers(p).getCompound(42).putInt("Slot",-1);
            for(int preset=0;preset<3;preset++)h.assertTrue(ArmyMenu.loadPreset(p,preset)&&ArmyRoster.soldiers(p).getCompound(42).getInt("Slot")==42,"Large presets restore paid identity");
            m.view.set(0,(short)70000);m.view.set(119,1);h.assertTrue(m.total()==70000,"Signed 16-bit transport preserves large counts");m.refresh();
            var positions=new java.util.HashSet<Vec3>();for(int i=0;i<43;i++)positions.add(ArmyRoster.slot(Vec3.ZERO,0,i,4));
            h.assertTrue(positions.size()==43,"Additional ring slots do not overlap first ring");
            for(int i=12;i<43;i++)ArmyRoster.soldiers(p).getCompound(i).putInt("Slot",-1);
            for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=51;y<56;y++)h.setBlock(x,y,z,y==51?Blocks.STONE:Blocks.AIR);
            h.assertTrue(ArmyRoster.deploy(p,0,43)==12,"Twelve paid soldiers deploy together on valid ground");
            for(var row:ArmyRoster.soldiers(p)){
                var n=(net.minecraft.nbt.CompoundTag)row;
                if(n.hasUUID("Entity")){var e=h.getLevel().getEntity(n.getUUID("Entity"));if(e!=null)e.discard();}
            }
        }finally{h.getLevel().players().remove(p);p.discard();}
        h.succeed();
    }
}
