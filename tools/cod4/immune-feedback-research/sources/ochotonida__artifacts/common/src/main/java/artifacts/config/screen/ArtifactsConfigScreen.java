package artifacts.config.screen;

import artifacts.Artifacts;
import artifacts.config.ConfigEntryKey;
import artifacts.config.ConfigManager;
import artifacts.config.display.ConfigEntryDisplay;
import artifacts.config.value.ConfigValue;
import artifacts.lang.LangEntry;
import me.shedaniel.clothconfig2.api.AbstractConfigListEntry;
import me.shedaniel.clothconfig2.api.ConfigBuilder;
import me.shedaniel.clothconfig2.api.ConfigCategory;
import me.shedaniel.clothconfig2.gui.entries.SubCategoryListEntry;
import me.shedaniel.clothconfig2.impl.builders.AbstractFieldBuilder;
import me.shedaniel.clothconfig2.impl.builders.DropdownMenuBuilder;
import me.shedaniel.clothconfig2.impl.builders.FieldBuilder;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;

import java.util.*;

// TODO: cleanup this mess
public class ArtifactsConfigScreen {

    private final ConfigBuilder builder;

    private final Map<ConfigEntryKey, List<AbstractConfigListEntry<?>>> subCategories = new HashMap<>();

    public ArtifactsConfigScreen(Screen parent) {
        builder = ConfigBuilder.create()
                .setParentScreen(parent)
                .setTitle(Component.translatable("%s.config.title".formatted(Artifacts.MOD_ID)))
                .setSavingRunnable(() -> {
                    for (ConfigManager config : Artifacts.CONFIG.configs.values()) {
                        config.onConfigChanged();
                    }
                });
    }

    public Screen build() {
        for (ConfigManager config : List.of(
                // Explicitly define category order
                Artifacts.CONFIG.general,
                Artifacts.CONFIG.client,
                Artifacts.CONFIG.items
        )) {
            addConfigs(config);
        }

        // Add top-level subcategories to their categories
        subCategories.keySet().stream().sorted().forEach(key -> {
            if (key.parent().isEmpty()) {
                SubCategoryListEntry subCategory = (SubCategoryListEntry) buildSubCategory(key);
                appendSearchTagsToSubCategories(List.of(), subCategory.getFieldName(), subCategory.getValue());
                builder.getOrCreateCategory(getCategoryTitle(key.configManager())).addEntry(subCategory);
            }
        });

        return builder.build();
    }

    private AbstractConfigListEntry<?> buildSubCategory(ConfigEntryKey key) {
        List<AbstractConfigListEntry<?>> entries = subCategories.get(key);
        // TODO: Query actual item holder/key instead of parsing from string
        if (isItem(key.path().getLast())) {
            return new ItemSubCategoryListEntry(getTitle(key), Artifacts.id("textures/item/%s.png".formatted(key.path().getLast())), entries);
        }
        return builder.entryBuilder().startSubCategory(getTitle(key), List.copyOf(entries)).build();
    }

    @SuppressWarnings({"unchecked", "rawtypes"}) // Dumbass api uses raw types
    private static void appendSearchTagsToSubCategories(List<String> parentSearchTags, Component fieldName, List<AbstractConfigListEntry> entries) {
        List<String> searchTags = new ArrayList<>(parentSearchTags);
        searchTags.addAll(List.of(fieldName.getString().split(" ")));
        entries.forEach(value -> {
            // noinspection unchecked
            value.appendSearchTags(searchTags);
            if (value instanceof SubCategoryListEntry entry) {
                appendSearchTagsToSubCategories(searchTags, value.getFieldName(), entry.getValue());
            }
        });
    }

    private void addConfigEntry(ConfigCategory category, ConfigManager config, ConfigEntryKey key) {
        AbstractConfigListEntry<?> field = createField(config, key, config.getValues().get(key));
        Optional<ConfigEntryKey> parent = key.parent();
        if (parent.isEmpty()) {
            category.addEntry(field);
        } else {
            ConfigEntryKey subCategory = parent.get();
            while (subCategory.parent().isPresent()) {
                subCategory = subCategory.parent().get();
            }

            getOrCreateSubCategory(subCategory).add(field);
        }
    }

    private void addConfigs(ConfigManager config) {
        ConfigCategory category = builder.getOrCreateCategory(getCategoryTitle(config.getName()));
        config.getValues().keySet()
                .stream()
                .sorted(Comparator.naturalOrder())
                .sorted(Comparator.comparingInt(key -> getDisplay(key).displayPriority()))
                .sorted(Comparator.comparingInt(key -> key.path().size()))
                .forEach(key -> addConfigEntry(category, config, key));
    }

    private List<AbstractConfigListEntry<?>> getOrCreateSubCategory(ConfigEntryKey key) {
        return subCategories.computeIfAbsent(key, _ -> new ArrayList<>());
    }

    private AbstractConfigListEntry<?> createField(ConfigManager config, ConfigEntryKey key, ConfigValue<?> value) {
        Component[] tooltips = getTooltips(key);
        FieldBuilder<?, ?, ?> configEntry = createConfigEntry(config, value, config.getDisplay(key).title().asComponent());
        setTooltips(configEntry, tooltips);
        return configEntry.build();
    }

    private static void setTooltips(FieldBuilder<?, ?, ?> builder, Component[] tooltips) {
        if (builder instanceof AbstractFieldBuilder<?, ?, ?> b) {
            b.setTooltip(tooltips);
        } else if (builder instanceof DropdownMenuBuilder<?> b) {
            b.setTooltip(tooltips);
        }
    }

    /* Config entries read and write from the config file directly when saved,
     * rather than modifying the in-memory config and then saving it to disk.
     * This allows connected clients to display and modify their own config options,
     * without overriding settings received from the server.
     */
    private <T> FieldBuilder<?, ?, ?> createConfigEntry(ConfigManager config, ConfigValue<T> value, Component title) {
        FieldBuilder<?, ?, ?> configEntry = value.type().getConfigEntryFactory()
                .createConfigEntry(config, builder.entryBuilder(), title, value);
        configEntry.requireRestart(value.requiresRestart());
        return configEntry;
    }

    private static boolean isItem(String name) {
        return Identifier.isValidPath(name) && BuiltInRegistries.ITEM.containsKey(Artifacts.id(name));
    }

    private static Component getCategoryTitle(String categoryKey) {
        return Component.translatable("%s.config.%s.title".formatted(Artifacts.MOD_ID, categoryKey));
    }

    private static Component getTitle(ConfigEntryKey key) {
        return getDisplay(key).title().asComponent();
    }

    private static Component[] getTooltips(ConfigEntryKey key) {
        return getDisplay(key).description().stream().map(LangEntry::asComponent).toArray(Component[]::new);
    }

    private static ConfigEntryDisplay getDisplay(ConfigEntryKey key) {
        return Artifacts.CONFIG.configs.get(key.configManager()).getDisplay(key);
    }
}
