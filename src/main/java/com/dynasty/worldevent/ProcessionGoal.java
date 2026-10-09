package com.dynasty.worldevent;
import com.dynasty.blueprint.TemplateMob;
import net.minecraft.world.entity.ai.goal.Goal;
import java.util.EnumSet;
/** One server route controller; peaceful marching preempts combat/strolling without disabling navigation. */
public final class ProcessionGoal extends Goal {
    private final TemplateMob mob;private long nextPath;
    public ProcessionGoal(TemplateMob mob){this.mob=mob;setFlags(EnumSet.of(Flag.MOVE,Flag.LOOK));}
    @Override public boolean canUse(){return DynastyWorldEventManager.marching(mob);}
    @Override public boolean canContinueToUse(){return canUse();}
    @Override public void start(){mob.setTarget(null);nextPath=0;}
    @Override public void tick(){if(mob.level().getGameTime()>=nextPath){nextPath=mob.level().getGameTime()+20;DynastyWorldEventManager.march(mob);}}
    @Override public void stop(){mob.getNavigation().stop();}
}
