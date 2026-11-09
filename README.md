# Lordbound Fixes

Bug fixes for **[Lordbound](https://www.nexusmods.com/skyrimspecialedition/mods/160493)** 0.8.1 (Skyrim Special Edition, by the Lordbound Team), made by tonycubed2.

This repository holds the **documentation and the tools** used to find and build the fixes. The patch itself (`Lordbound Fixes.esp` and the patched scripts) is **not** included here, because it modifies the Lordbound Team's records and scripts and redistributing it needs their permission.

## What was fixed

21 reported bugs fixed, 5 ruled out as not Lordbound bugs. Highlights:

- **143 empty script properties** filled. The authors declared and used them in scripts but never filled them in the Creation Kit, so stages, scenes and triggers silently did nothing (Ill Omens, the Empyrean Vault Catacombs stall, Grave of the First, Monuments of Sin, Enigmatic Origins and more).
- Quest dead-ends: The Masters of Highreach, Just Deserts, The Lost Children, Kinslayer, Wrath, The Sacking of Garshakur, Marks of a Fighter, Chasing Dreams counters, The Lost Legion appearing at the end.
- Wrong door landing spots, missing models, a lootable decoration, dev test-room spell tomes with broken effects.
- **No purple textures left**: missing textures found under the wrong name or folder in Lordbound itself, fixed name typos against the base game, and matched the rest from other mods (UVs checked where a texture was reused on a different model).
- All 3,045 of Lordbound's old-format (LE) meshes converted to SE with SSE NIF Optimizer and checked.

Full details:

| File | Contents |
|---|---|
| [docs/full-fix-list.txt](docs/full-fix-list.txt) | Every fix, plus the filled properties grouped by quest |
| [docs/detailed-changes.txt](docs/detailed-changes.txt) | Exact records (form IDs), conditions and script changes for each fix |
| [docs/README.txt](docs/README.txt) | Install steps, in-game test points, and what is still open |
| [docs/missing-textures.txt](docs/missing-textures.txt) | Textures Lordbound's meshes need but does not ship |

## Tools

Plain Python 3 (no third-party packages except `lz4` for SE archives). They read the plugin and compiled scripts directly; no xEdit or Creation Kit needed.

| File | Purpose |
|---|---|
| `esm.py` | Reads any Skyrim plugin (records, subrecords, groups, compressed records) |
| `vmad.py` / `vmadw.py` | Reads and edits script attachments and their properties |
| `pex.py` / `pexw.py` | Reads, disassembles, edits and re-writes compiled Papyrus scripts (`.pex`) |
| `espw.py` | Writes the override plugin |
| `bsa.py` / `niftex.py` | Lists and extracts from BSA archives; finds textures referenced by meshes |
| `lb.py` | Analysis helpers: quest dumps, dialogue trees, condition decoding |
| `scanprops.py` → `autofill.py` | Finds script properties that are used but never filled, and matches them to records |
| `scanstages.py` / `scandeadend.py` | Finds dialogue that needs a quest stage nothing sets, and replies that can never be chosen |
| `fixes.py` / `scriptfixes.py` | The fixes themselves (plugin records / script bytecode) |
| `dlscan3.py` / `report.py` | Searches downloaded archives (7z/zip/rar, including BSAs inside them) for missing textures and models; regenerates the missing-textures report |
| `build.py` / `verify.py` | Builds `Lordbound Fixes.esp` and checks its structure |
| `dec/Dec.java` | Batch decompiler using ReSaver's `ReSaver.jar` |

The tools expect Lordbound at `~/mnt/Lordbound` and write to `~/mnt/Lordbound Fixes` (the paths are at the top of `lb.py`, `build.py`, `scriptfixes.py` and `verify.py`). To rebuild after a Lordbound update:

```
python3 scanprops.py > unfilled.txt
```
```
python3 autofill.py
```
```
python3 scriptfixes.py
```
```
python3 build.py
```
```
python3 verify.py
```

Re-check each fix against the new version before trusting the result: the fixes target Lordbound 0.8.1's form IDs.
