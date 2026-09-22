package com.dynasty;

import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.ChatFormatting;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.List;

/** Optional integration: calls the installed compass's own bounded search worker, never /locate on tick. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class DynastyCompassBridge {
    public record Destination(String id,String label,String dimension,String target,boolean biome) {}
    public static final List<Destination> DESTINATIONS=List.of(
        new Destination("palace","皇家宫殿","celestial_dynasty","palace",false),
        new Destination("academy","国子监","celestial_dynasty","academy",false),
        new Destination("imperial_tomb","帝陵建筑（不保证刷始皇）","celestial_dynasty","imperial_tomb",false),
        new Destination("great_wall_gate","长城关隘","celestial_dynasty","great_wall_gate",false),
        new Destination("star_altar","九霄星坛","jiuxiao","star_altar",false),
        new Destination("stone_grove","幽冥石林","underworld","stone_grove",false),
        new Destination("dragon_emperor","龙帝栖息区","celestial_dynasty","celestial_plains",true),
        new Destination("eunuch_mastermind","宦官首脑栖息区","celestial_dynasty","celestial_plains",true),
        new Destination("undead_first_emperor","不死始皇栖息区","underworld","underworld_wastes",true),
        new Destination("rebel_general","叛将的幽冥栖息区","underworld","underworld_wastes",true),
        new Destination("nine_heaven_general","九霄天将栖息区","jiuxiao","jiuxiao_skyland",true),
        new Destination("dragon_king","东海龙王栖息区","dragon_palace","dragon_palace_hall",true));

    @SubscribeEvent public static void register(RegisterCommandsEvent e) {
        e.getDispatcher().register(Commands.literal("dynasty_find")
            .executes(c->menu(c.getSource()))
            .then(Commands.argument("destination",StringArgumentType.word())
                .suggests((c,b)->{DESTINATIONS.forEach(d->b.suggest(d.id));return b.buildFuture();})
                .executes(c->search(c.getSource(),StringArgumentType.getString(c,"destination")))));
    }
    private static int menu(CommandSourceStack source) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        var player=source.getPlayerOrException();
        player.sendSystemMessage(Component.literal("王朝导航：手持探索者罗盘找建筑，手持自然罗盘找 Boss 栖息区。先进入目标维度，再点击："));
        for(var d:DESTINATIONS)player.sendSystemMessage(Component.literal("["+d.label+"] · dynasty:"+d.dimension)
            .withStyle(s->s.withColor(ChatFormatting.AQUA).withUnderlined(true)
                .withClickEvent(new ClickEvent(ClickEvent.Action.RUN_COMMAND,"/dynasty_find "+d.id))));
        return 1;
    }
    private static int search(CommandSourceStack source,String id) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        var p=source.getPlayerOrException();
        var d=DESTINATIONS.stream().filter(v->v.id.equals(id)).findFirst().orElse(null);
        if(d==null){source.sendFailure(Component.literal("未知王朝目的地；输入 /dynasty_find 查看列表。"));return 0;}
        if(!p.level().dimension().location().equals(new ResourceLocation("dynasty",d.dimension))) {
            source.sendFailure(Component.literal("请先进入 dynasty:"+d.dimension+"。罗盘不会跨维度传送或搜索。"));return 0;
        }
        String mod=d.biome?"naturescompass":"explorerscompass";
        if(!ModList.get().isLoaded(mod)){source.sendFailure(Component.literal("未安装 "+mod+"，王朝本体仍可正常使用。"));return 0;}
        ItemStack stack=p.getMainHandItem();
        if(!new ResourceLocation(mod,mod).equals(ForgeRegistries.ITEMS.getKey(stack.getItem()))) {
            source.sendFailure(Component.literal("请在主手拿着"+(d.biome?"自然罗盘":"探索者罗盘")+"再点击。"));return 0;
        }
        long now=p.serverLevel().getGameTime();
        var data=p.getPersistentData();
        if(data.contains("DynastyCompassNext")&&now<data.getLong("DynastyCompassNext")
                &&data.getLong("DynastyCompassNext")-now<=100) {
            source.sendFailure(Component.literal("请稍等，导航请求间隔为 5 秒。"));return 0;
        }
        try {
            Object compass=stack.getItem();Class<?> type=compass.getClass();
            if((boolean)type.getMethod("isBroken",ItemStack.class).invoke(compass,stack)) {
                source.sendFailure(Component.literal("罗盘已损坏，请修复或更换。"));return 0;
            }
            var target=new ResourceLocation("dynasty",d.target);
            // Respect the compass owner's blacklist and XP rules instead of bypassing its GUI checks.
            Class<?> utility=Class.forName("com.chaosthedude."+mod+".util."+(d.biome?"BiomeUtils":"StructureUtils"));
            List<?> allowed=(List<?>)(d.biome
                ?utility.getMethod("getAllowedBiomeKeys",net.minecraft.world.level.Level.class).invoke(null,p.serverLevel())
                :utility.getMethod("getAllowedStructureKeys",ServerLevel.class).invoke(null,p.serverLevel()));
            if(!allowed.contains(target)){source.sendFailure(Component.literal("当前罗盘配置不允许搜索这个目标。"));return 0;}
            int cost=(int)(d.biome
                ?utility.getMethod("getXpLevelsForBiome",ResourceLocation.class).invoke(null,target)
                :utility.getMethod("getXpLevelsForStructure",ServerLevel.class,ResourceLocation.class).invoke(null,p.serverLevel(),target));
            if(!p.getAbilities().instabuild&&p.experienceLevel<cost) {
                source.sendFailure(Component.literal("本次搜索需要 "+cost+" 级经验。"));return 0;
            }
            if(d.biome)type.getMethod("searchForBiome",ServerLevel.class,Player.class,ResourceLocation.class,BlockPos.class,ItemStack.class)
                .invoke(compass,p.serverLevel(),p,target,p.blockPosition(),stack);
            else type.getMethod("searchForStructure",ServerLevel.class,Player.class,BlockPos.class,ResourceLocation.class,boolean.class,ItemStack.class)
                .invoke(compass,p.serverLevel(),p,p.blockPosition(),target,false,stack);
            data.putLong("DynastyCompassNext",now+100);
            p.sendSystemMessage(Component.literal(d.biome
                ?"已请求寻找栖息生物群系，不是追踪 Boss 实体；到达后仍需探索。已有信物可用法阵·祭坛召唤复战。"
                :"已请求寻找建筑，搜索结果和距离以罗盘界面为准。"));
            return 1;
        } catch(ReflectiveOperationException | LinkageError ex) {
            Dynasty.LOGGER.warn("Compass integration failed for {}",mod,ex);
            source.sendFailure(Component.literal("当前罗盘版本接口不兼容，请直接右键罗盘手动搜索。"));return 0;
        }
    }
}
