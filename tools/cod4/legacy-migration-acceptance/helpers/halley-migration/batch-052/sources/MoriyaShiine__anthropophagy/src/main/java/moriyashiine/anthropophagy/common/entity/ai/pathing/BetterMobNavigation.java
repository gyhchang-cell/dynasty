/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.entity.ai.pathing;

import net.minecraft.entity.ai.NavigationConditions;
import net.minecraft.entity.ai.pathing.MobNavigation;
import net.minecraft.entity.mob.PathAwareEntity;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.MathHelper;
import net.minecraft.util.math.Vec3d;
import net.minecraft.world.World;

public class BetterMobNavigation extends MobNavigation {
	private final PathAwareEntity entity;
	private final int timeOutSpeed;

	public BetterMobNavigation(PathAwareEntity mobEntity, World world, int timeOutSpeed) {
		super(mobEntity, world);
		this.entity = mobEntity;
		this.timeOutSpeed = timeOutSpeed;
	}

	@Override
	public void tick() {
		BlockPos targetPos = getTargetPos();
		if (NavigationConditions.isSolidAt(entity, entity.getBlockPos()) && entity.getSteppingBlockState().isFullCube(entity.getWorld(), entity.getSteppingPos())) {
			entity.getJumpControl().setActive();
		}
		if (isIdle() || targetPos == null) {
			return;
		}
		tickCount += timeOutSpeed;
		continueFollowingPath();
		moveToOrStop(targetPos);
	}

	@Override
	protected void continueFollowingPath() {
		Vec3d currentPos = getPos();
		int index = currentPath.getCurrentNodeIndex();
		Vec3d nodePos = Vec3d.ofBottomCenter(currentPath.getNodePos(index));
		double dX = Math.abs(entity.getX() - nodePos.getX());
		double dY = nodePos.getY() - entity.getY();
		double dZ = Math.abs(entity.getZ() - nodePos.getZ());
		boolean isWithinReach = dX < nodeReachProximity && dZ < nodeReachProximity && (dY <= entity.getStepHeight() && dY > -3);
		if (isWithinReach || canJumpToNext(currentPath.getNode(index).type) && shouldJumpToNextNode(currentPos)) {
			currentPath.next();
		}
		checkTimeouts(currentPos);
	}

	private void moveToOrStop(BlockPos target) {
		nodeReachProximity = (float) Math.sqrt(180 * entity.getWidth());
		entity.getMoveControl().moveTo(target.getX(), target.getY(), target.getZ(), speed);
		if (entity.squaredDistanceTo(target.getX(), target.getY(), target.getZ()) <= nodeReachProximity) {
			entity.getNavigation().stop();
		}
	}

	private boolean shouldJumpToNextNode(Vec3d currentPos) {
		if (currentPath.getCurrentNodeIndex() + 1 < currentPath.getLength()) {
			Vec3d currentNodePosition = Vec3d.ofBottomCenter(currentPath.getCurrentNodePos());
			if (currentPos.isInRange(currentNodePosition, MathHelper.clamp(entity.getWidth(), 0, 1.5))) {
				if (canPathDirectlyThrough(currentPos, currentPath.getNodePosition(entity))) {
					return true;
				}
				Vec3d nextNodePosition = Vec3d.ofBottomCenter(currentPath.getNodePos(currentPath.getCurrentNodeIndex() + 1));
				Vec3d directionToNextNode = nextNodePosition.subtract(currentNodePosition);
				Vec3d dirFromCurrentPos = currentPos.subtract(currentNodePosition);
				return directionToNextNode.dotProduct(dirFromCurrentPos) > 0.0D;
			}
		}
		return false;
	}
}