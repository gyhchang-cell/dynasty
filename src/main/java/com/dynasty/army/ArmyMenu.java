package com.dynasty.army;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.*;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.ItemStack;

/** Indexed requests resolve against the server's own roster. A revision rejects repeated/stale button packets. */
public final class ArmyMenu extends AbstractContainerMenu {
    public static final int LAYOUT_REVISION = 3;
    public final BlockPos desk;
    private final Player owner;
    public static final int WINDOW=36;
    private int selected=-1,rosterWindow,slotPage;
    public int total(){return readInt(0,119);}
    public int balance(){return readInt(1,120);}
    public int window(){return readInt(116,122);}
    public int slotPage(){return readInt(117,123);}
    public int selectedIndex(){return readInt(114,121);}
    public int rowSlot(int local){return readInt(160+local*2,161+local*2);}
    private int readInt(int low,int high){return (view.get(low)&65535)|(view.get(high)<<16);}
    private void putInt(int low,int high,int value){view.set(low,value&65535);view.set(high,value>>>16);}
    private long retreatUntil=-1;
    public final ContainerData view=new SimpleContainerData(232);
    public ArmyMenu(int id,Inventory inventory,BlockPos desk) {
        super(ArmyContent.MENU.get(),id);owner=inventory.player;this.desk=desk;addDataSlots(view);
        if(!owner.level().isClientSide){view.set(2,nextRevision(owner));refresh();}
    }
    /** Original16-bit UI revision now advances in the same player save as inventory and paid roster. */
    private static int nextRevision(Player player){
        var data=ArmyRoster.data(player);int previous=data.getInt("MenuRevision");
        int next=previous>=1&&previous<32760?previous+1:1;data.putInt("MenuRevision",next);return next;
    }
    public void refresh() {
        if(owner.level().isClientSide)return;
        var list=ArmyRoster.soldiers(owner);putInt(0,119,list.size());putInt(1,120,ArmyRoster.coins(owner));
        rosterWindow=Math.min(rosterWindow,Math.max(0,(list.size()-1)/WINDOW));slotPage=Math.min(slotPage,Math.max(0,(list.size()-1)/9));
        putInt(116,122,rosterWindow);putInt(117,123,slotPage);view.set(118,deployed()?1:0);
        view.set(3,ArmyRoster.data(owner).getInt("Formation"));view.set(4,desk!=null?1:0);view.set(5,owner instanceof ServerPlayer p?(ArmyEncounters.active(p)?2:ArmyEncounters.inside(p)?1:0):0);
        putInt(114,121,selected);
        view.set(115,owner instanceof ServerPlayer p&&retreatUntil>=p.server.overworld().getGameTime()?1:0);
        for(int i=0;i<36;i++) {
            int index=rosterWindow*WINDOW+i;var r=list.getCompound(index);view.set(6+i*3,r.getInt("Role"));view.set(7+i*3,(int)Math.ceil(r.getFloat("Health")));
            view.set(8+i*3,(r.getBoolean("RecallRequested")?128:r.getString("State").equals("DEPLOYED")?32:r.getString("State").equals("WOUNDED")?64:0)+(index<list.size()&&r.getInt("Slot")>=0?1:0));
            putInt(160+i*2,161+i*2,index<list.size()?r.getInt("Slot"):-1);
        }
    }
    @Override public void broadcastChanges(){refresh();super.broadcastChanges();}
    @Override public boolean stillValid(Player p) {
        return p==owner&&p.isAlive()&&(desk==null?ArmyRoster.hasTally(p):p.level().hasChunkAt(desk)&&p.distanceToSqr(desk.getX()+.5,desk.getY()+.5,desk.getZ()+.5)<=64&&p.level().getBlockState(desk).is(ArmyContent.DESK.get()));
    }
    @Override public ItemStack quickMoveStack(Player p,int index){return ItemStack.EMPTY;}
    @Override public boolean clickMenuButton(Player player,int code) {
        if(!(player instanceof ServerPlayer p)||!stillValid(p)||(code>>>8)!=view.get(2))return false;
        int action=code&255;view.set(2,nextRevision(p));
        boolean ok=false;
        if(ArmyEncounters.active(p)&&action!=12&&action!=201&&(action<80||action>83))return false;
        if(action==80||action==81){rosterWindow=Math.max(0,Math.min(Math.max(0,(ArmyRoster.soldiers(p).size()-1)/WINDOW),rosterWindow+(action==80?-1:1)));selected=-1;ok=true;}
        else if(action==82||action==83){slotPage=Math.max(0,Math.min(Math.max(0,(ArmyRoster.soldiers(p).size()-1)/9),slotPage+(action==82?-1:1)));ok=true;}
        else if(action>=130&&action<136)ok=ArmyEncounters.prepare(p,action-130);
        else if(action>=150&&action<186&&!deployed()) {selected=rosterWindow*WINDOW+action-150;ok=selected<ArmyRoster.soldiers(p).size();if(!ok)selected=-1;}
        else if(action>=186&&action<195&&!deployed()&&selected>=0&&selected<ArmyRoster.soldiers(p).size()) {
            var list=ArmyRoster.soldiers(p);var record=list.getCompound(selected);
            if(record.getString("State").equals("RESERVE")) {
                int slot=slotPage*9+action-186;if(slot>=list.size())return false;int old=record.getInt("Slot");
                for(var value:list){var other=(net.minecraft.nbt.CompoundTag)value;if(other!=record&&other.getInt("Slot")==slot)other.putInt("Slot",old);}
                record.putInt("Slot",slot);ok=true;
            }
        }
        else if(action==200)ok=ArmyEncounters.start(p);
        else if(action==201&&ArmyEncounters.inside(p)) {
            long now=p.server.overworld().getGameTime();
            if(ArmyEncounters.active(p)&&retreatUntil<now){retreatUntil=now+100;ok=true;}
            else {ArmyEncounters.finish(p,false,"主动撤离");retreatUntil=-1;ok=true;}
        }
        else if(action<3&&desk!=null)ok=ArmyRoster.recruit(p,action);
        else if(action==10)ok=ArmyRoster.deploy(p,view.get(3),ArmyRoster.soldiers(p).size())>0;
        else if(action==11)ok=ArmyRoster.recall(p)>0;
        else if(action==12) {
            for(var level:p.server.getAllLevels())for(var r:ArmyRoster.soldiers(p)) {
                var n=(net.minecraft.nbt.CompoundTag)r;
                if(n.hasUUID("Entity")&&level.getEntity(n.getUUID("Entity")) instanceof com.dynasty.entity.ImperialSoldier s&&ArmyRoster.valid(s,p))s.getPersistentData().putFloat("ArmyYaw",p.getYRot());
            }
            ok=true;
        } else if(action>=20&&action<25&&!deployed()) {ArmyRoster.data(p).putInt("Formation",action-20);ok=true;}
        else if(action==13&&!deployed()) {
            int slot=0;for(var value:ArmyRoster.soldiers(p)){var n=(net.minecraft.nbt.CompoundTag)value;n.putInt("Slot",n.getString("State").equals("RESERVE")?slot++:-1);}ok=true;
        } else if(action>=40&&action<76&&!deployed()) {
            int index=rosterWindow*WINDOW+action-40;var list=ArmyRoster.soldiers(p);
            if(index<list.size()) {
                var n=list.getCompound(index);
                if(desk!=null&&n.getString("State").equals("WOUNDED"))ok=ArmyRoster.repair(p,index);
                else if(n.getInt("Slot")>=0){n.putInt("Slot",-1);ok=true;}
                else {var used=new java.util.HashSet<Integer>();for(var v:list){int slot=((net.minecraft.nbt.CompoundTag)v).getInt("Slot");if(slot>=0)used.add(slot);}int free=0;while(used.contains(free))free++;n.putInt("Slot",free);ok=true;}
            }
        } else if(action>=100&&action<103&&!deployed()) {
            var preset=new net.minecraft.nbt.ListTag();for(var value:ArmyRoster.soldiers(p)) {var n=(net.minecraft.nbt.CompoundTag)value;var row=new net.minecraft.nbt.CompoundTag();row.putUUID("Id",n.getUUID("Id"));row.putInt("Slot",n.getInt("Slot"));preset.add(row);}
            ArmyRoster.data(p).put("Preset"+(action-100),preset);ArmyRoster.data(p).putInt("PresetFormation"+(action-100),view.get(3));ok=true;
        } else if(action>=110&&action<113&&!deployed()&&ArmyRoster.data(p).contains("Preset"+(action-110),9)) {
            ok=loadPreset(p,action-110);
        }
        if(ok)ArmyRoster.changed(p);refresh();broadcastChanges();return ok;
    }
    /** Validate the complete stored preset before touching the current formation. */
    static boolean loadPreset(ServerPlayer p,int presetIndex) {
        if(presetIndex<0||presetIndex>2||ArmyEncounters.active(p))return false;
        var data=ArmyRoster.data(p);String key="Preset"+presetIndex;
        if(!data.contains(key,9))return false;
        int formation=data.getInt("PresetFormation"+presetIndex);if(formation<0||formation>=5)return false;
        var usedIds=new java.util.HashSet<java.util.UUID>();var usedSlots=new java.util.HashSet<Integer>();
        var assignments=new java.util.HashMap<java.util.UUID,Integer>();
        for(var value:data.getList(key,10)) {
            var row=(net.minecraft.nbt.CompoundTag)value;
            if(!row.hasUUID("Id")||!usedIds.add(row.getUUID("Id")))return false;
            int slot=row.getInt("Slot");if(slot< -1)return false;
            if(slot>=0&&!usedSlots.add(slot))return false;
            var soldier=ArmyRoster.find(p,row.getUUID("Id"));
            // An unavailable former member leaves a gap; it never creates an asset.
            if(soldier!=null&&slot>=0&&(soldier.getString("State").equals("RESERVE")||soldier.getString("State").equals("WOUNDED")))
                assignments.put(row.getUUID("Id"),slot);
        }
        for(var value:ArmyRoster.soldiers(p)) {
            var row=(net.minecraft.nbt.CompoundTag)value;
            if(row.getString("State").equals("DEPLOYED"))return false;
        }
        for(var value:ArmyRoster.soldiers(p)) {
            var row=(net.minecraft.nbt.CompoundTag)value;
            row.putInt("Slot",row.hasUUID("Id")?assignments.getOrDefault(row.getUUID("Id"),-1):-1);
        }
        data.putInt("Formation",formation);return true;
    }
    private boolean deployed(){for(var value:ArmyRoster.soldiers(owner))if(((net.minecraft.nbt.CompoundTag)value).getString("State").equals("DEPLOYED"))return true;return false;}
}
