package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.SkillDefinition;
import java.util.List;

/** One server timeline per move; animation contact keys use the same tick numbers. */
public final class TemplateSkills {
    public static final int SWORD_COMBO = 1, SHIELD_COMBO = 2, TALISMAN_VOLLEY = 3,
            POSSESSION = 4, POUNCE = 5, ROCK_THROW = 6;
    public static final SkillDefinition SWORD = new SkillDefinition(SWORD_COMBO, "sword_combo",
            12, 11, 13, 46, 0, 3.2, 110, 1.0F, .2, true, true, List.of(12, 22));
    public static final SkillDefinition SHIELD = new SkillDefinition(SHIELD_COMBO, "shield_combo",
            16, 9, 7, 56, 0, 3.5, 95, 1.0F, .65, true, true, List.of(16, 24));
    public static final SkillDefinition TALISMAN = new SkillDefinition(TALISMAN_VOLLEY, "talisman_volley",
            24, 9, 17, 72, 3, 24, 90, 1.0F, .1, true, true, List.of(24, 28, 32));
    public static final SkillDefinition BUFF = new SkillDefinition(POSSESSION, "possession",
            20, 1, 19, 200, 0, 16, 360, 0, 0, true, true, List.of(20));
    public static final SkillDefinition LEAP = new SkillDefinition(POUNCE, "pounce",
            14, 11, 17, 62, 0, 7, 115, 1.15F, .35, true, true, List.of(14, 24));
    public static final SkillDefinition ROCK = new SkillDefinition(ROCK_THROW, "rock_throw",
            18, 1, 13, 76, 8, 24, 100, 1.1F, .9, true, true, List.of(18));

    private TemplateSkills() { }

    public static SkillDefinition byId(int id) {
        return switch (id) {
            case SWORD_COMBO -> SWORD;
            case SHIELD_COMBO -> SHIELD;
            case TALISMAN_VOLLEY -> TALISMAN;
            case POSSESSION -> BUFF;
            case POUNCE -> LEAP;
            case ROCK_THROW -> ROCK;
            default -> null;
        };
    }

    /** Possession accelerates the whole contact timeline, including recovery and cooldown. */
    public static SkillDefinition accelerated(SkillDefinition skill, float speed) {
        if (speed <= 1.001F) return skill;
        int windup = Math.max(1, Math.round(skill.windupTicks() / speed));
        int lastImpact = Math.round(skill.impactTicks().get(skill.impactTicks().size() - 1) / speed);
        int active = Math.max(1, lastImpact - windup + 1);
        int recovery = Math.max(1, Math.round(skill.totalTicks() / speed) - windup - active);
        return new SkillDefinition(skill.id(), skill.key(), windup, active, recovery,
                Math.max(1, Math.round(skill.cooldownTicks() / speed)), skill.minRange(), skill.maxRange(),
                skill.angleDegrees(), skill.damageMultiplier(), skill.knockback(), skill.interruptible(),
                skill.requiresSight(), skill.impactTicks().stream().map(t -> Math.round(t / speed)).distinct().toList());
    }
}
