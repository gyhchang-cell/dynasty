package net.minecraft.world.level.entity;

import java.io.IOException;
import java.util.concurrent.CompletableFuture;
import net.minecraft.world.level.ChunkPos;

public interface EntityPersistentStorage<T> extends AutoCloseable {
   CompletableFuture<ChunkEntities<T>> m_141930_(ChunkPos p_156824_);

   void m_141971_(ChunkEntities<T> p_156825_);

   void m_182219_(boolean p_182503_);

   default void close() throws IOException {
   }
}
