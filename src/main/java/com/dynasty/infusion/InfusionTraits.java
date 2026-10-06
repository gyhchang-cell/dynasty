package com.dynasty.infusion;

import java.util.*;
import net.minecraft.nbt.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraftforge.registries.ForgeRegistries;

/** Additive stack data only. Never changes the registered material or its original recipes. */
public final class InfusionTraits {
    public static final String KEY="DynastyInfusion";
    public static final int SLOTS=3, CAPACITY=4, MATERIAL_COST=2, XP_COST=3;
    public enum Kind { WEAPON, ARMOR, BOTH }
    public record Trait(String material, String name, String description, Kind kind, String family, int cost, String gate) {
        public boolean accepts(ItemStack stack) {return !(stack.getItem() instanceof ProjectileWeaponItem && (material.equals("shanxiao_claw")||material.equals("baihu_fang")))&&eligible(stack)&&(kind==Kind.BOTH||(kind==Kind.ARMOR)==(stack.getItem() instanceof ArmorItem||stack.getItem() instanceof ShieldItem));}
    }
    private static Trait t(String id,String name,String description,Kind kind,String family,int cost,String gate){return new Trait(id,name,description,kind,family,cost,gate);}
    public static final List<Trait> ALL=List.of(
        t("shanxiao_claw","魈爪连袭","同目标三次蓄满近战：撕裂，追加15%伤害并短暂减速。",Kind.WEAPON,"pursuit",1,""),
        t("ghost_face_fur","鬼面脱身","受敌人重击（≥最大生命8%）后隐身2秒；冷却12秒。",Kind.ARMOR,"escape",1,""),
        t("yin_jade_shard","寒玉镇魂","蓄满攻击亡灵时减速2秒；冷却6秒。",Kind.WEAPON,"yin",1,""),
        t("nether_tatter","幽缕卸力","受到魔法伤害时减伤20%，获得缓降3秒；冷却8秒。",Kind.ARMOR,"yin",1,""),
        t("blackened_bone","腐骨镇煞","受到亡灵攻击后净化中毒并获得抗性2秒；冷却10秒。",Kind.ARMOR,"purify",1,""),
        t("vengeful_war_soul","战魂蓄煞","蓄满攻击积煞，第四击释放：追加20%伤害、虚弱目标2秒。",Kind.WEAPON,"yin",2,"entered_underworld"),
        t("heavy_shield_remnant","残盾定势","成功格挡时减免盾牌耐久消耗；冷却6秒。",Kind.ARMOR,"guard",1,""),
        t("fine_steel_chain","钢链稳身","敌人击退强度减半；冷却5秒。",Kind.ARMOR,"stability",1,""),
        t("swift_boot_scrap","疾履借势","受敌人攻击后疾行2秒；冷却8秒。",Kind.ARMOR,"escape",1,""),
        t("dry_peach_branch","桃木辟邪","命中亡灵后驱邪：发光4秒、虚弱2秒；冷却6秒。",Kind.WEAPON,"purify",1,""),
        t("bronze_ingot","青铜破势","蓄满攻击正在使用物品的敌人时打断使用；冷却8秒。",Kind.WEAPON,"impact",1,""),
        t("silver_ingot","银华照隐","蓄满命中隐身敌人时解除隐身并标记4秒；冷却6秒。",Kind.WEAPON,"purify",1,""),
        t("jade","玉息回元","同目标三次蓄满命中恢复1点饥饿值；冷却10秒。",Kind.WEAPON,"resource",1,""),
        t("dragon_scale","龙鳞护身","受重击后获得4点伤害吸收，持续3秒；冷却12秒。",Kind.ARMOR,"ward",2,"entered_celestial"),
        t("dragon_crystal","龙晶雷印","连续蓄满命中同目标两次引雷：追加12%伤害、短暂减速；冷却8秒。",Kind.WEAPON,"spell",2,"entered_celestial"),
        t("cinnabar","朱砂火印","蓄满命中点燃目标3秒；冷却6秒。",Kind.WEAPON,"spell",1,""),
        t("refined_steel","精钢破甲","蓄满命中有护甲敌人时追加10%伤害；冷却5秒。",Kind.WEAPON,"impact",1,""),
        t("xuanwu_shell","玄甲完璧","举盾前8刻成功格挡获得3秒抗性；冷却10秒。",Kind.ARMOR,"guard",2,"entered_celestial"),
        t("qinglong_scale","青龙追身","蓄满命中半血以下目标后获得2秒疾行与跳跃；冷却8秒。",Kind.WEAPON,"pursuit",2,"entered_celestial"),
        t("baihu_fang","白虎重袭","蓄满暴击时追加15%伤害并击退；冷却6秒。",Kind.WEAPON,"impact",2,"entered_celestial"),
        t("zhuque_feather","朱羽阳炁","受到火焰伤害时熄火并获得3秒抗火；冷却12秒。",Kind.ARMOR,"ward",2,"entered_celestial"),
        t("taiyi_jade","太乙御风","下落超过3格时坠落伤害减半；冷却8秒。",Kind.ARMOR,"escape",2,"entered_celestial"),
        t("ink_stick","墨引符法","佩戴后符箓法术命中敌人时获得3秒抗性；冷却10秒。",Kind.ARMOR,"spell",1,""),
        t("talisman_paper","符纸回气","佩戴后符箓法术命中敌人时恢复2点饥饿值；冷却12秒。",Kind.ARMOR,"resource",1,"")
    );
    public static Trait get(String id){return ALL.stream().filter(t->t.material.equals(id)).findFirst().orElse(null);}
    public static Trait material(ItemStack stack){var id=ForgeRegistries.ITEMS.getKey(stack.getItem());return id!=null&&id.getNamespace().equals("dynasty")?get(id.getPath()):null;}
    public static boolean eligible(ItemStack s){return s.getCount()==1&&s.isDamageableItem()&&(s.getItem() instanceof TieredItem||s.getItem() instanceof ArmorItem||s.getItem() instanceof ShieldItem||s.getItem() instanceof ProjectileWeaponItem||s.getItem() instanceof TridentItem);}
    public static List<String> slots(ItemStack s){
        var result=new ArrayList<>(List.of("","",""));
        if(s.hasTag()){var tag=s.getTag().getCompound(KEY);for(int i=0;i<SLOTS;i++){String id=tag.getString("slot"+i);if(get(id)!=null)result.set(i,id);}}
        return result;
    }
    public static int capacity(List<String> slots){return slots.stream().map(InfusionTraits::get).filter(Objects::nonNull).mapToInt(Trait::cost).sum();}
    public static boolean valid(List<String> slots){var families=new HashSet<String>();for(String id:slots){var t=get(id);if(t!=null&&!families.add(t.family))return false;}return capacity(slots)<=CAPACITY;}
    public static Set<String> active(ItemStack s){var slots=slots(s);if(!eligible(s)||!valid(slots))return Set.of();var result=new HashSet<String>();for(String id:slots){var t=get(id);if(t!=null&&t.accepts(s))result.add(id);}return result;}
    public static ItemStack preview(ItemStack base,Trait trait,int slot,boolean remove){
        if(!eligible(base)||slot<0||slot>=SLOTS||(!remove&&(trait==null||!trait.accepts(base))))return ItemStack.EMPTY;
        var ids=slots(base);if(remove&&ids.get(slot).isEmpty())return ItemStack.EMPTY;
        if(!remove&&ids.get(slot).equals(trait.material))return ItemStack.EMPTY;
        ids.set(slot,remove?"":trait.material);if(!valid(ids))return ItemStack.EMPTY;
        ItemStack out=base.copy();CompoundTag tag=new CompoundTag();tag.putInt("version",1);
        for(int i=0;i<SLOTS;i++)if(!ids.get(i).isEmpty())tag.putString("slot"+i,ids.get(i));
        if(ids.stream().allMatch(String::isEmpty))out.removeTagKey(KEY);else out.getOrCreateTag().put(KEY,tag);
        return out;
    }
    public static boolean unlocked(Player p,String id){
        if(p.isCreative()||id.isEmpty())return true;
        if(!(p instanceof ServerPlayer sp))return false;
        var advancement=sp.server.getAdvancements().getAdvancement(new ResourceLocation("dynasty",id));
        return advancement!=null&&sp.getAdvancements().getOrStartProgress(advancement).isDone();
    }
    private InfusionTraits(){}
}
