package net.minecraft.client.renderer.block.model;

import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import com.mojang.datafixers.util.Either;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import net.minecraft.client.renderer.texture.SpriteContents;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.Material;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Vector3f;

@OnlyIn(Dist.CLIENT)
public class ItemModelGenerator {
   public static final List<String> f_111635_ = Lists.newArrayList("layer0", "layer1", "layer2", "layer3", "layer4");
   private static final float f_173437_ = 7.5F;
   private static final float f_173438_ = 8.5F;

   public BlockModel m_111670_(Function<Material, TextureAtlasSprite> p_111671_, BlockModel p_111672_) {
      Map<String, Either<Material, String>> map = Maps.newHashMap();
      List<BlockElement> list = Lists.newArrayList();

      for(int i = 0; i < f_111635_.size(); ++i) {
         String s = f_111635_.get(i);
         if (!p_111672_.m_111477_(s)) {
            break;
         }

         Material material = p_111672_.m_111480_(s);
         map.put(s, Either.left(material));
         SpriteContents spritecontents = p_111671_.apply(material).m_245424_();
         list.addAll(this.m_111638_(i, s, spritecontents));
      }

      map.put("particle", p_111672_.m_111477_("particle") ? Either.left(p_111672_.m_111480_("particle")) : map.get("layer0"));
      BlockModel blockmodel = new BlockModel((ResourceLocation)null, list, map, false, p_111672_.m_111479_(), p_111672_.m_111491_(), p_111672_.m_111484_());
      blockmodel.f_111416_ = p_111672_.f_111416_;
      blockmodel.customData.copyFrom(p_111672_.customData);
      blockmodel.customData.setGui3d(false);
      return blockmodel;
   }

   public List<BlockElement> m_111638_(int p_111639_, String p_111640_, SpriteContents p_251768_) {
      Map<Direction, BlockElementFace> map = Maps.newHashMap();
      map.put(Direction.SOUTH, new BlockElementFace((Direction)null, p_111639_, p_111640_, new BlockFaceUV(new float[]{0.0F, 0.0F, 16.0F, 16.0F}, 0)));
      map.put(Direction.NORTH, new BlockElementFace((Direction)null, p_111639_, p_111640_, new BlockFaceUV(new float[]{16.0F, 0.0F, 0.0F, 16.0F}, 0)));
      List<BlockElement> list = Lists.newArrayList();
      list.add(new BlockElement(new Vector3f(0.0F, 0.0F, 7.5F), new Vector3f(16.0F, 16.0F, 8.5F), map, (BlockElementRotation)null, true));
      list.addAll(this.m_111661_(p_251768_, p_111640_, p_111639_));
      return list;
   }

   private List<BlockElement> m_111661_(SpriteContents p_248810_, String p_111663_, int p_111664_) {
      float f = (float)p_248810_.m_246492_();
      float f1 = (float)p_248810_.m_245330_();
      List<BlockElement> list = Lists.newArrayList();

      for(ItemModelGenerator.Span itemmodelgenerator$span : this.m_247383_(p_248810_)) {
         float f2 = 0.0F;
         float f3 = 0.0F;
         float f4 = 0.0F;
         float f5 = 0.0F;
         float f6 = 0.0F;
         float f7 = 0.0F;
         float f8 = 0.0F;
         float f9 = 0.0F;
         float f10 = 16.0F / f;
         float f11 = 16.0F / f1;
         float f12 = (float)itemmodelgenerator$span.m_111686_();
         float f13 = (float)itemmodelgenerator$span.m_111687_();
         float f14 = (float)itemmodelgenerator$span.m_111688_();
         ItemModelGenerator.SpanFacing itemmodelgenerator$spanfacing = itemmodelgenerator$span.m_111683_();
         switch (itemmodelgenerator$spanfacing) {
            case UP:
               f6 = f12;
               f2 = f12;
               f4 = f7 = f13 + 1.0F;
               f8 = f14;
               f3 = f14;
               f5 = f14;
               f9 = f14 + 1.0F;
               break;
            case DOWN:
               f8 = f14;
               f9 = f14 + 1.0F;
               f6 = f12;
               f2 = f12;
               f4 = f7 = f13 + 1.0F;
               f3 = f14 + 1.0F;
               f5 = f14 + 1.0F;
               break;
            case LEFT:
               f6 = f14;
               f2 = f14;
               f4 = f14;
               f7 = f14 + 1.0F;
               f9 = f12;
               f3 = f12;
               f5 = f8 = f13 + 1.0F;
               break;
            case RIGHT:
               f6 = f14;
               f7 = f14 + 1.0F;
               f2 = f14 + 1.0F;
               f4 = f14 + 1.0F;
               f9 = f12;
               f3 = f12;
               f5 = f8 = f13 + 1.0F;
         }

         f2 *= f10;
         f4 *= f10;
         f3 *= f11;
         f5 *= f11;
         f3 = 16.0F - f3;
         f5 = 16.0F - f5;
         f6 *= f10;
         f7 *= f10;
         f8 *= f11;
         f9 *= f11;
         Map<Direction, BlockElementFace> map = Maps.newHashMap();
         map.put(itemmodelgenerator$spanfacing.m_111704_(), new BlockElementFace((Direction)null, p_111664_, p_111663_, new BlockFaceUV(new float[]{f6, f8, f7, f9}, 0)));
         switch (itemmodelgenerator$spanfacing) {
            case UP:
               list.add(new BlockElement(new Vector3f(f2, f3, 7.5F), new Vector3f(f4, f3, 8.5F), map, (BlockElementRotation)null, true));
               break;
            case DOWN:
               list.add(new BlockElement(new Vector3f(f2, f5, 7.5F), new Vector3f(f4, f5, 8.5F), map, (BlockElementRotation)null, true));
               break;
            case LEFT:
               list.add(new BlockElement(new Vector3f(f2, f3, 7.5F), new Vector3f(f2, f5, 8.5F), map, (BlockElementRotation)null, true));
               break;
            case RIGHT:
               list.add(new BlockElement(new Vector3f(f4, f3, 7.5F), new Vector3f(f4, f5, 8.5F), map, (BlockElementRotation)null, true));
         }
      }

      return list;
   }

