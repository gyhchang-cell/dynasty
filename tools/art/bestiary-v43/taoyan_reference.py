"""Research-only cards for the living cauldron's maw, support limbs and cast shell.
No production exports; no automatic acceptance or claims of100 reviewed references.
"""
from pathlib import Path
import importlib.util
s=importlib.util.spec_from_file_location('reference',Path(__file__).with_name('marshal_reference.py'));r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
r.OUT=r.ROOT/'build/bestiary-v43/taoyan-reference';r.OUT.mkdir(parents=True,exist_ok=True)
r.STUDY_LABEL='Cast shell / maw / multi-leg support / interior material study'
r.PICKS={
 'Polarice3__Goety-2':'EternalCauldron RedstoneCube TropicalSlime'.split(),
 'TeamTwilight__twilightforest':'HarbingerCube HelmetCrab PinchBeetle FireBeetle SlimeBeetle TFGhast UrGhast'.split(),
 'AlexModGuy__AlexsMobs':'Cockroach LeafcutterAnt LeafcutterAntQueen MantisShrimp Lobster Mimicube'.split(),
 'AlexModGuy__AlexsCaves':'Gammaroach Ferrouslime CaramelCube'.split(),
 'DivineRPG__DivineRPG':'CauldronFish Crab KingCrab HellSpider EnderSpider PumpkinSpider JungleSpider SoulSpider'.split(),
 'Angry-Pixel__The-Betweenlands':'BubblerCrab SiltCrab Lurker'.split(),
}
if __name__=='__main__':r.main()
