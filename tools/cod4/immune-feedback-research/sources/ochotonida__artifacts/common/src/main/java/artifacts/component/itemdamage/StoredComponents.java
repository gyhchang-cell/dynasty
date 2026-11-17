package artifacts.component.itemdamage;

import com.google.common.collect.ImmutableSet;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.component.DataComponentPatch;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.ItemStack;
import org.jetbrains.annotations.Nullable;

import java.util.List;
import java.util.Objects;
import java.util.Set;

public record StoredComponents(Set<DataComponentType<?>> prototypes, DataComponentPatch patch) {

    private static final Codec<DataComponentType<?>> DATA_COMPONENT_TYPE_CODEC = Identifier.CODEC.flatXmap(
            id -> {
                DataComponentType<?> type = BuiltInRegistries.DATA_COMPONENT_TYPE.getValue(id);
                if (type == null) {
                    return DataResult.error(() -> "No component with type: '%s'".formatted(id));
                }
                if (type.isTransient()) {
                    return DataResult.error(() -> "'%s' is not a persistent component".formatted(id));
                }
                return DataResult.success(type);
            },
            type -> DataResult.success(BuiltInRegistries.DATA_COMPONENT_TYPE.getKey(type))
    );

    public static final Codec<StoredComponents> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            DATA_COMPONENT_TYPE_CODEC.listOf().xmap(Set::copyOf, List::copyOf).fieldOf("prototypes").forGetter(StoredComponents::prototypes),
            DataComponentPatch.CODEC.fieldOf("patch").forGetter(StoredComponents::patch)
    ).apply(instance, StoredComponents::new));

    public static final StreamCodec<RegistryFriendlyByteBuf, StoredComponents> STREAM_CODEC = StreamCodec.composite(
            Identifier.STREAM_CODEC
                    .<DataComponentType<?>>map(
                            id -> Objects.requireNonNull(BuiltInRegistries.DATA_COMPONENT_TYPE.getValue(id)),
                            type -> Objects.requireNonNull(BuiltInRegistries.DATA_COMPONENT_TYPE.getKey(type))
                    )
                    .apply(ByteBufCodecs.list())
                    .map(Set::copyOf, List::copyOf),
            StoredComponents::prototypes,
            DataComponentPatch.STREAM_CODEC,
            StoredComponents::patch,
            StoredComponents::new
    );

    public static @Nullable StoredComponents from(ItemStack stack, Set<DataComponentType<?>> types) {
        if (!hasAny(stack, types)) {
            return null;
        }
        ImmutableSet.Builder<DataComponentType<?>> prototypes = new ImmutableSet.Builder<>();
        DataComponentPatch.Builder patch = DataComponentPatch.builder();
        for (DataComponentType<?> type : types) {
            addComponentFromStack(type, stack, prototypes, patch);
        }
        return new StoredComponents(prototypes.build(), patch.build());
    }

    private static boolean hasAny(ItemStack stack, Set<DataComponentType<?>> types) {
        for (DataComponentType<?> type : types) {
            if (stack.has(type) || stack.hasNonDefault(type)) {
                return true;
            }
        }
        return false;
    }

    private static <T> void addComponentFromStack(DataComponentType<T> type, ItemStack stack, ImmutableSet.Builder<DataComponentType<?>> prototypes, DataComponentPatch.Builder patch) {
        T value = stack.get(type);
        T prototype = stack.getPrototype().get(type);
        // equals isn't needed here (assuming the prototype is sanitized)
        if (value == prototype) {
            prototypes.add(type);
        } else if (value == null) {
            patch.remove(type);
        } else {
            patch.set(type, value);
        }
    }

    public void applyTo(ItemStack stack) {
        for (DataComponentType<?> type : prototypes) {
            resetComponent(stack, type);
        }
        stack.applyComponents(patch);
    }

    private static <T> void resetComponent(ItemStack stack, DataComponentType<T> type) {
        stack.set(type, stack.getPrototype().get(type));
    }
}
