package artifacts.client.item.model;

import artifacts.client.item.EquipmentRenderState;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.state.HumanoidRenderState;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.world.entity.HumanoidArm;
import org.jetbrains.annotations.Nullable;

public class PocketPistonModel extends HumanoidModel<HumanoidRenderState> {

    private final @Nullable ModelPart leftPistonHead;
    private final @Nullable ModelPart rightPistonHead;

    public PocketPistonModel(ModelPart modelPart) {
        super(modelPart, RenderTypes::armorCutoutNoCull);
        this.leftPistonHead = leftArm.hasChild("artifact")
                ? leftArm.getChild("artifact").getChild("piston_head")
                : null;
        this.rightPistonHead = rightArm.hasChild("artifact")
                ? rightArm.getChild("artifact").getChild("piston_head")
                : null;
    }

    @Override
    public void setupAnim(HumanoidRenderState renderState) {
        super.setupAnim(renderState);
        ModelPart mainHandPistonHead = getPistonHead(renderState.mainArm);
        ModelPart offHandPistonHead = getPistonHead(renderState.mainArm.getOpposite());

        if (mainHandPistonHead != null) {
            mainHandPistonHead.y = EquipmentRenderState.from(renderState).pocketPistonExtensionLength * 2;
        }
        if (offHandPistonHead != null){
            offHandPistonHead.y = 0;
        }
    }

    private @Nullable ModelPart getPistonHead(HumanoidArm arm) {
        return arm == HumanoidArm.LEFT ? leftPistonHead : rightPistonHead;
    }
}
