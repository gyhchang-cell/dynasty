# Dragon surface QA — geometry-only pass

This check used the actual `ImperialDragonMesh.FACES`, not an illustration or substitute display mesh. No shader, renderer, gameplay, damage or impact landmark was changed in this pass.

## Confirmed issue and correction

The raised body scales were wider/longer than the spacing of the staggered rows. A strict triangle/triangle crossing check found **3,263 intersecting pairs of neighboring scales**. These were not shared edges: an edge of one triangle passed through the interior plane and area of another triangle. This is a real geometry issue; it can produce irregular crossing ridges regardless of screenshot antialiasing.

The scale footprint was narrowed to fit its row and adjacent staggered columns. Face count remains **43,272**, with the same skin, mane, limbs, muzzle landmark and golden/jade palettes. Neighbor tests now report **0 crossing pairs** among 842 overlapping bounding-box candidates. The correction does not add any geometry.

## Results after correction

- 1,147 body scales; 100,936 internal triangle samples traced against the actual underlying body triangles.
- Sampled scale/body separation: minimum **0.001426048**, maximum **0.008188568** model units.
- Sampled penetration: **0**; near-coplanar samples within 0.00005 model units: **0**.
- Folded scale quads: **0**; minimum cosine between the two triangle normals in a quad: **0.761986**.
- Free mane tips: **2,040** samples checked against the closed skull; **0** were inside it. Attached hair roots are intentionally embedded and excluded from this free-tip test.
- General mesh checks still pass: finite vertices, nonzero face area, bounded geometry, unit smoothed normals, complete dual dragons, inward golden guardian facing, and exact compensated nose landing at age 20.

## What this does not claim

The body clearance and hair-tip checks are dense sampling, not a formal proof covering every point or every part of the model. The renderer deliberately uses dark scale bevels and recessed skin, which remain visible as normal material contrast. Small jaggies on extremely thin hairs in the CPU PNG may still be rasterization/antialiasing artifacts; this pass does not label them an in-game rendering bug. Actual Minecraft visual/performance verification is separate.

## Repeatable check

Compile `tools/art/VerifyDragonSurfaceClearance.java` against the current pure geometry classes, then run `VerifyDragonSurfaceClearance --strict`. The diagnostic asserts the known 100-by-28 base sweep and current mane-bundle layout; update the sampling map if those generator structures change.

The exact-mesh image produced for review is `build/dragon-remaster-check/dragon-clearance-fixed.png`. It is a Z-buffered model preview, not a Minecraft screenshot.
