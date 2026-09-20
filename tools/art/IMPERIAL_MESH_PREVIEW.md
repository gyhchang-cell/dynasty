# Actual mesh inspection

This viewer exports and displays the **same vertices and material colors as the compiled game**. It is not a separate concept model, SVG painter rendering, AI illustration, or Minecraft screenshot. Opaque surfaces write into a real depth buffer, preventing hidden interior faces from bleeding through the outside. Studio lighting is explicitly a review aid; the in-game result must be tested separately. This tool does not export UVs or render the added brocade/cloth bitmap textures; its PNGs are untextured geometry/material checks, not a complete preview of the latest game renderer.

## Export and serve

From the project root, after compiling the Java runtime:

```sh
sh tools/art/export_imperial_meshes.sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open the local preview:

```text
http://127.0.0.1:8765/tools/art/imperial-mesh-viewer.html
```

Optional query parameters:

- `model=guanyu`, `model=jade_dragon`, `model=gold_dragon`
- `view=front`, `view=side`, `view=back`, `view=threequarter`, `view=portrait`, `view=four`
- `data=/build/imperial-mesh-preview/before/meshes.json` for the preserved old mesh
- `lighting=studio` for optional studio highlights/shadows; default mode mirrors the runtime material shader at full scene light (without fog)

Drag to orbit, scroll to zoom. Four-view mode checks front, side, back, and three-quarter silhouette simultaneously. Head detail is a closer view of the **same** mesh. Formation clips at the rising height plane. Normal mode is useful for detecting shading seams and incorrect winding. The page sets `window.imperialPreviewReady = true` after a rendered frame for screenshot automation.

## Geometry QA

The exporter rejects missing meshes, non-finite vertices, outliers outside ±64 blocks, material indices outside the exported palette, and more than 5% zero-area quads. Its review ceilings match the dedicated verifiers: fewer than 120,000 Guan Yu quads and at most 45,000 quads per dragon. The final dragon's layered mane, facial anatomy and individually shaped scales use about 43,000 quads. It reports exact bounds, face count, degenerate-face count and material counts. Quad vertices are retained in the JSON. The viewer splits them into triangles using the same diagonal, `a-b-c` and `a-c-d`, for proper depth testing.

The old `GuanYuPreview` and `ImperialWeaponPreview` SVG tools remain geometry/layout diagnostics, with their finite-value and animation checks intact. Their obsolete pre-remaster limits were updated to the same bounded budgets: fewer than 120,000 guardian quads and 90,000 surfaces for a panel containing two dragons. They do **not** validate current opaque lighting or depth ordering. Their SVGs are labelled accordingly; use the depth-buffered viewer/PNG tool for model appearance.

## Generated data location

Large JSON exports are build artifacts, not source assets. The default export is `build/imperial-mesh-preview/after/meshes.json`, under the existing Git-ignored `build/` directory. The preserved pre-remaster export lives at `build/imperial-mesh-preview/before/meshes.json`. Both files created during this remaster were moved there intact, rather than deleted; comparison PNGs remain in `docs/art/imperial-remaster/`. A future clean build may remove these JSON caches, so copy the before snapshot outside `build/` yourself if long-term raw-mesh archiving is desired. The delivered comparison PNGs are not affected by cleaning build artifacts.

Normals are area-weighted across positions quantized to 1e-6 and matching material. Adjacent faces with a dot product below 0.55 are kept sharp. This does not certify anatomy, weapon clearance or animation safety; those need explicit mesh-specific assertions and visual multi-angle inspection. A clean build and automated geometry checks alone do not prove artistic quality.

Run the independent current-source checks (does not launch the game or modify a world):

```sh
sh tools/art/verify_imperial_meshes.sh
```

This compiles the current geometry sources into a separate tool directory, checks Guan Yu's grip/shaft clearance, whole-weapon/body triangle intersections, finite geometry, normals, closed caps and bounds, verifies dragon anatomy/material coverage and impact transforms, runs strict scale/body clearance, neighboring scale intersections and free mane tip sampling, then runs the legacy SVG diagnostics across 242 effect animation samples. It does not rebuild the Forge renderer or prove that the shipped jar contains the same revision; build/package checks remain separate. For actual production draw-path checks under Minecraft, use the isolated harness in `tools/art/runtime-qa/README.md`.

## Deliverable images

Any screenshot of this page must be labelled **actual mesh / studio preview, not in-game**. Do not present the studio highlights or shadows as an in-game feature unless they have actually been implemented and verified there.

## Offline depth-buffered PNGs

When an interactive browser is unavailable, the Java renderer rasterizes the exact triangles into a per-pixel Z-buffer. It uses perspective-correct interpolation, the shared smooth normals and the runtime material shader's light/specular algorithm. It does not rely on polygon painter ordering. It deliberately does not invent ambient-occlusion, shadows, or cinematic environment lighting that are absent in the game renderer.

```sh
sh tools/art/render_imperial_meshes.sh build/imperial-mesh-preview/after/meshes.json docs/art/imperial-remaster/after/guanyu-four.png guanyu four
sh tools/art/render_imperial_meshes.sh build/imperial-mesh-preview/after/meshes.json docs/art/imperial-remaster/after/guanyu-head.png guanyu portrait
sh tools/art/render_imperial_meshes.sh build/imperial-mesh-preview/after/meshes.json docs/art/imperial-remaster/after/jade-dragon.png jade_dragon threequarter
```

These images remain material previews, not game screenshots. They do not validate Forge shader compilation, live animation or frame rate.
