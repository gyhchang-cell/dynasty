package com.sammy.malum.client.renderer;

import com.sammy.malum.client.renderer.entity.*;
import com.sammy.malum.client.renderer.entity.activator.*;
import com.sammy.malum.client.renderer.entity.cultist.altar.*;
import com.sammy.malum.client.renderer.entity.cultist.believer.*;
import com.sammy.malum.client.renderer.entity.cultist.cardinal.*;
import com.sammy.malum.client.renderer.entity.cultist.cherub.*;
import com.sammy.malum.client.renderer.entity.cultist.evangelist.*;
import com.sammy.malum.client.renderer.entity.nitrate.*;
import com.sammy.malum.client.renderer.entity.weapon.scythe.*;
import com.sammy.malum.client.renderer.entity.weapon.staff.*;
import com.sammy.malum.registry.common.entity.*;
import net.minecraft.client.renderer.entity.*;
import net.neoforged.neoforge.client.event.*;

import static net.minecraft.client.renderer.entity.EntityRenderers.register;

public class EntityRenderers {

    public static void bindEntityRenderers(EntityRenderersEvent.RegisterRenderers event) {
        register(MalumCultistEntityTypes.ALTAR.get(), AltarRenderer::new);
        register(MalumCultistEntityTypes.CHERUB.get(), CherubRenderer::new);
        register(MalumCultistEntityTypes.BELIEVER.get(), BelieverRenderer::new);
        register(MalumCultistEntityTypes.CARDINAL.get(), CardinalRenderer::new);
        register(MalumCultistEntityTypes.EVANGELIST.get(), EvangelistRenderer::new);

        register(MalumCultistEntityTypes.CURSED_BOLT.get(), CultistBoltRenderer::new);
        register(MalumCultistEntityTypes.CULTIST_BLESSING.get(), CultistBlessingRenderer::new);
        register(MalumCultistEntityTypes.ENTROPY_CHARGE.get(), EntropyChargeRenderer::new);

        register(MalumEntityTypes.SOUL_TAG_ENTITY.get(), SoulTagRenderer::new);

        register(MalumEntityTypes.ASCENDING_BLOCK.get(), AscendingBlockRenderer::new);
        register(MalumEntityTypes.PILLOW_SEAT.get(), NoopRenderer::new);


        register(MalumEntityTypes.NATURAL_SPIRIT.get(), FloatingItemRenderer::new);

        register(MalumEntityTypes.SCYTHE_BOOMERANG.get(), ScytheBoomerangRenderer::new);
        register(MalumEntityTypes.SCYTHE_MAELSTROM.get(), NoopRenderer::new);

        register(MalumEntityTypes.GLUTTONY_LOCUST.get(), GluttonyLocustRenderer::new);

        register(MalumEntityTypes.ETHERIC_NITRATE.get(), EthericNitrateRenderer::new);
        register(MalumEntityTypes.VIVID_NITRATE.get(), VividNitrateRenderer::new);

        register(MalumEntityTypes.SPELLWEAVER_TOOL_EFFECT_ACTIVATOR.get(), SpellweaverToolEffectActivatorRenderer::new);
        register(MalumEntityTypes.RITE_ENTITY_EFFECT_ACTIVATOR.get(), EntityRiteEffectActivatorRenderer::new);
        register(MalumEntityTypes.RITE_BLOCK_EFFECT_ACTIVATOR.get(), BlockRiteEffectActivatorRenderer::new);
        register(MalumEntityTypes.RITE_BLOCK_WAVE_EFFECT_ACTIVATOR.get(), BlockRiteEffectWaveActivatorRenderer::new);

        register(MalumEntityTypes.SPIRIT_COLLECTION_ACTIVATOR.get(), SpiritCollectionActivatorRenderer::new);
        register(MalumEntityTypes.HIDDEN_BLADE_DELAYED_IMPACT.get(), NoopRenderer::new);

        register(MalumEntityTypes.HEX_BOLT.get(), HexBoltRenderer::new);
        register(MalumEntityTypes.DRAINING_BOLT.get(), DrainingBoltRenderer::new);
        register(MalumEntityTypes.ENTROPIC_FLAME_BOLT.get(), EntropicFlameBoltRenderer::new);

        register(MalumEntityTypes.SUNDERING_ANCHOR.get(), SunderingAnchorRenderer::new);
        register(MalumEntityTypes.RESENTMENT_RITUAL.get(), ResentmentRitualActivatorRenderer::new);

    }
}