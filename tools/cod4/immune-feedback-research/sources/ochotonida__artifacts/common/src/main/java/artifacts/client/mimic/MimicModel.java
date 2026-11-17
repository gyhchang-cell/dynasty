package artifacts.client.mimic;

import artifacts.Artifacts;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;

public class MimicModel extends EntityModel<MimicRenderState> {

    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(Artifacts.id("mimic"), "mimic");
    public static final ModelLayerLocation CHEST_LAYER_LOCATION = new ModelLayerLocation(Artifacts.id("mimic_overlay"), "mimic_overlay");

    protected final ModelPart bottom;
    protected final ModelPart lid;

    public MimicModel(ModelPart root) {
        super(root);
        bottom = root.getChild("bottom");
        lid = root.getChild("lid");
    }

    @Override
    public void setupAnim(MimicRenderState renderState) {
        super.setupAnim(renderState);
        setChestRotations(renderState);
    }

    protected void setChestRotations(MimicRenderState renderState) {
        if (renderState.ticksInAir > 0) {
            lid.xRot = Math.max(-60, renderState.ticksInAir * -6) * 0.0174533F;
            bottom.xRot = Math.min(30, renderState.ticksInAir * 3) * 0.0174533F;
        } else {
            lid.xRot = 0;
            bottom.xRot = 0;
        }
    }

    public static LayerDefinition createLayer() {
        MeshDefinition mesh = new MeshDefinition();

        mesh.getRoot().addOrReplaceChild(
                "bottom",
                CubeListBuilder.create()
                        .texOffs(0, 15)
                        .addBox(-6, -4, -13, 12, 3, 12)
                        .texOffs(36, 15)
                        .addBox(-6, -1, -13, 12, 0, 12, new CubeDeformation(0.02F)),
                PartPose.offset(0, 15, 7)
        );
        mesh.getRoot().addOrReplaceChild(
                "lid",
                CubeListBuilder.create()
                        .texOffs(0, 0) // teeth
                        .addBox(-6, 0, -13, 12, 3, 12)
                        .texOffs(24, 0) // overlay
                        .addBox(-6, 0, -13, 12, 0, 12, new CubeDeformation(0.02F)),
                PartPose.offset(0, 15, 7)
        );

        return LayerDefinition.create(mesh, 64, 32);
    }

    public static LayerDefinition createChestLayer() {
        MeshDefinition mesh = new MeshDefinition();

        mesh.getRoot().addOrReplaceChild(
                "bottom",
                CubeListBuilder.create()
                        .texOffs(0, 19)
                        .addBox(1, -9, 0, 14, 10, 14),
                PartPose.offset(0, 9, 1)
        );
        mesh.getRoot().addOrReplaceChild(
                "lid",
                CubeListBuilder.create()
                        .texOffs(0, 0)
                        .addBox(1, 0, 0, 14, 5, 14)
                        .texOffs(0, 0) // latch
                        .addBox(7, -1 - 1, 15 - 1, 2, 4, 1),
                PartPose.offset(0, 9, 1)
        );

        return LayerDefinition.create(mesh, 64, 64);
    }
}
