package com.grim3212.assorted.damagenumbers.client.data;

import com.grim3212.assorted.lib.data.LibManualProvider;
import com.grim3212.assorted.damagenumbers.Constants;
import net.minecraft.data.PackOutput;
import net.minecraft.resources.Identifier;

/** This mod's chapter of the Assorted Util section, which every Util mod shares. */
public class DamageNumbersManualProvider extends LibManualProvider {

    /** Every picture is the page's full width, 16:9, as in the other Assorted manuals. */
    private static final int PICTURE_WIDTH = 152;
    private static final int PICTURE_HEIGHT = 86;

    public DamageNumbersManualProvider(PackOutput output) {
        super(output, Constants.MOD_ID, Constants.FAMILY_ID);
    }

    @Override
    protected void addChapters() {
        this.chapter("damage_numbers", 50).image("info", picture("damage_numbers"), PICTURE_WIDTH, PICTURE_HEIGHT);
    }

    /** In-game screenshots under {@code textures/gui/manual}. */
    private static Identifier picture(String name) {
        return Identifier.fromNamespaceAndPath(Constants.MOD_ID, "textures/gui/manual/" + name + ".png");
    }
}
