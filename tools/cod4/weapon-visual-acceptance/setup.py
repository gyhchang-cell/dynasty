"""Generate observational QA mixins and private launcher; no production edits."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[3]; T=Path(__file__).parent
if (T/'resources/weapon-visual-qa.mixins.json').exists():raise SystemExit('Bootstrap already generated; build checked-in QA sources directly. Refusing to overwrite later observational probes.')
S=T/'src/com/dynasty/weaponqa'; M=S/'mixin'; M.mkdir(parents=True,exist_ok=True)
res=T/'resources';(res/'META-INF').mkdir(parents=True,exist_ok=True)
(res/'META-INF/mods.toml').write_text('modLoader="javafml"\nloaderVersion="[47,)"\nlicense="Private QA"\n[[mods]]\nmodId="dynastyweaponqa"\nversion="1.0"\ndisplayName="COD4 Native Weapon Visual Acceptance"\n')
(T/'qa.init.gradle').write_text('''allprojects { p ->
 p.layout.buildDirectory.set(p.file('build/cod4-weapon-visual-20261023/gradle'))
 p.afterEvaluate {
  if (!p.plugins.hasPlugin('net.minecraftforge.gradle')) return
  def qa=p.sourceSets.create('weaponVisualAcceptance') {
   java.srcDir p.file('tools/cod4/weapon-visual-acceptance/src')
   resources.srcDir p.file('tools/cod4/weapon-visual-acceptance/resources')
   compileClasspath += p.files('build/cod4-pack-20261022/compile-dynasty') + p.sourceSets.main.compileClasspath
  }
  p.tasks.register('weaponVisualAcceptanceJar',Jar) {
   dependsOn qa.classesTaskName
   archiveBaseName='dynasty-weapon-visual-acceptance'
   from qa.output
   manifest.attributes('MixinConfigs':'weapon-visual-qa.mixins.json')
  }
  p.reobf { weaponVisualAcceptanceJar {} }
 }
}
''')
launch=(R/'tools/cod4/pack-acceptance/launch.py').read_text().replace("ROOT=R/'build/cod4-pack-20261022'", "ROOT=R/'build/cod4-weapon-visual-20261023'").replace("OUT=R/'docs/cod4/audit-20261022/pack-acceptance'", "OUT=R/'docs/cod4/audit-20261022/weapon-visual-acceptance'")
start=launch.index("main=R/");end=launch.index('for p in [main,helper]:')
launch=launch[:start]+'''main=R/'build/cod4-pack-20261022/language-repair/dynasty-1.4.0.jar'
assert sha(main)=='0e1fbac34942714cd90a18ec1b404303b5d4d5bf96ce7c96277e16e561fe5c27'
manifest['language_repair_provenance']=json.loads((R/'docs/cod4/audit-20261022/pack-acceptance/language-repair-build.json').read_text())
helper=R/'build/cod4-weapon-visual-20261023/gradle/libs/dynasty-weapon-visual-acceptance-1.4.0.jar'
'''+launch[end:]
launch=launch.replace('dynasty.packqa.','dynasty.weaponqa.').replace('Cod4PackQA','Cod4VisualQA').replace("'1440'","'1280'").replace("'900'","'800'")
(T/'launch.py').write_text(launch)
(res/'pack.mcmeta').write_text(json.dumps({'pack':{'pack_format':15,'description':'Private QA only'}}))
names=[]
base='''package com.dynasty.weaponqa.mixin;
import com.dynasty.weaponqa.Probe;
import com.dynasty.cod3.*;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
'''
for target in ['WeaponImpact','FangtianSweep','WeaponLift','FluteWave','ArmorCrack','TangWind','DragonDecal','SevenStarFlash']:
 name=target+'Probe';names.append(name)
 if target in ['DragonDecal','SevenStarFlash']:
  # Their explicit triangles use separate position/alpha/color arguments.
  if target=='DragonDecal':continue
  args='Matrix4f m,Vec3 a,Vec3 b,Vec3 c,double alpha,int tint';call='Probe.triangle("'+target+'",m,a,b,c,tint,alpha)'
 else:
  args='Matrix4f m,WeaponImpactVisual.Triangle t';call='Probe.triangle("'+target+'",m,t.a(),t.b(),t.c(),t.color(),t.alpha())'
 (M/(name+'.java')).write_text(base+f'''@Mixin(targets="com.dynasty.client.{target}Renderer",remap=false)
public abstract class {name} {{
 @Inject(method="triangle",at=@At("HEAD"),remap=false)
 private static void qa$triangle({args},CallbackInfo ci){{{call};}}
}}
''')
names.remove('DragonDecalProbe')
names+=['VisualWireProbe','PrimitiveProbe','AfterimageProbe']
(M/'VisualWireProbe.java').write_text(base+'''@Mixin(targets="com.dynasty.cod3.Cod3VisualPacket",remap=false)
public abstract class VisualWireProbe {
 @Inject(method="handle",at=@At("HEAD"),remap=false)
 private static void qa$wire(Cod3VisualPacket p,java.util.function.Supplier<net.minecraftforge.network.NetworkEvent.Context> s,CallbackInfo ci){Probe.wire(p);}
}
''')
(M/'PrimitiveProbe.java').write_text(base+'''@Mixin(targets="com.dynasty.client.Cod3VfxRenderer$Geometry",remap=false)
public abstract class PrimitiveProbe {
 @Shadow @Final Matrix4f matrix; @Shadow @Final Vec3 camera;
 @Shadow @Final int color; @Shadow @Final double alpha;
 @Unique int qa$id;
 @Inject(method="draw",at=@At("HEAD"),remap=false)
 private void qa$kind(int id,DynastyVfxDefinition d,double expand,double life,double age,CallbackInfo ci){qa$id=id;}
 @Inject(method="vertex",at=@At("HEAD"),remap=false)
 private void qa$vertex(Vec3 p,CallbackInfo ci){Probe.vertex("Vfx"+qa$id,matrix,p,color,alpha);}
 @Inject(method="triangle",at=@At("HEAD"),remap=false)
 private void qa$triangle(Vec3 a,Vec3 b,Vec3 c,double shade,CallbackInfo ci){if(a.distanceToSqr(camera)>=.64&&b.distanceToSqr(camera)>=.64&&c.distanceToSqr(camera)>=.64)Probe.triangle("Vfx"+qa$id,matrix,a,b,c,color,alpha);}
}
''')
(M/'AfterimageProbe.java').write_text(base+'''@Mixin(targets="com.dynasty.client.Cod3AfterImages",remap=false)
public abstract class AfterimageProbe {
 @Inject(method="weapon(Lnet/minecraft/world/item/ItemStack;Lcom/mojang/blaze3d/vertex/PoseStack;Lnet/minecraft/client/renderer/MultiBufferSource;IFLnet/minecraft/world/item/ItemDisplayContext;)V",at=@At("HEAD"),remap=false)
 private static void qa$weapon(net.minecraft.world.item.ItemStack s,com.mojang.blaze3d.vertex.PoseStack p,net.minecraft.client.renderer.MultiBufferSource b,int tint,float alpha,net.minecraft.world.item.ItemDisplayContext c,CallbackInfo ci){Probe.ghost(s,p.last().pose(),tint,alpha,c);}
}
''')
(res/'weapon-visual-qa.mixins.json').write_text(json.dumps({'required':True,'minVersion':'0.8','package':'com.dynasty.weaponqa.mixin','compatibilityLevel':'JAVA_17','client':names,'injectors':{'defaultRequire':1}},indent=2))
