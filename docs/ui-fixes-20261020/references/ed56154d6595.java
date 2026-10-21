/*
 * BluSunrize
 * Copyright (c) 2024
 *
 * This code is licensed under "Blu's License of Common Sense"
 * Details can be found in the license file in the root folder of this project
 */

package blusunrize.immersiveengineering.client.gui.elements;

import blusunrize.immersiveengineering.api.Lib;
import com.google.common.base.Preconditions;
import com.mojang.blaze3d.platform.GlStateManager.DestFactor;
import com.mojang.blaze3d.platform.GlStateManager.SourceFactor;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;

public class GuiButtonIE extends Button
{
	protected final ButtonTexture texture;

	public GuiButtonIE(int x, int y, int w, int h, Component name, ButtonTexture texture, IIEPressable handler)
	{
		super(x, y, w, h, name, handler, DEFAULT_NARRATION);
		this.texture = texture;
	}

	private boolean isPressable(double mouseX, double mouseY)
	{
		return this.active&&this.visible&&mouseX >= this.getX()&&mouseY >= this.getY()&&mouseX < this.getX()+this.width&&mouseY < this.getY()+this.height;
	}

	@Override
	public void renderWidget(GuiGraphics graphics, int mouseX, int mouseY, float partialTicks)
	{
		Minecraft mc = Minecraft.getInstance();
		Font fontrenderer = mc.font;
		this.isHovered = isPressable(mouseX, mouseY);
		RenderSystem.enableBlend();
		RenderSystem.blendFuncSeparate(SourceFactor.SRC_ALPHA, DestFactor.ONE_MINUS_SRC_ALPHA, SourceFactor.ONE, DestFactor.ZERO);
		RenderSystem.blendFunc(770, 771);
		graphics.blitSprite(texture.get(this.isHovered), getX(), getY(), width, height);
		if(!getMessage().getString().isEmpty())
		{
			int txtCol = 0xE0E0E0;
			if(!this.active)
				txtCol = 0xA0A0A0;
			else if(this.isHovered)
				txtCol = Lib.COLOUR_I_ImmersiveOrange;
			graphics.drawCenteredString(fontrenderer, getMessage(), this.getX()+this.width/2, this.getY()+(this.height-8)/2, txtCol);
		}
	}

	@Override
	public void onPress()
	{
		this.onPress.onPress(this);
	}

	public interface IIEPressable<B extends Button> extends OnPress
	{
		void onIEPress(B var1);

		@Override
		default void onPress(Button var1)
		{
			this.onIEPress((B)var1);
		}
	}

	public record ButtonTexture(ResourceLocation texture, ResourceLocation hovered)
	{
		public ButtonTexture
		{
			Preconditions.checkArgument(texture!=null);
			Preconditions.checkArgument(hovered!=null);
		}

		public ButtonTexture(ResourceLocation texture)
		{
			this(texture, texture);
		}

		public ResourceLocation get(boolean hovered)
		{
			return hovered?this.hovered: texture;
		}
	}
}
