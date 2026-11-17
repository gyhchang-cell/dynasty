package net.minecraft.client.renderer.block.model;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Joiner;
import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import com.google.common.collect.Sets;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import com.mojang.datafixers.util.Either;
import com.mojang.logging.LogUtils;
import java.io.Reader;
import java.io.StringReader;
import java.lang.reflect.Type;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;
import javax.annotation.Nullable;
import net.minecraft.client.renderer.texture.MissingTextureAtlasSprite;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.client.resources.model.BuiltInModel;
import net.minecraft.client.resources.model.Material;
import net.minecraft.client.resources.model.ModelBaker;
import net.minecraft.client.resources.model.ModelBakery;
import net.minecraft.client.resources.model.ModelState;
import net.minecraft.client.resources.model.SimpleBakedModel;
import net.minecraft.client.resources.model.UnbakedModel;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.GsonHelper;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.slf4j.Logger;

@OnlyIn(Dist.CLIENT)
public class BlockModel implements UnbakedModel {
   private static final Logger f_111420_ = LogUtils.getLogger();
   private static final FaceBakery f_111421_ = new FaceBakery();
   @VisibleForTesting
   static final Gson f_111415_ = (new GsonBuilder()).registerTypeAdapter(BlockModel.class, new BlockModel.Deserializer()).registerTypeAdapter(BlockElement.class, new BlockElement.Deserializer()).registerTypeAdapter(BlockElementFace.class, new BlockElementFace.Deserializer()).registerTypeAdapter(BlockFaceUV.class, new BlockFaceUV.Deserializer()).registerTypeAdapter(ItemTransform.class, new ItemTransform.Deserializer()).registerTypeAdapter(ItemTransforms.class, new ItemTransforms.Deserializer()).registerTypeAdapter(ItemOverride.class, new ItemOverride.Deserializer()).create();
   private static final char f_173419_ = '#';
   public static final String f_173418_ = "particle";
   private static final boolean f_271537_ = true;
   private final List<BlockElement> f_111422_;
   @Nullable
   private final BlockModel.GuiLight f_111423_;
   @Nullable
   public final Boolean f_111424_;
   private final ItemTransforms f_111425_;
   private final List<ItemOverride> f_111426_;
   public String f_111416_ = "";
   @VisibleForTesting
   public final Map<String, Either<Material, String>> f_111417_;
   @Nullable
   public BlockModel f_111418_;
   @Nullable
   protected ResourceLocation f_111419_;
   public final net.minecraftforge.client.model.geometry.BlockGeometryBakingContext customData = new net.minecraftforge.client.model.geometry.BlockGeometryBakingContext(this);

   public static BlockModel m_111461_(Reader p_111462_) {
      return GsonHelper.m_13776_(net.minecraftforge.client.model.ExtendedBlockModelDeserializer.INSTANCE, p_111462_, BlockModel.class);
   }

   public static BlockModel m_111463_(String p_111464_) {
      return m_111461_(new StringReader(p_111464_));
   }

   public BlockModel(@Nullable ResourceLocation p_273263_, List<BlockElement> p_272668_, Map<String, Either<Material, String>> p_272821_, @Nullable Boolean p_272676_, @Nullable BlockModel.GuiLight p_273072_, ItemTransforms p_273480_, List<ItemOverride> p_273099_) {
      this.f_111422_ = p_272668_;
      this.f_111424_ = p_272676_;
      this.f_111423_ = p_273072_;
      this.f_111417_ = p_272821_;
      this.f_111419_ = p_273263_;
      this.f_111425_ = p_273480_;
      this.f_111426_ = p_273099_;
   }

   @Deprecated
   public List<BlockElement> m_111436_() {
      if (customData.hasCustomGeometry()) return java.util.Collections.emptyList();
      return this.f_111422_.isEmpty() && this.f_111418_ != null ? this.f_111418_.m_111436_() : this.f_111422_;
   }

   @Nullable
   public ResourceLocation getParentLocation() { return f_111419_; }

   public boolean m_111476_() {
      if (this.f_111424_ != null) {
         return this.f_111424_;
      } else {
         return this.f_111418_ != null ? this.f_111418_.m_111476_() : true;
      }
   }

   public BlockModel.GuiLight m_111479_() {
      if (this.f_111423_ != null) {
         return this.f_111423_;
      } else {
         return this.f_111418_ != null ? this.f_111418_.m_111479_() : BlockModel.GuiLight.SIDE;
      }
   }

   public boolean m_173420_() {
      return this.f_111419_ == null || this.f_111418_ != null && this.f_111418_.m_173420_();
   }

   public List<ItemOverride> m_111484_() {
      return this.f_111426_;
   }

