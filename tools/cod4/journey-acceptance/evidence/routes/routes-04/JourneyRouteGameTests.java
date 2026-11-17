package com.dynasty.expansion;

import com.google.gson.*;
import com.mojang.authlib.GameProfile;
import java.nio.file.*;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.gametest.framework.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.*;
import net.minecraft.world.item.crafting.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;

/** Connected native payments and real FTB submission. QA raw materials and boundary progress are explicit. */
@GameTestHolder("dynasty_journey_routes_qa") @PrefixGameTestTemplate(false)
public final class JourneyRouteGameTests {
    static final JsonArray RESULTS = new JsonArray();
    static final JsonObject GRAPH = resource("/route-quest-graph.json");
    static final JsonObject RECIPES = resource("/route-recipes.json");
    static final Set<String> EQUIPMENT = new HashSet<>();
    static { for (var e : resource("/route-equipment.json").getAsJsonArray("items")) EQUIPMENT.add(e.getAsString()); }
    static JsonObject resource(String name) {
        try (var r = new java.io.InputStreamReader(JourneyRouteGameTests.class.getResourceAsStream(name))) {
            return JsonParser.parseReader(r).getAsJsonObject();
        } catch (Exception e) { throw new RuntimeException(e); }
    }
    static String id(ItemStack s) { return BuiltInRegistries.ITEM.getKey(s.getItem()).toString(); }
    static String q(int n) { return String.format("1000000000c400%02x", n); }
    static String main(int n) { return String.format("100000000000%04x", n); }
    static String intro(int n) { return String.format("100000000001%04x", n); }
    static String build(int n) { return String.format("100000000003%04x", n); }

