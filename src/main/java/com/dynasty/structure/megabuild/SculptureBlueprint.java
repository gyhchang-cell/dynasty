package com.dynasty.structure.megabuild;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Set;
import java.util.zip.GZIPInputStream;

/** Immutable, bounded and checksum-verified imported original artwork. No world access here. */
public final class SculptureBlueprint {
    public static final Set<String> IDS = Set.of("longque_sanctuary", "yunqi_manor");
    public record Cell(int x, int y, int z, String state) {}
    public record Node(int slot, int x, int y, int z) {}
    public final String id, title, sha256, manifestSha256;
    public final int width, height, length, blockCount;
    public final List<String> palette;
    public final byte[] voxels;
    public final int[] ritualCore;
    public final List<Cell> ritualOwned;
    public final List<Node> ritualNodes;

    private SculptureBlueprint(JsonObject m, byte[] raw, String manifestHash) throws IOException {
        manifestSha256=manifestHash;
        id=m.get("id").getAsString(); title=m.get("title").getAsString(); sha256=m.get("sha256").getAsString();
        width=m.get("width").getAsInt(); height=m.get("height").getAsInt(); length=m.get("length").getAsInt();
        blockCount=m.get("blockCount").getAsInt(); voxels=raw;
        List<String> p=new ArrayList<>(); m.getAsJsonArray("palette").forEach(s->p.add(s.getAsString()));
        if(p.isEmpty()||p.size()>256||!p.get(0).equals("minecraft:air"))throw new IOException("Invalid palette");
        palette=List.copyOf(p); int count=0;
        for(byte value:raw){int v=Byte.toUnsignedInt(value);if(v>=palette.size())throw new IOException("Invalid palette index");if(v!=0)count++;}
        if(count!=blockCount)throw new IOException("Non-air count mismatch");
        List<Cell> owned=new ArrayList<>();List<Node> nodes=new ArrayList<>();
        var ritual=m.get("ritual");
        if(ritual!=null&&!ritual.isJsonNull()){
            var r=ritual.getAsJsonObject();var c=r.getAsJsonArray("returnFeet");
            if(c.size()!=3)throw new IOException("Invalid return feet");
            ritualCore=new int[]{c.get(0).getAsInt(),c.get(1).getAsInt(),c.get(2).getAsInt()};
            if(!inside(ritualCore[0],ritualCore[1],ritualCore[2]))throw new IOException("Return feet outside sculpture");
            if(ritualCore[1]<1||at(ritualCore[0],ritualCore[1]-1,ritualCore[2])==0)throw new IOException("Return feet has no supporting floor");
            Set<String> ownedPositions=new java.util.HashSet<>();
            for(var entry:r.getAsJsonArray("owned")){var o=entry.getAsJsonObject();Cell cell=new Cell(o.get("x").getAsInt(),o.get("y").getAsInt(),o.get("z").getAsInt(),o.get("state").getAsString());
                if(!inside(cell.x,cell.y,cell.z)||cell.y<ritualCore[1]||at(cell.x,cell.y,cell.z)==0||!palette.get(at(cell.x,cell.y,cell.z)).equals(cell.state)
                        ||!ownedPositions.add(cell.x+","+cell.y+","+cell.z))throw new IOException("Ritual ownership mismatch");owned.add(cell);}
            if(owned.size()>20_000)throw new IOException("Oversized altar ledger");
            for(var entry:r.getAsJsonArray("nodes")){var o=entry.getAsJsonObject();nodes.add(new Node(o.get("slot").getAsInt(),o.get("x").getAsInt(),o.get("y").getAsInt(),o.get("z").getAsInt()));}
            if(nodes.size()!=5||nodes.stream().map(Node::slot).distinct().count()!=5||nodes.stream().anyMatch(n->n.slot<0||n.slot>4||!inside(n.x,n.y,n.z)))throw new IOException("Invalid ritual nodes");
            Set<String> nodePositions=new java.util.HashSet<>();
            for(Node n:nodes){String pos=n.x+","+n.y+","+n.z, state=palette.get(at(n.x,n.y,n.z));
                if(!nodePositions.add(pos)||!ownedPositions.contains(pos)||!state.startsWith("dynasty:zhenyuan_node[")
                        ||!state.matches(".*(?:\\[|,)slot="+n.slot+"(?:,|\\]).*"))throw new IOException("Node is not owned or has wrong slot");}
        }else ritualCore=null;
        ritualOwned=List.copyOf(owned);ritualNodes=List.copyOf(nodes);
    }
    public boolean inside(int x,int y,int z){return x>=0&&x<width&&y>=0&&y<height&&z>=0&&z<length;}
    public int at(int x,int y,int z){return Byte.toUnsignedInt(voxels[x+z*width+y*width*length]);}
    public int volume(){return voxels.length;}

    public static SculptureBlueprint load(ResourceManager resources,String id)throws IOException{
        if(!IDS.contains(id))throw new IOException("Unknown sculpture id");
        byte[] manifest,gzip;
        try(var in=resources.getResourceOrThrow(new ResourceLocation("dynasty","sculptures/"+id+".json")).open()){
            manifest=in.readNBytes(4_000_001);if(manifest.length>4_000_000)throw new IOException("Manifest too large");}
        try(var in=resources.getResourceOrThrow(new ResourceLocation("dynasty","sculptures/"+id+".vox.gz")).open()){
            gzip=in.readNBytes(8_000_001);if(gzip.length>8_000_000)throw new IOException("Voxel resource too large");}
        return decode(id,manifest,gzip);
    }
    /** Public for pure resource integrity tests; full decompression never runs inside the placement tick. */
    public static SculptureBlueprint decode(String expectedId,byte[] manifest,byte[] gzip)throws IOException{
        try{
            JsonObject m=JsonParser.parseString(new String(manifest,StandardCharsets.UTF_8)).getAsJsonObject();
            if(!IDS.contains(expectedId)||!expectedId.equals(m.get("id").getAsString())||m.get("version").getAsInt()!=1
                    ||!m.get("format").getAsString().equals("dense-u8-gzip")||!m.get("order").getAsString().equals("x+z*width+y*width*length"))throw new IOException("Unsupported sculpture format");
            int w=m.get("width").getAsInt(),h=m.get("height").getAsInt(),l=m.get("length").getAsInt();
            long volume=(long)w*h*l;
            if(w<1||h<1||l<1||w>1024||h>384||l>1024||volume>64_000_000||volume!=m.get("voxelCount").getAsLong())throw new IOException("Invalid bounds");
            if(!digest(gzip).equals(m.get("gzipSha256").getAsString()))throw new IOException("Compressed checksum mismatch");
            byte[] raw;try(var in=new GZIPInputStream(new ByteArrayInputStream(gzip))){raw=in.readNBytes((int)volume+1);}
            if(raw.length!=volume||!digest(raw).equals(m.get("sha256").getAsString()))throw new IOException("Voxel checksum/length mismatch");
            return new SculptureBlueprint(m,raw,digest(manifest));
        }catch(IOException e){throw e;}catch(Exception e){throw new IOException("Invalid sculpture data",e);}
    }
    private static String digest(byte[] bytes)throws Exception{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));}
}
