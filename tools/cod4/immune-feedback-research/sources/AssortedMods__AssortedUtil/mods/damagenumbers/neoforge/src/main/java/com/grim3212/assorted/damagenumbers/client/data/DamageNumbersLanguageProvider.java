package com.grim3212.assorted.damagenumbers.client.data;

import com.grim3212.assorted.lib.data.LibLanguageProvider;
import com.grim3212.assorted.damagenumbers.Constants;
import net.minecraft.data.PackOutput;

/** Generates the en_us.json of this mod. */
public class DamageNumbersLanguageProvider extends LibLanguageProvider {

    /** A blank line between paragraphs; the manual splits its text the way the font does. */
    private static final String BREAK = "\n\n";

    public DamageNumbersLanguageProvider(PackOutput output) {
        super(output, Constants.MOD_ID);
    }

    @Override
    protected void addNames() {
        this.add("hud.assorteddamagenumbers.damage.melee", "Melee");
        this.add("hud.assorteddamagenumbers.damage.projectile", "Projectile");
        this.add("hud.assorteddamagenumbers.damage.explosion", "Explosion");
        this.add("hud.assorteddamagenumbers.damage.fire", "Fire");
        this.add("hud.assorteddamagenumbers.damage.magic", "Magic");
        this.add("hud.assorteddamagenumbers.damage.freezing", "Freezing");
        this.add("hud.assorteddamagenumbers.damage.lightning", "Lightning");
        this.add("hud.assorteddamagenumbers.damage.drowning", "Drowning");
        this.add("hud.assorteddamagenumbers.damage.fall", "Fall");
        this.add("hud.assorteddamagenumbers.damage.starvation", "Starvation");
        this.add("hud.assorteddamagenumbers.damage.cactus", "Cactus");
        this.add("hud.assorteddamagenumbers.damage.generic", "Generic");
        this.add("hud.assorteddamagenumbers.damage.healing", "Heal");

        this.addManual();
    }

    /** The chapters in {@code assets/assortedutil/manual} name these keys. */
    private void addManual() {
        this.add("manual.assortedutil.title", "Assorted Util");
        this.add("manual.assortedutil.description", "Graves, double doors, an item replacer, a clock, a light level overlay and damage numbers.");

        this.add("manual.assortedutil.chapter.damage_numbers", "Damage Numbers");
        this.add("manual.assortedutil.chapter.damage_numbers.info.title", "Damage Numbers");
        this.add("manual.assortedutil.chapter.damage_numbers.info",
                "Damage and healing pop off creatures as numbers, with what caused it beside them." + BREAK
                        + "A hit by a player will say the weapon, and a hit by a creature names the creature.");
    }
}
