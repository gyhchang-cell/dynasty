package com.dynasty.blueprint.client;

import com.dynasty.blueprint.BlueprintVisualEvent;
import com.dynasty.blueprint.BlueprintEntities;
import com.dynasty.blueprint.TemplateMob;
import net.minecraft.client.Minecraft;
import net.minecraft.client.ParticleStatus;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Vector3f;
import java.util.LinkedHashMap;
import java.util.UUID;
import java.util.ArrayList;

/** Bounded world-space hints and finite translucent glare; no camera or input mutation. */
@Mod.EventBusSubscriber(modid="dynasty", value=Dist.CLIENT)
public final class BlueprintVisuals {
    private record Key(UUID caster, long started) {}
    private static final LinkedHashMap<Key, BlueprintVisualEvent> ACTIVE = new LinkedHashMap<>();
    private static ResourceLocation world;
    private static final ArrayList<Integer> SUPPORTS = new ArrayList<>();
    private static final ArrayList<Integer> SHIELDS = new ArrayList<>();
    @SubscribeEvent public static void glare(net.minecraftforge.client.event.RenderGuiOverlayEvent.Post event) {
        if(!event.getOverlay().id().equals(net.minecraftforge.client.gui.overlay.VanillaGuiOverlay.HOTBAR.id()))return;
        var mc=Minecraft.getInstance();if(mc.player==null||!mc.player.isAlive()||mc.options.hideGui)return;
        var effect=mc.player.getEffect(BlueprintEntities.LANTERN_GLARE.get());if(effect==null)return;
        int width=mc.getWindow().getGuiScaledWidth(),height=mc.getWindow().getGuiScaledHeight();
        int color=effect.getAmplifier()>=2?0xE6C54A:effect.getAmplifier()>0?0x62D994:0xFFF9E6;
        int alpha=Math.min(48,Math.max(0,effect.getDuration())*3);var gui=event.getGuiGraphics();
        // Under25% combined opacity around the edges, under5% over the centre; expires with native effect sync.
        gui.fill(0,0,width,height,((alpha/4)<<24)|color);
        gui.fillGradient(0,0,width,height/4,(alpha<<24)|color,color);
        gui.fillGradient(0,height*3/4,width,height,color,(alpha<<24)|color);
    }
    private BlueprintVisuals() {}
    public static void accept(BlueprintVisualEvent p) {
        var mc=Minecraft.getInstance();
        if(mc.level==null || !mc.level.dimension().location().equals(p.dimension())) return;
        if(p.cancelled()) {ACTIVE.entrySet().removeIf(e->e.getKey().caster.equals(p.entityUuid()) && e.getKey().started<=p.started());return;}
        if(mc.level.getGameTime()-p.started()>p.duration()) return;
        var key=new Key(p.entityUuid(),p.started());
        if(ACTIVE.containsKey(key)) return;
        ACTIVE.entrySet().removeIf(e->e.getKey().caster.equals(p.entityUuid()));
        while(ACTIVE.size()>=64) ACTIVE.remove(ACTIVE.keySet().iterator().next());
        ACTIVE.put(key,p);
    }
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut e) { ACTIVE.clear();SUPPORTS.clear();SHIELDS.clear();world=null; }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if(event.phase!=TickEvent.Phase.END) return;
        var mc=Minecraft.getInstance();
        if(mc.level==null) {ACTIVE.clear();SUPPORTS.clear();SHIELDS.clear();world=null;return;}
        var dim=mc.level.dimension().location();
        if(world!=null && !world.equals(dim)) {ACTIVE.clear();SUPPORTS.clear();SHIELDS.clear();} world=dim;
        if(mc.isPaused()) return;
        long now=mc.level.getGameTime();
        int budget=mc.options.particles().get()==ParticleStatus.MINIMAL?8:mc.options.particles().get()==ParticleStatus.DECREASED?24:48;
        // Entity metadata survives tracking/rejoin; the possession beam outlives the brief casting event.
        if(now%10==0) {
            SUPPORTS.clear();SHIELDS.clear();
            for(var entity:mc.level.entitiesForRendering()) {
                if(entity instanceof TemplateMob mob && mob.kind()==TemplateMob.Kind.PRIEST && mob.isAlive()
                        && mob.buffTargetId()>=0 && mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(mob.position())<=48*48)
                    if(SUPPORTS.size()<32) SUPPORTS.add(mob.getId());
                if(entity instanceof TemplateMob mob && mob.kind()==TemplateMob.Kind.SHIELD && mob.isAlive()
                        && SHIELDS.size()<24 && mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(mob.position())<=24*24)
                    SHIELDS.add(mob.getId());
                if(SUPPORTS.size()>=32 && SHIELDS.size()>=24) break;
            }
        }
        for(int id:SUPPORTS) {
            if(budget<=0 || (now+id)%3!=0 || !(mc.level.getEntity(id) instanceof TemplateMob caster) || !caster.isAlive()) continue;
            if(!(mc.level.getEntity(caster.buffTargetId()) instanceof net.minecraft.world.entity.LivingEntity target)
                    || !target.isAlive() || !(target instanceof TemplateMob linked && linked.isPossessed())
                    || caster.distanceToSqr(target)>16*16) continue;
            int count=Math.min(6,budget);budget-=count;
            var dust=new DustParticleOptions(new Vector3f(.78F,.12F,.19F),.7F);
            for(int i=0;i<count;i++) {
                double u=(i+(now*.06)%1)/count;
                var at=caster.position().add(0,caster.getBbHeight()*.7,0).lerp(target.position().add(0,target.getBbHeight()*.6,0),u);
                mc.level.addParticle(dust,at.x,at.y,at.z,0,.005,0);
            }
        }
        for(int id:SHIELDS) {
            if(budget<=0 || (now+id)%10!=0 || !(mc.level.getEntity(id) instanceof TemplateMob mob)
                    || !mob.isAlive() || !mob.onGround() || mob.getDeltaMovement().horizontalDistanceSqr()<.0005) continue;
            var state=mc.level.getBlockState(mob.blockPosition().below());
            if(state.isAir())continue;
            var chips=new BlockParticleOption(ParticleTypes.BLOCK,state);
            for(int i=0;i<2 && budget>0;i++,budget--) {
                double side=i==0?-.24:.24;
                mc.level.addParticle(chips,mob.getX()+side,mob.getY()+.05,mob.getZ(),side*.05,.03,0);
            }
        }
        var iterator=ACTIVE.entrySet().iterator();
        while(iterator.hasNext()) {
            var p=iterator.next().getValue(); var caster=mc.level.getEntity(p.entityId()); long age=now-p.started();
            boolean death=p.key().startsWith("death_");
            if(!p.dimension().equals(dim) || age>p.duration()+4 || age< -20
                    || caster!=null && (!caster.getUUID().equals(p.entityUuid()) || !death && !caster.isAlive())) {iterator.remove();continue;}
            if(caster==null || age<0 || budget<=0 || (now+p.entityId())%3!=0 || mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(caster.position())>48*48)continue;
            if(death) {
                budget-=deathParticles(mc,p,age,budget);
                continue;
            }
            if(p.key().equals("stone_slam")){
                var d=p.direction().multiply(1,0,1).normalize();
                var side=new Vec3(-d.z,0,d.x).scale(com.dynasty.blueprint.StoneGuardBehavior.SLAM_WIDTH*.5);
                int count=Math.min(6,budget);budget-=count;
                for(int i=0;i<count;i++){
                    double u=((age/3+i/2)%6)/5.0;
                    var at=p.origin().add(d.scale(p.range()*u)).add(side.scale(i%2==0?1:-1)).add(0,.08,0);
                    if(age<p.windup())mc.level.addParticle(new DustParticleOptions(new Vector3f(.85F,.65F,.25F),.7F),at.x,at.y,at.z,0,0,0);
                    else if(age<p.windup()+6)mc.level.addParticle(new BlockParticleOption(ParticleTypes.BLOCK,Blocks.STONE.defaultBlockState()),at.x,at.y,at.z,0,.1,0);
                }continue;
            }
            if((p.key().equals("bronze_fire")||p.key().equals("bronze_poison"))&&age>=p.windup()){
                if(age>=p.windup()+60)continue;
                int count=Math.min(6,budget);budget-=count;
                for(int i=0;i<count;i++){
                    double u=((age+i*11)%30)/30.0;
                    double angle=Math.atan2(p.direction().z,p.direction().x)+Math.toRadians(p.angle())*(i/(double)Math.max(1,count-1)-.5);
                    var at=p.origin().add(Math.cos(angle)*p.range()*u,.4,Math.sin(angle)*p.range()*u);
                    var effect=p.key().equals("bronze_fire")?ParticleTypes.FLAME:new DustParticleOptions(new Vector3f(.35F,.65F,.18F),.8F);
                    mc.level.addParticle(effect,at.x,at.y,at.z,0,.005,0);
                }continue;
            }
            if(p.key().equals("spider_drop")&&age<p.windup()){
                var floor=mc.level.clip(new net.minecraft.world.level.ClipContext(p.origin(),p.origin().add(0,-12,0),net.minecraft.world.level.ClipContext.Block.COLLIDER,net.minecraft.world.level.ClipContext.Fluid.NONE,caster)).getLocation();
                int count=Math.min(6,budget);budget-=count;
                for(int i=0;i<count;i++){
                    double angle=(i/(double)count+age*.015)*Math.PI*2,r=com.dynasty.blueprint.MiningSpiderBehavior.IMPACT_RADIUS;
                    mc.level.addParticle(new DustParticleOptions(new Vector3f(.9F,.55F,.2F),.8F),floor.x+Math.cos(angle)*r,floor.y+.08,floor.z+Math.sin(angle)*r,0,0,0);
                }continue;
            }
            boolean buff=p.key().contains("buff")||p.key().contains("possession");
            if(p.key().equals("powder_detonate")){
                for(int i=0;i<2&&budget>0;i++,budget--)mc.level.addParticle(age<p.windup()?ParticleTypes.SMOKE:ParticleTypes.FLAME,
                        caster.getX()+(i==0?-.35:.35),caster.getY()+.85,caster.getZ(),0,.012,0);
                continue;
            }
            if(p.key().equals("scout_grapple")&&caster instanceof TemplateMob scout){
                // A thrown hook that misses must never appear attached to the intended victim.
                if(scout.hookTargetId()<0||now>=scout.hookExpires())continue;
                var hooked=mc.level.getEntity(scout.hookTargetId());
                if(hooked==null||scout.distanceToSqr(hooked)>400)continue;
                int count=Math.min(8,budget);budget-=count;
                var iron=new DustParticleOptions(new Vector3f(.38F,.42F,.43F),.4F);
                for(int i=0;i<count;i++){var at=caster.position().add(0,.8,0).lerp(hooked.position().add(0,.2,0),(i+1D)/(count+1));
                    mc.level.addParticle(iron,at.x,at.y,at.z,0,0,0);}continue;
            }
            var color=buff?new Vector3f(.78F,.12F,.19F):p.key().contains("talisman")?new Vector3f(.12F,.65F,.85F):new Vector3f(.70F,.50F,.24F);
            var dust=new DustParticleOptions(color,.7F);
            var target=mc.level.getEntity(p.targetId());
            int count=Math.min(budget,6); budget-=count;
            double offset=((p.seed()&1023)/1024.0 + age*.08)%1;
            for(int i=0;i<count;i++) {
                Vec3 at;
                if(buff && target!=null) {
                    double u=(i+offset)/count;
                    at=caster.position().add(0,caster.getBbHeight()*.7,0).lerp(target.position().add(0,target.getBbHeight()*.6,0),u);
                } else if(age<p.windup()) {
                    double a=Math.atan2(p.direction().z,p.direction().x)+Math.toRadians(p.angle())*((i+offset)/count-.5);
                    at=p.origin().add(Math.cos(a)*p.range(),.10,Math.sin(a)*p.range());
                } else {
                    double a=(i+offset)/count*Math.PI*2;
                    at=caster.position().add(Math.cos(a)*.55,.6+age*.007,Math.sin(a)*.55);
                }
                mc.level.addParticle(dust,at.x,at.y,at.z,0,.005,0);
            }
        }
    }
    private static int deathParticles(Minecraft mc,BlueprintVisualEvent p,long age,int budget) {
        boolean priest=p.key().endsWith("fufa_jijiu"),shield=p.key().endsWith("ludun_jiashi"),sword=p.key().endsWith("zuwu_daoshou"),
            cross=p.key().endsWith("liannu_zhenzu"),powder=p.key().endsWith("kuijun_sishi"),flag=p.key().endsWith("zhenwang_zhangqiguan");
        boolean child=p.key().endsWith("fuhun_baibu_tongzi"),paper=p.key().endsWith("zhiren_jianke"),skull=p.key().endsWith("muxue_feilu"),toad=p.key().endsWith("chimu_zhuha"),tree=p.key().endsWith("kumu_shujing"),scorpion=p.key().endsWith("mingsha_shixie");
        if(!(scorpion&&age<36||tree&&age>=8&&age<32||toad&&age>=12&&age<28||skull&&age<28||paper&&age<10||child&&age<30||priest&&age<18||shield&&age>=188||sword&&age>=40||cross&&age>=8&&age<20||powder&&age<30||flag&&age>=8&&age<28))return 0;
        int count=Math.min(budget,priest?8:4);
        // No visual entities, frame packets or random state to replicate: seed + absolute age is deterministic.
        var random=net.minecraft.util.RandomSource.create(p.seed()^age*0x9e3779b97f4a7c15L);
        for(int i=0;i<count;i++) {
            double x=p.origin().x+(random.nextDouble()-.5)*.8,z=p.origin().z+(random.nextDouble()-.5)*.8;
            double y=p.origin().y+(priest?.6:shield?.4:.15)+random.nextDouble()*(priest?.6:shield?1.2:.25);
            if(scorpion){
                mc.level.addParticle(age<8?ParticleTypes.END_ROD:new BlockParticleOption(ParticleTypes.BLOCK,Blocks.SANDSTONE.defaultBlockState()),x,y+.2,z,(x-p.origin().x)*.18,.015,(z-p.origin().z)*.18);
            } else if(tree){
                mc.level.addParticle(new BlockParticleOption(ParticleTypes.BLOCK,Blocks.DARK_OAK_LOG.defaultBlockState()),x,y+1,z,(x-p.origin().x)*.3,.03,(z-p.origin().z)*.3);
            } else if(toad){
                mc.level.addParticle(new ItemParticleOption(ParticleTypes.ITEM,new ItemStack(Items.WHITE_DYE)),x,y+.4,z,(x-p.origin().x)*.04,.005,(z-p.origin().z)*.04);
            } else if(skull){
                mc.level.addParticle(age<8?new ItemParticleOption(ParticleTypes.ITEM,new ItemStack(Items.IRON_NUGGET)):age<18?ParticleTypes.SMOKE:new ItemParticleOption(ParticleTypes.ITEM,new ItemStack(Items.BONE_MEAL)),x,y,z,(x-p.origin().x)*.1,.025,(z-p.origin().z)*.1);
            } else if(paper){
                mc.level.addParticle(age<6?ParticleTypes.END_ROD:ParticleTypes.SQUID_INK,x,y,z,0,age<6?.02:0,0);
            } else if(child){
                mc.level.addParticle(new ItemParticleOption(ParticleTypes.ITEM,new ItemStack(age<18?Items.PAPER:Items.BONE_MEAL)),x,y+.6,z,(x-p.origin().x)*.14,.025,(z-p.origin().z)*.14);
            } else if(priest) {
                if(i%3==0)mc.level.addParticle(ParticleTypes.SOUL_FIRE_FLAME,x,y,z,(x-p.origin().x)*.05,.025,(z-p.origin().z)*.05);
                else mc.level.addParticle(new ItemParticleOption(ParticleTypes.ITEM,new ItemStack(Items.PAPER)),x,y,z,(x-p.origin().x)*.2,.06,(z-p.origin().z)*.2);
            } else if(cross){
                mc.level.addParticle(new BlockParticleOption(ParticleTypes.BLOCK,Blocks.OAK_PLANKS.defaultBlockState()),x,y+.8,z,(x-p.origin().x)*.12,.03,(z-p.origin().z)*.12);
            } else if(powder){mc.level.addParticle(ParticleTypes.SMOKE,x,y+.3,z,0,.018,0);
            } else if(flag){mc.level.addParticle(ParticleTypes.SOUL,x,y+.7,z,0,.025,0);
            } else if(shield) {
                mc.level.addParticle(new BlockParticleOption(ParticleTypes.BLOCK,(i%2==0?Blocks.IRON_BLOCK:Blocks.DARK_OAK_PLANKS).defaultBlockState()),x,y,z,(x-p.origin().x)*.05,.02,(z-p.origin().z)*.05);
            } else mc.level.addParticle(ParticleTypes.SMOKE,x,y,z,0,.012,0);
        }
        return count;
    }
    public static int activeCount() {return ACTIVE.size();}
}
