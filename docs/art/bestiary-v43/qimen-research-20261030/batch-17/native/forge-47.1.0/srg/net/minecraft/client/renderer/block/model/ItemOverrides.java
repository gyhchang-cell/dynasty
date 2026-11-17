package net.minecraft.client.renderer.block.model;

import com.google.common.collect.Lists;
import it.unimi.dsi.fastutil.objects.Object2IntMap;
import it.unimi.dsi.fastutil.objects.Object2IntOpenHashMap;
import java.util.List;
import java.util.Objects;
import javax.annotation.Nullable;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.item.ItemProperties;
import net.minecraft.client.renderer.item.ItemPropertyFunction;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.client.resources.model.BlockModelRotation;
import net.minecraft.client.resources.model.ModelBaker;
import net.minecraft.client.resources.model.UnbakedModel;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class ItemOverrides {
   public static final ItemOverrides f_111734_ = new ItemOverrides();
   public static final float f_265997_ = Float.NEGATIVE_INFINITY;
   private final ItemOverrides.BakedOverride[] f_111735_;
   private final ResourceLocation[] f_173461_;

   protected ItemOverrides() {
      this.f_111735_ = new ItemOverrides.BakedOverride[0];
      this.f_173461_ = new ResourceLocation[0];
   }

   /**
    * @deprecated Forge: Use {@link #ItemOverrides(ModelBaker, UnbakedModel, List, java.util.function.Function)}
    */
   @Deprecated
   public ItemOverrides(ModelBaker p_251211_, BlockModel p_111741_, List<ItemOverride> p_111743_) {
      this(p_251211_, p_111741_, p_111743_, p_251211_.getModelTextureGetter());
   }

   public ItemOverrides(ModelBaker p_251211_, UnbakedModel p_111741_, List<ItemOverride> p_111743_, java.util.function.Function<net.minecraft.client.resources.model.Material, net.minecraft.client.renderer.texture.TextureAtlasSprite> spriteGetter) {
      this.f_173461_ = p_111743_.stream().flatMap(ItemOverride::m_173449_).map(ItemOverride.Predicate::m_173459_).distinct().toArray((p_173479_) -> {
         return new ResourceLocation[p_173479_];
      });
      Object2IntMap<ResourceLocation> object2intmap = new Object2IntOpenHashMap<>();

      for(int i = 0; i < this.f_173461_.length; ++i) {
         object2intmap.put(this.f_173461_[i], i);
      }

      List<ItemOverrides.BakedOverride> list = Lists.newArrayList();

      for(int j = p_111743_.size() - 1; j >= 0; --j) {
         ItemOverride itemoverride = p_111743_.get(j);
         BakedModel bakedmodel = this.bakeModel(p_251211_, p_111741_, itemoverride, spriteGetter);
         ItemOverrides.PropertyMatcher[] aitemoverrides$propertymatcher = itemoverride.m_173449_().map((p_173477_) -> {
            int k = object2intmap.getInt(p_173477_.m_173459_());
            return new ItemOverrides.PropertyMatcher(k, p_173477_.m_173460_());
         }).toArray((p_173463_) -> {
            return new ItemOverrides.PropertyMatcher[p_173463_];
         });
         list.add(new ItemOverrides.BakedOverride(aitemoverrides$propertymatcher, bakedmodel));
      }

      this.f_111735_ = list.toArray(new ItemOverrides.BakedOverride[0]);
   }

   @Nullable
   private BakedModel bakeModel(ModelBaker p_249483_, UnbakedModel p_251965_, ItemOverride p_250816_, java.util.function.Function<net.minecraft.client.resources.model.Material, net.minecraft.client.renderer.texture.TextureAtlasSprite> spriteGetter) {
      UnbakedModel unbakedmodel = p_249483_.m_245361_(p_250816_.m_111718_());
      return Objects.equals(unbakedmodel, p_251965_) ? null : p_249483_.bake(p_250816_.m_111718_(), BlockModelRotation.X0_Y0, spriteGetter);
   }

   @Nullable
   public BakedModel m_173464_(BakedModel p_173465_, ItemStack p_173466_, @Nullable ClientLevel p_173467_, @Nullable LivingEntity p_173468_, int p_173469_) {
      if (this.f_111735_.length != 0) {
         Item item = p_173466_.m_41720_();
         int i = this.f_173461_.length;
         float[] afloat = new float[i];

         for(int j = 0; j < i; ++j) {
            ResourceLocation resourcelocation = this.f_173461_[j];
            ItemPropertyFunction itempropertyfunction = ItemProperties.m_117829_(item, resourcelocation);
            if (itempropertyfunction != null) {
               afloat[j] = itempropertyfunction.m_141951_(p_173466_, p_173467_, p_173468_, p_173469_);
            } else {
               afloat[j] = Float.NEGATIVE_INFINITY;
            }
         }

         for(ItemOverrides.BakedOverride itemoverrides$bakedoverride : this.f_111735_) {
            if (itemoverrides$bakedoverride.m_173485_(afloat)) {
               BakedModel bakedmodel = itemoverrides$bakedoverride.f_173481_;
               if (bakedmodel == null) {
                  return p_173465_;
               }

               return bakedmodel;
            }
         }
      }

      return p_173465_;
   }

   public com.google.common.collect.ImmutableList<BakedOverride> getOverrides() {
      return com.google.common.collect.ImmutableList.copyOf(f_111735_);
   }

   @OnlyIn(Dist.CLIENT)
   public static class BakedOverride {
      private final ItemOverrides.PropertyMatcher[] f_173480_;
      @Nullable
      final BakedModel f_173481_;

      BakedOverride(ItemOverrides.PropertyMatcher[] p_173483_, @Nullable BakedModel p_173484_) {
         this.f_173480_ = p_173483_;
         this.f_173481_ = p_173484_;
      }

      boolean m_173485_(float[] p_173486_) {
         for(ItemOverrides.PropertyMatcher itemoverrides$propertymatcher : this.f_173480_) {
            float f = p_173486_[itemoverrides$propertymatcher.f_173487_];
            if (f < itemoverrides$propertymatcher.f_173488_) {
               return false;
            }
         }

         return true;
      }
   }

   @OnlyIn(Dist.CLIENT)
   static class PropertyMatcher {
      public final int f_173487_;
      public final float f_173488_;

      PropertyMatcher(int p_173490_, float p_173491_) {
         this.f_173487_ = p_173490_;
         this.f_173488_ = p_173491_;
      }
   }
}
