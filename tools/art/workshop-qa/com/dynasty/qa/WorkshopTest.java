package com.dynasty.qa;
import com.dynasty.DynastyBlocks;
import com.dynasty.DynastyItems;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty") @PrefixGameTestTemplate(false)
public class WorkshopTest {
 @GameTest(templateNamespace="dynasty",template="bow_ritual_test",timeoutTicks=100)
 public static void geometry(GameTestHelper h) {
  String[] ids={"marrow_vat","essence_condenser","jade_mending_forge","vitality_shrine","hide_stretcher","herbal_basin","lapidary_bench","ember_brazier"};
  for(String id:ids) {
   var block=net.minecraftforge.registries.ForgeRegistries.BLOCKS.getValue(new net.minecraft.resources.ResourceLocation("dynasty",id));
   var pos=h.absolutePos(new BlockPos(1,2,1));
   com.google.gson.JsonArray elements;
   try(var stream=WorkshopTest.class.getResourceAsStream("/assets/dynasty/models/block/"+id+".json")) {
    elements=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(stream,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject().getAsJsonArray("elements");
   } catch(Exception e) {throw new AssertionError("Missing model for "+id,e);}
   for(var facing:new Direction[]{Direction.NORTH,Direction.EAST,Direction.SOUTH,Direction.WEST}) {
    var state=block.defaultBlockState().setValue(net.minecraft.world.level.block.state.properties.BlockStateProperties.HORIZONTAL_FACING,facing);
    var shape=state.getCollisionShape(h.getLevel(),pos);var aabbs=shape.toAabbs();
    h.assertTrue(!state.canOcclude(),id+" must not occlude as a full cube");
    h.assertTrue(shape.bounds().minX>=0&&shape.bounds().maxX<=1&&shape.bounds().maxY<=1,id+" bounds");
    int filled=0;
    for(int x=0;x<16;x++) for(int y=0;y<16;y++) for(int z=0;z<16;z++) {
     double px=x+.5,py=y+.5,pz=z+.5;
     double nx=px,nz=pz;
     switch(facing){case EAST -> {nx=pz;nz=16-px;} case SOUTH -> {nx=16-px;nz=16-pz;} case WEST -> {nx=16-pz;nz=px;} default -> {}}
     boolean model=false;
     for(var element:elements) {
      var a=element.getAsJsonObject().getAsJsonArray("from");var b=element.getAsJsonObject().getAsJsonArray("to");
      if(nx>=a.get(0).getAsDouble()&&nx<b.get(0).getAsDouble()&&py>=a.get(1).getAsDouble()&&py<b.get(1).getAsDouble()&&nz>=a.get(2).getAsDouble()&&nz<b.get(2).getAsDouble())model=true;
     }
     boolean solid=false;
     for(var box:aabbs)if(box.contains(px/16,py/16,pz/16))solid=true;
     h.assertTrue(model==solid,id+" facing "+facing+" visual/collision mismatch at "+x+","+y+","+z);
     if(solid)filled++;
    }
    h.assertTrue(filled<3000,id+" must not be a full cube");
    h.assertTrue(!net.minecraft.world.phys.shapes.Shapes.joinIsNotEmpty(shape,state.getShape(h.getLevel(),pos),net.minecraft.world.phys.shapes.BooleanOp.NOT_SAME),id+" selection and collision agree");
   }
  }
  var pos=h.absolutePos(new BlockPos(1,2,1));
  for(var block:java.util.List.of(DynastyBlocks.MARROW_VAT.get(),DynastyBlocks.HERBAL_BASIN.get(),DynastyBlocks.EMBER_BRAZIER.get())) {
   h.assertTrue(block.defaultBlockState().getCollisionShape(h.getLevel(),pos).toAabbs().stream().noneMatch(b->b.contains(.5,.7,.5)),"Open basin must have no invisible lid");
  }
  System.out.println("WORKSHOP V9 QA: 8 models x 4 orientations x 4096 voxel occupancy matches; hollow basin centers PASS");h.succeed();
 }
 @GameTest(templateNamespace="dynasty",template="bow_ritual_test",timeoutTicks=100)
 public static void new_workstations(GameTestHelper h) {
  var p=h.makeMockPlayer();var pos=h.absolutePos(new BlockPos(1,2,1));var level=h.getLevel();
  var hit=new BlockHitResult(Vec3.atCenterOf(pos),Direction.UP,pos,false);
  var rack=DynastyBlocks.HIDE_STRETCHER.get();level.setBlock(pos,rack.defaultBlockState(),3);
  p.getInventory().clearContent();p.getInventory().add(new ItemStack(Items.ROTTEN_FLESH,8));
  rack.use(rack.defaultBlockState(),level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(p.getInventory().countItem(Items.ROTTEN_FLESH)==8,"Missing bone meal must not consume flesh");
  p.getInventory().add(new ItemStack(Items.BONE_MEAL,2));
  rack.use(rack.defaultBlockState(),level,pos,p,InteractionHand.OFF_HAND,hit);
  h.assertTrue(p.getInventory().countItem(Items.LEATHER)==0,"Offhand must not transact");
  p.setShiftKeyDown(true);rack.use(rack.defaultBlockState(),level,pos,p,InteractionHand.MAIN_HAND,hit);p.setShiftKeyDown(false);
  h.assertTrue(p.getInventory().countItem(Items.ROTTEN_FLESH)==8,"Help must not consume ingredients");
  rack.use(rack.defaultBlockState(),level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(p.getInventory().countItem(Items.LEATHER)==2&&p.getInventory().countItem(Items.ROTTEN_FLESH)==0&&p.getInventory().countItem(Items.BONE_MEAL)==0,"Hide exact conversion");
  h.assertTrue(level.getBlockState(pos).getValue(net.minecraft.world.level.block.state.properties.BlockStateProperties.LIT),"Successful use sets LIT");
  p.getInventory().add(new ItemStack(Items.ROTTEN_FLESH,8));p.getInventory().add(new ItemStack(Items.BONE_MEAL,2));
  level.setBlock(pos,rack.defaultBlockState(),3);rack.use(rack.defaultBlockState(),level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(p.getInventory().countItem(Items.ROTTEN_FLESH)==8,"Replacing workstation cannot bypass cooldown");
  var bench=DynastyBlocks.LAPIDARY_BENCH.get();level.setBlock(pos,bench.defaultBlockState(),3);p.getInventory().clearContent();
  p.getInventory().add(new ItemStack(Items.AMETHYST_SHARD,4));bench.use(bench.defaultBlockState(),level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(p.getInventory().countItem(Items.AMETHYST_SHARD)==4,"Missing quartz atomicity");
  p.getInventory().add(new ItemStack(Items.QUARTZ,4));bench.use(bench.defaultBlockState(),level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(p.getInventory().countItem(DynastyItems.JADE.get())==1&&p.getInventory().countItem(Items.AMETHYST_SHARD)==0&&p.getInventory().countItem(Items.QUARTZ)==0,"Jade exact conversion");
  var basin=DynastyBlocks.HERBAL_BASIN.get();level.setBlock(pos,basin.defaultBlockState(),3);p.getInventory().clearContent();
  p.getInventory().add(new ItemStack(Items.WHEAT,4));p.getInventory().add(new ItemStack(Items.SUGAR,2));p.getInventory().add(new ItemStack(Items.KELP,2));p.setHealth(p.getMaxHealth());
  basin.use(basin.defaultBlockState(),level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(p.getInventory().countItem(Items.WHEAT)==4,"Healthy herbal use costs nothing");
  p.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.POISON,200));
  basin.use(basin.defaultBlockState(),level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(!p.hasEffect(net.minecraft.world.effect.MobEffects.POISON)&&p.getEffect(net.minecraft.world.effect.MobEffects.REGENERATION).getDuration()==100,"Herbal cure and duration");
  h.assertTrue(p.getInventory().countItem(Items.WHEAT)==0&&p.getInventory().countItem(Items.SUGAR)==0&&p.getInventory().countItem(Items.KELP)==0,"Herbal exact cost");
  var fire=DynastyBlocks.EMBER_BRAZIER.get();level.setBlock(pos,fire.defaultBlockState(),3);p.getInventory().clearContent();
  p.getInventory().add(new ItemStack(Items.CHARCOAL,2));fire.use(fire.defaultBlockState(),level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(p.getInventory().countItem(Items.CHARCOAL)==2,"Missing blaze powder atomicity");
  p.getInventory().add(new ItemStack(Items.BLAZE_POWDER,1));fire.use(fire.defaultBlockState(),level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(p.getEffect(net.minecraft.world.effect.MobEffects.FIRE_RESISTANCE).getDuration()==2400,"Fire resistance 120 seconds");
  h.assertTrue(p.getInventory().countItem(Items.CHARCOAL)==0&&p.getInventory().countItem(Items.BLAZE_POWDER)==0,"Fire exact cost");
  long now=level.getServer().overworld().getGameTime();
  h.assertTrue(p.getPersistentData().getLong("dynasty_workshop_ember")==now+600,"Fire personal cooldown 30s");
  h.assertTrue(p.getPersistentData().getLong("dynasty_workshop_herbal")==now+600,"Herbal personal cooldown 30s");
  h.runAfterDelay(45,()->{h.assertTrue(!level.getBlockState(pos).getValue(net.minecraft.world.level.block.state.properties.BlockStateProperties.LIT),"Working light resets");System.out.println("WORKSHOP V9 QA: 4 new recipes/interactions, no-cost failures, help/offhand, cooldown, statuses, light reset PASS");h.succeed();});
 }
 @GameTest(templateNamespace="dynasty",template="bow_ritual_test",timeoutTicks=100)
 public static void transactions(GameTestHelper h) {
  var p=h.makeMockPlayer();var pos=h.absolutePos(new BlockPos(1,2,1));var level=h.getLevel();
  var vat=DynastyBlocks.MARROW_VAT.get();var state=vat.defaultBlockState();level.setBlock(pos,state,3);
  var hit=new BlockHitResult(Vec3.atCenterOf(pos),Direction.UP,pos,false);
  p.getInventory().clearContent();p.getInventory().add(new ItemStack(Items.ROTTEN_FLESH,7));
  vat.use(state,level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(p.getInventory().countItem(Items.ROTTEN_FLESH)==7,"Missing-input transaction must not consume");
  p.getInventory().add(new ItemStack(Items.ROTTEN_FLESH,1));vat.use(state,level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(p.getInventory().countItem(Items.ROTTEN_FLESH)==0&&p.getInventory().countItem(Items.BONE_MEAL)==4,"Exact marrow conversion");
  p.getInventory().add(new ItemStack(Items.ROTTEN_FLESH,8));vat.use(state,level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(p.getInventory().countItem(Items.ROTTEN_FLESH)==8,"Cooldown must prevent a duplicate transaction");
  var condenser=DynastyBlocks.ESSENCE_CONDENSER.get();level.setBlock(pos,condenser.defaultBlockState(),3);
  p.getInventory().add(new ItemStack(Items.AMETHYST_SHARD,4));condenser.use(condenser.defaultBlockState(),level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(p.getInventory().countItem(Items.EXPERIENCE_BOTTLE)==1&&p.getInventory().countItem(Items.BONE_MEAL)==0,"Essence output and both costs");
  var forge=DynastyBlocks.JADE_MENDING_FORGE.get();level.setBlock(pos,forge.defaultBlockState(),3);
  p.getInventory().clearContent();var sword=new ItemStack(Items.DIAMOND_SWORD);sword.setDamageValue(1000);sword.getOrCreateTag().putInt("DynastyRefine",17);
  sword.enchant(net.minecraft.world.item.enchantment.Enchantments.SHARPNESS,3);var before=sword.getTag().copy();
  p.setItemInHand(InteractionHand.MAIN_HAND,sword);p.getInventory().add(new ItemStack(DynastyItems.JADE.get(),2));
  forge.use(forge.defaultBlockState(),level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(sword.getDamageValue()==1000&&p.getInventory().countItem(DynastyItems.JADE.get())==2,"Partial cost must not consume jade");
  p.getInventory().add(new ItemStack(Items.IRON_INGOT,4));forge.use(forge.defaultBlockState(),level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(sword.getDamageValue()==1000-sword.getMaxDamage()/4,"Repair exactly 25 percent");
  var after=sword.getTag().copy();before.remove("Damage");after.remove("Damage");h.assertTrue(before.equals(after),"Preserve all non-durability NBT");
  var shrine=DynastyBlocks.VITALITY_SHRINE.get();level.setBlock(pos,shrine.defaultBlockState(),3);
  p.getInventory().clearContent();p.getInventory().add(new ItemStack(Items.HONEY_BOTTLE));p.setHealth(p.getMaxHealth());
  shrine.use(shrine.defaultBlockState(),level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(p.getInventory().countItem(Items.HONEY_BOTTLE)==1,"Full health costs nothing");
  p.setHealth(8);shrine.use(shrine.defaultBlockState(),level,pos,p,InteractionHand.MAIN_HAND,hit);
  h.assertTrue(p.getHealth()==14&&p.getInventory().countItem(Items.GLASS_BOTTLE)==1,"Heal and bottle refund");
  System.out.println("WORKSHOP QA: missing inputs, outputs, cooldown, full health, repair NBT PASS");h.succeed();
 }
}
