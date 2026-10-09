package com.dynasty.blueprint;

import com.mojang.serialization.Codec;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.MobSpawnSettings;
import net.minecraftforge.common.world.BiomeModifier;
import net.minecraftforge.common.world.ModifiableBiomeInfo;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/** Missing cod1 types are skipped at registry construction rather than breaking a world datapack. */
public record EcologyBiomeModifier(ResourceLocation region) implements BiomeModifier {
    public static final DeferredRegister<Codec<? extends BiomeModifier>> SERIALIZERS=DeferredRegister.create(ForgeRegistries.Keys.BIOME_MODIFIER_SERIALIZERS,"dynasty");
    public static final RegistryObject<Codec<EcologyBiomeModifier>> TYPE=SERIALIZERS.register("ecology",()->ResourceLocation.CODEC.fieldOf("region").xmap(EcologyBiomeModifier::new,EcologyBiomeModifier::region).codec());
    @Override public void modify(Holder<Biome> biome,Phase phase,ModifiableBiomeInfo.BiomeInfo.Builder builder){
        var rule=EcologyRules.get(region).orElseThrow(()->new IllegalArgumentException("Unknown ecology region "+region));
        if(phase!=Phase.ADD||!rule.naturalSpawning()||rule.biomeTag()==null||!biome.is(TagKey.create(Registries.BIOME,rule.biomeTag())))return;
        for(var member:rule.members()){
            if(member.existingSpawner()||member.elite()||!ForgeRegistries.ENTITY_TYPES.containsKey(member.mobType()))continue;
            var type=ForgeRegistries.ENTITY_TYPES.getValue(member.mobType());
            if(type==null||type.getCategory()!=net.minecraft.world.entity.MobCategory.MONSTER)continue;
            builder.getMobSpawnSettings().addSpawn(type.getCategory(),new MobSpawnSettings.SpawnerData(type,member.weight(),member.minGroup(),member.maxGroup()));
        }
    }
    @Override public Codec<? extends BiomeModifier> codec(){return TYPE.get();}
}
