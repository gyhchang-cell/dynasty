package artifacts.config.display;

import artifacts.lang.LangEntry;
import artifacts.lang.LangUtil;

public class SharedConfigLang {

    public static final LangEntry ENABLED = title("enabled");
    public static final LangEntry COOLDOWN = title("cooldown");
    public static final ConfigEntry GENERATE_AS_LOOT = entry("generateAsLoot",
            "Whether this item can be found in structures or drop from entities"
    );

    public static final LangEntry DURABILITY = title("durability");

    public static final ConfigEntry CAN_BE_DAMAGED = durabilityEntry("canBeDamaged",
            "Whether this item has a limited number of uses"
    );
    public static final ConfigEntry CAN_BE_REPAIRED = durabilityEntry("canBeRepaired",
            "Whether this item can be repaired using items in the %s item tag"
    );
    public static final ConfigEntry INDESTRUCTIBLE = durabilityEntry("indestructible",
            "Whether this item should remain intact and stop working when its durability reaches 1"
    );
    public static final ConfigEntry MAX_DAMAGE = durabilityEntry("maxDamage",
            "The maximum amount of damage that this item can take before breaking"
    );
    public static final ConfigEntry DAMAGE_PER_ACTIVATION = durabilityEntry("damagePerActivation",
            "The amount of durability lost every time this item's ability is triggered"
    );
    public static final ConfigEntry DAMAGE_PER_ATTACK = durabilityEntry("damagePerAttack",
            "The amount of durability lost for every melee attack performed while wearing this item"
    );
    public static final ConfigEntry DAMAGE_PER_KILL = durabilityEntry("damagePerKill",
            "The amount of durability lost for every entity killed while wearing this item"
    );
    public static final ConfigEntry DAMAGE_PER_ORE_MINED = durabilityEntry("damagePerOreMined",
            "The amount of durability lost for every ore block mined"
    );
    public static final ConfigEntry DAMAGE_PER_SECOND_ACTIVE = durabilityEntry("damagePerSecondActive",
            "The amount of durability lost for every second this item is toggled on"
    );
    public static final ConfigEntry DAMAGE_PER_ITEM_DRUNK = durabilityEntry("damagePerItemDrunk",
            "The amount of durability lost every time an item is drunk"
    );
    public static final ConfigEntry DAMAGE_PER_ITEM_EATEN = durabilityEntry("damagePerItemEaten",
            "The amount of durability lost every time an item is eaten"
    );
    public static final ConfigEntry DAMAGE_WHEN_CONSUMED = durabilityEntry("damageWhenConsumed",
            "The amount of durability that is lost when this item is consumed"
    );

    private static ConfigEntry durabilityEntry(String key, String description) {
        return durabilityEntry(key, LangUtil.fromCamelCasedString(key), description);
    }

    private static ConfigEntry durabilityEntry(String key, String englishTitle, String englishDescription) {
        return entry("durability." + key, englishTitle, englishDescription);
    }

    private static ConfigEntry entry(String key, String description) {
        return entry(key, LangUtil.fromCamelCasedString(key), description);
    }

    private static ConfigEntry entry(String key, String englishTitle, String englishDescription) {
        return new ConfigEntry(title(key, englishTitle), description(key, englishDescription));
    }

    private static LangEntry title(String key) {
        return title(key, LangUtil.fromCamelCasedString(key));
    }

    private static LangEntry title(String key, String english) {
        return new LangEntry(key, english).withPrefix("artifacts.config").withSuffix("title");
    }

    private static LangEntry description(String key, String english) {
        return new LangEntry(key, english).withPrefix("artifacts.config").withSuffix("description");
    }

    public record ConfigEntry(LangEntry title, LangEntry description) {

    }
}
