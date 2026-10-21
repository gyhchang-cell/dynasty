# Dynasty CurseForge export

Build only the CF distribution:

```sh
python3 tools/art/make_uploadable_packs.py --platform curseforge
python3 -m unittest discover -s tools/art -p test_curseforge_export.py -v
```

`curseforge.lock.json` is independent of the shared QOL/FTB registrations and
Modrinth index. It records every release dependency's installed filename and
SHA-1/SHA-256/SHA-512, plus its distribution identity and exact distribution hashes.
The exporter requires curl, Python 3.11+, Java 11+, and Maven Artifact 3.8.8 /
Commons Lang already downloaded into the user's Gradle cache by this project.
It does not build or edit the core.

Every export rechecks public CF metadata through `api.curse.tools/v1/cf`, downloads
all locked CF files from the API's official CF download URLs, verifies every hash,
and checks `isAvailable`, approval status, loader, identity and dependency metadata.
CFWidget was used for discovery, not as the hash authority. All 79 CF files were
available and approved when checked on 2026-10-21.

The remaining three releases are explicitly on CF's linked approved non-CF list:
MemoryLeakFix, Noisium, and ToroHealth Damage Indicators (Updated). Their exact
installed versions are retained in overrides, fetched from the registered official
Modrinth CDN URLs and hash-verified. The exporter rechecks their list membership on
every run. In particular, archived Noisium is not referenced using an unavailable
old CF file ID. The approval sheet has inconsistent author/license columns in some
rows; membership is checked by its actual mod-name column, not inferred from those
columns. Noisium is listed as both `Noisium` and `noisium`.

References:

- [CF submission/export rules](https://support.curseforge.com/support/solutions/articles/9000198500-exporting-a-modpack-for-curseforge-project-submission)
- [CF non-CurseForge policy and official list link](https://support.curseforge.com/support/solutions/articles/9000197913-non-curseforge-mods)
- [Approved list: K–O, including MemoryLeakFix and Noisium](https://docs.google.com/spreadsheets/d/176Wv-PZUo9hFxy6oC6N8tWdquBLPRtSuLbNK-r0_byM/edit#gid=2137482024)
- [Approved list: P–T, including ToroHealth Updated](https://docs.google.com/spreadsheets/d/176Wv-PZUo9hFxy6oC6N8tWdquBLPRtSuLbNK-r0_byM/edit#gid=755531188)
- [CFWidget API](https://cfwidget.com/)

All 82 external mod versions are preserved. Eleven CF binaries differ from the
installed cross-platform JARs only in `META-INF/MANIFEST.MF`; every other ZIP entry
was compared byte-for-byte. The lock explicitly records both hashes and this
substitution. Crafting Tweaks, TrashSlot, Sophisticated Backpacks and GeckoLib
4.8.4 use available official CF references, never embedded JARs. The existing
custom Dynasty core remains an unchanged override.

Validation reconstructs all 83 JARs, recursively reads Forge mods.toml and JarJar
metadata, rejects duplicate top-level mod IDs, checks mandatory dependency
presence and uses Forge's Maven Artifact version parser for ranges. There are
185 mandatory dependency checks. CF project dependency coverage is also checked.
One metadata exception is explicit in the lock: Great Scrollable Tooltips' Forge
file incorrectly lists Fabric API as required; its actual Forge TOML requires
only Minecraft and Forge. Fabric API is therefore not installed on Forge.

Missing, extra or changed installed dependency JARs, unavailable CF files, revoked
third-party approval, changed metadata/download hashes and unresolved mappings
stop the export before replacing the previous ZIP. There is no removal fallback.
Workshop WorldEdit remains excluded under the existing export policy.

Outputs are `dist/dynasty-modpack-1.4.0.zip` and the adjacent `.validation.json`
receipt containing the archive SHA-256, complete file mappings/hashes, dependency
checks, explicit metadata exceptions, and unresolved list. The Desktop copy is
copied only after successful validation; invoke this builder for future exports
and copy that ZIP to the Desktop distribution directory as needed.

Validation covers packaging, online availability, exact bytes and dependency
metadata. CF moderation and an in-game launch are separate checks; no upload was
performed by this repair.
