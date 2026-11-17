package net.minecraft.client.renderer.block.model;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Maps;
import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import java.lang.reflect.Type;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.GsonHelper;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class ItemOverride {
   private final ResourceLocation f_111713_;
   private final List<ItemOverride.Predicate> f_111714_;

   public ItemOverride(ResourceLocation p_173447_, List<ItemOverride.Predicate> p_173448_) {
      this.f_111713_ = p_173447_;
      this.f_111714_ = ImmutableList.copyOf(p_173448_);
   }

   public ResourceLocation m_111718_() {
      return this.f_111713_;
   }

   public Stream<ItemOverride.Predicate> m_173449_() {
      return this.f_111714_.stream();
   }

   @OnlyIn(Dist.CLIENT)
   public static class Deserializer implements JsonDeserializer<ItemOverride> {
      public ItemOverride deserialize(JsonElement p_111725_, Type p_111726_, JsonDeserializationContext p_111727_) throws JsonParseException {
         JsonObject jsonobject = p_111725_.getAsJsonObject();
         ResourceLocation resourcelocation = new ResourceLocation(GsonHelper.m_13906_(jsonobject, "model"));
         List<ItemOverride.Predicate> list = this.m_173450_(jsonobject);
         return new ItemOverride(resourcelocation, list);
      }

      protected List<ItemOverride.Predicate> m_173450_(JsonObject p_173451_) {
         Map<ResourceLocation, Float> map = Maps.newLinkedHashMap();
         JsonObject jsonobject = GsonHelper.m_13930_(p_173451_, "predicate");

         for(Map.Entry<String, JsonElement> entry : jsonobject.entrySet()) {
            map.put(new ResourceLocation(entry.getKey()), GsonHelper.m_13888_(entry.getValue(), entry.getKey()));
         }

         return map.entrySet().stream().map((p_173453_) -> {
            return new ItemOverride.Predicate(p_173453_.getKey(), p_173453_.getValue());
         }).collect(ImmutableList.toImmutableList());
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static class Predicate {
      private final ResourceLocation f_173454_;
      private final float f_173455_;

      public Predicate(ResourceLocation p_173457_, float p_173458_) {
         this.f_173454_ = p_173457_;
         this.f_173455_ = p_173458_;
      }

      public ResourceLocation m_173459_() {
         return this.f_173454_;
      }

      public float m_173460_() {
         return this.f_173455_;
      }
   }
}
