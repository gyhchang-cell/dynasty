# COD4-13 native interaction acceptance

Scope: existing 15 registered `SmallInteractions` sites only. Production Java, assets,
original TODO and other workers' builds are never edited. This is read-only asset
verification, not new architectural production; no building-reference quota is claimed.

`python3 tools/cod4/interaction-acceptance/prepare.py` freezes current source and records
SHA256; `cp -cR` uses separate APFS clone files for the private Gradle home. All build
output, world data, caches and frozen inputs are in `.work/` (ignored).

`sh tools/cod4/interaction-acceptance/run.sh UNIQUE_WORLD` runs the main suite.
`sh tools/cod4/interaction-acceptance/run.sh UNIQUE_WORLD dynasty_interaction_extra_qa`
runs the independent full 2400-tick sword dance. Preserve earlier worlds and logs.
Runtime observations are written under the required audit directory. Archive this JSON
before another run because the JVM's record list starts anew. A Gradle success alone
never counts as successful native execution: require GameTestServer's final test result.

- Calls existing `TravelSitePiece.postProcess` once per real chunk clipping box; uses
  inherited `StructurePiece` world transforms. Three styles x four orientations,
  all15 sites x both LIT states =120 placement/shape/collision observations.
- This checks the production piece's placement branch. It does not measure natural
  biome/seed frequency, terrain selection by `Structure.findGenerationPoint`, or GUI.
  The production natural structure currently constructs NORTH-facing pieces; other
  orientations exercise the existing native transform via a QA-only subclass.
- Native ServerLevel chunks are explicitly forced in this playerless harness, as real
  players would keep nearby entity sections accessible. `getChunk` alone does not
  maintain NPC tracking for 2400 ticks. ServerLevel warns that stair post-processing
  is unsupported outside WorldGenRegion; interaction placement and collision use the
  actual resulting states. This is not an assertion about all roof/stair worldgen.
- Native ServerboundUseItemOnPacket far rejection has near positive controls. Direct
  internal BlockState.use is separately audited; a missing internal guard must not be
  reported as proven remote packet exploitation.
- Timers advance through real GameTestServer world ticks, without editing *_start,
  *_next, native Last or done flags. GameTestServer runs accelerated, so3600 ticks are
  three minutes at20TPS, not a claim of three minutes wall time.
- Historical native test copies are marked explicitly; they preseed deadlines to test
  legacy/clone/negative boundaries. They are not full elapsed-time observations.
- Two constructed ServerPlayer instances exercise independent NBT and native entity
  ownership; this is not human multiplayer or authenticated network-client evidence.
