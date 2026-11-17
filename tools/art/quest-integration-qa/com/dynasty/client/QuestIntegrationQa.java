package com.dynasty.client;

import net.minecraft.client.Minecraft;
import net.minecraft.world.Difficulty;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;
import java.lang.reflect.*;
import java.util.concurrent.CompletableFuture;

/** QA source set only, never included in the shipped mod or player's existing world. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class QuestIntegrationQa {
    static final Path OUT=Path.of(System.getProperty("dynasty.questIntegrationQa.output"));
    static boolean started,finished,checked;
    static int frames,step;
    static Object file;
    static CompletableFuture<Void> serverCheck;
    static final List<String> results=new ArrayList<>();
    static final long[] PAGES={0x4000000000000500L,0x4000000000000000L,0x4000000000000004L,0x1000000000041002L,0x1000000000c40002L,0x1000000000020006L,0x1000000000c4002eL,0x1000000000c40028L,0x1000000000010026L,0x1000000000000022L,0x100000000000014bL,0x10d31e35d10a9311L,0x10d3a23ed18f19c9L,0x1000000000030208L,0x10d3070ef334c455L,0x10d336483f3340eeL,0x1000000000030001L,0x10d379d49ab6889cL,0x10000000000000d8L,0x1000000000000107L,0x10d38da876ddcf94L};
    static final String[] NAMES={"home","workshop","accessories","curios","gear","altar","locks","boat","wind","academy","army-stage","brewing","empty-bottle","archery-target","infusion-table","writing","guard-materials","charm-directory","charm-day-night","charm-cost","healing-potion"};
    static final String[] FIGURES={"altar","qimen","bronze","portals","infusion","exam","army","compasses","curios","smithing","locks","sword_moves","well","boat","rescue","bellows","compass_recipe","refining","wind_recipe","academy_materials","army_stage","brewing","glass_bottle","target_recipe","infusion_table","writing_recipe"};
    static Class<?> type(String n)throws Exception{return Class.forName("dev.ftb.mods.ftbquests."+n);}
    static Object call(Object o,String name,Class<?>[] types,Object...args)throws Exception{return o.getClass().getMethod(name,types).invoke(o,args);}
    static void check(boolean okay,String message){if(!okay)throw new AssertionError(message);results.add(message);}
    @SubscribeEvent public static void frame(TickEvent.RenderTickEvent e){
        if(!Boolean.getBoolean("dynasty.questIntegrationQa")||finished||e.phase!=TickEvent.Phase.END)return;
        Minecraft mc=Minecraft.getInstance();
        try{
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                check(mc.gameDirectory.getCanonicalPath().endsWith("/build/quest-journey-client-v3"),"Isolated QA directory, existing saves untouched");
                Files.createDirectories(OUT);started=true;
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);
                var settings=new LevelSettings("Quest integration QA",GameType.CREATIVE,false,Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT);
                mc.createWorldOpenFlows().createFreshLevel("quest-qa-"+System.currentTimeMillis(),settings,new WorldOptions(7L,false,false),
                    registry->registry.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null||++frames<100)return;
            if(!checked){
                file=type("client.ClientQuestFile").getField("INSTANCE").get(null);if(file==null)return;
                Collection<?> objects=(Collection<?>)call(file,"getAllObjects",new Class<?>[0]);
                if(objects.isEmpty())return;
                var raw=type("quest.QuestObjectBase").getDeclaredField("rawIcon");raw.setAccessible(true);
                int quests=0,adv=0;var listing=new ArrayList<String>();
                for(Object object:objects){
                    boolean q=type("quest.Quest").isInstance(object),a=type("quest.task.AdvancementTask").isInstance(object);
                    if(!q&&!a)continue;
                    ItemStack icon=(ItemStack)raw.get(object);
                    if(icon.isEmpty())throw new AssertionError("Empty native icon: "+object);
                    if(q)quests++;else{adv++;if(((String)call(object,"getRawTitle",new Class<?>[0])).isBlank())throw new AssertionError("Blank advancement title: "+object);}
                    listing.add(object+" -> "+icon);
                }
                check(quests==1259,"Native client loaded all 1259 quests, including every old identity with nonempty icons");
                check(adv>46,"All "+adv+" native advancement tasks have explicit icons and titles");
                var covers=new HashSet<String>();
                for(Object chapter:(Collection<?>)call(file,"getAllChapters",new Class<?>[0])){
                    ItemStack icon=(ItemStack)raw.get(chapter);
                    if(icon.isEmpty())throw new AssertionError("Empty chapter cover: "+chapter);
                    covers.add(net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(icon.getItem()).toString());
                }
                check(covers.size()==20,"All 20 native chapter covers are distinct registered items");
                check(!covers.contains("minecraft:iron_sword")&&!covers.contains("dynasty:dynasty_manual"),"No generic sword or manual chapter covers");
                Files.write(OUT.resolve("native-icons.txt"),listing);
                int figures=0;
                for(String name:FIGURES){
                    var location=new net.minecraft.resources.ResourceLocation("dynasty","textures/gui/quests/journey/"+name+".png");
                    var resource=mc.getResourceManager().getResource(location).orElseThrow(()->new AssertionError("Missing GUI image "+location));
                    try(var stream=resource.open();var pixels=com.mojang.blaze3d.platform.NativeImage.read(stream)){
                        if(pixels.getWidth()!=512||pixels.getHeight()!=256)throw new AssertionError("Bad GUI figure dimensions "+name);
                    }
                    figures++;
                }
                check(figures==26,"All 26 actual GUI operation figures loaded from selected resources");
                for(int i=0;i<4;i++){
                    var location=new net.minecraft.resources.ResourceLocation("dynasty","textures/gui/quests/journey/labels/charm_"+i+".png");
                    var resource=mc.getResourceManager().getResource(location).orElseThrow(()->new AssertionError("Missing charm group label "+location));
                    try(var stream=resource.open();var pixels=com.mojang.blaze3d.platform.NativeImage.read(stream)){
                        if(pixels.getWidth()!=512||pixels.getHeight()!=48)throw new AssertionError("Bad charm label dimensions "+location);
                    }
                }
                check(true,"All four functional charm labels decoded from selected resources");

                Object brewedQuest=call(file,"getQuest",new Class<?>[]{long.class},0x10d31e35d10a9311L);
                var tasksField=type("quest.Quest").getDeclaredField("tasks");tasksField.setAccessible(true);
                Object brewedTask=((java.util.List<?>)tasksField.get(brewedQuest)).get(0);
                var awkward=net.minecraft.world.item.alchemy.PotionUtils.setPotion(new ItemStack(net.minecraft.world.item.Items.POTION),net.minecraft.world.item.alchemy.Potions.AWKWARD);
                var water=net.minecraft.world.item.alchemy.PotionUtils.setPotion(new ItemStack(net.minecraft.world.item.Items.POTION),net.minecraft.world.item.alchemy.Potions.WATER);
                check((Boolean)call(brewedTask,"test",new Class<?>[]{ItemStack.class},awkward),"Actual FTB potion filter accepts an awkward potion");
                check(!(Boolean)call(brewedTask,"test",new Class<?>[]{ItemStack.class},water),"Actual FTB potion filter rejects a plain water bottle");
                Object healingQuest=call(file,"getQuest",new Class<?>[]{long.class},0x10d38da876ddcf94L);
                Object healingTask=((java.util.List<?>)tasksField.get(healingQuest)).get(0);
                var healing=net.minecraft.world.item.alchemy.PotionUtils.setPotion(new ItemStack(net.minecraft.world.item.Items.POTION),net.minecraft.world.item.alchemy.Potions.HEALING);
                var strongHealing=net.minecraft.world.item.alchemy.PotionUtils.setPotion(new ItemStack(net.minecraft.world.item.Items.POTION),net.minecraft.world.item.alchemy.Potions.STRONG_HEALING);
                check((Boolean)call(healingTask,"test",new Class<?>[]{ItemStack.class},healing),"Actual FTB rescue filter accepts ordinary healing potion");
                check(!(Boolean)call(healingTask,"test",new Class<?>[]{ItemStack.class},strongHealing),"Actual FTB rescue filter rejects strong healing potion");
                check(!(Boolean)call(healingTask,"test",new Class<?>[]{ItemStack.class},water),"Actual FTB rescue filter rejects plain water bottle");

                Object gear=call(file,"getQuest",new Class<?>[]{long.class},0x1000000000c40002L);
                check(((ItemStack)raw.get(gear)).getCount()==1,"Actual gear icon stack has Count 1");
                serverCheck=mc.getSingleplayerServer().submit(()->{try{persistence();}catch(Exception ex){throw new RuntimeException(ex);}});
                checked=true;frames=0;
                show();return;
            }
            if(step>=PAGES.length){
                if(frames<8)return;frames=0;
                if(!QuestJourneyUiQa.tick(mc,file))return;
                serverCheck.join();Files.write(OUT.resolve("PASS.txt"),results);finished=true;mc.stop();return;
            }
            if(frames<35)return;frames=0;
            check(mc.screen!=null&&mc.screen.getClass().getName().contains("ftblibrary"),"Actual native FTB GUI rendered: "+NAMES[step]);
            try(var pixels=Screenshot.takeScreenshot(mc.getMainRenderTarget())){pixels.writeToFile(OUT.resolve(NAMES[step]+".png"));}
            if(++step<PAGES.length)show();
        }catch(Throwable error){
            finished=true;error.printStackTrace();try{Files.createDirectories(OUT);Files.writeString(OUT.resolve("FAIL.txt"),error+"\n"+String.join("\n",results));}catch(Exception ignored){}mc.stop();
        }
    }
    static void show()throws Exception{
        type("client.ClientQuestFile").getMethod("openBookToQuestObject",long.class).invoke(null,PAGES[step]);
        Object screen=((Optional<?>)call(file,"getQuestScreen",new Class<?>[0])).orElseThrow();
        var field=type("client.gui.quests.QuestScreen").getDeclaredField("chapterPanel");field.setAccessible(true);
        call(field.get(screen),"setExpanded",new Class<?>[]{boolean.class},false);
    }
    static void persistence()throws Exception{
        Object server=type("quest.ServerQuestFile").getField("INSTANCE").get(null);
        Class<?> teamType=type("quest.TeamData"),taskType=type("quest.task.Task"),objectType=type("quest.QuestObject");
        UUID id=UUID.randomUUID();Object old=teamType.getConstructor(UUID.class,type("quest.BaseQuestFile")).newInstance(id,server);
        // Detached legacy-style fixture: these IDs were completed before their chapter move.
        for(long number:new long[]{0x0c40002L,0x0c4000eL,0x0c40021L}){
            Object task=call(server,"getTask",new Class<?>[]{long.class},0x2000000000000000L+number);
            call(old,"setProgress",new Class<?>[]{taskType,long.class},task,1L);
            call(old,"setCompleted",new Class<?>[]{long.class,Date.class},0x1000000000000000L+number,new Date());
        }
        Object saved=call(old,"serializeNBT",new Class<?>[0]);
        Object restored=teamType.getConstructor(UUID.class,type("quest.BaseQuestFile")).newInstance(id,server);
        call(restored,"deserializeNBT",new Class<?>[]{saved.getClass()},saved);
        for(long number:new long[]{0x0c40002L,0x0c4000eL,0x0c40021L}){
            Object task=call(server,"getTask",new Class<?>[]{long.class},0x2000000000000000L+number);
            Object quest=call(server,"getQuest",new Class<?>[]{long.class},0x1000000000000000L+number);
            if((long)call(restored,"getProgress",new Class<?>[]{taskType},task)!=1L || !(boolean)call(restored,"isCompleted",new Class<?>[]{objectType},quest))throw new AssertionError("Moved quest progress lost: "+number);
        }
        Files.writeString(OUT.resolve("native-persistence.txt"),"Native TeamData serialize/deserialize retains completed gear, crafted pill and three-site survey identities after chapter relocation. Detached fixture; no player saves edited.\n");
    }
}
