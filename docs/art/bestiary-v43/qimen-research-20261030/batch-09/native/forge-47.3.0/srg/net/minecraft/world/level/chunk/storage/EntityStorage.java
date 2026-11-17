package net.minecraft.world.level.chunk.storage;

import com.google.common.collect.ImmutableList;
import com.mojang.datafixers.DataFixer;
import com.mojang.logging.LogUtils;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import it.unimi.dsi.fastutil.longs.LongSet;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.IntArrayTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.datafix.DataFixTypes;
import net.minecraft.util.thread.ProcessorMailbox;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.entity.ChunkEntities;
import net.minecraft.world.level.entity.EntityPersistentStorage;
import org.slf4j.Logger;

public class EntityStorage implements EntityPersistentStorage<Entity> {
   private static final Logger f_156535_ = LogUtils.getLogger();
   private static final String f_156536_ = "Entities";
   private static final String f_156537_ = "Position";
   private final ServerLevel f_156538_;
   private final IOWorker f_156539_;
   private final LongSet f_156540_ = new LongOpenHashSet();
   private final ProcessorMailbox<Runnable> f_182485_;
   protected final DataFixer f_156534_;

   public EntityStorage(ServerLevel p_196924_, Path p_196925_, DataFixer p_196926_, boolean p_196927_, Executor p_196928_) {
      this.f_156538_ = p_196924_;
      this.f_156534_ = p_196926_;
      this.f_182485_ = ProcessorMailbox.m_18751_(p_196928_, "entity-deserializer");
      this.f_156539_ = new IOWorker(p_196925_, p_196927_, "entities");
   }

   public CompletableFuture<ChunkEntities<Entity>> m_141930_(ChunkPos p_156551_) {
      return this.f_156540_.contains(p_156551_.m_45588_()) ? CompletableFuture.completedFuture(m_156568_(p_156551_)) : this.f_156539_.m_156587_(p_156551_).thenApplyAsync((p_223458_) -> {
         if (p_223458_.isEmpty()) {
            this.f_156540_.add(p_156551_.m_45588_());
            return m_156568_(p_156551_);
         } else {
            try {
               ChunkPos chunkpos = m_156570_(p_223458_.get());
               if (!Objects.equals(p_156551_, chunkpos)) {
                  f_156535_.error("Chunk file at {} is in the wrong location. (Expected {}, got {})", p_156551_, p_156551_, chunkpos);
               }
            } catch (Exception exception) {
               f_156535_.warn("Failed to parse chunk {} position info", p_156551_, exception);
            }

            CompoundTag compoundtag = this.m_156572_(p_223458_.get());
            ListTag listtag = compoundtag.m_128437_("Entities", 10);
            List<Entity> list = EntityType.m_147045_(listtag, this.f_156538_).collect(ImmutableList.toImmutableList());
            return new ChunkEntities<>(p_156551_, list);
         }
      }, this.f_182485_::m_6937_);
   }

   private static ChunkPos m_156570_(CompoundTag p_156571_) {
      int[] aint = p_156571_.m_128465_("Position");
      return new ChunkPos(aint[0], aint[1]);
   }

   private static void m_156562_(CompoundTag p_156563_, ChunkPos p_156564_) {
      p_156563_.m_128365_("Position", new IntArrayTag(new int[]{p_156564_.f_45578_, p_156564_.f_45579_}));
   }

   private static ChunkEntities<Entity> m_156568_(ChunkPos p_156569_) {
      return new ChunkEntities<>(p_156569_, ImmutableList.of());
   }

   public void m_141971_(ChunkEntities<Entity> p_156559_) {
      ChunkPos chunkpos = p_156559_.m_156791_();
      if (p_156559_.m_156793_()) {
         if (this.f_156540_.add(chunkpos.m_45588_())) {
            this.f_156539_.m_63538_(chunkpos, (CompoundTag)null);
         }

      } else {
         ListTag listtag = new ListTag();
         p_156559_.m_156792_().forEach((p_156567_) -> {
            CompoundTag compoundtag1 = new CompoundTag();
            try {
            if (p_156567_.m_20223_(compoundtag1)) {
               listtag.add(compoundtag1);
            }
            } catch (Exception e) {
               f_156535_.error("An Entity type {} has thrown an exception trying to write state. It will not persist. Report this to the mod author", p_156567_.m_6095_(), e);
            }

         });
         CompoundTag compoundtag = NbtUtils.m_264171_(new CompoundTag());
         compoundtag.m_128365_("Entities", listtag);
         m_156562_(compoundtag, chunkpos);
         this.f_156539_.m_63538_(chunkpos, compoundtag).exceptionally((p_156554_) -> {
            f_156535_.error("Failed to store chunk {}", chunkpos, p_156554_);
            return null;
         });
         this.f_156540_.remove(chunkpos.m_45588_());
      }
   }

   public void m_182219_(boolean p_182487_) {
      this.f_156539_.m_182498_(p_182487_).join();
      this.f_182485_.m_182329_();
   }

   private CompoundTag m_156572_(CompoundTag p_156573_) {
      int i = NbtUtils.m_264487_(p_156573_, -1);
      return DataFixTypes.ENTITY_CHUNK.m_264218_(this.f_156534_, p_156573_, i);
   }

   public void close() throws IOException {
      this.f_156539_.close();
   }
}
