package com.dynasty.cod3;

import com.dynasty.DynastyWeapons;
import com.dynasty.client.ImperialRenderState;
import com.dynasty.entity.DynastyEntities;
import com.mojang.authlib.GameProfile;
import com.mojang.blaze3d.pipeline.*;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.texture.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.*;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.*;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.level.block.state.properties.DoubleBlockHalf;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.phys.*;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import org.lwjgl.opengl.GL11;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Actual registered block models and transactions in one isolated integrated Forge client. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class RemainsQa {
    private static final Path OUT=Path.of(System.getProperty("dynasty.cod3RemainsQa.output","build/cod3-remains-unset"));
    private static final List<String> RESULTS=Collections.synchronizedList(new ArrayList<>());
    private static boolean started,done,views;
    private static int ticks;
    private static CompletableFuture<Void> checks,reload;
    private static final long DEADLINE=System.nanoTime()+300_000_000_000L;
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
        if(!Boolean.getBoolean("dynasty.cod3RemainsQa")||done||e.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            Files.createDirectories(OUT);
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Single remains client timeout");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                started=true;var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("cod3-remains",new LevelSettings("Disposable remains QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(311,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;
            if(mc.screen!=null)mc.setScreen(null);
            if(checks==null){checks=mc.getSingleplayerServer().submit(()->server(mc.getSingleplayerServer().overworld()));return;}
            if(!checks.isDone())return;checks.join();
            if(!views){views=true;modelChecks(mc);for(int angle:new int[]{180,135,90,0}){frame("statue-"+angle,angle,false,true);frame("coffer-"+angle,angle,false,false);}frame("statue-silhouette",180,true,true);frame("coffer-silhouette",180,true,false);frame("statue-empty",180,false,true,false);reload=mc.reloadResourcePacks();return;}
            if(!reload.isDone())return;reload.join();
            if(++ticks<30)return;
            modelChecks(mc);frame("statue-after-reload",180,false,true);
            mc.options.hideGui=true;mc.options.fov().set(45);
            mc.player.setPos(0.5,-59.8,-4.5);mc.player.setYRot(0);mc.player.setXRot(7);
            if(ticks<60)return;
            try(var shot=Screenshot.takeScreenshot(mc.getMainRenderTarget())){shot.writeToFile(OUT.resolve("world.png"));}
            RESULTS.add("PASS actual world blockstates after resource reload; one integrated client, not two network peers");
            Files.write(OUT.resolve("PASS.txt"),RESULTS);done=true;mc.stop();
        }catch(Throwable t){t.printStackTrace();try{Files.writeString(OUT.resolve("FAIL.txt"),t.toString());}catch(Exception ignored){}done=true;mc.stop();}
    }
    private static void require(boolean test,String message){if(!test)throw new AssertionError(message);RESULTS.add("PASS "+message);}
    private static FakePlayer player(ServerLevel l,BlockPos p,String name){var result=new FakePlayer(l,new GameProfile(UUID.randomUUID(),name));result.setPos(Vec3.atCenterOf(p));return result;}
    private static int count(FakePlayer p,Item item){return p.getInventory().items.stream().filter(s->s.is(item)).mapToInt(ItemStack::getCount).sum();}
    private static List<ItemStack> drops(){var sword=new ItemStack(DynastyWeapons.YITIAN_SWORD.get());sword.setDamageValue(7);sword.getOrCreateTag().putString("QaReceipt","existing-drop");return List.of(sword,new ItemStack(Items.DIAMOND,3));}
    private static RebelStatueBlock.Statue statue(ServerLevel l,BlockPos p){return (RebelStatueBlock.Statue)l.getBlockEntity(p);}
    private static void server(ServerLevel l){
        l.setDayTime(6000);for(var p:BlockPos.betweenClosed(new BlockPos(-16,-61,-16),new BlockPos(16,-61,16)))l.setBlockAndUpdate(p,Blocks.STONE.defaultBlockState());
        int x=-12;
        for(Direction facing:Direction.Plane.HORIZONTAL){
            var p=new BlockPos(x,-60,6);x+=3;
            require(RebelStatueBlock.place(l,p,facing,drops(),UUID.randomUUID()),"two-block placement "+facing);
            require(l.getBlockState(p).getValue(RebelStatueBlock.FACING)==facing&&l.getBlockState(p.above()).getValue(RebelStatueBlock.FACING)==facing,"matching facing "+facing);
            require(l.getBlockEntity(p.above())==null&&statue(l,p).getContainerSize()==54,"one authoritative inventory "+facing);
            var restored=BlockEntity.loadStatic(p,l.getBlockState(p),statue(l,p).saveWithFullMetadata());
            require(restored instanceof RebelStatueBlock.Statue s&&s.getItem(0).getDamageValue()==7&&s.getItem(0).getTag().getString("QaReceipt").equals("existing-drop")&&s.saveWithoutMetadata().hasUUID("Boss"),"registered NBT restore preserves captured sword and boss "+facing);
        }
        var p=new BlockPos(0,-60,0);require(RebelStatueBlock.place(l,p,Direction.NORTH,drops(),UUID.randomUUID()),"front-view fixture");
        var s=statue(l,p);var a=player(l,p,"PullA");var b=player(l,p,"PullB");
        for(int i=0;i<36;i++)a.getInventory().setItem(i,new ItemStack(Items.DIRT,64));
        require(!s.pullSword(a)&&s.swordSlot()==0&&l.getBlockState(p).getValue(RebelStatueBlock.WEAPON),"full inventory restores sword without loss");
        a.getInventory().setItem(0,ItemStack.EMPTY);
        var hit=new BlockHitResult(Vec3.atCenterOf(p.above()),Direction.NORTH,p.above(),false);
        l.getBlockState(p.above()).use(l,a,InteractionHand.MAIN_HAND,hit);
        require(count(a,DynastyWeapons.YITIAN_SWORD.get())==1&&!s.pullSword(b)&&count(b,DynastyWeapons.YITIAN_SWORD.get())==0,"upper-half click and two claimants issue one captured sword");
        require(!l.getBlockState(p).getValue(RebelStatueBlock.WEAPON)&&!l.getBlockState(p.above()).getValue(RebelStatueBlock.WEAPON),"both weapon states clear after withdrawal");
        var saved=s.saveWithoutMetadata();s.load(saved);s.onLoad();
        require(s.swordSlot()<0&&!s.pullSword(b)&&s.getItem(1).getCount()==3,"reload never recreates extracted weapon or other loot");
        var menu=s.createMenu(1,b.getInventory(),b);require(menu!=null&&menu.stillValid(b)&&menu.getSlot(1).getItem().getCount()==3,"memorial exposes existing 54-slot loot menu");
        menu.quickMoveStack(b,1);require(count(b,Items.DIAMOND)==3&&s.getItem(1).isEmpty(),"shift-click collects remaining original loot");
        // Refill only this disposable fixture so world and views show the armed memorial.
        s.setItem(0,drops().get(0));
        var taken=s.removeItemNoUpdate(0);require(!l.getBlockState(p).getValue(RebelStatueBlock.WEAPON),"menu extraction without inventory callback still clears visual sword");s.setItem(0,taken);
        for(boolean upper:List.of(false,true)){
            var at=new BlockPos(upper?8:5,-60,0);RebelStatueBlock.place(l,at,Direction.SOUTH,drops(),UUID.randomUUID());
            l.destroyBlock(upper?at.above():at,true);
            require(l.isEmptyBlock(at)&&l.isEmptyBlock(at.above()),"breaking "+(upper?"upper":"lower")+" clears both halves");
            int swords=l.getEntitiesOfClass(ItemEntity.class,new AABB(at).inflate(1),entity->entity.getItem().is(DynastyWeapons.YITIAN_SWORD.get())).stream().mapToInt(entity->entity.getItem().getCount()).sum();
            require(swords==1,"breaking "+(upper?"upper":"lower")+" drops weapon once");
            int blocks=l.getEntitiesOfClass(ItemEntity.class,new AABB(at).inflate(1),entity->entity.getItem().is(RebelStatueBlock.ITEM.get())).stream().mapToInt(entity->entity.getItem().getCount()).sum();
            require(blocks==1,"breaking "+(upper?"upper":"lower")+" returns one decorative block");
        }
        var blocked=new BlockPos(11,-60,0);l.setBlockAndUpdate(blocked.above(),Blocks.STONE.defaultBlockState());
        require(!RebelStatueBlock.place(l,blocked,Direction.NORTH,drops(),UUID.randomUUID())&&l.isEmptyBlock(blocked)&&l.getBlockState(blocked.above()).is(Blocks.STONE),"occupied upper block is never overwritten");
        var placement=new BlockPos(14,-60,7);var builder=player(l,placement.offset(0,0,-3),"StatueBuilder");
        var context=new net.minecraft.world.item.context.BlockPlaceContext(builder,InteractionHand.MAIN_HAND,new ItemStack(RebelStatueBlock.ITEM.get()),new BlockHitResult(Vec3.atCenterOf(placement.below()).add(0,.5,0),Direction.UP,placement.below(),false));
        require(((BlockItem)RebelStatueBlock.ITEM.get()).place(context).consumesAction()&&l.getBlockState(placement).is(RebelStatueBlock.BLOCK.get())&&l.getBlockState(placement.above()).getValue(RebelStatueBlock.HALF)==DoubleBlockHalf.UPPER&&!l.getBlockState(placement).getValue(RebelStatueBlock.WEAPON),"actual BlockItem placement creates two empty halves without minting a sword");
        var storage=l.getDataStorage();var original=BossDeathState.get(l);
        try{
            storage.set("dynasty_cod3_deaths",new BossDeathState());
            var boss=DynastyEntities.REBEL_GENERAL.get().create(l);boss.setNoAi(true);boss.moveTo(-8.5,-60,-7.5,90,0);l.addFreshEntity(boss);boss.setHealth(0);boss.die(boss.damageSources().genericKill());
            var journal=BossDeathState.get(l).save(new CompoundTag());var entry=journal.getList("Entries",10).getCompound(0);var captured=new ListTag();for(var drop:drops())captured.add(drop.save(new CompoundTag()));entry.put("Loot",captured);entry.putInt("XP",0);
            storage.set("dynasty_cod3_deaths",BossDeathState.load(journal));BossDeathState.settle(l);
            var near=new AABB(boss.blockPosition().offset(-3,0,-3),boss.blockPosition().offset(3,4,3));int memorials=0;
            for(var at:BlockPos.betweenClosed(boss.blockPosition().offset(-2,0,-2),boss.blockPosition().offset(2,3,2)))if(l.getBlockEntity(at) instanceof RebelStatueBlock.Statue)memorials++;
            require(boss.isRemoved()&&memorials==1,"death restart places permanent memorial before corpse removal");
            var settled=BossDeathState.get(l).save(new CompoundTag());var receipt=settled.getList("Entries",10).getCompound(0);
            require(receipt.getBoolean("RewardGranted")&&receipt.getBoolean("LootPlaced")&&receipt.getBoolean("Cleaned"),"death rewards and cleanup retain existing receipts");
            storage.set("dynasty_cod3_deaths",BossDeathState.load(settled));BossDeathState.settle(l);
            int again=0;for(var at:BlockPos.betweenClosed(boss.blockPosition().offset(-2,0,-2),boss.blockPosition().offset(2,3,2)))if(l.getBlockEntity(at) instanceof RebelStatueBlock.Statue)again++;
            require(again==1&&l.getEntitiesOfClass(ItemEntity.class,near,e->e.getItem().is(DynastyWeapons.YITIAN_SWORD.get())).isEmpty(),"repeat restart creates neither extra statue nor loose sword");
            var stale=DynastyEntities.REBEL_GENERAL.get().create(l);stale.setUUID(boss.getUUID());var join=new net.minecraftforge.event.entity.EntityJoinLevelEvent(stale,l);BossDeathState.join(join);require(join.isCanceled(),"completed journal rejects stale corpse");
            var low=new BlockPos(-6,-60,12);
            for(var ceiling:BlockPos.betweenClosed(low.offset(-2,1,-2),low.offset(2,3,2)))l.setBlockAndUpdate(ceiling,Blocks.STONE.defaultBlockState());
            var legacy=new CompoundTag();legacy.putUUID("Boss",UUID.randomUUID());legacy.putString("Type","dynasty:rebel_general");legacy.putLong("Position",low.asLong());legacy.put("Loot",captured.copy());
            var entries=new ListTag();entries.add(legacy);var legacySave=new CompoundTag();legacySave.put("Entries",entries);storage.set("dynasty_cod3_deaths",BossDeathState.load(legacySave));BossDeathState.settle(l);
            int boxes=0;for(var at:BlockPos.betweenClosed(low.offset(-2,0,-2),low.offset(2,3,2)))if(l.getBlockEntity(at) instanceof LootableRemains.Remains r&&!(r instanceof RebelStatueBlock.Statue)&&r.getItem(0).is(DynastyWeapons.YITIAN_SWORD.get()))boxes++;
            require(boxes==1&&l.getBlockState(low.above()).is(Blocks.STONE),"legacy death under low ceiling settles in one coffer without overwriting terrain");
        }finally{storage.set("dynasty_cod3_deaths",original);}
        l.setBlockAndUpdate(new BlockPos(-2,-60,0),LootableRemains.BLOCK.get().defaultBlockState());
        l.setBlockAndUpdate(new BlockPos(2,-60,0),Blocks.WHITE_WOOL.defaultBlockState());
        l.setBlockAndUpdate(new BlockPos(2,-59,0),Blocks.GRAY_WOOL.defaultBlockState());
    }
    private static void modelChecks(Minecraft mc){
        for(var state:RebelStatueBlock.BLOCK.get().getStateDefinition().getPossibleStates())require(mc.getBlockRenderer().getBlockModel(state)!=mc.getModelManager().getMissingModel(),"baked registered state "+state);
        var atlas=mc.getModelManager().getAtlas(TextureAtlas.LOCATION_BLOCKS);
        for(String name:List.of("rebel_general_statue","lootable_remains"))require(!atlas.getSprite(new net.minecraft.resources.ResourceLocation("dynasty","block/"+name)).contents().name().equals(MissingTextureAtlasSprite.getLocation()),"loaded exact 16px texture "+name);
    }
    private static void frame(String name,int angle,boolean black,boolean memorial)throws Exception{frame(name,angle,black,memorial,true);}
    private static void frame(String name,int angle,boolean black,boolean memorial,boolean armed)throws Exception{
        var mc=Minecraft.getInstance();var projection=new Matrix4f(RenderSystem.getProjectionMatrix());var sorting=RenderSystem.getVertexSorting();
        float fs=RenderSystem.getShaderFogStart(),fe=RenderSystem.getShaderFogEnd();var target=new TextureTarget(600,600,true,Minecraft.ON_OSX);var view=RenderSystem.getModelViewStack();view.pushPose();
        try(ImperialRenderState restore=new ImperialRenderState()){
            target.setClearColor(.72f,.76f,.8f,1);target.clear(Minecraft.ON_OSX);target.bindWrite(true);view.setIdentity();
            view.mulPoseMatrix(new Matrix4f().lookAt(0,.8f,3.8f,0,.8f,0,0,1,0));RenderSystem.applyModelViewMatrix();
            RenderSystem.setProjectionMatrix(new Matrix4f().perspective(.57f,1,.05f,256),VertexSorting.DISTANCE_TO_ORIGIN);RenderSystem.setShaderFogStart(1000);RenderSystem.setShaderFogEnd(2000);RenderSystem.enableDepthTest();RenderSystem.depthMask(true);RenderSystem.disableBlend();RenderSystem.disableCull();RenderSystem.setShaderColor(1,1,1,1);
            var pose=new PoseStack();pose.mulPose(com.mojang.math.Axis.YP.rotationDegrees(angle));pose.translate(-.5,0,-.5);
            var buffers=mc.renderBuffers().bufferSource();var type=RenderType.entityCutoutNoCull(TextureAtlas.LOCATION_BLOCKS);VertexConsumer consumer=buffers.getBuffer(type);if(black)consumer=new Black(consumer);
            if(memorial){var state=RebelStatueBlock.BLOCK.get().defaultBlockState().setValue(RebelStatueBlock.WEAPON,armed);draw(mc,pose,consumer,state,type);pose.translate(0,1,0);draw(mc,pose,consumer,state.setValue(RebelStatueBlock.HALF,DoubleBlockHalf.UPPER),type);}
            else draw(mc,pose,consumer,LootableRemains.BLOCK.get().defaultBlockState(),type);
            buffers.endBatch();GL11.glFinish();require(GL11.glGetError()==GL11.GL_NO_ERROR,"GL state "+name);
            try(var shot=Screenshot.takeScreenshot(target)){shot.writeToFile(OUT.resolve(name+".png"));}
        }finally{view.popPose();RenderSystem.applyModelViewMatrix();RenderSystem.setProjectionMatrix(projection,sorting);RenderSystem.setShaderFogStart(fs);RenderSystem.setShaderFogEnd(fe);target.destroyBuffers();mc.getMainRenderTarget().bindWrite(true);}
    }
    private static void draw(Minecraft mc,PoseStack pose,VertexConsumer consumer,BlockState state,RenderType type){mc.getBlockRenderer().getModelRenderer().renderModel(pose.last(),consumer,state,mc.getBlockRenderer().getBlockModel(state),1,1,1,15728880,OverlayTexture.NO_OVERLAY,net.minecraftforge.client.model.data.ModelData.EMPTY,type);}
    private record Black(VertexConsumer target) implements VertexConsumer {
        public VertexConsumer vertex(double x,double y,double z){target.vertex(x,y,z);return this;}
        public VertexConsumer color(int r,int g,int b,int a){target.color(0,0,0,255);return this;}
        public VertexConsumer uv(float u,float v){target.uv(u,v);return this;}
        public VertexConsumer overlayCoords(int u,int v){target.overlayCoords(u,v);return this;}
        public VertexConsumer uv2(int u,int v){target.uv2(u,v);return this;}
        public VertexConsumer normal(float x,float y,float z){target.normal(x,y,z);return this;}
        public void endVertex(){target.endVertex();}
        public void defaultColor(int r,int g,int b,int a){target.defaultColor(0,0,0,255);}
        public void unsetDefaultColor(){target.unsetDefaultColor();}
    }
}
