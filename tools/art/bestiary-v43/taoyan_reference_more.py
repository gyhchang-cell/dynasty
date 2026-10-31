"""More *candidates* for the existing living cauldron. Research only.

No download or card creation is counted as a viewed/accepted reference.
Relevance, reconstruction completeness and bindings are reviewed separately.
"""
from pathlib import Path
import importlib.util
s=importlib.util.spec_from_file_location('reference',Path(__file__).with_name('marshal_reference.py'))
r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
r.OUT=r.ROOT/'build/bestiary-v43/taoyan-reference-more';r.OUT.mkdir(parents=True,exist_ok=True)
r.STUDY_LABEL='Shell / maw / load-bearing limbs / cast shell and interior material study'
r.PICKS={
 'AlexModGuy__AlexsMobs': 'AlligatorSnappingTurtle CaveCentipede CrimsonMosquito Enderiophage RockyRoller TarantulaHawk Terrapin Triops WarpedMosco Endergrade WarpedToad'.split(),
 'AlexModGuy__AlexsCaves': 'Trilocaris MineGuardian Caniac Forsaken Brainiac Nucleeper'.split(),
 'Polarice3__Goety-2': 'BroodMother CarrionFly CarrionMaggot Gnasher GraveGolem RedstoneGolem RedstoneMonstrosity Ministrosity FlameConstruct Inferno Wildfire WebSpider ModSpider Snareling Snapper Watchling Ripper Ravaged ModRavager Leapleaf'.split(),
 'lender544__new1.20.1': 'Amethyst_Crab_ Netherite_Monstrosity_ Netherite_Ministrosity_ Coral_Golem_ Coralssus_ Endermaptera_ Clawdian_ Urchinkin_ Hippocamtus_ The_Prowler_ The_Watcher_ The_Harbinger_ The_Immolator_ The_Annihilator_ Ignited_Revenant_ Ender_Guardian_'.split(),
 'AlexModGuy__Ice_and_Fire': 'MyrmexWorker MyrmexSoldier MyrmexQueen MyrmexSentinel MyrmexRoyal DeathWorm DreadScuttler'.split(),
 'BobMowzie__MowziesMobs-Public': 'Foliaath Grottol Wroughtnaut Lantern'.split(),
 'team-abnormals__endergetic': 'ChargerEetle GliderEetle BroodEetle PuffBug Booflo'.split(),
 'VazkiiMods__Quark': 'Crab Toretoise'.split(),
 'Angry-Pixel__The-Betweenlands': 'MireSnail BloodSnail CryptCrawler Pyrad TarBeast SludgeMenace Shambler Termite BoulderSprite RockSnot'.split(),
 'Quek04__The-Undergarden': 'Muncher Stoneborn Scintling'.split(),
 'DivineRPG__DivineRPG': 'TheHunger HiveQueen Parasecta Termasect Termid CaveCrawler DesertCrawler Scorcher InsectFourteen Rotatick Snapper StoneGolem DungeonConstructor Megalith DemonFurnace BoneChest FrostedChest EdenChest'.split(),
}
if __name__=='__main__':r.main()