    static final class Route {
        final GameTestHelper h; final ServerPlayer p; final String name;
        final JsonObject report = new JsonObject(); final JsonArray steps = new JsonArray();
        final Class<?> fileType, taskType, teamType, objectType, questType;
        final Object file, team; final Set<String> produced = new HashSet<>();
        final List<ChunkPos> forced = new ArrayList<>(); final List<Runnable> cleanup = new ArrayList<>();
        final long start;
        Route(GameTestHelper helper, String key) {
            h=helper; name=key; start=h.getLevel().getGameTime();
            p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"route-"+key));
            p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),
                new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
            p.setGameMode(GameType.SURVIVAL);p.setPos(h.absolutePos(new BlockPos(2,2,2)).getCenter());
            h.getLevel().getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING).set(false,h.getLevel().getServer());
            com.dynasty.FtbRewardGameTests.FixtureTeams.player(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedInEvent(p));
            try {
                fileType=Class.forName("dev.ftb.mods.ftbquests.quest.ServerQuestFile");
                taskType=Class.forName("dev.ftb.mods.ftbquests.quest.task.Task");
                teamType=Class.forName("dev.ftb.mods.ftbquests.quest.TeamData");
                objectType=Class.forName("dev.ftb.mods.ftbquests.quest.QuestObject");
                questType=Class.forName("dev.ftb.mods.ftbquests.quest.Quest");
                file=fileType.getField("INSTANCE").get(null);
                team=fileType.getMethod("getOrCreateTeamData",net.minecraft.world.entity.Entity.class).invoke(file,p);
                var f=GameTestHelper.class.getDeclaredField("testInfo");f.setAccessible(true);
                ((GameTestInfo)f.get(h)).addListener(new GameTestListener() {
                    public void testStructureLoaded(GameTestInfo info) {}
                    public void testPassed(GameTestInfo info) { finish(info,true); }
                    public void testFailed(GameTestInfo info) { finish(info,false); }
                    void finish(GameTestInfo info,boolean pass) {
                        report.addProperty("pass",pass);report.addProperty("status",pass?"SEGMENT_EXECUTED":"FAILED");report.addProperty("native_test",info.getTestName());
                        report.addProperty("elapsed_server_ticks",h.getLevel().getGameTime()-start);
                        report.add("final_inventory",inventory());
                        if(!pass)report.addProperty("failure",String.valueOf(info.getError()));
                        flush(); p.closeContainer();p.discard();cleanup.forEach(Runnable::run);
                        for(var chunk:forced)h.getLevel().setChunkForced(chunk.x,chunk.z,false);
                    }
                });
            } catch(Exception e) { throw new RuntimeException(e); }
            report.addProperty("case",key);report.addProperty("status","RUNNING");report.add("steps",steps);
            report.addProperty("scope","Headless detached survival ServerPlayer; native inventory/menu/FTB; QA materials/progress recorded; no natural discovery or human duration claim");
            RESULTS.add(report);flush();
        }
        void flush() {
            try { Files.writeString(Path.of(System.getProperty("dynasty.journey.routes.report")),new GsonBuilder().setPrettyPrinting().create().toJson(RESULTS)+"\n"); }
            catch(Exception e){throw new RuntimeException(e);}
        }
        JsonObject row(String kind) { var r=new JsonObject();r.addProperty("kind",kind);r.addProperty("tick",h.getLevel().getGameTime()-start);r.addProperty("sequence",steps.size());steps.add(r);return r; }
        JsonObject inventory() {
            var v=new JsonObject();for(var s:p.getInventory().items)if(!s.isEmpty())v.addProperty(id(s),(v.has(id(s))?v.get(id(s)).getAsInt():0)+s.getCount());return v;
        }
        int count(String item) { return p.getInventory().items.stream().filter(s->id(s).equals(item)).mapToInt(ItemStack::getCount).sum(); }
        void supply(String item,int n,String reason) {
            h.assertTrue(!EQUIPMENT.contains(item),"Never QA-inject a predecessor equipment stack: "+item);
            if(n<=0)return;
            var stack=new ItemStack(BuiltInRegistries.ITEM.get(new ResourceLocation(item)),n);
            h.assertTrue(!stack.isEmpty(),"Registered QA material "+item);
            h.assertTrue(p.getInventory().add(stack),"Inventory has room for declared material");
            var r=row("qa_material");r.addProperty("item",item);r.addProperty("count",n);r.addProperty("reason",reason);flush();
        }
        boolean equipment(ItemStack s) {
            return EQUIPMENT.contains(id(s)) || s.getItem() instanceof ArmorItem || s.getItem() instanceof TieredItem
                || s.getItem() instanceof BowItem || s.getItem() instanceof CrossbowItem || s.getItem() instanceof ShieldItem;
        }
        void ensure(ItemStack s,int n,String reason) {
            while(count(id(s))<n) {
                if(equipment(s)) craftFor(id(s));
                else supply(id(s),n-count(id(s)),reason);
            }
        }
        ItemStack take(String item) {
            for(int i=0;i<p.getInventory().items.size();i++)if(id(p.getInventory().items.get(i)).equals(item))return p.getInventory().removeItem(i,1);
            throw new AssertionError("No actual paid stock: "+item);
        }
        void craftFor(String item) {
            String preferred=item;
            if(!h.getLevel().getRecipeManager().byKey(new ResourceLocation(preferred)).isPresent())
                preferred=h.getLevel().getRecipeManager().getAllRecipesFor(RecipeType.CRAFTING).stream()
                    .filter(r->id(r.getResultItem(h.getLevel().registryAccess())).equals(item))
                    .map(r->r.getId().toString()).sorted().findFirst().orElseThrow(()->new AssertionError("No original crafting predecessor: "+item));
            craft(preferred);
        }
        void prepare(String recipeId) {
            var recipe=(CraftingRecipe)h.getLevel().getRecipeManager().byKey(new ResourceLocation(recipeId)).orElseThrow();
            var counts=new LinkedHashMap<String,Integer>();var samples=new HashMap<String,ItemStack>();
            for(var ing:recipe.getIngredients())if(!ing.isEmpty()) {
                var s=ing.getItems()[0];counts.merge(id(s),1,Integer::sum);samples.put(id(s),s);
            }
            counts.forEach((item,n)->ensure(samples.get(item),n,"input for "+recipeId));
        }
        void craft(String recipeId) {
            prepare(recipeId);
            var recipe=(CraftingRecipe)h.getLevel().getRecipeManager().byKey(new ResourceLocation(recipeId)).orElseThrow();
            var before=inventory();var menu=new CraftingMenu(7,p.getInventory(),ContainerLevelAccess.create(h.getLevel(),p.blockPosition()));p.containerMenu=menu;
            var paid=new JsonArray();int width=recipe instanceof ShapedRecipe shaped?shaped.getWidth():3;
            for(int i=0;i<recipe.getIngredients().size();i++) {
                var ing=recipe.getIngredients().get(i);if(ing.isEmpty())continue;
                var s=take(id(ing.getItems()[0]));var cost=new JsonObject();cost.addProperty("item",id(s));cost.addProperty("count",1);cost.addProperty("damage",s.getDamageValue());paid.add(cost);
                int slot=recipe instanceof ShapedRecipe?1+(i/width)*3+i%width:1+i;
                menu.getSlot(slot).set(s);
            }
            var grid=new TransientCraftingContainer(menu,3,3);for(int i=0;i<9;i++)grid.setItem(i,menu.getSlot(i+1).getItem().copy());
            var selected=h.getLevel().getRecipeManager().getRecipeFor(RecipeType.CRAFTING,grid,h.getLevel()).orElseThrow();
            h.assertTrue(selected.getId().equals(recipe.getId()),"Exact original recipe selected: "+recipeId+" != "+selected.getId());
            var expected=recipe.assemble(grid,h.getLevel().registryAccess());var remainder=recipe.getRemainingItems(grid);
            var out=menu.getSlot(0).remove(64);menu.getSlot(0).onTake(p,out);
            h.assertTrue(ItemStack.matches(out,expected),"Native output "+recipeId);
            for(int i=0;i<9;i++)h.assertTrue(ItemStack.matches(menu.getSlot(i+1).getItem(),remainder.get(i)),"Actual input paid/remainder preserved "+recipeId+" slot "+i);
            h.assertTrue(menu.getSlot(0).getItem().isEmpty(),"No free result replay "+recipeId);
            String result=id(out);int amount=out.getCount();h.assertTrue(p.getInventory().add(out),"Result fits carried inventory");p.closeContainer();produced.add(result);
            var r=row("native_craft");r.addProperty("recipe",recipeId);r.addProperty("output",result);r.addProperty("count",amount);r.add("paid",paid);r.add("before",before);r.add("after",inventory());flush();
        }
        Object quest(String id) throws Exception {return fileType.getMethod("getQuest",long.class).invoke(file,Long.parseLong(id,16));}
        boolean done(String id) throws Exception {return (Boolean)teamType.getMethod("isCompleted",objectType).invoke(team,quest(id));}
        void submit(String id) {
            try {
                var node=GRAPH.getAsJsonObject(id);var quest=quest(id);boolean already=done(id);
                h.assertTrue((Boolean)teamType.getMethod("areDependenciesComplete",questType).invoke(team,quest),"Actual prerequisites complete before submit "+id);
                ContentProgress.reconcile(p);
                Class.forName("dev.ftb.mods.ftbquests.util.FTBQuestsInventoryListener").getMethod("detect",ServerPlayer.class,ItemStack.class,long.class).invoke(null,p,ItemStack.EMPTY,0L);
                for(var e:node.getAsJsonArray("tasks")) {
                    var def=e.getAsJsonObject();String type=def.get("type").getAsString();
                    var task=fileType.getMethod("getTask",long.class).invoke(file,Long.parseLong(def.get("id").getAsString(),16));
                    if(!type.equals("item")) {
                        h.assertTrue((Boolean)task.getClass().getMethod("canSubmit",teamType,ServerPlayer.class).invoke(task,team,p),"Native detector sees objective "+id);
                        taskType.getMethod("submitTask",teamType,ServerPlayer.class).invoke(task,team,p);
                    }
                }
                h.assertTrue(done(id),"Actual FTB quest completes: "+id+" inventory="+inventory());
                var r=row("native_ftb_submit");r.addProperty("quest",id);r.addProperty("title",node.get("title").getAsString());r.addProperty("already_completed_by_native_detection",already);r.add("inventory",inventory());flush();
            } catch(RuntimeException|AssertionError e){throw e;} catch(Exception e){throw new RuntimeException(e);}
        }
        void prefix(String id,Set<String> keep) {
            var seen=new LinkedHashSet<String>();collect(id,seen);seen.removeAll(keep);
            try {
                var list=new JsonArray();for(String a:seen)if(!done(a)) {
                    teamType.getMethod("setCompleted",long.class,Date.class).invoke(team,Long.parseLong(a,16),new Date());list.add(a);
                }
                teamType.getMethod("clearCachedProgress").invoke(team);
                var r=row("qa_boundary_progress");r.addProperty("target",id);r.add("completed_quest_ids",list);r.addProperty("reason","External story/discovery or previous-stage history; NOT native achievement in this segment");flush();
            }catch(Exception e){throw new RuntimeException(e);}
        }
        void collect(String id,Set<String> seen) {for(var e:GRAPH.getAsJsonObject(id).getAsJsonArray("dependencies")){String a=e.getAsString();if(seen.add(a))collect(a,seen);}}
        void smith(String recipeId) {
            var json=RECIPES.getAsJsonObject(recipeId);var slots=new String[]{"template","base","addition"};
            var before=inventory();var menu=new SmithingMenu(8,p.getInventory(),ContainerLevelAccess.NULL);p.containerMenu=menu;
            var paid=new JsonArray();
            for(int i=0;i<3;i++) {
                String item=json.getAsJsonObject(slots[i]).get("item").getAsString();h.assertTrue(count(item)>0,"Smithing requires actual existing stock "+item);
                menu.getSlot(i).set(take(item));paid.add(item);
            }
            var recipe=h.getLevel().getRecipeManager().byKey(new ResourceLocation(recipeId)).orElseThrow();var expected=recipe.getResultItem(h.getLevel().registryAccess());
            var out=menu.getSlot(3).remove(64);menu.getSlot(3).onTake(p,out);
            h.assertTrue(out.is(expected.getItem())&&out.getCount()==expected.getCount(),"Native original smithing output");
            for(int i=0;i<4;i++)h.assertTrue(menu.getSlot(i).getItem().isEmpty(),"All smithing slots paid exactly once");
            String result=id(out);p.getInventory().add(out);p.closeContainer();produced.add(result);
            var r=row("native_smith");r.addProperty("recipe",recipeId);r.addProperty("output",result);r.add("paid",paid);r.add("before",before);r.add("after",inventory());flush();
        }
        void finish() {report.addProperty("status","SEGMENT_EXECUTED");h.succeed();}
    }

    static void opening(Route r) {
        r.submit(intro(0));
        String[] recipes={"crafting_table","chest","torch","furnace","iron_pickaxe"};int[] quests={1,2,3,4,0x20};
        for(int i=0;i<recipes.length;i++){r.craft("minecraft:"+recipes[i]);if(recipes[i].equals("torch"))r.craft("minecraft:torch");r.submit(intro(quests[i]));}
        r.supply("minecraft:water_bucket",1,"Explicit filled-bucket entry fixture; no water acquisition claim");r.submit(intro(0x21));
        for(int i=0;i<4;i++){r.craft("dynasty:"+new String[]{"mu_mao","shi_ge","tong_dao","tie_jian"}[i]);r.submit(main(i));}
        r.craft("minecraft:shield");r.submit(intro(5));r.craft("dynasty:cloth_chestplate");r.craft("dynasty:bamboo_chestplate");r.submit(main(0x79));
    }
    static void early(Route r) {
        opening(r);r.supply("minecraft:cobblestone",4,"Navigation task possession");r.submit(intro(0xa));
        for(String mod:new String[]{"naturescompass:natures_compass","explorerscompass:explorers_compass"}){r.craft("minecraft:compass");r.craft(mod);}
        r.submit(intro(0xb));r.craft("dynasty:bronze_ingot_alloy");r.submit(main(5));
        r.supply("dynasty:cinnabar",1,"Read-only ore/loot source association; QA seed");r.submit(main(0xa));
        for(String item:new String[]{"bamboo_slip","ink_stick","blueprint","refined_steel"}) {
            r.craft("dynasty:"+item);r.submit(main(switch(item){case "bamboo_slip"->0xb;case "ink_stick"->0xc;case "blueprint"->0x1d;default->6;}));
        }
        for(String item:new String[]{"qimen_gear","qimen_cable","repeating_crossbow"}){r.craft("dynasty:cod4/"+item);r.submit(q(switch(item){case "qimen_gear"->2;case "qimen_cable"->1;default->3;}));}
        r.craft("dynasty:cod4/army_ration");r.submit(q(0x15));r.craft("dynasty:bronze_chestplate");r.submit(main(0x7c));
    }

    static final class Piece extends com.dynasty.structure.TravelSitePiece {
        Piece(BlockPos p,int style){super(p,style);setOrientation(Direction.NORTH);}
        BlockPos point(int x,int y,int z){return world(x,y,z);}
    }
    static BlockPos site(Route r,int style,int index) {
        var origin=new BlockPos(4096+style*128,80,4096);var piece=new Piece(origin,style);var box=piece.getBoundingBox();var l=r.h.getLevel();
        for(int x=box.minX()>>4;x<=box.maxX()>>4;x++)for(int z=box.minZ()>>4;z<=box.maxZ()>>4;z++) {
            l.setChunkForced(x,z,true);l.getChunk(x,z);var cp=new ChunkPos(x,z);r.forced.add(cp);
            piece.postProcess(l,l.structureManager(),l.getChunkSource().getGenerator(),net.minecraft.util.RandomSource.create(42000+style),
                new BoundingBox(x*16,l.getMinBuildHeight(),z*16,x*16+15,l.getMaxBuildHeight()-1,z*16+15),cp,origin);
        }
        var at=piece.point(5+index*4,1,28);r.p.setPos(Vec3.atBottomCenterOf(piece.point(5+index*4,1,27)));return at;
    }
    static void use(Route r,BlockPos at) {
        var s=r.h.getLevel().getBlockState(at);s.use(r.h.getLevel(),r.p,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(at),Direction.UP,at,false));
    }

    @GameTest(template="bow_ritual_test",batch="route_opening",timeoutTicks=200)
    public static void openingActualQuestPrefixAndCarriedPredecessorPayments(GameTestHelper h) {var r=new Route(h,"opening");opening(r);r.finish();}
    @GameTest(template="bow_ritual_test",batch="route_early",timeoutTicks=200)
    public static void navigationPrefixToQimenAndCraftOnlySupply(GameTestHelper h) {var r=new Route(h,"early");early(r);r.finish();}
    @GameTest(template="bow_ritual_test",batch="route_middle",timeoutTicks=700)
    public static void rackYieldPaysOriginalBuildCostAfterRealClock(GameTestHelper h) {
        var r=new Route(h,"rack_build");r.prefix(q(0x26),Set.of());r.prefix(build(0x101),Set.of());
        var at=site(r,0,1);h.assertTrue(h.getLevel().getBlockState(at).is(SmallInteractions.ENTRIES.get("old_weapon_rack").get()),"Original rack placement");
        use(r,at);long start=h.getLevel().getGameTime();
        h.runAfterDelay(600,()->{
            use(r,at);h.assertTrue(r.count("dynasty:tie_jian")==1,"Actual rack grants one sword");
            var reward=r.row("native_site_yield");reward.addProperty("site","old_weapon_rack");reward.addProperty("elapsed_server_ticks",h.getLevel().getGameTime()-start);reward.addProperty("item","dynasty:tie_jian");r.produced.add("dynasty:tie_jian");
            r.submit(q(0x26));h.assertTrue(r.count("dynasty:tie_jian")==1,"FTB submission retains actual rack reward for Build payment");
            r.prepare("dynasty:liuyun_sword");r.submit(build(0x101));r.submit("10d3dbbbab55883b");r.craft("dynasty:liuyun_sword");r.submit(build(0x102));
            r.craft("dynasty:pojun_ring");r.submit(build(0x190));r.craft("dynasty:wuqu_sword_knot");r.submit(build(0x191));r.finish();
        });
    }
    @GameTest(template="bow_ritual_test",batch="route_midlate",timeoutTicks=3700)
    public static void armoryYieldPaysCrossbowThenSiegeAfterRealClock(GameTestHelper h) {
        var r=new Route(h,"armory_build");var keep=Set.of(q(2),q(1),q(3),q(4),q(0x24));r.prefix(q(0x24),keep);r.prefix(q(4),keep);
        var at=site(r,2,0);h.assertTrue(h.getLevel().getBlockState(at).is(SmallInteractions.ENTRIES.get("abandoned_armory").get()),"Original armory placement");use(r,at);long start=h.getLevel().getGameTime();
        h.runAfterDelay(3600,()->{
            use(r,at);h.assertTrue(r.count("dynasty:qimen_gear")==1,"Actual armory grants one gear");
            var reward=r.row("native_site_yield");reward.addProperty("site","abandoned_armory");reward.addProperty("elapsed_server_ticks",h.getLevel().getGameTime()-start);reward.addProperty("item","dynasty:qimen_gear");
            r.submit(q(0x24));r.submit(q(2));r.craft("dynasty:cod4/qimen_cable");r.submit(q(1));
            h.assertTrue(r.count("dynasty:qimen_gear")==1,"Real armory gear carried into repeating crossbow");r.craft("dynasty:cod4/repeating_crossbow");r.submit(q(3));
            // The extra siege gear is paid through its recipe, never confused with the already consumed reward.
            r.craft("dynasty:cod4/qimen_gear");r.craft("dynasty:cod4/siege_crossbow");r.submit(q(4));
            r.craft("dynasty:cod4/repeating_bolt");r.submit(q(0xd));r.finish();
        });
    }
    @GameTest(template="bow_ritual_test",batch="route_silver_jade",timeoutTicks=200)
    public static void silverToJadeAndBronzeToJadeWithSupplyPouchBranch(GameTestHelper h) {
        var r=new Route(h,"middle");r.prefix(main(0x45),Set.of());r.prefix(q(0x1e),Set.of(q(0x15)));
        r.craft("dynasty:sword_silver");r.submit(main(0x45));r.craft("dynasty:sword_jade");r.submit(main(0x46));
        r.craft("dynasty:bronze_chestplate");r.submit(main(0x7c));r.craft("dynasty:jade_chestplate");r.submit(main(0x9e));
        r.craft("dynasty:cod4/army_ration");r.submit(q(0x15));r.craft("dynasty:silk_pouch");r.submit(q(0x1e));r.finish();
    }
    @GameTest(template="bow_ritual_test",batch="route_late",timeoutTicks=200)
    public static void guardEvolutionPaysCarriedBladeAndCurrentFtbCosts(GameTestHelper h) {
        var r=new Route(h,"late");var keep=new HashSet<String>();for(int n:new int[]{2,0x62,0x63,0x64,0x65,0x66,0x67})keep.add(build(n));r.prefix(build(0x67),keep);
        r.craft("dynasty:zhenyue_blade");r.submit(build(2));
        for(int i=1;i<=3;i++) {
            String recipe="dynasty:evolve_guard_"+i;var def=RECIPES.getAsJsonObject(recipe);
            for(String slot:new String[]{"template","addition"}){String item=def.getAsJsonObject(slot).get("item").getAsString();r.supply(item,Math.max(0,1-r.count(item)),"Explicit Boss/template material for "+recipe);}
            r.submit(build(0x60+2*i));r.smith(recipe);r.submit(build(0x61+2*i));
        }
        r.finish();
    }
    @GameTest(template="bow_ritual_test",batch="route_terminal",timeoutTicks=200)
    public static void terminalChestplatesConsumeEveryExistingEquipmentPredecessor(GameTestHelper h) {
        var r=new Route(h,"terminal");
        r.craft("dynasty:xuantian_chestplate");r.submit(main(0xa0));r.craft("dynasty:hongmeng_chestplate");r.submit(main(0xb0));r.finish();
    }
}
