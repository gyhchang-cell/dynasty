package com.dynasty.structure.megabuild;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.zip.GZIPInputStream;
/** Reviewed normalized workshop edits. Original save remains untouched. */
final class PlayerCityEdits {
    record Run(int x,int y,int z,int end,Blueprint.Kind kind){}
    private static final List<Run> RUNS=load();
    private static List<Run> load(){
        var raw=PlayerCityEdits.class.getResourceAsStream("/data/dynasty/structure_edits/player_city_v9.tsv.gz");
        if(raw==null)throw new IllegalStateException("Missing player city edits");
        try(var reader=new BufferedReader(new InputStreamReader(new GZIPInputStream(raw),StandardCharsets.UTF_8))){
            var rows=new ArrayList<Run>();
            for(String line;(line=reader.readLine())!=null;){
                String[] v=line.split(" ");
                rows.add(new Run(Integer.parseInt(v[0]),Integer.parseInt(v[1]),Integer.parseInt(v[2]),Integer.parseInt(v[3]),Blueprint.Kind.valueOf(v[4])));
            }return List.copyOf(rows);
        }catch(IOException e){throw new UncheckedIOException(e);}
    }
    static void apply(Blueprint b){
        var baseline=new LegacyCitadelV3(0).blueprint();
        for(var r:RUNS)for(int z=r.z;z<=r.end;z++){
            var existing=b.at(r.x,r.y,z);
            if(r.kind==Blueprint.Kind.LIGHT && existing!=Blueprint.Kind.AIR && existing!=baseline.at(r.x,r.y,z))continue;
            b.set(r.x,r.y,z,r.kind);
        }
    }
    static Blueprint originalWithEdits(){
        var b=new LegacyCitadelV3(0).blueprint();
        // Encode the old SOUTH-placement mirror before applying corrected user stairs.
        for(int x=0;x<176;x++)for(int y=0;y<56;y++)for(int z=0;z<176;z++){
            var k=b.at(x,y,z);
            if(k==Blueprint.Kind.STAIR_N)b.set(x,y,z,Blueprint.Kind.STAIR_S);
            if(k==Blueprint.Kind.STAIR_S)b.set(x,y,z,Blueprint.Kind.STAIR_N);
        }
        for(var r:RUNS)for(int z=r.z;z<=r.end;z++)b.set(r.x,r.y,z,r.kind);
        return b;
    }
}
