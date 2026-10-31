package com.sammy.malum.registry.client;

import com.sammy.malum.client.extensions.*;
import com.sammy.malum.client.model.armor.MalignantStrongholdArmorModel;
import com.sammy.malum.client.model.armor.SoulHunterArmorModel;
import com.sammy.malum.client.model.armor.SoulStainedSteelArmorModel;
import net.neoforged.neoforge.client.extensions.common.*;
import team.lodestar.lodestone.modules.rendering.model.entity.armor.*;

import static com.sammy.malum.registry.common.MalumContent.*;
import static com.sammy.malum.registry.common.MalumContent.Gear.*;
import static com.sammy.malum.registry.common.MalumContent.Sorcery.*;

public class MalumClientExtensions {

    public static void registerClientExtensions(RegisterClientExtensionsEvent event) {
        event.registerItem(new SpiritJarItemExtension(), SPIRIT_JAR.asItem());
        event.registerItem(new GeasItemExtension(), GEAS);

        event.registerItem(new LodestoneArmorClientItemExtensions(SoulHunterArmorModel.MODEL),
                SOUL_HUNTER_CLOAK, SOUL_HUNTER_ROBE, SOUL_HUNTER_LEGGINGS, SOUL_HUNTER_BOOTS);
        event.registerItem(new LodestoneArmorClientItemExtensions(SoulStainedSteelArmorModel.MODEL),
                SOUL_STAINED_STEEL_HELMET, SOUL_STAINED_STEEL_CHESTPLATE, SOUL_STAINED_STEEL_LEGGINGS, SOUL_STAINED_STEEL_BOOTS);
        event.registerItem(new MalignantArmorItemExtensions(() -> MalignantStrongholdArmorModel.MODEL.getModel()),
                MALIGNANT_STRONGHOLD_HELMET, MALIGNANT_STRONGHOLD_CHESTPLATE, MALIGNANT_STRONGHOLD_LEGGINGS, MALIGNANT_STRONGHOLD_BOOTS);
    }
}
