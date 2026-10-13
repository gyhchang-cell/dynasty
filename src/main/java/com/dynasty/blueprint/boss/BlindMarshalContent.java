package com.dynasty.blueprint.boss;
import com.dynasty.Dynasty;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.*;

/** Independent Boss2 registrations; final sovereign identity is unchanged. */
public final class BlindMarshalContent {
    public static final DeferredRegister<EntityType<?>> ENTITIES=DeferredRegister.create(ForgeRegistries.ENTITY_TYPES,Dynasty.MODID);
    public static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,Dynasty.MODID);
    public static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,Dynasty.MODID);
    public static final DeferredRegister<StructureType<?>> STRUCTURES=DeferredRegister.create(Registries.STRUCTURE_TYPE,Dynasty.MODID);
    public static final DeferredRegister<StructurePieceType> PIECES=DeferredRegister.create(Registries.STRUCTURE_PIECE,Dynasty.MODID);
    public static final RegistryObject<EntityType<BlindMarshal>> MARSHAL=ENTITIES.register(BlindMarshal.ID,()->EntityType.Builder.<BlindMarshal>of(BlindMarshal::new,MobCategory.MONSTER).sized(5.2F,3.8F).clientTrackingRange(14).updateInterval(1).build(BlindMarshal.ID));
    public static final RegistryObject<EntityType<MarshalProjectile>> PROJECTILE=ENTITIES.register("marshal_finite_projectile",()->EntityType.Builder.<MarshalProjectile>of(MarshalProjectile::new,MobCategory.MISC).sized(.35F,.35F).clientTrackingRange(12).updateInterval(1).build("marshal_finite_projectile"));
    public static final RegistryObject<Item> EGG=ITEMS.register(BlindMarshal.ID+"_spawn_egg",()->new ForgeSpawnEggItem(MARSHAL,0x313D40,0xCEBD96,new Item.Properties()));
    public static final RegistryObject<Item> BLADE=ITEMS.register("marshal_broken_horse_cleaver",()->new Item(new Item.Properties()));
    public static final RegistryObject<Item> HELMET=ITEMS.register("marshal_broken_wing_helmet",()->new Item(new Item.Properties()));
    public static final RegistryObject<Item> OATH=ITEMS.register("marshal_last_city_oath",()->new Item(new Item.Properties()));
    public static final RegistryObject<Block> SOCKET=BLOCKS.register("marshal_oath_socket",()->new Block(BlockBehaviour.Properties.of().strength(-1,3600000)));
    public static final RegistryObject<Item> SOCKET_ITEM=ITEMS.register("marshal_oath_socket",()->new BlockItem(SOCKET.get(),new Item.Properties()));
    public static final RegistryObject<StructureType<MarshalCourtyardStructure>> YARD_TYPE=STRUCTURES.register("marshal_courtyard",()->()->MarshalCourtyardStructure.CODEC);
    public static final RegistryObject<StructurePieceType> YARD_PIECE=PIECES.register("marshal_courtyard",()->MarshalCourtyardPiece::new);
    public static void register(IEventBus bus){ENTITIES.register(bus);ITEMS.register(bus);BLOCKS.register(bus);STRUCTURES.register(bus);PIECES.register(bus);bus.addListener(BlindMarshalContent::attributes);}
    private static void attributes(EntityAttributeCreationEvent e){e.put(MARSHAL.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,2200).add(Attributes.ATTACK_DAMAGE,16).add(Attributes.ARMOR,14).add(Attributes.MOVEMENT_SPEED,.24).add(Attributes.KNOCKBACK_RESISTANCE,.85).add(Attributes.FOLLOW_RANGE,32).build());}
    private BlindMarshalContent(){}
}
