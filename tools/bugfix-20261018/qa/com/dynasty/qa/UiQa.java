package com.dynasty.qa;

import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.Difficulty;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;

@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public class UiQa {
    static boolean started,done;static int frames,step;static final Path OUT=Path.of(System.getProperty("dynasty.bugfix.output"));
    @SubscribeEvent public static void tick(TickEvent.RenderTickEvent e){
        if(done||e.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();
        try{
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                Files.createDirectories(OUT);started=true;
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("bugfix-isolated",new LevelSettings("UI QA",GameType.CREATIVE,false,Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(7,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.player==null||mc.level==null||++frames<150)return;
            if(step==0){mc.setScreen(null);var id=mc.player.getUUID();mc.getSingleplayerServer().execute(()->{var p=mc.getSingleplayerServer().getPlayerList().getPlayer(id);p.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(36);p.setHealth(27);});step++;frames=0;}
            else if(step==1){capture(mc,"health-27-of-36.png");com.dynasty.navigation.CreatureCompassScreen.open();step++;frames=0;}
            else if(step==2){capture(mc,"creature-compass.png");
                if(JeiProbe.runtime==null)throw new AssertionError("JEI runtime absent");
                var focus=JeiProbe.runtime.getJeiHelpers().getFocusFactory().createFocus(mezz.jei.api.recipe.RecipeIngredientRole.OUTPUT,mezz.jei.api.constants.VanillaTypes.ITEM_STACK,new net.minecraft.world.item.ItemStack(com.dynasty.DynastyItems.SKY_TOKEN.get()));
                JeiProbe.runtime.getRecipesGui().show(java.util.List.of(focus));step++;frames=0;
            }else if(step==3){capture(mc,"sky-token-jei.png");Files.writeString(OUT.resolve("PASS.txt"),"Native client: 36 max /27 current, creature screen, JEI output focus opened. Inspect screenshots for visual acceptance.\n");done=true;mc.stop();}
        }catch(Throwable ex){try{Files.createDirectories(OUT);Files.writeString(OUT.resolve("FAIL.txt"),ex.toString());}catch(Exception ignored){}done=true;mc.stop();}
    }
    static void capture(Minecraft mc,String name){Screenshot.grab(OUT.toFile(),name,mc.getMainRenderTarget(),msg->{});}
}
