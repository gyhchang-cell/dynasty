package com.lothrazar.cyclic.item.datacard.filter;

import com.lothrazar.cyclic.gui.ButtonTextured;
import com.lothrazar.cyclic.gui.ScreenBase;
import com.lothrazar.cyclic.gui.TextureEnum;
import com.lothrazar.cyclic.registry.TextureRegistry;
import com.lothrazar.library.core.Const;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.neoforged.neoforge.network.PacketDistributor;

public class ScreenFilterCard extends ScreenBase<ContainerFilterCard> {

  private ButtonTextured btnType;
  private ButtonTextured btnTagMatch;
  private final ContainerFilterCard screenContainer;

  public ScreenFilterCard(ContainerFilterCard screenContainer, Inventory inv, Component titleIn) {
    super(screenContainer, inv, titleIn);
    this.screenContainer = screenContainer;
  }

  @Override
  public void render(GuiGraphics ms, int mouseX, int mouseY, float partialTicks) {
    this.renderBackground(ms, mouseX, mouseY, partialTicks);
    super.render(ms, mouseX, mouseY, partialTicks);
    this.renderTooltip(ms, mouseX, mouseY);
  }

  @Override
  public void init() {
    super.init();
    int x = leftPos + 150;
    int y = topPos + 8;
     int size = 20;
    btnType = this.addRenderableWidget(new ButtonTextured(x, y, size, size, TextureEnum.RENDER_HIDE, "", b -> {
      //pressed
      PacketDistributor.sendToServer(new PacketFilterCard(PacketFilterCard.TOGGLE_IGNORE));
      FilterCardItem.toggleFilterType(screenContainer.bag);
    }));
    size=14;
    btnTagMatch = this.addRenderableWidget(new ButtonTextured(x+3, topPos + 51, size, size, TextureEnum.CRAFT_EMPTY, "", b -> {
      //pressed
      PacketDistributor.sendToServer(new PacketFilterCard(PacketFilterCard.TOGGLE_TAGMATCH));
      FilterCardItem.toggleTagMatch(screenContainer.bag);
    }));
  }

  @Override
  protected void renderLabels(GuiGraphics ms, int mouseX, int mouseY) {
    super.renderLabels(ms, mouseX, mouseY);
    this.drawButtonTooltips(ms, mouseX, mouseY);
    boolean filter = screenContainer.bag != null && FilterCardItem.getIsIgnoreList(screenContainer.bag);
    btnType.setTextureId(filter ? TextureEnum.RENDER_HIDE : TextureEnum.RENDER_SHOW);
    btnType.setTooltip("cyclic.screen.filter." + filter);
    boolean tagMatch = screenContainer.bag != null && FilterCardItem.getIsTagMatch(screenContainer.bag);
    btnTagMatch.setTextureId(tagMatch ? TextureEnum.CRAFT_MATCH : TextureEnum.CRAFT_EMPTY);
    btnTagMatch.setTooltip("cyclic.screen.filter.tagmatch." + tagMatch);
  }

  @Override
  protected void renderBg(GuiGraphics ms, float partialTicks, int mouseX, int mouseY) {
    this.drawBackground(ms, TextureRegistry.INVENTORY);
    for (int i = 0; i < 9; i++) {
      this.drawSlot(ms, 7 + i * Const.SQ, 31);
    }
  }
}
