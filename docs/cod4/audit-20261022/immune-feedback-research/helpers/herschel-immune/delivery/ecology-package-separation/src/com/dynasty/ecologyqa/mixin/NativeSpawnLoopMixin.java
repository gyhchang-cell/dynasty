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
@Mixin(NaturalSpawner.class)
public abstract class NativeSpawnLoopMixin {
        @Inject(method="m_47029_(Lnet/minecraft/server/level/ServerLevel;Lnet/minecraft/world/level/chunk/LevelChunk;Lnet/minecraft/world/level/NaturalSpawner$SpawnState;ZZZ)V",at=@At("HEAD"),remap=false)
        private static void observeBegin(ServerLevel level,LevelChunk chunk,NaturalSpawner.SpawnState state,boolean friendlies,boolean enemies,boolean persistentPhase,CallbackInfo ci){NativeCreatureGateObserver.begin(level,chunk,state,friendlies,enemies,persistentPhase);}
        @Inject(method="m_47029_(Lnet/minecraft/server/level/ServerLevel;Lnet/minecraft/world/level/chunk/LevelChunk;Lnet/minecraft/world/level/NaturalSpawner$SpawnState;ZZZ)V",at=@At("RETURN"),remap=false)
        private static void observeEnd(ServerLevel level,LevelChunk chunk,NaturalSpawner.SpawnState state,boolean friendlies,boolean enemies,boolean persistentPhase,CallbackInfo ci){NativeCreatureGateObserver.end();}
    }
