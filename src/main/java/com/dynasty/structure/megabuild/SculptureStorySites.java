package com.dynasty.structure.megabuild;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.LinkedHashMap;
import java.util.Map;

/** Completed command placements only. Natural sites use vanilla location advancements.
 * Per-dimension ledger; never loads chunks, scans blocks or awards the command sender.
 */
@Mod.EventBusSubscriber(modid="dynasty")
public final class SculptureStorySites extends SavedData {
    public record Site(String id, BlockPos origin, int width, int height, int length) {
        public AABB bounds() {return new AABB(origin.getX(),origin.getY(),origin.getZ(),
                origin.getX()+(double)width,origin.getY()+(double)height,origin.getZ()+(double)length);}
    }
    private final Map<String,Site> sites=new LinkedHashMap<>();
    public static SculptureStorySites get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(SculptureStorySites::load,SculptureStorySites::new,"dynasty_sculpture_story_sites_v1");
    }
    public void register(String id,BlockPos origin,int width,int height,int length) {
        if(!SculptureBlueprint.IDS.contains(id)||width<1||width>1024||height<1||height>384||length<1||length>1024)
            throw new IllegalArgumentException("Invalid sculpture story bounds");
        Site site=new Site(id,origin.immutable(),width,height,length);
        if(!site.equals(sites.put(id+"@"+origin.asLong(),site)))setDirty();
    }
    public boolean contains(String id,net.minecraft.world.phys.Vec3 pos) {
        return sites.values().stream().anyMatch(s->s.id().equals(id)&&s.bounds().contains(pos));
    }
    public static SculptureStorySites load(CompoundTag tag) {
        var result=new SculptureStorySites();
        for(var entry:tag.getList("Sites",10)) {
            var t=(CompoundTag)entry;
            try {result.register(t.getString("Id"),BlockPos.of(t.getLong("Origin")),t.getInt("Width"),t.getInt("Height"),t.getInt("Length"));}
            catch(IllegalArgumentException ignored) { /* Skip invalid entries without losing valid sites. */ }
        }
        result.setDirty(false);return result;
    }
    @Override public CompoundTag save(CompoundTag tag) {
        var list=new ListTag();
        for(var s:sites.values()) {
            var t=new CompoundTag();t.putString("Id",s.id());t.putLong("Origin",s.origin().asLong());
            t.putInt("Width",s.width());t.putInt("Height",s.height());t.putInt("Length",s.length());list.add(t);
        }
        tag.put("Sites",list);return tag;
    }
    @SubscribeEvent public static void tick(TickEvent.LevelTickEvent e) {
        if(e.phase!=TickEvent.Phase.END||!(e.level instanceof ServerLevel level)||level.getGameTime()%20!=0||level.players().isEmpty())return;
        var data=get(level);if(data.sites.isEmpty())return;
        for(var player:level.players())data.checkPlayer(player);
    }
    void checkPlayer(net.minecraft.server.level.ServerPlayer player) {
        if(player.isSpectator())return;
        for(String id:SculptureBlueprint.IDS) {
            var adv=player.server.getAdvancements().getAdvancement(new ResourceLocation("dynasty","story_visit_"+id));
            if(adv!=null&&!player.getAdvancements().getOrStartProgress(adv).isDone()&&contains(id,player.position()))
                player.getAdvancements().award(adv,"placed");
        }
    }
}
