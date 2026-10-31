package net.minecraft.client.renderer.block.model;

import com.google.gson.JsonArray;
import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import com.mojang.blaze3d.vertex.PoseStack;
import java.lang.reflect.Type;
import net.minecraft.util.GsonHelper;
import net.minecraft.util.Mth;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import org.joml.Vector3fc;

@OnlyIn(Dist.CLIENT)
public class ItemTransform {
   public static final ItemTransform f_111754_ = new ItemTransform(new Vector3f(), new Vector3f(), new Vector3f(1.0F, 1.0F, 1.0F));
   public final Vector3f f_111755_;
   public final Vector3f f_111756_;
   public final Vector3f f_111757_;

   public ItemTransform(Vector3f p_254427_, Vector3f p_254496_, Vector3f p_254022_) {
      this.f_111755_ = new Vector3f((Vector3fc)p_254427_);
      this.f_111756_ = new Vector3f((Vector3fc)p_254496_);
      this.f_111757_ = new Vector3f((Vector3fc)p_254022_);
   }

   public void m_111763_(boolean p_111764_, PoseStack p_111765_) {
      if (this != f_111754_) {
         float f = this.f_111755_.x();
         float f1 = this.f_111755_.y();
         float f2 = this.f_111755_.z();
         if (p_111764_) {
            f1 = -f1;
            f2 = -f2;
         }

         int i = p_111764_ ? -1 : 1;
         p_111765_.m_252880_((float)i * this.f_111756_.x(), this.f_111756_.y(), this.f_111756_.z());
         p_111765_.m_252781_((new Quaternionf()).rotationXYZ(f * ((float)Math.PI / 180F), f1 * ((float)Math.PI / 180F), f2 * ((float)Math.PI / 180F)));
         p_111765_.m_85841_(this.f_111757_.x(), this.f_111757_.y(), this.f_111757_.z());
      }
   }

   public boolean equals(Object p_111767_) {
      if (this == p_111767_) {
         return true;
      } else if (this.getClass() != p_111767_.getClass()) {
         return false;
      } else {
         ItemTransform itemtransform = (ItemTransform)p_111767_;
         return this.f_111755_.equals(itemtransform.f_111755_) && this.f_111757_.equals(itemtransform.f_111757_) && this.f_111756_.equals(itemtransform.f_111756_);
      }
   }

   public int hashCode() {
      int i = this.f_111755_.hashCode();
      i = 31 * i + this.f_111756_.hashCode();
      return 31 * i + this.f_111757_.hashCode();
   }

   @OnlyIn(Dist.CLIENT)
   public static class Deserializer implements JsonDeserializer<ItemTransform> {
      public static final Vector3f f_111769_ = new Vector3f(0.0F, 0.0F, 0.0F);
      public static final Vector3f f_111770_ = new Vector3f(0.0F, 0.0F, 0.0F);
      public static final Vector3f f_111771_ = new Vector3f(1.0F, 1.0F, 1.0F);
      public static final float f_173492_ = 5.0F;
      public static final float f_173493_ = 4.0F;

      public ItemTransform deserialize(JsonElement p_111775_, Type p_111776_, JsonDeserializationContext p_111777_) throws JsonParseException {
         JsonObject jsonobject = p_111775_.getAsJsonObject();
         Vector3f vector3f = this.m_111778_(jsonobject, "rotation", f_111769_);
         Vector3f vector3f1 = this.m_111778_(jsonobject, "translation", f_111770_);
         vector3f1.mul(0.0625F);
         vector3f1.set(Mth.m_14036_(vector3f1.x, -5.0F, 5.0F), Mth.m_14036_(vector3f1.y, -5.0F, 5.0F), Mth.m_14036_(vector3f1.z, -5.0F, 5.0F));
         Vector3f vector3f2 = this.m_111778_(jsonobject, "scale", f_111771_);
         vector3f2.set(Mth.m_14036_(vector3f2.x, -4.0F, 4.0F), Mth.m_14036_(vector3f2.y, -4.0F, 4.0F), Mth.m_14036_(vector3f2.z, -4.0F, 4.0F));
         return new ItemTransform(vector3f, vector3f1, vector3f2);
      }

      private Vector3f m_111778_(JsonObject p_111779_, String p_111780_, Vector3f p_253777_) {
         if (!p_111779_.has(p_111780_)) {
            return p_253777_;
         } else {
            JsonArray jsonarray = GsonHelper.m_13933_(p_111779_, p_111780_);
            if (jsonarray.size() != 3) {
               throw new JsonParseException("Expected 3 " + p_111780_ + " values, found: " + jsonarray.size());
            } else {
               float[] afloat = new float[3];

               for(int i = 0; i < afloat.length; ++i) {
                  afloat[i] = GsonHelper.m_13888_(jsonarray.get(i), p_111780_ + "[" + i + "]");
               }

               return new Vector3f(afloat[0], afloat[1], afloat[2]);
            }
         }
      }
   }
}