   private ItemOverrides m_246736_(ModelBaker p_250138_, BlockModel p_251800_) {
      return this.f_111426_.isEmpty() ? ItemOverrides.f_111734_ : new ItemOverrides(p_250138_, p_251800_, this.f_111426_);
   }

   public ItemOverrides getOverrides(ModelBaker p_250138_, BlockModel p_251800_, Function<Material, TextureAtlasSprite> spriteGetter) {
      return this.f_111426_.isEmpty() ? ItemOverrides.f_111734_ : new ItemOverrides(p_250138_, p_251800_, this.f_111426_, spriteGetter);
   }

   public Collection<ResourceLocation> m_7970_() {
      Set<ResourceLocation> set = Sets.newHashSet();

      for(ItemOverride itemoverride : this.f_111426_) {
         set.add(itemoverride.m_111718_());
      }

      if (this.f_111419_ != null) {
         set.add(this.f_111419_);
      }

      return set;
   }

   public void m_5500_(Function<ResourceLocation, UnbakedModel> p_249059_) {
      Set<UnbakedModel> set = Sets.newLinkedHashSet();

      for(BlockModel blockmodel = this; blockmodel.f_111419_ != null && blockmodel.f_111418_ == null; blockmodel = blockmodel.f_111418_) {
         set.add(blockmodel);
         UnbakedModel unbakedmodel = p_249059_.apply(blockmodel.f_111419_);
         if (unbakedmodel == null) {
            f_111420_.warn("No parent '{}' while loading model '{}'", this.f_111419_, blockmodel);
         }

         if (set.contains(unbakedmodel)) {
            f_111420_.warn("Found 'parent' loop while loading model '{}' in chain: {} -> {}", blockmodel, set.stream().map(Object::toString).collect(Collectors.joining(" -> ")), this.f_111419_);
            unbakedmodel = null;
         }

         if (unbakedmodel == null) {
            blockmodel.f_111419_ = ModelBakery.f_119230_;
            unbakedmodel = p_249059_.apply(blockmodel.f_111419_);
         }

         if (!(unbakedmodel instanceof BlockModel)) {
            throw new IllegalStateException("BlockModel parent has to be a block model.");
         }

         blockmodel.f_111418_ = (BlockModel)unbakedmodel;
      }

      if (customData.hasCustomGeometry()) {
         customData.getCustomGeometry().resolveParents(p_249059_, customData);
      }

      this.f_111426_.forEach((p_247932_) -> {
         UnbakedModel unbakedmodel1 = p_249059_.apply(p_247932_.m_111718_());
         if (!Objects.equals(unbakedmodel1, this)) {
            unbakedmodel1.m_5500_(p_249059_);
         }
      });
   }

   /**
    * @deprecated Forge: Use {@link #bake(ModelBaker, BlockModel, Function, ModelState, ResourceLocation, boolean)}.
    */
   @Deprecated
   public BakedModel m_7611_(ModelBaker p_252120_, Function<Material, TextureAtlasSprite> p_250023_, ModelState p_251130_, ResourceLocation p_252208_) {
      return this.m_111449_(p_252120_, this, p_250023_, p_251130_, p_252208_, true);
   }

   public BakedModel m_111449_(ModelBaker p_249720_, BlockModel p_111451_, Function<Material, TextureAtlasSprite> p_111452_, ModelState p_111453_, ResourceLocation p_111454_, boolean p_111455_) {
      return net.minecraftforge.client.model.geometry.UnbakedGeometryHelper.bake(this, p_249720_, p_111451_, p_111452_, p_111453_, p_111454_, p_111455_);
   }
   private BakedModel bakeVanilla(ModelBaker p_249720_, BlockModel p_111451_, Function<Material, TextureAtlasSprite> p_111452_, ModelState p_111453_, ResourceLocation p_111454_, boolean p_111455_, net.minecraftforge.client.RenderTypeGroup renderTypes) {
      TextureAtlasSprite textureatlassprite = p_111452_.apply(this.m_111480_("particle"));
      if (this.m_111490_() == ModelBakery.f_119233_) {
         return new BuiltInModel(this.m_111491_(), this.m_246736_(p_249720_, p_111451_), textureatlassprite, this.m_111479_().m_111526_());
      } else {
         SimpleBakedModel.Builder simplebakedmodel$builder = (new SimpleBakedModel.Builder(this, this.m_246736_(p_249720_, p_111451_), p_111455_)).m_119528_(textureatlassprite);

         for(BlockElement blockelement : this.m_111436_()) {
            for(Direction direction : blockelement.f_111310_.keySet()) {
               BlockElementFace blockelementface = blockelement.f_111310_.get(direction);
               TextureAtlasSprite textureatlassprite1 = p_111452_.apply(this.m_111480_(blockelementface.f_111356_));
               if (blockelementface.f_111354_ == null) {
                  simplebakedmodel$builder.m_119526_(m_111437_(blockelement, blockelementface, textureatlassprite1, direction, p_111453_, p_111454_));
               } else {
                  simplebakedmodel$builder.m_119530_(Direction.m_252919_(p_111453_.m_6189_().m_252783_(), blockelementface.f_111354_), m_111437_(blockelement, blockelementface, textureatlassprite1, direction, p_111453_, p_111454_));
               }
            }
         }

         return simplebakedmodel$builder.m_119533_();
      }
   }

