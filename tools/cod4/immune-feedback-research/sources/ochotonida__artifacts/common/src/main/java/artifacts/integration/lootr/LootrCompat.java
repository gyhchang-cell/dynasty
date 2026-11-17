package artifacts.integration.lootr;

import noobanidus.mods.lootr.common.api.LootrAPI;

public class LootrCompat {

    public static boolean useVanillaTextures() {
        return LootrAPI.isVanillaTextures();
    }
}
