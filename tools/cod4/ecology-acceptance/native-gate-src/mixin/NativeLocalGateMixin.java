package com.dynasty.ecologyqa.mixin;
import com.dynasty.ecologyqa.NativeCreatureGateObserver;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.NaturalSpawner;
import net.minecraft.world.level.LocalMobCapCalculator;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.entity.MobCategory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
@Mixin(LocalMobCapCalculator.class)
public abstract class NativeLocalGateMixin {
        @Inject(method="m_186504_(Lnet/minecraft/world/entity/MobCategory;Lnet/minecraft/world/level/ChunkPos;)Z",at=@At("RETURN"),remap=false)
        private void observeLocal(MobCategory category,ChunkPos chunk,CallbackInfoReturnable<Boolean> ci){NativeCreatureGateObserver.local(this,category,chunk,ci.getReturnValueZ());}
    }
