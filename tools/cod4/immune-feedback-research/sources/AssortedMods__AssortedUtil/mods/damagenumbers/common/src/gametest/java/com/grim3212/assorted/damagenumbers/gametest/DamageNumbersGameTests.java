package com.grim3212.assorted.damagenumbers.gametest;

import com.grim3212.assorted.damagenumbers.Constants;
import com.grim3212.assorted.lib.test.CommonTests;
import net.minecraft.gametest.framework.GameTestHelper;

import java.util.function.BiConsumer;
import java.util.function.Consumer;

/**
 * Automated in-world checks for Assorted Damage Numbers. The tests live in small {@code <Feature>Tests} classes;
 * this only lists them. Each name needs a matching {@code data/assorteddamagenumbers/test_instance/<name>.json}.
 */
public final class DamageNumbersGameTests {

    private DamageNumbersGameTests() {
    }

    /** Every test in this mod, named once, so both loaders register the same set. */
    public static void forEach(BiConsumer<String, Consumer<GameTestHelper>> out) {
        SmokeTests.register(out);
        DamageNumbersTests.register(out);
        CommonTests.register(out, Constants.MOD_ID);
    }
}
