package com.dynasty.cod3;

import com.dynasty.Dynasty;
import com.google.gson.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Immutable, reviewed definitions. Missing boss bindings remain unbound, never guessed at runtime. */
public final class Cod3Catalog {
    private static final Gson GSON=new Gson();
    private static final JsonObject data=readBuiltin();
    private static final Map<Integer,DynastyVfxDefinition> VFX=new HashMap<>();
    private static final Map<String,BossSequenceDefinition> SEQUENCES=new HashMap<>();
    private static final Map<String,BossSequenceDefinition> SEQUENCE_IDS=new HashMap<>();
    static {
        for(var row:entries("vfx")){var definition=GSON.fromJson(row,DynastyVfxDefinition.class);if(definition.radius()<=0||definition.length()<=0||definition.width()<=0||definition.duration()<=0)throw new IllegalArgumentException("Invalid VFX "+definition.id());VFX.put(definition.id(),definition);}
        for(String group:List.of("intros","deaths"))for(var row:entries(group)){var definition=BossSequenceDefinition.fromJson(row.toString());if(SEQUENCE_IDS.put(definition.id(),definition)!=null)throw new IllegalArgumentException("Duplicate sequence id "+definition.id());for(String boss:definition.bossIds())if(SEQUENCES.put(group+":"+boss,definition)!=null)throw new IllegalArgumentException("Duplicate boss sequence "+boss);}
    }
    private static JsonObject readBuiltin(){
        try(var stream=Cod3Catalog.class.getResourceAsStream("/data/dynasty/cod3/catalog.json")){
            if(stream==null)throw new IOException("Missing cod3 catalogue");
            return JsonParser.parseReader(new InputStreamReader(stream,StandardCharsets.UTF_8)).getAsJsonObject();
        }catch(IOException e){throw new IllegalStateException(e);}
    }
    public static JsonArray entries(String group){return data.getAsJsonArray(group);}
    public static JsonObject find(String group,String id){for(var e:entries(group))if(e.getAsJsonObject().get("id").getAsString().equals(id))return e.getAsJsonObject();throw new IllegalArgumentException("Unknown cod3 id: "+id);}
    public static BossSequenceDefinition sequence(String group,String boss){
        return SEQUENCES.get(group+":"+boss);
    }
    public static BossSequenceDefinition sequenceById(String id){return SEQUENCE_IDS.get(id);}
    public static DynastyVfxDefinition vfx(int id){var d=VFX.get(id);if(d==null)throw new IllegalArgumentException("Unknown VFX "+id);return d;}
    private Cod3Catalog(){}
}
