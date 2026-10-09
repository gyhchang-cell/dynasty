package com.dynasty.infusion;

import com.google.gson.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import net.minecraft.nbt.*;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraftforge.registries.ForgeRegistries;

/** Stack-owned, version-one compatible material IDs backed by the runtime mapping. */
public final class InfusionTraits {
    public static final String KEY="DynastyInfusion";
    public static final int SLOTS=3, CAPACITY=4, MATERIAL_COST=2, XP_COST=3;
    public enum Kind { WEAPON, ARMOR, BOTH }
    public record Trait(String material,String effect,String category,Kind kind,String family,int cost,int count,int tier,String gate,String nameKey,String descriptionKey,String vfx,String sfx) {
        public Component name(){return Component.translatable(nameKey);}
        public Component description(){return Component.translatable(descriptionKey);}
        private boolean meleeOnly(){return Set.of("shanxiao_claw","baihu_fang","heavy_stagger","backstrike","air_step").contains(effect);}
        public Component applicability(){return Component.translatable("infusion.dynasty."+(effect.equals("cold_ward")?"LEATHER":effect.equals("hunter_mark")?"RANGED":material.equals("wolf_fang")?"MELEE_OR_FANG":meleeOnly()?"MELEE":kind.name()));}
        public boolean accepts(ItemStack stack){
            if(!eligible(stack))return false;
            if(effect.equals("cold_ward")&&(!(stack.getItem() instanceof ArmorItem armor)
                    ||armor.getMaterial()!=ArmorMaterials.LEATHER&&armor.getMaterial()!=com.dynasty.DynastyArmorMaterials.LEATHER))return false;
            boolean ranged=stack.getItem() instanceof ProjectileWeaponItem;
            if(meleeOnly()&&ranged||effect.equals("hunter_mark")&&!ranged)return false;
            // Original claw accessory can carry its material-owned melee pursuit; no other weapon trait is broadened.
            if(material.equals("wolf_fang")&&stack.is(com.dynasty.expansion.ExpansionContent.item("tiger_claw")))return true;
            boolean defense=stack.getItem() instanceof ArmorItem||stack.getItem() instanceof ShieldItem||accessory(stack);
            return kind==Kind.BOTH||(kind==Kind.ARMOR)==defense;
        }
    }
    public static final List<Trait> ALL=load();
    private static final Map<String,Trait> BY_MATERIAL=index();
    private static List<Trait> load(){
        try(var stream=InfusionTraits.class.getResourceAsStream("/data/dynasty/infusion/materials.json")){
            if(stream==null)throw new IllegalStateException("Missing infusion definitions");
            var array=JsonParser.parseReader(new InputStreamReader(stream,StandardCharsets.UTF_8)).getAsJsonArray();
            var rows=new ArrayList<Trait>();
            for(var value:array){var o=value.getAsJsonObject();
                var item=new ResourceLocation(o.get("itemId").getAsString());var effect=new ResourceLocation(o.get("enhancementId").getAsString());
                if(!item.getNamespace().equals("dynasty")||!effect.getNamespace().equals("dynasty"))throw new IllegalStateException("Foreign infusion definition");
                rows.add(new Trait(item.getPath(),effect.getPath(),o.get("materialCategory").getAsString(),Kind.valueOf(o.getAsJsonArray("applicableTypes").get(0).getAsString()),o.get("conflictGroup").getAsString(),o.get("capacityCost").getAsInt(),o.get("requiredCount").getAsInt(),o.get("tier").getAsInt(),o.get("gate").getAsString(),o.get("nameKey").getAsString(),o.get("descriptionKey").getAsString(),o.get("VFX").getAsString(),o.get("SFX").getAsString()));
            }return List.copyOf(rows);
        }catch(IOException|RuntimeException e){throw new IllegalStateException("Invalid infusion definitions",e);}
    }
    private static Map<String,Trait> index(){var map=new LinkedHashMap<String,Trait>();for(var t:ALL)if(t.cost<1||t.cost>3||t.count<1||t.tier<1||map.put(t.material,t)!=null)throw new IllegalStateException("Invalid material "+t.material);return Map.copyOf(map);}
    public static Trait get(String id){return BY_MATERIAL.get(id);}
    public static Trait material(ItemStack stack){var id=ForgeRegistries.ITEMS.getKey(stack.getItem());return id!=null&&id.getNamespace().equals("dynasty")?get(id.getPath()):null;}
    public static boolean accessory(ItemStack stack){return stack.getItem() instanceof com.dynasty.DynastyTrinketTips.Charm;}
    public static boolean eligible(ItemStack s){return s.getCount()==1&&(accessory(s)||s.isDamageableItem()&&(s.getItem() instanceof TieredItem||s.getItem() instanceof ArmorItem||s.getItem() instanceof ShieldItem||s.getItem() instanceof ProjectileWeaponItem||s.getItem() instanceof TridentItem));}
    public static int maxCapacity(ItemStack s){int rarity=switch(s.getRarity()){case EPIC->5;case RARE->4;default->3;};return Math.max(rarity,s.getMaxDamage()>=45000?5:s.getMaxDamage()>=8000?4:3);}
    public static List<String> slots(ItemStack s){
        var out=new ArrayList<>(List.of("","",""));
        if(s.hasTag()){var tag=s.getTag().getCompound(KEY);for(int i=0;i<SLOTS;i++){String id=tag.getString("slot"+i);if(get(id)!=null)out.set(i,id);}}return out;
    }
    public static int capacity(List<String> ids){return ids.stream().map(InfusionTraits::get).filter(Objects::nonNull).mapToInt(Trait::cost).sum();}
    private static boolean familiesValid(List<String> ids){var families=new HashSet<String>();for(String id:ids){var t=get(id);if(t!=null&&!families.add(t.family))return false;}return true;}
    public static Set<String> active(ItemStack s){
        var ids=slots(s);
        // Preserve legal old four-capacity equipment while all new writes use native capacity.
        if(!eligible(s)||!familiesValid(ids)||capacity(ids)>Math.max(CAPACITY,maxCapacity(s)))return Set.of();
        var out=new HashSet<String>();for(String id:ids){var t=get(id);if(t!=null&&t.accepts(s))out.add(id);}return out;
    }
    public static Set<String> effects(ItemStack s){var out=new HashSet<String>();for(String id:active(s))out.add(get(id).effect);return out;}
    public static int automaticSlot(ItemStack base){var ids=slots(base);for(int i=0;i<SLOTS;i++)if(ids.get(i).isEmpty())return i;return -1;}
    public static int problem(ItemStack base,Trait trait,int slot,boolean remove){
        if(!eligible(base))return 3;
        if(slot<0||slot>=SLOTS)return remove?12:10;
        var ids=slots(base);if(remove)return ids.get(slot).isEmpty()?12:0;
        if(trait==null)return 11;if(!trait.accepts(base))return 6;
        for(int i=0;i<SLOTS;i++){var old=get(ids.get(i));if(old==null)continue;if(old.effect.equals(trait.effect))return 9;if(i!=slot&&old.family.equals(trait.family))return 8;}
        ids.set(slot,trait.material);return capacity(ids)>maxCapacity(base)?7:0;
    }
    public static ItemStack preview(ItemStack base,Trait trait,int slot,boolean remove){
        if(problem(base,trait,slot,remove)!=0)return ItemStack.EMPTY;
        var ids=slots(base);ids.set(slot,remove?"":trait.material);
        var out=base.copy();var tag=new CompoundTag();tag.putInt("version",1);
        for(int i=0;i<SLOTS;i++)if(!ids.get(i).isEmpty())tag.putString("slot"+i,ids.get(i));
        if(ids.stream().allMatch(String::isEmpty))out.removeTagKey(KEY);else out.getOrCreateTag().put(KEY,tag);return out;
    }
    public static boolean unlocked(Player p,String id){
        if(p.isCreative()||id.isEmpty())return true;if(!(p instanceof ServerPlayer sp))return false;
        var a=sp.server.getAdvancements().getAdvancement(new ResourceLocation("dynasty",id));return a!=null&&sp.getAdvancements().getOrStartProgress(a).isDone();
    }
    private InfusionTraits(){}
}
