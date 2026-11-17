package com.sammy.malum.registry.client;

import com.sammy.malum.MalumMod;
import team.lodestar.lodestone.systems.rendering.rendeertype.*;

import static com.sammy.malum.MalumMod.*;
import static team.lodestar.lodestone.LodestoneLib.*;

public class MalumRenderTypeTokens {

    public static final RenderTypeToken CONCENTRATED_TRAIL = RenderTypeToken.createToken(malumPath("textures/vfx/concentrated_trail.png"));
    public static final RenderTypeToken TWINKLE = RenderTypeToken.createToken(lodestonePath("textures/particle/twinkle.png"));
    public static final RenderTypeToken STAR = RenderTypeToken.createToken(malumPath("textures/particle/star.png"));

    public static final RenderTypeToken DEBUG_GIZMO = RenderTypeToken.createToken(malumPath("textures/particle/funky_star.png"));

    public static final RenderTypeToken DIODE_LOCKED = RenderTypeToken.createToken(malumPath("textures/block/waveform_artifice/runewood_frame_locked_overlay.png"));
    public static final RenderTypeToken DIODE_INPUT = RenderTypeToken.createToken(malumPath("textures/block/waveform_artifice/runewood_frame_input_overlay.png"));

    public static final RenderTypeToken WIND_COVERAGE_BORDER = RenderTypeToken.createToken(malumPath("textures/block/artifice/wind_tunnel/wind_border.png"));
    public static final RenderTypeToken WIND_TUNNEL = RenderTypeToken.createToken(malumPath("textures/block/artifice/wind_tunnel/wind_tunnel.png"));
    public static final RenderTypeToken WIND_STREAKS = RenderTypeToken.createToken(malumPath("textures/block/artifice/wind_tunnel/wind_streaks.png"));

    public static final RenderTypeToken PYLON_GLOW_TOP = RenderTypeToken.createToken(MalumMod.malumPath("textures/vfx/arcana_pylon_glow_top.png"));
    public static final RenderTypeToken PYLON_GLOW_SIDE = RenderTypeToken.createToken(MalumMod.malumPath("textures/vfx/arcana_pylon_glow_side.png"));

    public static final RenderTypeToken RITE_ANCHOR_GLOW_TOP = RenderTypeToken.createToken(MalumMod.malumPath("textures/vfx/rite_anchor_glow_top.png"));
    public static final RenderTypeToken RITE_ANCHOR_GLOW_SIDE = RenderTypeToken.createToken(MalumMod.malumPath("textures/vfx/rite_anchor_glow_side.png"));
    public static final RenderTypeToken RITE_ANCHOR_GLOW_POINTER = RenderTypeToken.createToken(MalumMod.malumPath("textures/vfx/rite_anchor_glow_pointer.png"));
    public static final RenderTypeToken RITE_ANCHOR_GLOW_POINTER_SMALL = RenderTypeToken.createToken(MalumMod.malumPath("textures/vfx/rite_anchor_glow_pointer_small.png"));


    public static final RenderTypeToken AREA_COVERAGE_BORDER = RenderTypeToken.createToken(malumPath("textures/vfx/area_coverage_border.png"));
    public static final RenderTypeToken AREA_COVERAGE_SQUIGGLES = RenderTypeToken.createToken(malumPath("textures/vfx/area_coverage_squiggles.png"));
    public static final RenderTypeToken AREA_COVERAGE_CHECKERBOARD = RenderTypeToken.createToken(malumPath("textures/vfx/area_coverage_checkerboard.png"));

    public static final RenderTypeToken VOID_VIGNETTE = RenderTypeToken.createToken(malumPath("textures/vfx/void_vignette.png"));
    public static final RenderTypeToken VOID_NOISE = RenderTypeToken.createToken(malumPath("textures/vfx/void_noise.png"));

    public static final RenderTypeToken SCARF = RenderTypeToken.createToken(malumPath("textures/vfx/scarf/default.png"));

}
