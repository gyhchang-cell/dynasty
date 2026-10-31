package artifacts.neoforge.integration.curios;

import artifacts.equipment.EquipmentSlotManager;
import artifacts.event.ArtifactHooks;
import artifacts.integration.ModCompat;
import artifacts.util.DamageSourceHelper;
import net.neoforged.neoforge.common.NeoForge;
import top.theillusivec4.curios.api.common.DropRule;
import top.theillusivec4.curios.api.event.CurioChangeEvent;
import top.theillusivec4.curios.api.event.DropRulesEvent;

public class CuriosCompat {

    public static void setup() {
        if (!ModCompat.CCLAYER.isLoaded()) {
            EquipmentSlotManager.register(new CuriosSlotProvider());
        }

        NeoForge.EVENT_BUS.addListener(
                (CurioChangeEvent.State event) -> ArtifactHooks.onItemChanged(event.getEntity(), event.getFrom(), event.getTo())
        );
        NeoForge.EVENT_BUS.addListener(
                (CurioChangeEvent.Item event) -> ArtifactHooks.onItemChanged(event.getEntity(), event.getFrom(), event.getTo())
        );
        NeoForge.EVENT_BUS.addListener(CuriosCompat::onDropItem);
    }

    private static void onDropItem(DropRulesEvent event) {
        event.addOverride(stack -> DamageSourceHelper.shouldDestroyWornItemOnDeath(event.getEntity(), stack), DropRule.DESTROY);
    }
}
