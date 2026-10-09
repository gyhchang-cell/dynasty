package com.dynasty.cod3;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.*;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.shapes.*;
import net.minecraftforge.registries.*;
import java.util.UUID;

/** Structure-local landmarks. Registration happens when the chunk loads, never on a worldgen thread. */
public final class StoryAnchor extends BaseEntityBlock {
    public static final IntegerProperty KIND=IntegerProperty.create("kind",0,44);
    public static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,Dynasty.MODID);
    public static final DeferredRegister<BlockEntityType<?>> TYPES=DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES,Dynasty.MODID);
    public static final RegistryObject<Block> BLOCK=BLOCKS.register("story_anchor",StoryAnchor::new);
    public static final RegistryObject<BlockEntityType<Anchor>> TYPE=TYPES.register("story_anchor",()->BlockEntityType.Builder.of(Anchor::new,BLOCK.get()).build(null));
    private StoryAnchor(){super(Properties.copy(Blocks.STONE).noOcclusion());registerDefaultState(stateDefinition.any().setValue(KIND,0));}
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> b){b.add(KIND);}
    @Override public RenderShape getRenderShape(BlockState s){return RenderShape.MODEL;}
    @Override public VoxelShape getShape(BlockState s,net.minecraft.world.level.BlockGetter l,BlockPos p,CollisionContext c){return s.getValue(KIND)>=30?Shapes.block():Block.box(2,0,2,14,12,14);}
    @Override public VoxelShape getCollisionShape(BlockState s,net.minecraft.world.level.BlockGetter l,BlockPos p,CollisionContext c){return getShape(s,l,p,c);}
    @Override public net.minecraft.world.InteractionResult use(BlockState state,Level level,BlockPos pos,net.minecraft.world.entity.player.Player player,net.minecraft.world.InteractionHand hand,net.minecraft.world.phys.BlockHitResult hit){
        if(player instanceof net.minecraft.server.level.ServerPlayer p&&hand==net.minecraft.world.InteractionHand.MAIN_HAND&&state.getValue(KIND)<30){
            int number=state.getValue(KIND)+1;
            if(number==1||number==26)SecretTracker.trigger(p,pos,SecretDefinition.Trigger.PLAY_INSTRUMENT);
            p.displayClientMessage(net.minecraft.network.chat.Component.translatable("cod3.dynasty.secret.clue."+number),true);
        }
        return net.minecraft.world.InteractionResult.sidedSuccess(level.isClientSide);
    }
    @Override public BlockEntity newBlockEntity(BlockPos p,BlockState s){return new Anchor(p,s);}
    public static final class Anchor extends BlockEntity {
        private boolean npcSpawned;
        public Anchor(BlockPos p,BlockState s){super(TYPE.get(),p,s);}
        @Override public void onLoad(){super.onLoad();if(!(level instanceof ServerLevel server))return;
            int kind=getBlockState().getValue(KIND);
            if(kind<30)SecretTracker.attach(server,worldPosition,kind+1);
            else if(!npcSpawned){String role=Cod3Catalog.entries("npcs").get(kind-30).getAsJsonObject().get("id").getAsString();
                var npc=NpcContent.NPCS.get(role).get().create(server);if(npc==null)return;
                npc.setUUID(UUID.nameUUIDFromBytes((server.dimension().location()+":"+worldPosition+":"+role).getBytes(java.nio.charset.StandardCharsets.UTF_8)));
                npc.moveTo(worldPosition.getX()+.5,worldPosition.getY()+1,worldPosition.getZ()+.5,0,0);npc.home(worldPosition.above());
                if(server.addFreshEntity(npc)){npcSpawned=true;setChanged();}
            }
        }
        @Override public void setRemoved(){if(level instanceof ServerLevel server&&getBlockState().getValue(KIND)<30)SecretTracker.detach(server,worldPosition);super.setRemoved();}
        @Override protected void saveAdditional(CompoundTag n){super.saveAdditional(n);n.putBoolean("NpcSpawned",npcSpawned);}
        @Override public void load(CompoundTag n){super.load(n);npcSpawned=n.getBoolean("NpcSpawned");}
    }
}
