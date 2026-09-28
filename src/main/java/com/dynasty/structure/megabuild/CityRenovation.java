package com.dynasty.structure.megabuild;

import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.entity.SpawnerBlockEntity;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Conflict-aware renovation of the explicitly identified workshop copy, never a bulk overwrite. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class CityRenovation {
    private static Job active;
    static final BlockPos ORIGIN=new BlockPos(-80,-60,-96);
    static class Job {
        final CommandSourceStack source;
        final BlockPos origin;
        final Blueprint before=PlayerCityEdits.originalWithEdits().rotate(2);
        final Blueprint after=new TiangongCitadel(0).blueprint().rotate(2);
        int x,changed,conflicts,preservedChests;boolean done;
        Job(CommandSourceStack s){this(s,ORIGIN);}
        Job(CommandSourceStack s,BlockPos origin){source=s;this.origin=origin;}
        void step(){
            var level=source.getLevel();
            // One x stripe per tick; compare expected saved states before every write.
            for(int y=0;y<56;y++)for(int z=0;z<176;z++){
                var old=before.at(x,y,z);var next=after.at(x,y,z);
                if(old==next)continue;
                BlockPos pos=origin.offset(x,y,z);
                var actual=level.getBlockState(pos);
                String id=net.minecraft.core.registries.BuiltInRegistries.BLOCK.getKey(actual.getBlock()).toString();
                if(id.equals("minecraft:chest")||id.equals("lootr:lootr_chest")){preservedChests++;continue;}
                var expected=MegabuildPiece.blockState(old);
                // Weathering and leaf distance are not user edits; no other mismatch is overwritten.
                boolean same=actual.equals(expected)
                    ||(old==Blueprint.Kind.CROP&&actual.is(Blocks.OAK_LEAVES))
                    ||(old==Blueprint.Kind.COPPER&&id.endsWith("cut_copper"));
                if(!same){conflicts++;continue;}
                if(next==Blueprint.Kind.CHEST||next==Blueprint.Kind.RICH_CHEST){
                    level.setBlock(pos,Blocks.CHEST.defaultBlockState(),3);
                    if(level.getBlockEntity(pos) instanceof ChestBlockEntity chest)
                        chest.setLootTable(new ResourceLocation("dynasty","chests/"+(next==Blueprint.Kind.RICH_CHEST?"tiangong_rich":"tiangong_common")),pos.asLong());
                }else{
                    level.setBlock(pos,MegabuildPiece.blockState(next),3);
                    if(level.getBlockEntity(pos) instanceof SpawnerBlockEntity spawner){
                        spawner.load(CityEncounters.spawnerTag(next));spawner.setChanged();
                    }
                }
                changed++;
            }
            if(++x==176){
                done=true;
                source.sendSuccess(()->Component.literal("原地修缮完成："+changed+" 格；保留原宝箱 "+preservedChests+" 处；跳过后来修改 "+conflicts+" 格。"),false);
            }
        }
    }
    @SubscribeEvent public static void commands(RegisterCommandsEvent event){
        event.getDispatcher().register(Commands.literal("dynasty_renovate").requires(s->s.hasPermission(2))
            .executes(c->{
                c.getSource().sendSuccess(()->Component.literal("仅用于你的超平坦建筑：西北角 -80 -60 -96，176×176。请先备份；只应用差异，保留原宝箱并跳过后续修改。输入 /dynasty_renovate confirm 开始。"),false);return 1;
            }).then(Commands.literal("confirm").executes(c->{
                var s=c.getSource();
                if(active!=null||s.getLevel().dimension()!=Level.OVERWORLD){s.sendFailure(Component.literal("已有修缮任务，或不在主世界。"));return 0;}
                // Several separated original landmarks must match before touching anything.
                int matches=0;
                for(BlockPos p:new BlockPos[]{new BlockPos(7,-60,-96),new BlockPos(7,-60,79),new BlockPos(-37,-60,-37)})
                    if(s.getLevel().getBlockState(p).is(Blocks.SMOOTH_STONE)||s.getLevel().getBlockState(p).is(Blocks.WATER))matches++;
                if(matches!=3){s.sendFailure(Component.literal("未识别到原建筑，取消修缮；没有修改方块。"));return 0;}
                active=new Job(s);s.sendSuccess(()->Component.literal("开始差异修缮，请不要同时改建筑，等待完成提示。"),false);return 1;
            })));
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event){
        if(event.phase==TickEvent.Phase.END&&active!=null){
            try{active.step();if(active.done)active=null;}
            catch(Exception e){active.source.sendFailure(Component.literal("修缮中止，已完成部分保留："+e.getMessage()));active=null;}
        }
    }
    @SubscribeEvent public static void stop(ServerStoppingEvent e){active=null;}
}
