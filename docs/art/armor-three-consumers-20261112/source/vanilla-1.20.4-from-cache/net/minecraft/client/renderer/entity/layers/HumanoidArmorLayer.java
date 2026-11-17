package net.minecraft.client.renderer.entity.layers;

import com.google.common.collect.Maps;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import java.util.Map;
import javax.annotation.Nullable;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.Sheets;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.ModelManager;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.DyeableArmorItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.armortrim.ArmorTrim;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class HumanoidArmorLayer<T extends LivingEntity, M extends HumanoidModel<T>, A extends HumanoidModel<T>> extends RenderLayer<T, M> {
   private static final Map<String, ResourceLocation> f_117070_ = Maps.newHashMap();
   private final A f_117071_;
   private final A f_117072_;
   private final TextureAtlas f_266073_;

   public HumanoidArmorLayer(RenderLayerParent<T, M> p_267286_, A p_267110_, A p_267150_, ModelManager p_267238_) {
      super(p_267286_);
      this.f_117071_ = p_267110_;
      this.f_117072_ = p_267150_;
      this.f_266073_ = p_267238_.m_119428_(Sheets.f_265912_);
   }

   public void m_6494_(PoseStack p_117096_, MultiBufferSource p_117097_, int p_117098_, T p_117099_, float p_117100_, float p_117101_, float p_117102_, float p_117103_, float p_117104_, float p_117105_) {
      this.m_117118_(p_117096_, p_117097_, p_117099_, EquipmentSlot.CHEST, p_117098_, this.m_117078_(EquipmentSlot.CHEST));
      this.m_117118_(p_117096_, p_117097_, p_117099_, EquipmentSlot.LEGS, p_117098_, this.m_117078_(EquipmentSlot.LEGS));
      this.m_117118_(p_117096_, p_117097_, p_117099_, EquipmentSlot.FEET, p_117098_, this.m_117078_(EquipmentSlot.FEET));
      this.m_117118_(p_117096_, p_117097_, p_117099_, EquipmentSlot.HEAD, p_117098_, this.m_117078_(EquipmentSlot.HEAD));
   }

   private void m_117118_(PoseStack p_117119_, MultiBufferSource p_117120_, T p_117121_, EquipmentSlot p_117122_, int p_117123_, A p_117124_) {
      ItemStack itemstack = p_117121_.m_6844_(p_117122_);
      Item $$9 = itemstack.m_41720_();
      if ($$9 instanceof ArmorItem armoritem) {
         if (armoritem.m_40402_() == p_117122_) {
            this.m_117386_().m_102872_(p_117124_);
            this.m_117125_(p_117124_, p_117122_);
            net.minecraft.client.model.Model model = getArmorModelHook(p_117121_, itemstack, p_117122_, p_117124_);
            boolean flag = this.m_117128_(p_117122_);
            if (armoritem instanceof net.minecraft.world.item.DyeableLeatherItem) {
               int i = ((net.minecraft.world.item.DyeableLeatherItem)armoritem).m_41121_(itemstack);
               float f = (float)(i >> 16 & 255) / 255.0F;
               float f1 = (float)(i >> 8 & 255) / 255.0F;
               float f2 = (float)(i & 255) / 255.0F;
               this.renderModel(p_117119_, p_117120_, p_117123_, armoritem, model, flag, f, f1, f2, this.getArmorResource(p_117121_, itemstack, p_117122_, null));
               this.renderModel(p_117119_, p_117120_, p_117123_, armoritem, model, flag, 1.0F, 1.0F, 1.0F, this.getArmorResource(p_117121_, itemstack, p_117122_, "overlay"));
            } else {
               this.renderModel(p_117119_, p_117120_, p_117123_, armoritem, model, flag, 1.0F, 1.0F, 1.0F, this.getArmorResource(p_117121_, itemstack, p_117122_, null));
            }

            ArmorTrim.m_266285_(p_117121_.m_9236_().m_9598_(), itemstack, true).ifPresent((p_289638_) -> {
               this.renderTrim(armoritem.m_40401_(), p_117119_, p_117120_, p_117123_, p_289638_, model, flag);
            });
            if (itemstack.m_41790_()) {
               this.renderGlint(p_117119_, p_117120_, p_117123_, model);
            }

         }
      }
   }

   protected void m_117125_(A p_117126_, EquipmentSlot p_117127_) {
      p_117126_.m_8009_(false);
      switch (p_117127_) {
         case HEAD:
            p_117126_.f_102808_.f_104207_ = true;
            p_117126_.f_102809_.f_104207_ = true;
            break;
         case CHEST:
            p_117126_.f_102810_.f_104207_ = true;
            p_117126_.f_102811_.f_104207_ = true;
            p_117126_.f_102812_.f_104207_ = true;
            break;
         case LEGS:
            p_117126_.f_102810_.f_104207_ = true;
            p_117126_.f_102813_.f_104207_ = true;
            p_117126_.f_102814_.f_104207_ = true;
            break;
         case FEET:
            p_117126_.f_102813_.f_104207_ = true;
            p_117126_.f_102814_.f_104207_ = true;
      }

   }

   private void m_289609_(PoseStack p_289664_, MultiBufferSource p_289689_, int p_289681_, ArmorItem p_289650_, A p_289658_, boolean p_289668_, float p_289678_, float p_289674_, float p_289693_, @Nullable String p_289682_) {
       renderModel(p_289664_, p_289689_, p_289681_, p_289650_, p_289658_, p_289668_, p_289678_, p_289674_, p_289693_, this.m_117080_(p_289650_, p_289668_, p_289682_));
   }
   private void renderModel(PoseStack p_289664_, MultiBufferSource p_289689_, int p_289681_, ArmorItem p_289650_, net.minecraft.client.model.Model p_289658_, boolean p_289668_, float p_289678_, float p_289674_, float p_289693_, ResourceLocation armorResource) {
      VertexConsumer vertexconsumer = p_289689_.m_6299_(RenderType.m_110431_(armorResource));
      p_289658_.m_7695_(p_289664_, vertexconsumer, p_289681_, OverlayTexture.f_118083_, p_289678_, p_289674_, p_289693_, 1.0F);
   }

   private void m_289604_(ArmorMaterial p_289690_, PoseStack p_289687_, MultiBufferSource p_289643_, int p_289683_, ArmorTrim p_289692_, A p_289663_, boolean p_289651_) {
      m_289604_(p_289690_, p_289687_, p_289643_, p_289683_, p_289692_, p_289663_, p_289651_);
   }
   private void renderTrim(ArmorMaterial p_289690_, PoseStack p_289687_, MultiBufferSource p_289643_, int p_289683_, ArmorTrim p_289692_, net.minecraft.client.model.Model p_289663_, boolean p_289651_) {
      TextureAtlasSprite textureatlassprite = this.f_266073_.m_118316_(p_289651_ ? p_289692_.m_267774_(p_289690_) : p_289692_.m_267606_(p_289690_));
      VertexConsumer vertexconsumer = textureatlassprite.m_118381_(p_289643_.m_6299_(Sheets.m_266442_(p_289692_.m_266429_().m_203334_().f_290976_())));
      p_289663_.m_7695_(p_289687_, vertexconsumer, p_289683_, OverlayTexture.f_118083_, 1.0F, 1.0F, 1.0F, 1.0F);
   }

   private void m_289597_(PoseStack p_289673_, MultiBufferSource p_289654_, int p_289649_, A p_289659_) {
      m_289597_(p_289673_, p_289654_, p_289649_, p_289659_);
   }
   private void renderGlint(PoseStack p_289673_, MultiBufferSource p_289654_, int p_289649_, net.minecraft.client.model.Model p_289659_) {
      p_289659_.m_7695_(p_289673_, p_289654_.m_6299_(RenderType.m_110484_()), p_289649_, OverlayTexture.f_118083_, 1.0F, 1.0F, 1.0F, 1.0F);
   }

   private A m_117078_(EquipmentSlot p_117079_) {
      return (A)(this.m_117128_(p_117079_) ? this.f_117071_ : this.f_117072_);
   }

   private boolean m_117128_(EquipmentSlot p_117129_) {
      return p_117129_ == EquipmentSlot.LEGS;
   }

   @Deprecated //Use the more sensitive version getArmorResource below
   private ResourceLocation m_117080_(ArmorItem p_117081_, boolean p_117082_, @Nullable String p_117083_) {
      String s = "textures/models/armor/" + p_117081_.m_40401_().m_6082_() + "_layer_" + (p_117082_ ? 2 : 1) + (p_117083_ == null ? "" : "_" + p_117083_) + ".png";
      return f_117070_.computeIfAbsent(s, ResourceLocation::new);
   }

   /*=================================== FORGE START =========================================*/

   /**
    * Hook to allow item-sensitive armor model. for HumanoidArmorLayer.
    */
   protected net.minecraft.client.model.Model getArmorModelHook(T entity, ItemStack itemStack, EquipmentSlot slot, A model) {
      return net.minecraftforge.client.ForgeHooksClient.getArmorModel(entity, itemStack, slot, model);
   }

   /**
    * More generic ForgeHook version of the above function, it allows for Items to have more control over what texture they provide.
    *
    * @param entity Entity wearing the armor
    * @param stack ItemStack for the armor
    * @param slot Slot ID that the item is in
    * @param type Subtype, can be null or "overlay"
    * @return ResourceLocation pointing at the armor's texture
    */
   public ResourceLocation getArmorResource(net.minecraft.world.entity.Entity entity, ItemStack stack, EquipmentSlot slot, @Nullable String type) {
      ArmorItem item = (ArmorItem)stack.m_41720_();
      String texture = item.m_40401_().m_6082_();
      String domain = "minecraft";
      int idx = texture.indexOf(':');
      if (idx != -1) {
         domain = texture.substring(0, idx);
         texture = texture.substring(idx + 1);
      }
      String s1 = String.format(java.util.Locale.ROOT, "%s:textures/models/armor/%s_layer_%d%s.png", domain, texture, (m_117128_(slot) ? 2 : 1), type == null ? "" : String.format(java.util.Locale.ROOT, "_%s", type));

      s1 = net.minecraftforge.client.ForgeHooksClient.getArmorTexture(entity, stack, s1, slot, type);
      ResourceLocation resourcelocation = f_117070_.get(s1);

      if (resourcelocation == null) {
         resourcelocation = new ResourceLocation(s1);
         f_117070_.put(s1, resourcelocation);
      }

      return resourcelocation;
   }
   /*=================================== FORGE END ===========================================*/
}
