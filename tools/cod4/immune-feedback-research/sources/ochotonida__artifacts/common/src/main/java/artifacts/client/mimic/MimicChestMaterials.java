package artifacts.client.mimic;

import artifacts.Artifacts;
import artifacts.entity.MimicEntity;
import artifacts.integration.ModCompat;
import artifacts.integration.lootr.LootrCompat;
import net.minecraft.client.renderer.Sheets;
import net.minecraft.client.resources.model.sprite.SpriteId;
import net.minecraft.resources.Identifier;
import net.minecraft.util.SpecialDates;

import java.time.Month;
import java.time.MonthDay;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

// TODO (Quark 26.1+): Update quark texture path
public class MimicChestMaterials {

    public static final List<String> QUARK_WOODEN_CHEST_MATERIALS = Arrays.asList(
            "oak",
            "spruce",
            "birch",
            "cherry",
            "jungle",
            "acacia",
            "dark_oak",
            "warped",
            "crimson",
            "azalea",
            "blossom",
            "mangrove",
            "bamboo"
    );

    private static final SpriteId CHEST_LOOTR = createSpriteId(ModCompat.LOOTR.id("entity/chest/normal"));

    private final boolean isChristmas = SpecialDates.isExtendedChristmas()
            || SpecialDates.dayNow().equals(MonthDay.of(Month.APRIL, 1));
    private final List<SpriteId> moddedChestMaterials = new ArrayList<>();
    private final List<SpriteId> moddedLootrChestMaterials = new ArrayList<>();

    public MimicChestMaterials() {
        addQuarkMaterials(moddedChestMaterials, "normal");
        addQuarkMaterials(moddedLootrChestMaterials, "lootr_normal");
    }

    private static SpriteId createSpriteId(Identifier id) {
        return new SpriteId(Sheets.CHEST_SHEET, id);
    }

    private static void addQuarkMaterials(List<SpriteId> chestMaterials, String chestVariant) {
        if (ModCompat.QUARK.isLoaded()) {
            for (String chestMaterial : QUARK_WOODEN_CHEST_MATERIALS) {
                String path = String.format("quark_variant_chests/%s/%s", chestMaterial, chestVariant);
                chestMaterials.add(createSpriteId(ModCompat.QUARK.id(path)));
            }
        }
    }

    public SpriteId getChestSprite(MimicEntity mimic) {
        if (isChristmas) {
            return Sheets.CHEST_CHRISTMAS.single();
        }

        boolean useLootrTextures = ModCompat.LOOTR.isLoaded() && !LootrCompat.useVanillaTextures();
        SpriteId defaultSprite = useLootrTextures ? CHEST_LOOTR : Sheets.CHEST_REGULAR.single();
        List<SpriteId> moddedSprites = useLootrTextures ? moddedLootrChestMaterials : moddedChestMaterials;

        if (moddedSprites.isEmpty() || !Artifacts.CONFIG.client.useModdedMimicTextures.get()) {
            return defaultSprite;
        }
        return selectRandomSprite(defaultSprite, moddedSprites, mimic);
    }

    private SpriteId selectRandomSprite(SpriteId defaultSprite, List<SpriteId> moddedSprites, MimicEntity mimic) {
        int spriteIndex = (int) Math.abs(mimic.getUUID().getMostSignificantBits()) % (moddedSprites.size() + 1);
        if (spriteIndex >= moddedSprites.size()) {
            return defaultSprite;
        }
        return moddedSprites.get(spriteIndex);
    }
}
