LORDBOUND FIXES  -  personal patch for Lordbound 0.8.1 (Nexus 160493)
=====================================================================
Files: Lordbound Fixes.esp (ESL-flagged, master: Druadach.esm), 5 patched scripts in scripts\,
and 251 textures copied from your other MO2 mods + 164 from your Downloads archives into textures\.
The _work folder is my analysis workspace. The game ignores it; leave it or hide it in MO2.

INSTALL
1. In MO2, tick "Lordbound Fixes" in the left pane, placed BELOW "Lordbound" (so its scripts win).
2. In the right pane (Plugins), tick "Lordbound Fixes.esp" and make sure it loads after Druadach.esm.
3. Best results on a character that has not started these quests yet. Fixes to script properties
   and quest scripts only take hold for quests that start after the patch is installed.

WHAT IS FIXED (cause found in the data before changing anything)
- 143 script properties the authors declared and use in their scripts but never filled in the CK.
  An empty property makes the call do nothing, so stages, scenes and triggers silently stall.
  Full list in "Lordbound Fixes - filled properties.txt". Reported bugs this covers:
  * Knowing Your Enemy / Ill Omens: Legate cuts off mid-sentence (scout scene was never started)
  * Lordbound (DD_LBMQ10) Empyrean Vault Catacombs stall and Lordbound vanishing (catch-up triggers
    had no quest to call)
  * Arcane Sealing Orb pedestal trigger, Skylock gate blocker, Empyrean kill trigger
  * Grave of the First boss death scene, Monuments of Sin bone totems, Enigmatic Origins
    Revenant portals, Lost Children "cast Banish Shadows" trigger, Oathbreaker catapults and
    finale marker, Sacking of Garshakur keep doors, and more
- Masters of Highreach: Lanelle had no reaction line when Fardris's quest was the master quest
  you finished first, so the talk ended before stage 2.
- Just Deserts: options 2 and 3 dead-ended (replies required stage <100, killing Sergus sets 100).
- The Lost Children: Lanelle stopped following you the moment you left Highreach.
- Kinslayer: sparing Azgoth and passing the speech check never completed the quest.
- Wrath: Garom's optional answers dropped you into a "..." loop.
- The Sacking of Garshakur: Faaram Marvani is essential, so "Defeat Faaram" could never complete.
- Sins of the Father: speed debuffs also removed at stage 260, and any SpeedMult lost during the
  Lanrick transformation is restored when you change back. (Root cause not proven; this measures
  your speed before the change and restores the difference afterwards.)
- Grave of the First: Fulaz-Ahl only removed the barrier after his "cast at the barrier" action
  finished; if it never finished he stood there busy forever. The barrier now goes away a few
  seconds into that part of the scene, and the scene ends itself if it is still stuck.
- Marks of a Fighter: Luzgrath asks for "Stonebark Ale" and skulls but only counted the vanilla Ale
  (rare in the valley) and the vanilla skull. Any Stonebark drink or Ale and either skull now count
  and are the ones taken.
- Chasing Dreams: the "Find 3 Brainrot Mushrooms (x/3)" and "Find 3 Nightshade (x/3)" counters
  showed "[...]/3" because the counters were never registered with the quest.
- The Lost Legion appearing at the end of Lordbound: the epilogue quest's Imperial journal entry had
  a stray OR flag on its only condition. Removed. (Cause likely but not proven; check when you get
  there.)
- Tour of Duty: M'zaad's tracking spell property filled so it is removed afterwards.
- Models that pointed at files Lordbound never shipped (red "!" in game), repointed to an existing
  model: Ashlorn rib-cap pieces, a blue crystal in Ysgramor's Folly (typo'd path), a Highrock Stop
  roof, Aedron's armor spaulders on female characters, and the Liquor of Rooting bottle. 9 more missing
  models were copied from your other mods and Downloads (incl. the Barbarian Orcish cuirass
  first-person model and the Cyrodiilic Silver dagger and shortsword).
- Enigmatic Origins: the Jagged Crown on the throne skeleton in the Revenant's Highreach was real
  loose loot; it is now a static decoration with the same model.
- Door landing spots: Garshakur Tailor exit and Putrid Cove Retreat entrance.