   public static BakedQuad m_111437_(BlockElement p_111438_, BlockElementFace p_111439_, TextureAtlasSprite p_111440_, Direction p_111441_, ModelState p_111442_, ResourceLocation p_111443_) {
      return f_111421_.m_111600_(p_111438_.f_111308_, p_111438_.f_111309_, p_111439_, p_111440_, p_111441_, p_111442_, p_111438_.f_111311_, p_111438_.f_111312_, p_111443_);
   }

   public boolean m_111477_(String p_111478_) {
      return !MissingTextureAtlasSprite.m_118071_().equals(this.m_111480_(p_111478_).m_119203_());
   }

   public Material m_111480_(String p_111481_) {
      if (m_111488_(p_111481_)) {
         p_111481_ = p_111481_.substring(1);
      }

      List<String> list = Lists.newArrayList();

      while(true) {
         Either<Material, String> either = this.m_111485_(p_111481_);
         Optional<Material> optional = either.left();
         if (optional.isPresent()) {
            return optional.get();
         }

         p_111481_ = either.right().get();
         if (list.contains(p_111481_)) {
            f_111420_.warn("Unable to resolve texture due to reference chain {}->{} in {}", Joiner.on("->").join(list), p_111481_, this.f_111416_);
            return new Material(TextureAtlas.f_118259_, MissingTextureAtlasSprite.m_118071_());
         }

         list.add(p_111481_);
      }
   }

   private Either<Material, String> m_111485_(String p_111486_) {
      for(BlockModel blockmodel = this; blockmodel != null; blockmodel = blockmodel.f_111418_) {
         Either<Material, String> either = blockmodel.f_111417_.get(p_111486_);
         if (either != null) {
            return either;
         }
      }

      return Either.left(new Material(TextureAtlas.f_118259_, MissingTextureAtlasSprite.m_118071_()));
   }

   static boolean m_111488_(String p_111489_) {
      return p_111489_.charAt(0) == '#';
   }

   public BlockModel m_111490_() {
      return this.f_111418_ == null ? this : this.f_111418_.m_111490_();
   }

   public ItemTransforms m_111491_() {
      ItemTransform itemtransform = this.m_269178_(ItemDisplayContext.THIRD_PERSON_LEFT_HAND);
      ItemTransform itemtransform1 = this.m_269178_(ItemDisplayContext.THIRD_PERSON_RIGHT_HAND);
      ItemTransform itemtransform2 = this.m_269178_(ItemDisplayContext.FIRST_PERSON_LEFT_HAND);
      ItemTransform itemtransform3 = this.m_269178_(ItemDisplayContext.FIRST_PERSON_RIGHT_HAND);
      ItemTransform itemtransform4 = this.m_269178_(ItemDisplayContext.HEAD);
      ItemTransform itemtransform5 = this.m_269178_(ItemDisplayContext.GUI);
      ItemTransform itemtransform6 = this.m_269178_(ItemDisplayContext.GROUND);
      ItemTransform itemtransform7 = this.m_269178_(ItemDisplayContext.FIXED);

      var builder = com.google.common.collect.ImmutableMap.<ItemDisplayContext, ItemTransform>builder();
      for(ItemDisplayContext type : ItemDisplayContext.values()) {
         if (type.isModded()) {
            var transform = this.m_269178_(type);
            if (transform != ItemTransform.f_111754_) {
               builder.put(type, transform);
            }
         }
      }

      return new ItemTransforms(itemtransform, itemtransform1, itemtransform2, itemtransform3, itemtransform4, itemtransform5, itemtransform6, itemtransform7, builder.build());
   }

   private ItemTransform m_269178_(ItemDisplayContext p_270662_) {
      return this.f_111418_ != null && !this.f_111425_.m_269504_(p_270662_) ? this.f_111418_.m_269178_(p_270662_) : this.f_111425_.m_269404_(p_270662_);
   }

   public String toString() {
      return this.f_111416_;
   }

