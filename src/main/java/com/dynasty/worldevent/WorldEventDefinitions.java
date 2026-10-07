package com.dynasty.worldevent;

import com.google.gson.*;
import net.minecraft.resources.ResourceLocation;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Runtime definitions only; the design brief belongs in the local implementation map, not the shipped jar. */
public final class WorldEventDefinitions {
    public static final Map<ResourceLocation,WorldEventDefinition> ALL=load();
    private static ResourceLocation id(String text){return new ResourceLocation(text.contains(":")?text:"dynasty:"+text);}
    private static ResourceLocation optional(JsonObject json,String key){return json.has(key)&&!json.get(key).isJsonNull()?id(json.get(key).getAsString()):null;}
    private static Set<String> strings(JsonObject json,String key){var out=new LinkedHashSet<String>();if(json.has(key))for(var value:json.getAsJsonArray(key))out.add(value.getAsString());return out;}
    private static Map<ResourceLocation,WorldEventDefinition> load(){
        var result=new LinkedHashMap<ResourceLocation,WorldEventDefinition>();
        try(var stream=WorldEventDefinitions.class.getResourceAsStream("/data/dynasty/world_events/catalog.json")){
            if(stream==null)throw new IllegalStateException("Missing world event catalog");
            for(var value:JsonParser.parseReader(new InputStreamReader(stream,StandardCharsets.UTF_8)).getAsJsonArray()){
                var o=value.getAsJsonObject();var actors=new ArrayList<WorldEventDefinition.Actor>();
                for(var a:o.getAsJsonArray("actors")){var x=a.getAsJsonObject();actors.add(new WorldEventDefinition.Actor(id(x.get("type").getAsString()),x.get("count").getAsInt(),x.get("team").getAsString()));}
                var d=new WorldEventDefinition(id(o.get("id").getAsString()),o.get("name").getAsString(),id(o.get("dimensionTag").getAsString()),
                    optional(o,"biomeTag"),optional(o,"structureTag"),o.get("minY").getAsInt(),o.get("maxY").getAsInt(),o.get("startTime").getAsInt(),o.get("endTime").getAsInt(),
                    o.get("weather").getAsString(),strings(o,"requiredWorldStates"),strings(o,"forbiddenWorldStates"),o.get("minDistanceFromSpawn").getAsInt(),o.get("cooldown").getAsInt(),
                    o.get("globalCooldownGroup").getAsString(),o.get("maxConcurrent").getAsInt(),o.get("radius").getAsInt(),o.get("duration").getAsInt(),o.get("rarity").getAsInt(),
                    WorldEventDefinition.RewardMode.valueOf(o.get("rewardMode").getAsString()),WorldEventDefinition.CleanupPolicy.valueOf(o.get("cleanupPolicy").getAsString()),
                    WorldEventDefinition.Controller.valueOf(o.get("controller").getAsString()),optional(o,"rewardTable"),actors,strings(o,"dependencies").stream().map(WorldEventDefinitions::id).toList());
                if(result.put(d.id(),d)!=null)throw new IllegalStateException("Duplicate event "+d.id());
            }
        }catch(java.io.IOException e){throw new IllegalStateException(e);}
        if(result.size()!=30)throw new IllegalStateException("Expected exactly 30 source events");
        return Collections.unmodifiableMap(result);
    }
    private WorldEventDefinitions(){}
}
