package artifacts.config.screen;

import me.shedaniel.clothconfig2.api.AbstractConfigListEntry;
import me.shedaniel.clothconfig2.gui.entries.SubCategoryListEntry;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.CommonComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.resources.Identifier;

import java.util.List;

public class ItemSubCategoryListEntry extends SubCategoryListEntry {

    private final Identifier textureId;

    @SuppressWarnings("deprecation")
    public ItemSubCategoryListEntry(Component title, Identifier textureId, List<AbstractConfigListEntry<?>> entries) {
        super(title, List.copyOf(entries), false);
        this.textureId = textureId;
    }

    // https://github.com/shedaniel/cloth-config/issues/153
    @Override
    @SuppressWarnings("rawtypes")
    public boolean isRequiresRestart() {
        for (AbstractConfigListEntry entry : getValue()) {
            if (entry.isRequiresRestart() && entry.isEdited()) {
                return true;
            }
        }
        return false;
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor graphics, int index, int y, int x, int entryWidth, int entryHeight, int mouseX, int mouseY, boolean isHovered, float delta) {
        super.extractRenderState(graphics, index, y, x, entryWidth, entryHeight, mouseX, mouseY, isHovered, delta);

        graphics.blit(RenderPipelines.GUI_TEXTURED, textureId, x - 4, y + 2, 0, 0, 16, 16, 16, 16);
        graphics.text(Minecraft.getInstance().font, this.getActualDisplayedFieldName().getVisualOrderText(), x + 16, y + 6, -1);
    }

    @Override
    public Component getDisplayedFieldName() {
        // We render this ourselves to offset it to the right
        return CommonComponents.EMPTY;
    }

    public Component getActualDisplayedFieldName() {
        MutableComponent text = this.getFieldName().copy();
        boolean hasError = this.getConfigError().isPresent();
        boolean isEdited = this.isEdited();
        if (hasError) {
            text.withStyle(ChatFormatting.RED);
        }

        if (isEdited) {
            text.withStyle(ChatFormatting.ITALIC);
        }

        if (!hasError && !isEdited) {
            text.withStyle(ChatFormatting.GRAY);
        }

        if (!this.isEnabled()) {
            text.withStyle(ChatFormatting.DARK_GRAY);
        }

        return text;
    }
}
