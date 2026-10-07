package com.dynasty.worldevent;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid="dynasty")
public final class WorldEventCommands {
    @SubscribeEvent public static void register(RegisterCommandsEvent e){
        e.getDispatcher().register(Commands.literal("dynasty").then(Commands.literal("event").requires(s->s.hasPermission(2))
            .then(Commands.literal("start").then(Commands.argument("id",StringArgumentType.word()).suggests((c,b)->net.minecraft.commands.SharedSuggestionProvider.suggest(WorldEventDefinitions.ALL.keySet().stream().map(ResourceLocation::toString),b)).executes(c->{
                String value=StringArgumentType.getString(c,"id");var id=ResourceLocation.tryParse(value.contains(":")?value:"dynasty:"+value);var d=WorldEventDefinitions.ALL.get(id);
                if(d==null){c.getSource().sendFailure(Component.literal("未知事件："+value));return 0;}
                var result=DynastyWorldEventManager.start(c.getSource().getLevel(),d,net.minecraft.core.BlockPos.containing(c.getSource().getPosition()),c.getSource().getPlayer(),true);
                if(!result.started()){c.getSource().sendFailure(Component.literal("事件未启动，尚缺："+String.join(", ",result.missing())));return 0;}
                c.getSource().sendSuccess(()->Component.literal("事件已启动："+d.name()+" / "+result.instance()),false);return 1;
            })))
            .then(Commands.literal("dependencies").executes(c->{
                for(var d:WorldEventDefinitions.ALL.values()){
                    var missing=DynastyWorldEventManager.missing(c.getSource().getLevel(),d);
                    c.getSource().sendSuccess(()->Component.literal(d.id()+": "+(missing.isEmpty()?"基础流程可运行":String.join(", ",missing))),false);
                }return 1;
            }))
            .then(Commands.literal("active").executes(c->{
                var store=WorldEventStore.get(c.getSource().getLevel());for(var i:store.instances.values())if(i.active())c.getSource().sendSuccess(()->Component.literal(i.uuid+" "+i.definition+" "+i.phase),false);return 1;
            }))
            .then(Commands.literal("stop").then(Commands.argument("instance",net.minecraft.commands.arguments.UuidArgument.uuid()).executes(c->{
                return DynastyWorldEventManager.stop(c.getSource().getLevel(),net.minecraft.commands.arguments.UuidArgument.getUuid(c,"instance"))?1:0;
            })))));
        e.getDispatcher().register(Commands.literal("dynasty").then(Commands.literal("ecology").requires(s->s.hasPermission(2)).then(Commands.literal("dependencies").executes(c->{
            var missing=com.dynasty.blueprint.EcologyRules.missingDependencies();c.getSource().sendSuccess(()->Component.literal("缺失实体："+missing+"；未绑定原设定角色："+com.dynasty.blueprint.EcologyRules.UNBOUND_SOURCE_ROLES),false);return missing.isEmpty()?1:0;
        }))));
    }
    private WorldEventCommands(){}
}