   private List<ItemModelGenerator.Span> m_247383_(SpriteContents p_250338_) {
      int i = p_250338_.m_246492_();
      int j = p_250338_.m_245330_();
      List<ItemModelGenerator.Span> list = Lists.newArrayList();
      p_250338_.m_245638_().forEach((p_173444_) -> {
         for(int k = 0; k < j; ++k) {
            for(int l = 0; l < i; ++l) {
               boolean flag = !this.m_245924_(p_250338_, p_173444_, l, k, i, j);
               this.m_246249_(ItemModelGenerator.SpanFacing.UP, list, p_250338_, p_173444_, l, k, i, j, flag);
               this.m_246249_(ItemModelGenerator.SpanFacing.DOWN, list, p_250338_, p_173444_, l, k, i, j, flag);
               this.m_246249_(ItemModelGenerator.SpanFacing.LEFT, list, p_250338_, p_173444_, l, k, i, j, flag);
               this.m_246249_(ItemModelGenerator.SpanFacing.RIGHT, list, p_250338_, p_173444_, l, k, i, j, flag);
            }
         }

      });
      return list;
   }

   private void m_246249_(ItemModelGenerator.SpanFacing p_251572_, List<ItemModelGenerator.Span> p_248882_, SpriteContents p_249847_, int p_250616_, int p_251416_, int p_249664_, int p_250174_, int p_250897_, boolean p_248773_) {
      boolean flag = this.m_245924_(p_249847_, p_250616_, p_251416_ + p_251572_.m_111707_(), p_249664_ + p_251572_.m_111708_(), p_250174_, p_250897_) && p_248773_;
      if (flag) {
         this.m_111665_(p_248882_, p_251572_, p_251416_, p_249664_);
      }

   }

   private void m_111665_(List<ItemModelGenerator.Span> p_111666_, ItemModelGenerator.SpanFacing p_111667_, int p_111668_, int p_111669_) {
      ItemModelGenerator.Span itemmodelgenerator$span = null;

      for(ItemModelGenerator.Span itemmodelgenerator$span1 : p_111666_) {
         if (itemmodelgenerator$span1.m_111683_() == p_111667_) {
            int i = p_111667_.m_111709_() ? p_111669_ : p_111668_;
            if (itemmodelgenerator$span1.m_111688_() == i) {
               itemmodelgenerator$span = itemmodelgenerator$span1;
               break;
            }
         }
      }

      int j = p_111667_.m_111709_() ? p_111669_ : p_111668_;
      int k = p_111667_.m_111709_() ? p_111668_ : p_111669_;
      if (itemmodelgenerator$span == null) {
         p_111666_.add(new ItemModelGenerator.Span(p_111667_, k, j));
      } else {
         itemmodelgenerator$span.m_111684_(k);
      }

   }

   private boolean m_245924_(SpriteContents p_249650_, int p_250692_, int p_251914_, int p_252343_, int p_250258_, int p_248997_) {
      return p_251914_ >= 0 && p_252343_ >= 0 && p_251914_ < p_250258_ && p_252343_ < p_248997_ ? p_249650_.m_245970_(p_250692_, p_251914_, p_252343_) : true;
   }

   @OnlyIn(Dist.CLIENT)
   static class Span {
      private final ItemModelGenerator.SpanFacing f_111675_;
      private int f_111676_;
      private int f_111677_;
      private final int f_111678_;

      public Span(ItemModelGenerator.SpanFacing p_111680_, int p_111681_, int p_111682_) {
         this.f_111675_ = p_111680_;
         this.f_111676_ = p_111681_;
         this.f_111677_ = p_111681_;
         this.f_111678_ = p_111682_;
      }

      public void m_111684_(int p_111685_) {
         if (p_111685_ < this.f_111676_) {
            this.f_111676_ = p_111685_;
         } else if (p_111685_ > this.f_111677_) {
            this.f_111677_ = p_111685_;
         }

      }

      public ItemModelGenerator.SpanFacing m_111683_() {
         return this.f_111675_;
      }

      public int m_111686_() {
         return this.f_111676_;
      }

      public int m_111687_() {
         return this.f_111677_;
      }

      public int m_111688_() {
         return this.f_111678_;
      }
   }

   @OnlyIn(Dist.CLIENT)
   static enum SpanFacing {
      UP(Direction.UP, 0, -1),
      DOWN(Direction.DOWN, 0, 1),
      LEFT(Direction.EAST, -1, 0),
      RIGHT(Direction.WEST, 1, 0);

      private final Direction f_111693_;
      private final int f_111694_;
      private final int f_111695_;

      private SpanFacing(Direction p_111701_, int p_111702_, int p_111703_) {
         this.f_111693_ = p_111701_;
         this.f_111694_ = p_111702_;
         this.f_111695_ = p_111703_;
      }

      public Direction m_111704_() {
         return this.f_111693_;
      }

      public int m_111707_() {
         return this.f_111694_;
      }

      public int m_111708_() {
         return this.f_111695_;
      }

      boolean m_111709_() {
         return this == DOWN || this == UP;
      }
   }
}