   @OnlyIn(Dist.CLIENT)
   public static class Deserializer implements JsonDeserializer<BlockModel> {
      public BlockModel deserialize(JsonElement p_111498_, Type p_111499_, JsonDeserializationContext p_111500_) throws JsonParseException {
         JsonObject jsonobject = p_111498_.getAsJsonObject();
         List<BlockElement> list = this.m_111506_(p_111500_, jsonobject);
         String s = this.m_111511_(jsonobject);
         Map<String, Either<Material, String>> map = this.m_111509_(jsonobject);
         Boolean obool = this.m_271865_(jsonobject);
         ItemTransforms itemtransforms = ItemTransforms.f_111786_;
         if (jsonobject.has("display")) {
            JsonObject jsonobject1 = GsonHelper.m_13930_(jsonobject, "display");
            itemtransforms = p_111500_.deserialize(jsonobject1, ItemTransforms.class);
         }

         List<ItemOverride> list1 = this.m_111494_(p_111500_, jsonobject);
         BlockModel.GuiLight blockmodel$guilight = null;
         if (jsonobject.has("gui_light")) {
            blockmodel$guilight = BlockModel.GuiLight.m_111527_(GsonHelper.m_13906_(jsonobject, "gui_light"));
         }

         ResourceLocation resourcelocation = s.isEmpty() ? null : new ResourceLocation(s);
         return new BlockModel(resourcelocation, list, map, obool, blockmodel$guilight, itemtransforms, list1);
      }

      protected List<ItemOverride> m_111494_(JsonDeserializationContext p_111495_, JsonObject p_111496_) {
         List<ItemOverride> list = Lists.newArrayList();
         if (p_111496_.has("overrides")) {
            for(JsonElement jsonelement : GsonHelper.m_13933_(p_111496_, "overrides")) {
               list.add(p_111495_.deserialize(jsonelement, ItemOverride.class));
            }
         }

         return list;
      }

      private Map<String, Either<Material, String>> m_111509_(JsonObject p_111510_) {
         ResourceLocation resourcelocation = TextureAtlas.f_118259_;
         Map<String, Either<Material, String>> map = Maps.newHashMap();
         if (p_111510_.has("textures")) {
            JsonObject jsonobject = GsonHelper.m_13930_(p_111510_, "textures");

            for(Map.Entry<String, JsonElement> entry : jsonobject.entrySet()) {
               map.put(entry.getKey(), m_111503_(resourcelocation, entry.getValue().getAsString()));
            }
         }

         return map;
      }

      private static Either<Material, String> m_111503_(ResourceLocation p_111504_, String p_111505_) {
         if (BlockModel.m_111488_(p_111505_)) {
            return Either.right(p_111505_.substring(1));
         } else {
            ResourceLocation resourcelocation = ResourceLocation.m_135820_(p_111505_);
            if (resourcelocation == null) {
               throw new JsonParseException(p_111505_ + " is not valid resource location");
            } else {
               return Either.left(new Material(p_111504_, resourcelocation));
            }
         }
      }

      private String m_111511_(JsonObject p_111512_) {
         return GsonHelper.m_13851_(p_111512_, "parent", "");
      }

      @Nullable
      protected Boolean m_271865_(JsonObject p_273052_) {
         return p_273052_.has("ambientocclusion") ? GsonHelper.m_13912_(p_273052_, "ambientocclusion") : null;
      }

      protected List<BlockElement> m_111506_(JsonDeserializationContext p_111507_, JsonObject p_111508_) {
         List<BlockElement> list = Lists.newArrayList();
         if (p_111508_.has("elements")) {
            for(JsonElement jsonelement : GsonHelper.m_13933_(p_111508_, "elements")) {
               list.add(p_111507_.deserialize(jsonelement, BlockElement.class));
            }
         }

         return list;
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static enum GuiLight {
      FRONT("front"),
      SIDE("side");

      private final String f_111519_;

      private GuiLight(String p_111525_) {
         this.f_111519_ = p_111525_;
      }

      public static BlockModel.GuiLight m_111527_(String p_111528_) {
         for(BlockModel.GuiLight blockmodel$guilight : values()) {
            if (blockmodel$guilight.f_111519_.equals(p_111528_)) {
               return blockmodel$guilight;
            }
         }

         throw new IllegalArgumentException("Invalid gui light: " + p_111528_);
      }

      public boolean m_111526_() {
         return this == SIDE;
      }

      public String getSerializedName() { return f_111519_; }
   }

   @OnlyIn(Dist.CLIENT)
   public static class LoopException extends RuntimeException {
      public LoopException(String p_173424_) {
         super(p_173424_);
      }
   }
}
