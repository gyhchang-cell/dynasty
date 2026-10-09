package com.dynasty.blueprint.combat;
import net.minecraft.world.entity.Entity;
public interface Combatant {
    Faction faction();
    MobRole role();
    static boolean allied(Entity a, Entity b) {
        return a instanceof com.dynasty.blueprint.TemplateMob first&&b instanceof com.dynasty.blueprint.TemplateMob second
            &&!first.encounterSite().isBlank()&&first.encounterSite().equals(second.encounterSite())
            &&(first.faction()==Faction.CONSTRUCT||first.faction()==Faction.DYNASTY_ARMY)
            &&(second.faction()==Faction.CONSTRUCT||second.faction()==Faction.DYNASTY_ARMY)
            || a == b || a.isAlliedTo(b) || a instanceof Combatant ca && b instanceof Combatant cb && ca.faction() == cb.faction()
                && !com.dynasty.blueprint.EcologyRules.predates(a,b) && !com.dynasty.blueprint.EcologyRules.predates(b,a);
    }
}
