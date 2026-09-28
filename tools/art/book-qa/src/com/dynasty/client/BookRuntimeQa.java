package com.dynasty.client;

import com.mojang.blaze3d.pipeline.TextureTarget;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.VertexSorting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.*;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.core.registries.Registries;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import org.joml.Matrix4f;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Isolated real client + newly created QA world. Never accesses the user's launcher saves. */
@Mod.EventBusSubscriber(modid="dynasty", value=Dist.CLIENT)
public final class BookRuntimeQa {
    static final Path OUT=Path.of(System.getProperty("dynasty.bookQa.output","build/book-qa/results"));
    static CompletableFuture<Void> reload;
    static boolean started,finished;
    static int frames;
    static final List<String> results=new ArrayList<>();
    @SubscribeEvent public static void frame(TickEvent.RenderTickEvent event) {
        if (!Boolean.getBoolean("dynasty.bookQa") || finished || event.phase!=TickEvent.Phase.END) return;
        Minecraft mc=Minecraft.getInstance();
        try {
            if (mc.getOverlay()!=null) return;
            if(mc.screen instanceof AccessibilityOnboardingScreen) mc.setScreen(new TitleScreen());
            if (!started && mc.screen instanceof TitleScreen) {
                if (reload==null) {
                    mc.getLanguageManager().setSelected("zh_cn");
                    reload=mc.reloadResourcePacks(); return;
                }
                if(!reload.isDone())return;
                reload.join();started=true;
                if(!mc.gameDirectory.getCanonicalPath().equals(Path.of(System.getProperty("dynasty.bookQa.workDir",mc.gameDirectory.getPath())).toRealPath().toString())
                        || !mc.gameDirectory.getCanonicalPath().contains("/build/")
                        || !mc.gameDirectory.getCanonicalPath().endsWith("/book-qa/client"))
                    throw new AssertionError("Wrong game directory: refusing to create test world");
                GameRules rules=new GameRules();
                rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);
                var settings=new LevelSettings("Book QA",GameType.CREATIVE,false,
                        net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT);
                mc.createWorldOpenFlows().createFreshLevel("book-qa-"+System.currentTimeMillis(),settings,
                        new WorldOptions(25L,false,false),registry->registry.registryOrThrow(Registries.WORLD_PRESET)
                                .getOrThrow(WorldPresets.FLAT).createWorldDimensions());
                return;
            }
            if(mc.level==null||mc.player==null||++frames<80)return;
            finished=true; Files.createDirectories(OUT);
            Class<?> registry=Class.forName("vazkii.patchouli.common.book.BookRegistry");
            Object owner=registry.getField("INSTANCE").get(null);
            var books=(Map<?,?>)registry.getField("books").get(owner);
            Object book=books.get(new ResourceLocation("dynasty","imperial_codex"));
            require(book!=null,"Dynasty book registered");
            Object contents=book.getClass().getMethod("getContents").invoke(book);
            require(!(Boolean)contents.getClass().getMethod("isErrored").invoke(contents),
                    "Book parsing: "+contents.getClass().getMethod("getException").invoke(contents));
            require(((Map<?,?>)contents.getClass().getField("categories").get(contents)).size()==8,"Eight categories loaded");
            results.add("Entry count="+((Map<?,?>)contents.getClass().getField("entries").get(contents)).size());
            ClientGuide.open();
            require(mc.screen.getClass().getName().startsWith("vazkii.patchouli"),"Original Dynasty manual opens native Patchouli");
            capture(mc,"book-home",mc.screen);
            Class<?> api=Class.forName("vazkii.patchouli.api.PatchouliAPI");
            Object instance=api.getMethod("get").invoke(null);
            var open=Class.forName("vazkii.patchouli.api.PatchouliAPI$IPatchouliAPI").getMethod(
                    "openBookEntry",ResourceLocation.class,ResourceLocation.class,int.class);
            open.invoke(instance,new ResourceLocation("dynasty","imperial_codex"),new ResourceLocation("dynasty","schools/sword"),0);
            capture(mc,"book-evolution",mc.screen);
            open.invoke(instance,new ResourceLocation("dynasty","imperial_codex"),new ResourceLocation("dynasty","schools/growth"),0);
            capture(mc,"book-growth",mc.screen);
            open.invoke(instance,new ResourceLocation("dynasty","imperial_codex"),new ResourceLocation("dynasty","accessories/baizhan_ring"),0);
            capture(mc,"book-new-accessory",mc.screen);
            open.invoke(instance,new ResourceLocation("dynasty","imperial_codex"),new ResourceLocation("dynasty","schools/accessory_refining"),0);
            capture(mc,"book-refining",mc.screen);
            open.invoke(instance,new ResourceLocation("dynasty","imperial_codex"),new ResourceLocation("dynasty","accessories/wanjun_ring"),0);
            capture(mc,"book-third-tier",mc.screen);
            var melee=stack("baizhan_ring").getTooltipLines(mc.player,TooltipFlag.Default.NORMAL);
            for(String stat:new String[]{"近战伤害 +28%","生命 +120","攻速 +6%"})
                require(melee.stream().filter(l->l.getString().contains(stat)).count()==1,"Exactly one passive stat: "+stat);
            require(stack("guanri_thumbring").getTooltipLines(mc.player,TooltipFlag.Default.NORMAL).stream()
                .anyMatch(l->l.getString().contains("箭矢伤害 +28%")),"Arrow bonus localized");
            require(stack("taiqing_talisman_case").getTooltipLines(mc.player,TooltipFlag.Default.NORMAL).stream()
                .anyMatch(l->l.getString().contains("律令兵器伤害 +40%")),"Edict bonus localized");
            capture(mc,"school-accessory-tooltips",new Screen(Component.literal("School Accessory QA")) {
                @Override public void render(GuiGraphics g,int x,int y,float partial) {
                    g.fill(0,0,width,height,0xff252b2a);
                    g.drawString(font,"实际游戏悬浮说明 · 新增被动饰品",20,20,0xffffff,false);
                    g.renderTooltip(font,stack("baizhan_ring"),30,70);
                    g.renderTooltip(font,stack("guanri_thumbring"),330,70);
                    g.renderTooltip(font,stack("beichen_heartguard"),30,210);
                    g.renderTooltip(font,stack("taiqing_talisman_case"),330,210);
                }
            });
            ItemStack armour=stack("hongmeng_chestplate");
            if(armour.isEmpty())armour=stack("jade_chestplate");
            var lines=armour.getTooltipLines(mc.player,TooltipFlag.Default.NORMAL);
            int toughness=-1,reduction=-1,health=-1;int reductions=0,healths=0;
            for(int i=0;i<lines.size();i++) {
                String s=lines.get(i).getString();results.add("ARMOUR "+s);
                if(s.contains("盔甲韧性"))toughness=i;
                if(s.contains("伤害减免")){reduction=i;reductions++;}
                if(s.contains("生命上限")){health=i;healths++;}
            }
            require(toughness>=0&&reduction==toughness+1&&health==reduction+1,"Blue bonuses immediately follow toughness");
            require(reductions==1&&healths==1,"No repeated health/reduction lines");
            require(net.minecraft.ChatFormatting.BLUE.getColor().equals(lines.get(reduction).getStyle().getColor().getValue()),"Reduction is blue");
            capture(mc,"compact-tooltips",new Screen(Component.literal("Tooltip QA")) {
                @Override public void render(GuiGraphics g,int x,int y,float partial) {
                    g.fill(0,0,width,height,0xff252b2a);
                    g.drawString(font,"实际游戏悬浮说明 · 不按 Shift",20,20,0xffffff,false);
                    g.renderTooltip(font,lines,Optional.empty(),40,70);
                    g.renderTooltip(font,stack("zhenguan_mirror"),350,70);
                    g.renderTooltip(font,stack("liuyun_sword"),350,190);
                }
            });
            for(var item:ForgeRegistries.ITEMS.getValues()) if(item instanceof com.dynasty.DynastyTrinketTips.Charm)
                for(var line:new ItemStack(item).getTooltipLines(mc.player,TooltipFlag.Default.NORMAL))
                    require(!line.getString().contains("常驻"),"Accessory has no redundant label: "+item);
            var paw=stack("bear_paw").getTooltipLines(mc.player,TooltipFlag.Default.NORMAL);
            require(paw.stream().anyMatch(l->l.getString().contains("生命")&&!l.getString().contains("攻击"))
                    &&paw.stream().anyMatch(l->l.getString().contains("攻击")&&!l.getString().contains("生命")),
                    "Bear paw separates health and attack into two lines");
            for(String realm:new String[]{"celestial_dynasty","underworld","jiuxiao","dragon_palace"}) {
                String key="travelerstitles.dynasty."+realm;
                require(!Component.translatable(key).getString().equals(key),"Translated dimension title "+realm);
            }
            capture(mc,"two-line-accessory",new Screen(Component.literal("Accessory QA")) {
                @Override public void render(GuiGraphics g,int x,int y,float partial) {
                    g.fill(0,0,width,height,0xff252b2a);
                    g.renderTooltip(font,paw,Optional.empty(),80,80);
                }
            });
            Files.write(OUT.resolve("PASS.txt"),results);
            mc.stop();
        } catch(Throwable error) {
            finished=true;error.printStackTrace();
            try{Files.createDirectories(OUT);Files.writeString(OUT.resolve("FAIL.txt"),error.toString()+"\n"+String.join("\n",results));}catch(Exception ignored){}
            mc.stop();
        }
    }
    static ItemStack stack(String id){return new ItemStack(ForgeRegistries.ITEMS.getValue(new ResourceLocation("dynasty",id)));}
    static void require(boolean test,String detail){if(!test)throw new AssertionError(detail);results.add(detail);}
    static void capture(Minecraft mc,String name,Screen screen)throws Exception {
        int w=640,h=360;screen.init(mc,w,h);
        Matrix4f projection=new Matrix4f(RenderSystem.getProjectionMatrix());
        VertexSorting sorting=RenderSystem.getVertexSorting();
        var target=new TextureTarget(w*2,h*2,true,Minecraft.ON_OSX);
        var model=RenderSystem.getModelViewStack();model.pushPose();
        try{
            target.setClearColor(.11F,.14F,.13F,1);target.clear(Minecraft.ON_OSX);target.bindWrite(true);
            model.setIdentity();model.translate(0,0,-11000);RenderSystem.applyModelViewMatrix();
            RenderSystem.setProjectionMatrix(new Matrix4f().setOrtho(0,w,h,0,1000,21000),VertexSorting.ORTHOGRAPHIC_Z);
            RenderSystem.setShaderColor(1,1,1,1);RenderSystem.disableDepthTest();RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();
            GuiGraphics g=new GuiGraphics(mc,mc.renderBuffers().bufferSource());
            screen.renderWithTooltip(g,-100,-100,0);g.flush();
            try(var image=Screenshot.takeScreenshot(target)){image.writeToFile(OUT.resolve(name+".png"));}
        }finally{
            model.popPose();RenderSystem.applyModelViewMatrix();RenderSystem.setProjectionMatrix(projection,sorting);
            target.destroyBuffers();mc.getMainRenderTarget().bindWrite(true);
        }
    }
}
