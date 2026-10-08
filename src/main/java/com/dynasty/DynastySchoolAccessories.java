package com.dynasty;

import java.util.Set;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;

/** Passive equipment bonuses. Called once by the primary-hit progression handler. */
final class DynastySchoolAccessories {
    private DynastySchoolAccessories() { }

    static int count(Set<String> equipped, String school) {
        int count = 0;
        for (String id : equipped) {
            var bonus = DynastyAccessoryData.get(id);
            if (bonus != null && bonus.school().equals(school)) count++;
        }
        return count;
    }

    static double bonus(Set<String> equipped, boolean melee, boolean arrow, boolean edict, double toughness) {
        double result = 0;
        for (String id : equipped) {
            var data = DynastyAccessoryData.get(id);
            if (data == null) continue;
            result += switch (data.kind()) {
                case "melee" -> melee ? data.amount() : 0;
                case "arrow" -> arrow ? data.amount() : 0;
                case "edict" -> melee && edict ? data.amount() : 0;
                case "toughness" -> melee ? Math.min(.60, Math.max(0, toughness) * data.amount()) : 0;
                default -> 0;
            };
        }
        return result;
    }

    static double bonus(Player player, DamageSource source, Set<String> equipped) {
        boolean melee = source.is(DamageTypes.PLAYER_ATTACK) && source.getDirectEntity() == player;
        boolean arrow = source.getDirectEntity() instanceof AbstractArrow projectile && projectile.getOwner() == player;
        // Edict means the actual ritual weapon, not a sword relabelled by wearing a necklace.
        boolean edict = switch (DynastySchoolCombat.weapon(player)) {
            case "chiling_brush", "leifu_staff", "taiyi_sword", "taiyi_whisk", "hunyuan_staff", "zhuque_fan" -> true;
            default -> false;
        };
        if (EdictSpells.isSpell(source)) {
            double amount=0;
            for (String id:equipped) { var data=DynastyAccessoryData.get(id); if(data!=null && data.kind().equals("edict")) amount+=data.amount(); }
            return amount;
        }
        return bonus(equipped, melee, arrow, edict, player.getAttributeValue(Attributes.ARMOR_TOUGHNESS));
    }
}
