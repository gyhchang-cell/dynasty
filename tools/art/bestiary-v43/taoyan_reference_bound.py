"""Research cards with explicit namespace/variant bindings, never runtime assets."""
from pathlib import Path
import importlib.util
s=importlib.util.spec_from_file_location('reference',Path(__file__).with_name('marshal_reference.py'))
r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
r.OUT=r.ROOT/'build/bestiary-v43/taoyan-reference-bound';r.OUT.mkdir(parents=True,exist_ok=True)
r.STUDY_LABEL='Shell / cavity / jaw / weight-bearing support; one base skin per design'
r.PICKS={
 'AlexModGuy__Ice_and_Fire': 'MyrmexWorker MyrmexSoldier MyrmexQueen MyrmexSentinel MyrmexRoyal DeathWorm'.split(),
 'VazkiiMods__Quark': 'Crab Toretoise'.split(),
 'Polarice3__Goety-2': 'Ministrosity ModSpider'.split(),
 'RayTrace082__untamedwilds': 'KingCrab Tarantula GiantClam TurtleSoftshell'.split(),
 'peeko32213__Unusual-Prehistory': ['panacanthocaris.geo'],
 'superlord9362__Prehistoric-Fauna': ['DermestidBeetle'],
 'AlexModGuy__AlexsMobs': 'Bunfungus Mungus Laviathan'.split(),
 'Angry-Pixel__The-Betweenlands': ['GiantToad'],
 'Quek04__The-Undergarden': 'Gloomper Rotbelcher Nargoyle'.split(),
 'DivineRPG__DivineRPG': 'Behemoth Blubbertusk Dolossal Frostbite Duo Gorgosion HiveSoldier'.split(),
}
r.ATLAS_OVERRIDES={}
for short in r.PICKS['AlexModGuy__Ice_and_Fire']:
 suffix=short.removeprefix('Myrmex').lower()
 texture='src/main/resources/assets/iceandfire/textures/models/myrmex/myrmex_desert_'+suffix+'.png' if short.startswith('Myrmex') else 'src/main/resources/assets/iceandfire/textures/models/deathworm/deathworm_yellow.png'
 binding='src/main/java/com/github/alexthe666/iceandfire/'+('entity/Entity'+short+'.java' if short.startswith('Myrmex') else 'client/render/entity/RenderDeathWorm.java')
 r.ATLAS_OVERRIDES[('AlexModGuy__Ice_and_Fire',short)]=(texture,binding)
for short,texture,renderer in [('Ministrosity','servants/ministrosity/stone.png','StoneMinistrosity'),('ModSpider','servants/spider/bone_spider_original.png','BoneSpider')]:
 r.ATLAS_OVERRIDES[('Polarice3__Goety-2',short)]=('src/main/resources/assets/goety/textures/entity/'+texture,'src/main/java/com/Polarice3/Goety/client/render/'+renderer+'Renderer.java')
for short,name,skin in [('KingCrab','king_crab','red'),('Tarantula','tarantula','red_knee'),('GiantClam','giant_clam','gigas'),('TurtleSoftshell','softshell_turtle','chinese_1')]:
 r.ATLAS_OVERRIDES[('RayTrace082__untamedwilds',short)]=('src/main/resources/assets/untamedwilds/textures/entity/'+name+'/'+skin+'.png','src/main/resources/data/untamedwilds/entities/'+name+'.json')
r.ATLAS_OVERRIDES[('peeko32213__Unusual-Prehistory','panacanthocaris.geo')]=('src/main/resources/assets/unusualprehistory/textures/entity/panacanthocaris/panacanthocaris_solar.png','src/main/java/com/peeko32213/unusualprehistory/client/model/entity/prehistoric/aquatic/PanacanthocarisModel.java')
if __name__=='__main__':r.main()
