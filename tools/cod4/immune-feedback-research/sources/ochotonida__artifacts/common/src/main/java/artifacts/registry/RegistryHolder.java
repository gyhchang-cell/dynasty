package artifacts.registry;

import com.mojang.datafixers.util.Either;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderOwner;
import net.minecraft.core.component.DataComponentMap;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;

import java.util.Optional;
import java.util.function.Predicate;
import java.util.function.Supplier;
import java.util.stream.Stream;

public class RegistryHolder<R, V extends R> implements Holder<R>, Supplier<V> {

    private final ResourceKey<R> key;
    private final Supplier<V> factory;
    private Holder<R> holder;

    public RegistryHolder(ResourceKey<R> key, Supplier<V> factory) {
        this.key = key;
        this.factory = factory;
    }

    public Supplier<V> getFactory() {
        return factory;
    }

    public void bind(Holder<R> holder) {
        if (this.holder != null) {
            throw new IllegalStateException();
        }
        this.holder = holder;
    }

    public Holder<R> holder() {
        return holder;
    }

    @Override
    @SuppressWarnings("unchecked")
    public V get() {
        return (V) value();
    }

    @Override
    public R value() {
        return holder.value();
    }

    @Override
    public boolean isBound() {
        return holder != null && holder.isBound();
    }

    @Override
    public boolean areComponentsBound() {
        return isBound() && holder.areComponentsBound();
    }

    @Override
    public boolean is(Identifier resourceLocation) {
        return resourceLocation.equals(key.identifier());
    }

    @Override
    public boolean is(ResourceKey<R> resourceKey) {
        return resourceKey.equals(key);
    }

    @Override
    public boolean is(Predicate<ResourceKey<R>> predicate) {
        return predicate.test(key);
    }

    @Override
    public boolean is(TagKey<R> tagKey) {
        return isBound() && holder.is(tagKey);
    }

    @Override
    @SuppressWarnings("deprecation")
    public boolean is(Holder<R> holder) {
        return isBound() && this.holder.is(holder);
    }

    @Override
    public Stream<TagKey<R>> tags() {
        return isBound() ? holder.tags() : Stream.empty();
    }

    @Override
    public DataComponentMap components() {
        return isBound() ? holder.components() : DataComponentMap.EMPTY;
    }

    @Override
    public Either<ResourceKey<R>, R> unwrap() {
        return Either.left(key);
    }

    @Override
    public Optional<ResourceKey<R>> unwrapKey() {
        return Optional.of(key);
    }

    @Override
    public Kind kind() {
        return Kind.REFERENCE;
    }

    @Override
    public boolean canSerializeIn(HolderOwner<R> holderOwner) {
        return isBound() && holder.canSerializeIn(holderOwner);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        return obj instanceof Holder<?> h && h.kind() == Kind.REFERENCE && h.unwrapKey().isPresent() && h.unwrapKey().get() == this.key;
    }

    @Override
    public int hashCode() {
        return this.key.hashCode();
    }
}
