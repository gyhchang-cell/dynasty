package com.dynasty;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.TagParser;
import java.nio.file.Files;
import java.nio.file.Path;

/** Loads the separately reviewed finite contract as native SNBT; does not derive expectations from the copier. */
public final class LegacyProgressionFieldMatrix {
    private static int checks;
    private static void check(boolean yes,String why){checks++;if(!yes)throw new AssertionError(why);}
    public static void main(String[] args) throws Exception {
        CompoundTag source=TagParser.parseTag(Files.readString(Path.of(args[0])));
        CompoundTag expected=source.copy(),target=new CompoundTag();
        check(source.getAllKeys().size()==107,"reviewed field fixture drift");
        source.putString("dynasty_unreviewed","keep only at source");
        var invalid=LegacyPlayerProgression.copyAuditedRoot(source,target);
        check(invalid.isEmpty(),"valid complete fixture diagnosed "+invalid);
        check(target.equals(expected),"audited field set omitted/extra/changed");
        for(String key:expected.getAllKeys()){
            check(target.get(key).equals(expected.get(key)),"wrong value/type for "+key);
            CompoundTag corrupt=expected.copy(),actual=new CompoundTag(),wanted=expected.copy();
            corrupt.putString(key,"not the expected tag type");
            // String facts need a wrong numeric type instead.
            if(expected.get(key).getId()==8)corrupt.putInt(key,77);
            wanted.remove(key);
            if(key.equals("dynasty_merit_kill_window")||key.equals("dynasty_merit_kill_earned")){
                wanted.remove("dynasty_merit_kill_window");wanted.remove("dynasty_merit_kill_earned");
            }
            var errors=LegacyPlayerProgression.copyAuditedRoot(corrupt,actual);
            check(!errors.isEmpty(),"wrong type undiagnosed "+key);
            check(actual.equals(wanted),"corrupt field altered other facts or was coerced: "+key);
        }
        for(String key:expected.getAllKeys())if(key.startsWith("dynasty_firstkill_")){
            CompoundTag old=new CompoundTag(),persisted=new CompoundTag(),next=new CompoundTag();
            persisted.putBoolean(key,true);old.put("PlayerPersisted",persisted);next.put("PlayerPersisted",persisted);
            CompoundTag before=old.copy();LegacyPlayerProgression.copyAuditedRoot(old,next);
            check(next.getBoolean(key),"nested firstkill alias not restored "+key);
            check(old.equals(before),"shared nested source modified "+key);
        }
        System.out.println("PASS "+checks+" contract-driven native-SNBT assertions over107 fields; no Clone-event/player/world/runtime credit");
    }
}