TEST POINTS (each fix is unverified until you play through it)
- Masters of Highreach: talk to Lanelle after finishing Fardris's quest first.
- Ill Omens: after "If we work together...", a scout should run in and the quest move to stage 10.
- Lost Children: Lanelle should follow you all the way to Garza.
- Just Deserts: tell Mathieu option 2 or 3 after killing Sergus; quest should complete.
- Kinslayer: spare Azgoth, pass the speech check, Borgog should reward you.
- Sacking of Garshakur: Faaram should die in the stage 190 fight.
- Empyrean Vault Catacombs (Lordbound quest): the Lordbound should follow, not vanish.
- Grave of the First: Fulaz-Ahl should break the barrier and stop being busy.
- Marks of a Fighter: bring 12 skulls, a Stonebark drink and a Mammoth Snout; Luzgrath should accept.
- Chasing Dreams: the mushroom/nightshade objectives should show real counts.

STILL ON THE LIST (not fixed yet)
Checked with the base game files (Data folder):
- Bthar-Zel autosaves: Lordbound 0.8.1 has NO autosave triggers in Bthar-Zel (all 14 autosave
  triggers in the mod are in other dungeons). The red-valve side uses 29 vanilla fire-damage
  triggers (dunCGFireTriggerScript), which do not save. The reporter's own corrupted saves stopped
  after installing SSE Engine Fixes. Nothing to patch here.
- Lanelle's dagger: it reuses a vanilla dagger model (the one Skyrim.esm uses for DA02Dagger) and its textures exist in the base
  game. Purple there means a texture mod in that player's setup, not a Lordbound bug.
- Missing textures: see "Lordbound Fixes - missing textures.txt" (31 objects would show purple).
Checked but not fixable from the data alone:
- Imperial soldiers looking dark in Oathbreaker: they wear vanilla Imperial armor and their face
  files are all present; nothing broken in the data. Send a screenshot if you see it.
- Highreach doors without sound: every door record has valid open/close sounds and the door models
  have open/close animations; tell me which door if you hear silence.
- Raven Spiritualist Feathers on Khajiit: the armor is set up for Khajiit and Argonians; likely a
  clash with another worn item. Tell me what else was worn.
- Orc guards saying "crimes against Skyrim": that line is base-game guard dialogue; changing it
  means editing Skyrim.esm dialogue, left alone.
- Empyrean Vault doors that drop you inside stairs / under the floor, the Highreach servants'
  quarters door, and the Fort Rustagov marker: I can't see room geometry from the data, so I can't
  tell which landing spot is wrong. When it happens, open the console, click the door you came
  through, and send me the ID shown at the top (then type tcl to get out).
- 36 models still missing everywhere (mostly unused records; the Cyrodiilic Silver weapons need a
  mod Lordbound didn't include).
- Dialogue dead-end scan: found 6 places where a reply needs a stage the quest cannot be at yet.
  One was Kinslayer (fixed). The other 5: three are dead extra options next to a working one (Chasing
  Dreams "Care to explain", A Thousand Knives "I challenge you to a duel", Raven's Bluff scout
  questions), not blockers. The fifth, From Ash to Ash (Garom's "Ashlorn is safe" reply needs stage
  50 right after a stage-40 line), is probably bridged by the throne-room scene; check it there.
- Map-open freeze: compared the 6 freezing interiors against the rest (size, markers, lights,
  scale, broken positions). Nothing sets them apart. Next time it happens, have The Watcher running
  and send me its log plus the cell name.
- Getting back into the valley: the Mor Khazgur Passage gate starts locked (needs Mogus's key) and
  Mogus has no dialogue once The Trial Road ends. Picking up that key again restarts the quest
  (its script sets stage 30). Workaround: open console, click the gate, type unlock.
- Raven's Bluff Falx marker and A Shadow of a Doubt marker: the quest data points at the right
  people; needs your save to see why the marker drops.
Needs your game to reproduce (I found the setup, but the cause needs a live save):
- Son of a Chief (Malok/Garza scene stuck), Chasing Dreams freeze after "kill Fardris",
  Fallen Hearts council (one master missing at the table), Fardris stage 35 (Enigmatic Origins),
  Sealed Fate Fardris at stage 60, Ash and Blood Garom teleporting, Oathbreaker Gorek at stage 220,
  Blood for Blood Lurzok, Tour of Duty Lester marker, crash at Y'ffre's Wrath, crash at
  Blackthorn Knoll.
Needs the Creation Kit (I give steps when you get there):
- Garom walking into the shrine (navmesh), sunken trees, stream swimming, waterfall, flying
  grass/stones/trees, Tangled Shrine collision and terrain hole, Cragmere gate, rooms that vanish
  into the void, Highreach gate black plane, Mauloch floor gaps.
- The Carver: all three training options use his one class skill (needs separate trainer setups).
Needs a Windows tool:
- LOD: regenerate with DynDOLOD. Meshes: run Lordbound's meshes through SSE NIF Optimizer / CAO.
