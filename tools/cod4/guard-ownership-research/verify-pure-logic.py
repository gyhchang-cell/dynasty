"""Compile exact production permission/maintenance bodies with small Java fixtures.
This is pure logic, NOT native Minecraft AI, a server, or a network client.
"""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'.work/pure-logic';DOC=ROOT/'docs/cod4/audit-20261022/guard-ownership-research';WORK.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
sg=(ROOT/'src/main/java/com/dynasty/expansion/SummonedGuard.java').read_text();sm=(ROOT/'src/main/java/com/dynasty/expansion/SecondaryMob.java').read_text()
def method(src,signature):
 i=src.index(signature);b=src.index('{',i);depth=1;j=b+1
 while depth:
  depth+= (src[j]=='{')-(src[j]=='}');j+=1
 return src[i:j]
lease=method(sg,'private static Player leaseOwner(');permit=method(sg,'static boolean canAttack(');tick=method(sg,'public static void tick(');can=method(sm,'public boolean canAttack(');allied=method(sm,'public boolean isAlliedTo(')
damage=method(sm,'public boolean doHurtTarget(');prelude=damage[damage.index('{')+1:damage.index('        if(isAlliedTo(victim)')]
assert sm.index('SummonedGuard.tick(this);',sm.index('public void aiStep()'))<sm.index('super.aiStep();',sm.index('public void aiStep()'))
code='''import java.util.*;
import java.util.function.*;
public class GuardPureLogic {
 static int assertions=0;
 static void ok(boolean v,String why){if(!v)throw new AssertionError(why);assertions++;}
 static class Nbt extends HashMap<String,Object>{boolean hasUUID(String k){return get(k) instanceof UUID;} UUID getUUID(String k){return (UUID)get(k);} long getLong(String k){return ((Number)getOrDefault(k,0L)).longValue();} int getInt(String k){return ((Number)getOrDefault(k,0)).intValue();} boolean contains(String k){return containsKey(k);}}
 static class World{long now=599; Map<UUID,Player> players=new HashMap<>();List<LivingEntity> entities=new ArrayList<>(); Player getPlayerByUUID(UUID id){return players.get(id);}long getGameTime(){return now;}<T extends LivingEntity>List<T>getEntitiesOfClass(Class<T> t,Object box,Predicate<T> p){return entities.stream().filter(t::isInstance).map(t::cast).filter(p).toList();}}
 static class Entity{UUID id=UUID.randomUUID();World world;boolean alive=true,removed=false;int damage;Nbt data=new Nbt();Set<Entity> allies=new HashSet<>();Entity(World w){world=w;}UUID getUUID(){return id;}Nbt getPersistentData(){return data;}boolean isAlive(){return alive&&!removed;}boolean isRemoved(){return removed;}World level(){return world;}boolean isAlliedTo(Entity e){return allies.contains(e);}void discard(){removed=true;}}
 static class LivingEntity extends Entity{LivingEntity(World w){super(w);}}
 interface Enemy{}
 static class Hostile extends LivingEntity implements Enemy{Hostile(World w){super(w);}}
 static class Player extends LivingEntity{int pieces=4;Nbt saved=new Nbt();Player(World w){super(w);}}
 static class EquipmentBehaviors{static int pieces(Player p,String id){return p.pieces;}static Nbt saved(Player p){return p.saved;}}
 static class Box{Box inflate(int n){return this;}}
 static class Navigation{int stops,follows;void stop(){stops++;}void moveTo(Player p,double speed){follows++;}}
 static class BaseMob extends LivingEntity{boolean vanillaAllowed=true;int nativeCalls,effects;BaseMob(World w){super(w);}public boolean canAttack(LivingEntity t){return vanillaAllowed&&t!=null;}public boolean doHurtTarget(Entity v){nativeCalls++;v.damage++;return true;}}
 static class SecondaryMob extends BaseMob{int tickCount=1;LivingEntity target;Navigation nav=new Navigation();SecondaryMob(World w){super(w);}LivingEntity getTarget(){return target;}void setTarget(LivingEntity t){target=t;}Navigation getNavigation(){return nav;}Box getBoundingBox(){return new Box();}
 ALLIED
 CAN
 public boolean doHurtTarget(Entity victim){
 PRELUDE
 if(isAlliedTo(victim))return false;
 boolean hit=super.doHurtTarget(victim);if(hit)effects++;return hit;
 }
 }
 static class HostileGuard extends SecondaryMob implements Enemy{HostileGuard(World w){super(w);}}
 static class SummonedGuard{LEASE
 PERMIT
 TICK
 }
 static class F{World w=new World();Player owner=new Player(w),bystander=new Player(w);SecondaryMob guard=new HostileGuard(w);Hostile enemy=new Hostile(w);F(){w.players.put(owner.id,owner);owner.saved.put("guardGeneration",7L);guard.data.put("cod4Summoner",owner.id);guard.data.put("cod4Expires",600L);guard.data.put("cod4GuardGeneration",7L);guard.data.put("cod4MinPieces",4);}}
 static void boundary(String name,Consumer<F> mutate,Function<F,Entity> victim,boolean pass){F f=new F();mutate.accept(f);Entity v=victim.apply(f);boolean actual=f.guard.doHurtTarget(v);ok(actual==pass,name+" return");ok(f.guard.nativeCalls==(pass?1:0),name+" parent boundary");ok(f.guard.effects==(pass?1:0),name+" effects");ok(v.damage==(pass?1:0),name+" victim mutation");if(v instanceof LivingEntity living)ok(f.guard.canAttack(living)==pass,name+" canAttack");System.out.println("PASS "+name);}
 public static void main(String[] args){
 boundary("valid Enemy",f->{},f->f.enemy,true);
 boundary("owner",f->{},f->f.owner,false);
 boundary("unprovoked bystander",f->{},f->f.bystander,false);
 boundary("provoked player still non Enemy",f->{},f->f.bystander,false);
 boundary("same owner hostile guard",f->{},f->{SecondaryMob other=new HostileGuard(f.w);other.data.put("cod4Summoner",f.owner.id);return other;},false);
 boundary("different owner hostile Enemy",f->{},f->{SecondaryMob other=new HostileGuard(f.w);other.data.put("cod4Summoner",UUID.randomUUID());return other;},true);
 boundary("self",f->{},f->f.guard,false);
 boundary("dead target",f->f.enemy.alive=false,f->f.enemy,false);
 boundary("removed target",f->f.enemy.removed=true,f->f.enemy,false);
 boundary("target other world",f->f.enemy.world=new World(),f->f.enemy,false);
 boundary("owner outward ally",f->f.owner.allies.add(f.enemy),f->f.enemy,false);
 boundary("target allied to owner",f->f.enemy.allies.add(f.owner),f->f.enemy,false);
 boundary("guard outward ally",f->f.guard.allies.add(f.enemy),f->f.enemy,false);
 boundary("target allied to guard",f->f.enemy.allies.add(f.guard),f->f.enemy,false);
 boundary("owner offline",f->f.w.players.clear(),f->f.enemy,false);
 boundary("owner dead",f->f.owner.alive=false,f->f.enemy,false);
 boundary("owner removed",f->f.owner.removed=true,f->f.enemy,false);
 boundary("owner moved world",f->f.owner.world=new World(),f->f.enemy,false);
 boundary("guard dead",f->f.guard.alive=false,f->f.enemy,false);
 boundary("guard removed",f->f.guard.removed=true,f->f.enemy,false);
 boundary("crab minimum pieces lost",f->f.owner.pieces=3,f->f.enemy,false);
 boundary("shrimp three pieces allowed",f->{f.guard.data.put("cod4MinPieces",3);f.owner.pieces=3;},f->f.enemy,true);
 boundary("shrimp two pieces refused",f->{f.guard.data.put("cod4MinPieces",3);f.owner.pieces=2;},f->f.enemy,false);
 boundary("legacy minimum defaults three",f->{f.guard.data.remove("cod4MinPieces");f.owner.pieces=3;},f->f.enemy,true);
 boundary("generation superseded",f->f.owner.saved.put("guardGeneration",8L),f->f.enemy,false);
 boundary("generation mismatch reverse",f->f.guard.data.put("cod4GuardGeneration",8L),f->f.enemy,false);
 boundary("exact expiry refused",f->f.w.now=600,f->f.enemy,false);
 boundary("past expiry refused",f->f.w.now=601,f->f.enemy,false);
 boundary("no expiry refused",f->f.guard.data.remove("cod4Expires"),f->f.enemy,false);
 boundary("vanilla restriction retained",f->f.guard.vanillaAllowed=false,f->f.enemy,false);
 boundary("nonliving victim",f->{},f->new Entity(f.w),false);
 boundary("wild bystander original path",f->f.guard.data.remove("cod4Summoner"),f->f.bystander,true);
 boundary("wild Enemy original path",f->f.guard.data.remove("cod4Summoner"),f->f.enemy,true);
 boundary("wild vanilla refusal",f->{f.guard.data.remove("cod4Summoner");f.guard.vanillaAllowed=false;},f->f.enemy,true);
 // Wild doHurtTarget historically did not call canAttack; preserve this separately.
 F clear=new F();clear.guard.target=clear.bystander;SummonedGuard.tick(clear.guard);ok(clear.guard.target==null,"clear cached bystander");ok(clear.guard.nav.stops==1,"stop old navigation");
 F expired=new F();expired.guard.target=expired.enemy;expired.w.now=600;SummonedGuard.tick(expired.guard);ok(expired.guard.removed,"expired discard");ok(expired.guard.target==null,"expired clear target");ok(expired.guard.nav.stops==1,"expired stop");
 F scan=new F();scan.guard.tickCount=20;Hostile ally=new Hostile(scan.w);scan.owner.allies.add(ally);scan.w.entities.addAll(List.of(scan.owner,scan.bystander,ally,scan.enemy));SummonedGuard.tick(scan.guard);ok(scan.guard.target==scan.enemy,"scan chooses valid Enemy only");
 F follow=new F();follow.guard.tickCount=20;follow.w.entities.add(follow.bystander);SummonedGuard.tick(follow.guard);ok(follow.guard.target==null,"no invalid acquired");ok(follow.guard.nav.follows==1,"follow owner when safe empty");
 System.out.println("PURE_LOGIC_PASS boundary_cases=34 maintenance_cases=4 assertions="+assertions);
 }
}
'''
for name,value in [('ALLIED',allied),('CAN',can),('PRELUDE',prelude),('LEASE',lease),('PERMIT',permit),('TICK',tick)]:code=code.replace(name,value)
# A preserved wild doHurtTarget does not consult canAttack; test that behavior independently.
code=code.replace('boundary("wild vanilla refusal",f->{f.guard.data.remove("cod4Summoner");f.guard.vanillaAllowed=false;},f->f.enemy,true);','F wild=new F();wild.guard.data.remove("cod4Summoner");wild.guard.vanillaAllowed=false;ok(!wild.guard.canAttack(wild.enemy),"wild canAttack retains parent false");ok(wild.guard.doHurtTarget(wild.enemy),"wild doHurtTarget retains original parent delegation");System.out.println("PASS wild distinct original contracts");')
p=WORK/'GuardPureLogic.java';p.write_text(code);java=Path('/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin');compile=subprocess.run([str(java/'javac'),'--release','17','-d',str(WORK),str(p)],capture_output=True,text=True);log=compile.stdout+compile.stderr
if compile.returncode==0:
 run=subprocess.run([str(java/'java'),'-cp',str(WORK),'GuardPureLogic'],capture_output=True,text=True);log+=run.stdout+run.stderr;code=run.returncode
else:code=compile.returncode
(WORK/'run.log').write_text(log);receipt=dict(status='PASS' if code==0 and 'PURE_LOGIC_PASS' in log else 'FAIL',exitCode=code,validationType='pure Java fixtures executing extracted production method bodies; NOT native Minecraft AI/server/network',extractedMethodsSha256={k:sha(v.encode()) for k,v in dict(leaseOwner=lease,guardCanAttack=permit,tick=tick,mobCanAttack=can,mobIsAlliedTo=allied,damageGuardPrelude=prelude).items()},generatedHarnessSha256=sha(p.read_bytes()),logSha256=sha(log.encode()),productionSources={n:sha((ROOT/'src/main/java/com/dynasty/expansion'/n).read_bytes()) for n in ['SummonedGuard.java','SecondaryMob.java']},nativeGameStarted=False)
(DOC/'pure-logic-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(log);print(json.dumps(receipt,ensure_ascii=False));raise SystemExit(0 if receipt['status']=='PASS' else 1)
