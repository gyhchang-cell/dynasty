package artifacts.component;

import artifacts.equipment.EquipmentSlotAccess;

@FunctionalInterface
public interface ComponentVisitor<C> {

    void visit(C component, EquipmentSlotAccess slot);

}
