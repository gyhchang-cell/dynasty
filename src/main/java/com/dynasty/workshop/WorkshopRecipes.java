package com.dynasty.workshop;

import com.dynasty.block.LivingWorkshopBlock.Kind;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.List;

/** One source for server transactions, client fill visuals and JEI. Ordered, one item per click. */
public final class WorkshopRecipes {
    public record Cost(String id,int count) {
        public ItemStack stack(){return new ItemStack(ForgeRegistries.ITEMS.getValue(new ResourceLocation(id)),count);}
    }
    public record Recipe(Kind kind,String station,List<Cost> costs,String output,int count) {
        public int total(){return costs.stream().mapToInt(Cost::count).sum();}
        public Cost next(int deposited){for(var c:costs){if(deposited<c.count)return c;deposited-=c.count;}return null;}
        public ItemStack result(){return new Cost(output,count).stack();}
        /** Stone-sprite jade is a lapidary substitute, not a global crystal replacement. */
        public List<ItemStack> choices(Cost cost){
            if(kind==Kind.LAPIDARY && cost.id().equals("dynasty:dragon_crystal"))
                return List.of(cost.stack(),new Cost("dynasty:sprite_jade",cost.count()).stack());
            return List.of(cost.stack());
        }
        public boolean accepts(int deposited,ItemStack held){
            var cost=next(deposited);return cost!=null&&!held.isEmpty()&&choices(cost).stream().anyMatch(s->held.is(s.getItem()));
        }
    }
    private static Cost c(String id,int n){return new Cost("dynasty:"+id,n);}
    public static final List<Recipe> ALL=List.of(
        new Recipe(Kind.MARROW,"marrow_vat",List.of(c("emperor_bone",1),c("cinnabar",4),c("jade",2)),"dynasty:mingyuan_soul_lantern",1),
        new Recipe(Kind.ESSENCE,"essence_condenser",List.of(c("dragon_crystal",3),c("dragon_scale",2)),"dynasty:longmai_prism",1),
        new Recipe(Kind.REPAIR,"jade_mending_forge",List.of(c("jade",4),c("silver_ingot",2)),"dynasty:chengque_mending_seal",1),
        new Recipe(Kind.VITALITY,"vitality_shrine",List.of(c("jade",2),c("immortal_peach",1)),"dynasty:pill_longevity",1),
        new Recipe(Kind.HIDE,"hide_stretcher",List.of(c("dragon_scale",3),c("silk",2)),"dynasty:zhengwu_oath_tally",1),
        new Recipe(Kind.HERBAL,"herbal_basin",List.of(c("cinnabar",2),c("tea",2)),"dynasty:healing_salve",2),
        new Recipe(Kind.LAPIDARY,"lapidary_bench",List.of(c("bamboo_slip",2),c("dragon_crystal",1),c("ink_stick",1)),"dynasty:zhouguang_star_leaf",1),
        new Recipe(Kind.EMBER,"ember_brazier",List.of(c("zhuque_feather",1),c("cinnabar",3)),"dynasty:chixiao_ember",1));
    public static Recipe get(Kind kind){return ALL.stream().filter(r->r.kind==kind).findFirst().orElseThrow();}
    private WorkshopRecipes(){}
}
