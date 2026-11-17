package com.sammy.malum.client.model;

import net.minecraft.client.model.geom.*;

//TODO: This is pointless actually
public class CachedModelPart {

    private final ModelPart part;
    private final float baseX, baseY, baseZ;
    private final float baseXScale, baseYScale, baseZScale;
    private final float baseXRot, baseYRot, baseZRot;

    private CachedModelPart(ModelPart part) {
        this.part = part;
        this.baseX = part.x;
        this.baseY = part.y;
        this.baseZ = part.z;
        this.baseXScale = part.xScale;
        this.baseYScale = part.yScale;
        this.baseZScale = part.zScale;
        this.baseXRot = part.xRot;
        this.baseYRot = part.yRot;
        this.baseZRot = part.zRot;
    }

    public static CachedModelPart of(ModelPart part) {
        return new CachedModelPart(part);
    }

    public ModelPart getPart() {
        return part;
    }

    public void reset() {
        applyOffset(0, 0, 0);
        applyScale(1, 1, 1);
        applyRotation(0, 0, 0);
    }

    public void applyOffset(float x, float y, float z) {
        part.x = baseX + x;
        part.y = baseY + y;
        part.z = baseZ + z;
    }

    public void applyScale(float xScale, float yScale, float zScale) {
        part.xScale = baseXScale * xScale;
        part.yScale = baseYScale * yScale;
        part.zScale = baseZScale * zScale;
    }

    public void applyRotation(float xRot, float yRot, float zRot) {
        part.xRot = baseXRot + xRot;
        part.yRot = baseYRot + yRot;
        part.zRot = baseZRot + zRot;
    }

    public void setVisible(boolean visible) {
        part.visible = visible;
    }

    public void copyFrom(ModelPart other) {
        part.copyFrom(other);
    }

    public ModelPart getChild(String name) {
        return part.getChild(name);
    }
}