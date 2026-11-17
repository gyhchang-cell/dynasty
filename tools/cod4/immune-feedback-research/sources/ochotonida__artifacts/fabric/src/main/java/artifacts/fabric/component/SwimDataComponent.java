package artifacts.fabric.component;

import artifacts.component.SwimData;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import org.ladysnake.cca.api.v3.component.ComponentV3;

public class SwimDataComponent extends SwimData implements ComponentV3 {

    private static final String IS_SWIM_FLYING = "is_swim_flying";
    private static final String SHOULD_BREAK_SURFACE_TENSION = "should_break_surface_tension";
    private static final String SWIM_FLYING_CHARGE = "swim_flying_charge";

    @Override
    public void readData(ValueInput input) {
        isSwimFlying = input.getBooleanOr(IS_SWIM_FLYING, false);
        shouldBreakSurfaceTension = input.getBooleanOr(SHOULD_BREAK_SURFACE_TENSION, false);
        swimFlyingCharge = input.getDoubleOr(SWIM_FLYING_CHARGE, 1);
    }

    @Override
    public void writeData(ValueOutput output) {
        output.putBoolean(IS_SWIM_FLYING, isSwimFlying);
        output.putBoolean(SHOULD_BREAK_SURFACE_TENSION, shouldBreakSurfaceTension);
        output.putDouble(SWIM_FLYING_CHARGE, swimFlyingCharge);
    }
}
