package com.dynasty.structure.megabuild;

import com.dynasty.Dynasty;
import net.minecraft.commands.Commands;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Explicit workshop placement, one loaded chunk per tick, never touches saves offline. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class MegabuildWorkshop {
    private static Job active;
    static final class Job {
        final ServerLevel level;
        final CommandSourceStack source;
        final MegabuildPiece piece;
        final BlockPos origin;
        final int firstX,firstZ,lastX,lastZ;
        int x,z;
        boolean done;
        Exception failure;
        Job(CommandSourceStack s,boolean city,BlockPos p){
            source=s;level=s.getLevel();origin=p;
            int size=city?176:96,height=city?56:36;
            piece=new MegabuildPiece(city?MegabuildStructures.CITADEL_PIECE.get():MegabuildStructures.MINING_PIECE.get(),
                0,p,city?MegabuildStructures::citadel:MegabuildStructures::mining,0,0,size,height);
            firstX=p.getX()>>4;firstZ=p.getZ()>>4;
            lastX=(p.getX()+size-1)>>4;lastZ=(p.getZ()+size-1)>>4;x=firstX;z=firstZ;
        }
        void step(){
            try{
                level.getChunk(x,z);
                var box=new BoundingBox(x*16,level.getMinBuildHeight(),z*16,x*16+15,level.getMaxBuildHeight()-1,z*16+15);
                piece.postProcess(level,level.structureManager(),level.getChunkSource().getGenerator(),
                    level.random,box,new ChunkPos(x,z),origin);
                if(++x>lastX){x=firstX;z++;}
                if(z>lastZ){done=true;source.sendSuccess(()->Component.literal("建筑搭建完成。入口在起点东侧约 87 格，向南进入（矿庄约 47 格）。"),false);}
            }catch(Exception e){failure=e;done=true;source.sendFailure(Component.literal("搭建中止，已放置部分保留："+e.getMessage()));}
        }
    }
    @SubscribeEvent public static void commands(RegisterCommandsEvent e){
        var root=Commands.literal("dynasty_build").requires(s->s.hasPermission(2));
        for(String id:new String[]{"tiangong_citadel","tiangong_mining_estate"}){
            boolean city=id.equals("tiangong_citadel");
            root.then(Commands.literal(id).executes(c->{
                c.getSource().sendSuccess(()->Component.literal("会从当前位置向东、向南覆盖 "+(city?"176×176×56":"96×96×36")+" 区域！请先备份并选择空地。确认后输入 /dynasty_build "+id+" confirm。"),false);return 1;
            }).then(Commands.literal("confirm").executes(c->start(c.getSource(),city))));
        }
        e.getDispatcher().register(root);
    }
    private static int start(CommandSourceStack s,boolean city){
        if(active!=null){s.sendFailure(Component.literal("已有建筑正在搭建，请等待完成。"));return 0;}
        BlockPos p=BlockPos.containing(s.getPosition());int size=city?176:96,height=city?56:36;
        if(p.getY()<s.getLevel().getMinBuildHeight()||p.getY()+height>s.getLevel().getMaxBuildHeight()
            ||!s.getLevel().getWorldBorder().isWithinBounds(p)||!s.getLevel().getWorldBorder().isWithinBounds(p.offset(size-1,0,size-1))){
            s.sendFailure(Component.literal("超出世界高度或边界，请换一处空地。"));return 0;
        }
        active=new Job(s,city,p);
        s.sendSuccess(()->Component.literal("开始分区搭建，请等待完成提示。无需提前加载整片区域。"),false);return 1;
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e){
        if(e.phase==TickEvent.Phase.END&&active!=null){active.step();if(active.done)active=null;}
    }
    @SubscribeEvent public static void stop(ServerStoppingEvent e){active=null;}
}
