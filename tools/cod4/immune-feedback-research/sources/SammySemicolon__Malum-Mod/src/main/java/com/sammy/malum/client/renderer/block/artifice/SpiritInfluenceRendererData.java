package com.sammy.malum.client.renderer.block.artifice;

import com.sammy.malum.core.systems.artifice.IArtificeAcceptor;
import com.sammy.malum.core.systems.spirit.SpiritArcanaType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;

import java.util.HashMap;
import java.util.WeakHashMap;

public class SpiritInfluenceRendererData extends HashMap<SpiritArcanaType, Integer> {

    public static final WeakHashMap<IArtificeAcceptor, SpiritInfluenceRendererData> SPIRIT_INFLUENCE = new WeakHashMap<>();

    private long gameTimeCache;

    public SpiritInfluenceRendererData() {
        super();
    }

    private SpiritInfluenceRendererData tickData(IArtificeAcceptor target) {
        ClientLevel level = Minecraft.getInstance().level;
        if (level.getGameTime() == gameTimeCache) {
            return this;
        }
        gameTimeCache = level.getGameTime();
        var activeSpiritType = target.getActiveSpiritType();
        if (activeSpiritType != null) {
            merge(activeSpiritType, 1, (a, b) -> Math.min(a + b, maxValue()));
        }
        for (SpiritArcanaType spiritType : keySet()) {
            if (spiritType.equals(activeSpiritType)) {
                continue;
            }
            merge(spiritType, 1, (a, b) -> Math.max(a - b, 0));
        }
        return this;
    }

    public float getDelta(SpiritArcanaType spiritType) {
        return getOrDefault(spiritType, 0) / (float) maxValue();
    }

    public int maxValue() {
        return 60;
    }

    public static SpiritInfluenceRendererData getSpiritInfluenceData(IArtificeAcceptor target) {
        if (!SPIRIT_INFLUENCE.containsKey(target)) {
            SPIRIT_INFLUENCE.put(target, new SpiritInfluenceRendererData());
        }
        return SPIRIT_INFLUENCE.get(target).tickData(target);
    }
}
