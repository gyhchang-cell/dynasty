package com.dynasty.expansion;

import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.*;
import net.minecraft.world.level.storage.loot.*;
import net.minecraft.world.level.storage.loot.parameters.*;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class SecondaryDropGameTests {
    private static ServerPlayer player(GameTestHelper h){var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"loot-native"));p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(4,2,4))));return p;}
    private static LootParams context(GameTestHelper h,SecondaryMob m,ServerPlayer p){
        var builder=new LootParams.Builder(h.getLevel()).withParameter(LootContextParams.THIS_ENTITY,m).withParameter(LootContextParams.ORIGIN,m.position()).withParameter(LootContextParams.DAMAGE_SOURCE,p==null?m.damageSources().generic():p.damageSources().playerAttack(p));
        if(p!=null)builder.withParameter(LootContextParams.LAST_DAMAGE_PLAYER,p).withParameter(LootContextParams.KILLER_ENTITY,p).withParameter(LootContextParams.DIRECT_KILLER_ENTITY,p);
        return builder.create(LootContextParamSets.ENTITY);
    }
    @GameTest(template="bow_ritual_test",batch="cod4_secondary_loot",setupTicks=20,timeoutTicks=100)
    public static void actualNativeLootManagerLoadsAllThirtySecondaryAliasesRequiresPlayerKillAndKeepsLightBoundedDropsAndRealUses(GameTestHelper h){
        var p=player(h);int aliases=0;var recipes=h.getLevel().getRecipeManager().getRecipes();
        for(var spec:SecondaryMobs.SPECS){
            var m=SecondaryMobs.TYPES.get(spec.id()).get().create(h.getLevel());m.setPos(p.position());var table=h.getLevel().getServer().getLootData().getLootTable(new ResourceLocation("dynasty","entities/"+spec.id()));var paid=context(h,m,p);var environmental=context(h,m,null);Set<String> seen=new HashSet<>();int maximum=spec.id().equals("clockwork_rat")?3:2;
            for(int seed=1;seed<=192;seed++){
                h.assertTrue(table.getRandomItems(environmental,seed).isEmpty(),"Actual native environmental/unowned kill cannot produce primary or secondary farm loot: "+spec.id());var drops=table.getRandomItems(paid,seed);h.assertTrue(drops.size()<=maximum&&drops.stream().allMatch(s->s.getCount()==1),"Actual native tables produce only bounded single-unit light drops");
                for(var stack:drops)if(stack.hasTag()&&stack.getTag().contains("DynastySecondaryDrop")){
                    String alias=stack.getTag().getString("DynastySecondaryDrop");if(!seen.add(alias))continue;h.assertTrue(stack.hasCustomHoverName()&&!stack.is(ExpansionContent.item("fox_tail"))&&!stack.is(ExpansionContent.item("sea_pearl"))&&!stack.is(ExpansionContent.item("dragon_pearl")),"Real localized native alias never substitutes mythical boss or palace accessory gates");
                    boolean nativeUse=recipes.stream().anyMatch(r->r.getIngredients().stream().anyMatch(i->i.test(stack)))||net.minecraft.world.level.block.entity.AbstractFurnaceBlockEntity.isFuel(stack)||net.minecraft.world.item.alchemy.PotionBrewing.isIngredient(stack);
                    h.assertTrue(nativeUse,"Actual existing recipe/fuel/brewing consumer accepts this exact labeled native stack: "+alias+" -> "+stack);
                }
            }
            h.assertTrue(seen.size()==(spec.id().equals("clockwork_rat")?2:1),"All actual source-specific secondary pools are reachable via native RNG, not only registered text: "+spec.id());aliases+=seen.size();m.discard();
        }
        h.assertTrue(aliases==31&&com.dynasty.DynastyTrinkets.IDS.size()==201,"All thirty original actors/31 native aliases preserve201 original accessory registry");p.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_secondary_loot_death",setupTicks=20,timeoutTicks=80)
    public static void actualNativePlayerDamageDeathsUseOriginalLootOnceAndNeverMintMythicalFoxOrPalacePearl(GameTestHelper h){
        var p=player(h);String[] species={"famished_refugee","red_fox","giant_python","paper_cut_child","snail_maiden","clockwork_rat"};var actors=new ArrayList<SecondaryMob>();
        for(int i=0;i<species.length;i++){var m=SecondaryMobs.TYPES.get(species[i]).get().create(h.getLevel());m.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(2+i*2,3,8))));m.setNoAi(true);h.getLevel().addFreshEntity(m);actors.add(m);}
        h.startSequence().thenWaitUntil(()->{for(var m:actors)h.assertTrue(m.tickCount>=2&&h.getLevel().getEntity(m.getUUID())==m,"Actual native stationary damage fixture visible before kill");})
        .thenExecute(()->{
            for(var m:actors){h.assertTrue(m.hurt(p.damageSources().playerAttack(p),100000)&&m.isDeadOrDying(),"Real server player DamageSource drives native hurt/death/loot pipeline");h.assertTrue(!m.hurt(p.damageSources().playerAttack(p),100000),"Already dead native actor cannot pay another loot event");}
            h.runAfterDelay(3,()->{
                var bounds=new AABB(h.absolutePos(BlockPos.ZERO),h.absolutePos(new BlockPos(16,8,16)));var drops=h.getLevel().getEntitiesOfClass(ItemEntity.class,bounds);
                h.assertTrue(drops.stream().noneMatch(e->e.getItem().is(ExpansionContent.item("fox_tail"))||e.getItem().is(ExpansionContent.item("sea_pearl"))||e.getItem().is(ExpansionContent.item("dragon_pearl"))),"Real native deaths do not grant mythical material or palace-only accessory");
                h.assertTrue(!drops.isEmpty()&&drops.stream().mapToInt(e->e.getItem().getCount()).sum()<=13,"Actual six native deaths have finite light loot, no duplicated corpse payout");var count=drops.stream().mapToInt(e->e.getItem().getCount()).sum();
                h.runAfterDelay(5,()->{try{h.assertTrue(h.getLevel().getEntitiesOfClass(ItemEntity.class,bounds).stream().mapToInt(e->e.getItem().getCount()).sum()==count,"Further native corpse ticks cannot repeat primary/secondary rewards");h.succeed();}finally{drops.forEach(Entity::discard);actors.forEach(Entity::discard);p.discard();}});
            });
        });
    }
}
