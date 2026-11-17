package com.sammy.malum.registry.client;

import com.sammy.malum.client.model.armor.MalignantStrongholdArmorModel;
import com.sammy.malum.client.model.armor.SoulHunterArmorModel;
import com.sammy.malum.client.model.armor.SoulStainedSteelArmorModel;
import com.sammy.malum.client.model.armor.pride.PridewearArmorModel;
import com.sammy.malum.client.model.armor.pride.SlimPridewearArmorModel;

import com.sammy.malum.client.model.mob.altar.AltarModel;
import com.sammy.malum.client.model.mob.believer.BelieverModel;
import com.sammy.malum.client.model.mob.cardinal.CardinalModel;
import com.sammy.malum.client.model.mob.cherub.CherubModel;
import com.sammy.malum.client.model.mob.evangelist.EvangelistModel;
import net.neoforged.neoforge.client.event.*;

public class MalumModels {

    public static void registerLayerDefinitions(EntityRenderersEvent.RegisterLayerDefinitions event) {
        event.registerLayerDefinition(AltarModel.LAYER, AltarModel::createBodyLayer);
        event.registerLayerDefinition(BelieverModel.LAYER, BelieverModel::createBodyLayer);
        event.registerLayerDefinition(CherubModel.LAYER, CherubModel::createBodyLayer);
        event.registerLayerDefinition(CardinalModel.LAYER, CardinalModel::createBodyLayer);
        event.registerLayerDefinition(EvangelistModel.LAYER, EvangelistModel::createBodyLayer);

        SoulHunterArmorModel.MODEL.register(event);
        SoulStainedSteelArmorModel.MODEL.register(event);
        MalignantStrongholdArmorModel.MODEL.register(event);

        PridewearArmorModel.MODEL.register(event);
        SlimPridewearArmorModel.MODEL.register(event);
    }

    public static void addLayers(EntityRenderersEvent.AddLayers event) {
        SoulHunterArmorModel.MODEL.bake(event);
        SoulStainedSteelArmorModel.MODEL.bake(event);
        MalignantStrongholdArmorModel.MODEL.bake(event);

        PridewearArmorModel.MODEL.bake(event);
        SlimPridewearArmorModel.MODEL.bake(event);
    }
}