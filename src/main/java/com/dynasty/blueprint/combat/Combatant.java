package com.dynasty.blueprint.combat;
import net.minecraft.world.entity.Entity;
public interface Combatant {
    Faction faction();
    MobRole role();
    static boolean allied(Entity a, Entity b) {
        return a == b || a.isAlliedTo(b) || a instanceof Combatant ca && b instanceof Combatant cb && ca.faction() == cb.faction()
                && !com.dynasty.blueprint.EcologyRules.predates(a,b) && !com.dynasty.blueprint.EcologyRules.predates(b,a);
    }
}
