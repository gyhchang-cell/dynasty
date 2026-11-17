package com.grim3212.assorted.damagenumbers.client.damage;

import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.tags.TagKey;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.damagesource.DamageTypes;
import org.jetbrains.annotations.Nullable;

import java.util.Arrays;
import java.util.Locale;
import java.util.stream.Collectors;

/** RPG Damage's sources and colours, grouped by damage type tag so modded damage types fall into place. */
public enum DamageKind {
    MELEE(0xFE2712),
    PROJECTILE(0xFE2712),
    EXPLOSION(0xFE2712),
    FIRE(0xFF7F00),
    MAGIC(0xA020F0),
    FREEZING(0x7FD4FF),
    LIGHTNING(0xFFEE55),
    DROWNING(0x5599FF),
    FALL(0xBEBEBE),
    STARVATION(0xBEBEBE),
    CACTUS(0xBEBEBE),
    GENERIC(0xBEBEBE),
    HEALING(0x00A550);

    // NeoForge's tag, which magic mods fill; Fabric has no damage type conventions, so there it only has what mods add.
    private static final TagKey<DamageType> MODDED_MAGIC = TagKey.create(Registries.DAMAGE_TYPE, Identifier.fromNamespaceAndPath("neoforge", "is_magic"));

    private final int color;

    DamageKind(int color) {
        this.color = color;
    }

    public int color() {
        return this.color;
    }

    /** A modded type that ends up generic gets a colour of its own, picked from its id so it is the same every launch. */
    public int color(@Nullable DamageSource source) {
        Identifier id = this == GENERIC ? moddedId(source) : null;
        return id == null ? this.color : colorOf(id);
    }

    /** Hue from anywhere on the wheel, but kept light and not too strong, so it reads against the black outline. */
    public static int colorOf(Identifier id) {
        // String.hashCode is fixed by the Java spec, so the colour never changes between launches or machines.
        int hash = Mth.murmurHash3Mixer(id.toString().hashCode());
        float hue = (hash & 0xFFFF) / 65536.0F;
        float saturation = 0.45F + ((hash >>> 16) & 0xFF) / 255.0F * 0.3F;
        float value = 0.85F + ((hash >>> 24) & 0xFF) / 255.0F * 0.15F;
        return Mth.hsvToRgb(hue, saturation, value);
    }

    private static @Nullable Identifier moddedId(@Nullable DamageSource source) {
        Identifier id = source == null ? null : source.typeHolder().unwrapKey().map(ResourceKey::identifier).orElse(null);
        return id == null || id.getNamespace().equals(Identifier.DEFAULT_NAMESPACE) ? null : id;
    }

    public Component label() {
        return Component.translatable("hud.assorteddamagenumbers.damage." + this.name().toLowerCase(Locale.ROOT));
    }

    /** Damage types have no names, only death messages, so a modded generic one takes ours if a lang file gives it, else its id. */
    public Component label(@Nullable DamageSource source) {
        Identifier id = this == GENERIC ? moddedId(source) : null;
        return id == null ? this.label() : Component.translatableWithFallback("hud.assorteddamagenumbers.damage." + id.toLanguageKey(), nameOf(id));
    }

    /** {@code mymod:acid_splash} reads "Acid Splash". */
    public static String nameOf(Identifier id) {
        String path = id.getPath().substring(id.getPath().lastIndexOf('/') + 1);
        return Arrays.stream(path.split("_")).filter(word -> !word.isEmpty())
                .map(word -> word.substring(0, 1).toUpperCase(Locale.ROOT) + word.substring(1)).collect(Collectors.joining(" "));
    }

    public static DamageKind of(@Nullable DamageSource source) {
        if (source == null) {
            return GENERIC;
        }
        if (source.is(DamageTypeTags.IS_FIRE)) {
            return FIRE;
        }
        if (source.is(DamageTypeTags.IS_EXPLOSION)) {
            return EXPLOSION;
        }
        if (source.is(DamageTypeTags.IS_PROJECTILE)) {
            return PROJECTILE;
        }
        if (source.is(DamageTypeTags.IS_DROWNING)) {
            return DROWNING;
        }
        if (source.is(DamageTypeTags.IS_FREEZING)) {
            return FREEZING;
        }
        if (source.is(DamageTypeTags.IS_LIGHTNING)) {
            return LIGHTNING;
        }
        if (source.is(DamageTypeTags.IS_FALL)) {
            return FALL;
        }
        if (source.is(DamageTypes.STARVE)) {
            return STARVATION;
        }
        if (source.is(DamageTypes.CACTUS) || source.is(DamageTypes.SWEET_BERRY_BUSH)) {
            return CACTUS;
        }
        if (source.is(DamageTypes.MAGIC) || source.is(DamageTypes.INDIRECT_MAGIC) || source.is(DamageTypes.WITHER) || source.is(DamageTypes.DRAGON_BREATH)) {
            return MAGIC;
        }
        // Modded only: NeoForge also tags thorns, which stays a hit from the wearer on both loaders.
        if (source.is(MODDED_MAGIC) && moddedId(source) != null) {
            return MAGIC;
        }
        return source.getEntity() != null ? MELEE : GENERIC;
    }
}
