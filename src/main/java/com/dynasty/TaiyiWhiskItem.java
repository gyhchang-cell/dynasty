package com.dynasty;

import net.minecraft.world.item.*;

/** Original polearm identity/stats, now with an articulated client-held model. */
public final class TaiyiWhiskItem extends DynastyWeapons.PolearmItem {
    public TaiyiWhiskItem(Tier tier,int damage,float speed,Item.Properties properties){super(tier,damage,speed,properties);}
    @Override public void initializeClient(java.util.function.Consumer<net.minecraftforge.client.extensions.common.IClientItemExtensions> consumer){
        consumer.accept(new net.minecraftforge.client.extensions.common.IClientItemExtensions(){
            private com.dynasty.client.TaiyiWhiskRenderer renderer;
            @Override public net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer getCustomRenderer(){
                if(renderer==null)renderer=new com.dynasty.client.TaiyiWhiskRenderer();return renderer;
            }
        });
    }
}
