package com.dynasty.army;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.*;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.ItemStack;

/** Indexed requests resolve against the server's own roster. A revision rejects repeated/stale button packets. */
public final class ArmyMenu extends AbstractContainerMenu {
    public final BlockPos desk;
    private final Player owner;
    private int selected=-1;
    public final ContainerData view=new SimpleContainerData(6+36*3+1);
    public ArmyMenu(int id,Inventory inventory,BlockPos desk) {
        super(ArmyContent.MENU.get(),id);owner=inventory.player;this.desk=desk;addDataSlots(view);
        if(!owner.level().isClientSide){view.set(2,1+owner.getRandom().nextInt(30000));refresh();}
    }
    public void refresh() {
        if(owner.level().isClientSide)return;
        var list=ArmyRoster.soldiers(owner);view.set(0,list.size());view.set(1,ArmyRoster.coins(owner));
        view.set(3,ArmyRoster.data(owner).getInt("Formation"));view.set(4,desk!=null?1:0);view.set(5,owner instanceof ServerPlayer p?(ArmyEncounters.active(p)?2:ArmyEncounters.inside(p)?1:0):0);
        view.set(114,selected);
        for(int i=0;i<36;i++) {
            var r=list.getCompound(i);view.set(6+i*3,r.getInt("Role"));view.set(7+i*3,(int)Math.ceil(r.getFloat("Health")));
            view.set(8+i*3,(r.getBoolean("RecallRequested")?128:r.getString("State").equals("DEPLOYED")?32:r.getString("State").equals("WOUNDED")?64:0)+(i<list.size()?r.getInt("Slot")+1:0));
        }
    }
    @Override public void broadcastChanges(){refresh();super.broadcastChanges();}
    @Override public boolean stillValid(Player p) {
        return p==owner&&p.isAlive()&&(desk==null?ArmyRoster.hasTally(p):p.level().hasChunkAt(desk)&&p.distanceToSqr(desk.getX()+.5,desk.getY()+.5,desk.getZ()+.5)<=64&&p.level().getBlockState(desk).is(ArmyContent.DESK.get()));
    }
    @Override public ItemStack quickMoveStack(Player p,int index){return ItemStack.EMPTY;}
    @Override public boolean clickMenuButton(Player player,int code) {
        if(!(player instanceof ServerPlayer p)||!stillValid(p)||(code>>>8)!=view.get(2))return false;
        int action=code&255;view.set(2,view.get(2)==32760?1:view.get(2)+1);
        boolean ok=false;
        if(ArmyEncounters.active(p)&&action!=12&&action!=201)return false;
        if(action>=130&&action<136)ok=ArmyEncounters.prepare(p,action-130);
        else if(action>=150&&action<186&&!deployed()) {selected=action-150;ok=selected<ArmyRoster.soldiers(p).size();if(!ok)selected=-1;}
        else if(action>=186&&action<195&&!deployed()&&selected>=0&&selected<ArmyRoster.soldiers(p).size()) {
            var list=ArmyRoster.soldiers(p);var record=list.getCompound(selected);
            if(record.getString("State").equals("RESERVE")) {
                int slot=action-186,old=record.getInt("Slot");
                for(var value:list){var other=(net.minecraft.nbt.CompoundTag)value;if(other!=record&&other.getInt("Slot")==slot)other.putInt("Slot",old);}
                record.putInt("Slot",slot);ok=true;
            }
        }
        else if(action==200)ok=ArmyEncounters.start(p);
        else if(action==201){ArmyEncounters.finish(p,false,"主动撤离");ok=true;}
        else if(action<3&&desk!=null)ok=ArmyRoster.recruit(p,action);
        else if(action==10)ok=ArmyRoster.deploy(p,view.get(3),9)>0;
        else if(action==11)ok=ArmyRoster.recall(p)>0;
        else if(action==12) {
            for(var level:p.server.getAllLevels())for(var r:ArmyRoster.soldiers(p)) {
                var n=(net.minecraft.nbt.CompoundTag)r;
                if(n.hasUUID("Entity")&&level.getEntity(n.getUUID("Entity")) instanceof com.dynasty.entity.ImperialSoldier s&&ArmyRoster.valid(s,p))s.getPersistentData().putFloat("ArmyYaw",p.getYRot());
            }
            ok=true;
        } else if(action>=20&&action<25&&!deployed()) {ArmyRoster.data(p).putInt("Formation",action-20);ok=true;}
        else if(action==13&&!deployed()) {
            int slot=0;for(var value:ArmyRoster.soldiers(p)){var n=(net.minecraft.nbt.CompoundTag)value;n.putInt("Slot",slot<9&&n.getString("State").equals("RESERVE")?slot++:-1);}ok=true;
        } else if(action>=40&&action<76&&!deployed()) {
            int index=action-40;var list=ArmyRoster.soldiers(p);
            if(index<list.size()) {
                var n=list.getCompound(index);
                if(desk!=null&&n.getString("State").equals("WOUNDED"))ok=ArmyRoster.repair(p,index);
                else if(n.getInt("Slot")>=0){n.putInt("Slot",-1);ok=true;}
                else {var used=new boolean[9];for(var v:list){int slot=((net.minecraft.nbt.CompoundTag)v).getInt("Slot");if(slot>=0&&slot<9)used[slot]=true;}for(int i=0;i<9;i++)if(!used[i]){n.putInt("Slot",i);ok=true;break;}}
            }
        } else if(action>=100&&action<103&&!deployed()) {
            var preset=new net.minecraft.nbt.ListTag();for(var value:ArmyRoster.soldiers(p)) {var n=(net.minecraft.nbt.CompoundTag)value;var row=new net.minecraft.nbt.CompoundTag();row.putUUID("Id",n.getUUID("Id"));row.putInt("Slot",n.getInt("Slot"));preset.add(row);}
            ArmyRoster.data(p).put("Preset"+(action-100),preset);ArmyRoster.data(p).putInt("PresetFormation"+(action-100),view.get(3));ok=true;
        } else if(action>=110&&action<113&&!deployed()&&ArmyRoster.data(p).contains("Preset"+(action-110),9)) {
            for(var value:ArmyRoster.soldiers(p))((net.minecraft.nbt.CompoundTag)value).putInt("Slot",-1);
            for(var value:ArmyRoster.data(p).getList("Preset"+(action-110),10)){var n=(net.minecraft.nbt.CompoundTag)value;var r=ArmyRoster.find(p,n.getUUID("Id"));if(r!=null)r.putInt("Slot",n.getInt("Slot"));}
            ArmyRoster.data(p).putInt("Formation",ArmyRoster.data(p).getInt("PresetFormation"+(action-110)));ok=true;
        }
        if(ok)ArmyRoster.changed(p);refresh();broadcastChanges();return ok;
    }
    private boolean deployed(){for(var value:ArmyRoster.soldiers(owner))if(((net.minecraft.nbt.CompoundTag)value).getString("State").equals("DEPLOYED"))return true;return false;}
}
