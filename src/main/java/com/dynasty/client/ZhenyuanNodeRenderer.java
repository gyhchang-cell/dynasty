package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.ritual.ZhenyuanNodeBlockEntity;
import com.dynasty.ritual.ZhenyuanRitualContent;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import org.joml.Matrix4f;

/** Original continuous ritual geometry: translucent sockets, living seals and an armillary gold heart. */
@Mod.EventBusSubscriber(modid = Dynasty.MODID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class ZhenyuanNodeRenderer implements BlockEntityRenderer<ZhenyuanNodeBlockEntity> {
    private static final float[][] COLORS = {{.16F,.95F,.64F},{.84F,.92F,1F},{1F,.27F,.12F},{.15F,.57F,1F},{1F,.73F,.24F}};
    private static final String[] OFFERINGS = {"qinglong_scale","baihu_fang","zhuque_feather","xuanwu_shell","hunyuan_pearl"};
    private static final Vec3 X = new Vec3(1,0,0), Y = new Vec3(0,1,0), Z = new Vec3(0,0,1);
    private final Font font;
    public static double stageRadius(double count) {
        double[] radii={1.5,2.3,3.1,3.55,4.0};
        count=Math.max(0,Math.min(4,count));int i=(int)count;
        return i==4?radii[4]:radii[i]+(radii[i+1]-radii[i])*(count-i);
    }
    public ZhenyuanNodeRenderer(BlockEntityRendererProvider.Context context) { font = context.getFont(); }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers event) {
        event.registerBlockEntityRenderer(ZhenyuanRitualContent.NODE_ENTITY.get(), ZhenyuanNodeRenderer::new);
    }

    @Override public void render(ZhenyuanNodeBlockEntity node, float partial, PoseStack pose,
                                 MultiBufferSource buffers, int packedLight, int overlay) {
        if (node.getLevel() == null) return;
        renderAtTime(node, node.getLevel().getGameTime() + partial, partial, pose, buffers);
    }

    /** Explicit clock permits the real Minecraft renderer to be validated offscreen, without loading a save. */
    public void renderAtTime(ZhenyuanNodeBlockEntity node, double time, float partial, PoseStack pose,
                             MultiBufferSource buffers) {
        if (node.getStage() >= 2) return;
        if(node.timeline().getBoolean("Enabled")) { renderPhaseOne(node,time,partial,pose,buffers); return; }
        double transition = smooth(Math.max(0, Math.min(1, (time - node.getVisualChangedAt()) / 28.0)));
        int slot = node.getSlot();
        int mask = node.getOfferingMask();
        boolean active = (mask & (1 << slot)) != 0;
        double activation = active ? ((node.getPreviousVisualMask() & (1 << slot)) != 0 ? 1 : transition) : 0;
        pose.pushPose();
        pose.translate(.5, 0, .5);
        // Solid gold writes depth first. Transparent back-facing sphere patches must never sort over its front.
        if (slot == 4) {
            Geometry solid = new Geometry(pose.last().pose(), buffers.getBuffer(MagicType.SOLID));
            double power = heartPower(node, transition);
            double breath = 1 + Math.sin(time*(node.getStage()==1?.09:.025))*.025;
            solid.rotatedSphere(new Vec3(0,5.5+Math.sin(time*.022)*.055,0),
                    stageRadius(power*4)*breath,COLORS[4],1,time*.010,24,64);
        }
        Geometry g = new Geometry(pose.last().pose(), buffers.getBuffer(MagicType.TRANSLUCENT));
        if (slot == 4) drawHeart(g, node, time, transition);
        else {
            drawSocket(g, node, time, activation);
            if (active) drawElementMarker(g, slot, time, activation);
        }
        if (active) renderOffering(node, time, pose, buffers, activation);
        renderLabel(node, pose, buffers);
        pose.popPose();
    }

    private void drawSocket(Geometry g, ZhenyuanNodeBlockEntity node, double t, double active) {
        drawSocket(g,node,t,active,true);
    }
    private void drawSocket(Geometry g, ZhenyuanNodeBlockEntity node, double t, double active,boolean legacyFlow) {
        float[] color = COLORS[node.getSlot()];
        Vec3 center = new Vec3(0,1.12 + Math.sin(t*.045)*.025,0);
        // An empty, transparent receptacle: the middle stays clear and never hides the offering.
        double socketRadius=.42+active*.25;
        g.sphere(center, socketRadius, color, .025 + active*.025, true, 10, 24);
        for (int i=0;i<3;i++) {
            double angle = t*.010*(i==1?-1:1) + i*Math.PI/3;
            Vec3 a = new Vec3(Math.cos(angle),0,Math.sin(angle));
            g.ring(center,a,Y,socketRadius+.003,.006,color,.24+active*.35,0,Math.PI*2);
        }
        g.ring(center,X,Z,socketRadius+.004,.008,color,.35+active*.3,t*.01,Math.PI*2);
        for(int i=0;i<(int)(4+active*8);i++) {
            double a=t*.025+i*Math.PI/6;
            g.diamond(center.add(Math.cos(a)*(socketRadius+.08),Math.sin(a*2)*.16,Math.sin(a)*(socketRadius+.08)),.022,color,.3+active*.45);
        }
        g.sigil(new Vec3(0,.525,0), .52 + active*.07, color, t*.005, .35+active*.6, node.getSlot()+1);
        // Four carved-metal petals rise and open as the tribute arrives; the physical stand stays low.
        for(int i=0;i<4;i++) {
            double a=i*Math.PI/2+Math.PI/4;
            Vec3 radial=new Vec3(Math.cos(a),0,Math.sin(a));
            Vec3 side=new Vec3(-Math.sin(a),0,Math.cos(a));
            Vec3 root=radial.scale(.30).add(0,.46,0);
            Vec3 tip=radial.scale(.49+active*.16).add(0,.69+active*.12,0);
            Vec3 mid=root.lerp(tip,.50).add(0,.10,0);
            g.quad(root,mid.add(side.scale(.085)),tip,mid.subtract(side.scale(.085)),color,.45+active*.38);
            g.line(mid.add(side.scale(.055)),tip,.011,COLORS[4],.45+active*.45);
        }
        if(active>0&&legacyFlow) {
            // Thin, curved energy filaments lead to the heart, never a screen-filling solid beam.
            Vec3 destination=heartDestination(node,t);
            for(int strand=0;strand<2;strand++) {
                Vec3 old=center;
                for(int i=1;i<=36;i++) {
                    double u=i/36.0;
                    Vec3 p=center.lerp(destination,u).add(0,Math.sin(Math.PI*u)*1.1,0);
                    p=p.add(Math.sin(u*Math.PI*4+t*.035+strand*Math.PI)*.10*Math.sin(Math.PI*u),0,
                            Math.cos(u*Math.PI*4+t*.035+strand*Math.PI)*.10*Math.sin(Math.PI*u));
                    g.line(old,p,.012,color,active*.42);old=p;
                }
            }
            for(int i=0;i<6;i++) {
                double angle=t*.025+i*Math.PI/3;
                Vec3 spark=center.add(Math.cos(angle)*.51,Math.sin(angle*1.7)*.12,Math.sin(angle)*.51);
                g.diamond(spark,.025,color,.8*active);
            }
        }
    }

    private void renderPhaseOne(ZhenyuanNodeBlockEntity n,double t,float partial,PoseStack pose,MultiBufferSource buffers) {
        var data=n.timeline(); String stage=data.getString("Stage");
        double tick=data.getInt("Tick")+n.timelineAge(t);
        int slot=n.getSlot(), mask=n.getOfferingMask(), count=Integer.bitCount(mask&15);
        double transition=smooth(Math.max(0,Math.min(1,(t-n.getVisualChangedAt())/32)));
        double previous=Integer.bitCount(n.getPreviousVisualMask()&15);
        double growth=stageRadius(previous+(count-previous)*transition)/.825;
        boolean finale=stage.equals("FINAL_RITUAL")||stage.equals("TRANSFER_READY");
        double spin=count==0?0:t*(.004+count*.005);
        if(count>=3) growth*=1+Math.pow(Math.max(0,Math.sin(t*.12)),8)*.055;
        if(stage.equals("THIRD_OMEN")&&tick>=10) growth*=1+.22*Math.sin(Math.PI*Math.min(1,(tick-10)/24));
        if(stage.equals("FOURTH_CONVERGENCE")&&tick>38) growth*=1+.12*Math.sin(Math.PI*Math.min(1,(tick-38)/45));
        if(finale) {
            spin=t*(.07+Math.min(tick,130)*.002);
            growth=(tick<120 ? 4+.8*smooth(clamp((tick-40)/80)) : tick<140 ? 4.8-4.4*smooth(clamp((tick-120)/20)) : .4)/.825;
            if(tick>=170) growth=.4/.825*(1-smooth(clamp((tick-170)/20)));
        }
        Vec3 heart=new Vec3(0,5.5+(count>=3?Math.sin(t*.04)*.13:0),0);
        pose.pushPose(); pose.translate(.5,0,.5);
        Geometry g=new Geometry(pose.last().pose(),buffers.getBuffer(MagicType.TRANSLUCENT));
        if(slot==4) {
            RitualPhaseOneEffects.observe(n);
            if(growth>.001) {
                Geometry solid=new Geometry(pose.last().pose(),buffers.getBuffer(MagicType.SOLID));
                // Readable pulse under 3 Hz; avoid rapid high-contrast strobing.
                float[] gold=finale&&tick>90&&tick<140&&Math.sin(tick*.55)>.3?new float[]{1,.9f,.55f}:COLORS[4];
                solid.rotatedSphere(heart,.825*growth,gold,1,spin,20,48);
                for(int ring=0;ring<3;ring++) {
                    double a=spin*(ring%2==0?1:-1)+ring*Math.PI/3;
                    g.ring(heart,new Vec3(Math.cos(a),0,Math.sin(a)),new Vec3(-Math.sin(a)*.8,.6,Math.cos(a)*.8),
                            growth*(1.03+ring*.15),.018,COLORS[4],.65,0,Math.PI*2);
                }
            }
            for(int c=0;c<4;c++) if((mask&(1<<c))!=0) for(int i=0;i<6+count*2;i++) {
                double a=t*(.018+c*.007)+i*Math.PI*2/(6+count*2),r=(.98+c*.06)*growth;
                g.diamond(heart.add(Math.cos(a)*r,Math.sin(a*2+c)*r*.45,Math.sin(a)*r),.035,COLORS[c],.85);
            }
            g.sigil(new Vec3(0,.79,0),1.5+count*.22,COLORS[4],-spin*.3,.7,4);
            if(count>previous&&!finale) {
                int added=(mask&15)&~n.getPreviousVisualMask();
                int theme=added==0?4:Integer.numberOfTrailingZeros(added);
                wave(g,heart,t-n.getVisualChangedAt(),32,stageRadius(count)*1.35,COLORS[theme]);
            }
            if(stage.equals("THIRD_OMEN")&&tick>=10) wave(g,heart,tick-10,30,6,COLORS[4]);
            if(stage.equals("FOURTH_CONVERGENCE")&&tick>=42) wave(g,new Vec3(0,1.1,0),tick-42,44,12,COLORS[4]);
            if(finale&&tick>=140&&tick<170) for(int i=0;i<40;i++) {
                double u=((tick-140)/30+i/40.0)%1,a=i*2.39996,r=(1-u)*10;
                g.diamond(heart.add(Math.cos(a)*r,Math.sin(a*1.7)*r*.6,Math.sin(a)*r),.06,COLORS[i%4],.9);
            }
            if(finale&&tick>=170) {
                wave(g,new Vec3(0,1.2,0),tick-170,50,22,COLORS[4]);
                double opening=smooth(clamp((tick-170)/30));
                for(int side:new int[]{-1,1}) {
                    Vec3 foot=new Vec3(side*.15,1.1,0), edge=new Vec3(side*2.5*opening,5.2,0), top=new Vec3(side*.15,10,0);
                    g.line(foot,edge,.075,COLORS[4],.85);g.line(edge,top,.075,COLORS[4],.85);
                    g.quad(foot,edge,top,foot,COLORS[side<0?0:3],.10);
                }
                for(int theme=0;theme<4;theme++) {
                    double a=theme*Math.PI/2;
                    beast(g,theme,heart.add(Math.cos(a)*5,Math.sin(a)*3,1),.75,t,.55*opening);
                }
            }
        } else {
            boolean active=(mask&(1<<slot))!=0, pending=(data.getInt("Pending")&(1<<slot))!=0;
            int[] times=data.getIntArray("OfferingTicks"), order=data.getIntArray("Order");
            double anim=slot<times.length?times[slot]+n.timelineAge(t):0;
            double progress=clamp(anim/com.dynasty.ritual.ZhenyuanPhaseOne.DURATIONS[slot]);
            // Reuse the carved opening petals, but not the legacy static connecting ribbons.
            drawSocket(g,n,t,active?((n.getPreviousVisualMask()&(1<<slot))!=0?1:.6+.4*transition):pending?smooth(progress)*.6:0,false);
            if(active||pending) {
                if(pending) offeringAnimation(g,slot,anim,progress,t);
                if(active) {
                    drawElementMarker(g,slot,t,1);
                    wave(g,new Vec3(0,1.15,0),t-n.getVisualChangedAt(),28,2.5,COLORS[slot]);
                }
                boolean flowing=active;
                int rank=slot<order.length?order[slot]:slot+1;
                if(stage.equals("THIRD_OMEN")&&rank==3) flowing=tick>=32;
                if(stage.equals("FOURTH_CONVERGENCE")) flowing=tick>=20+(Math.max(1,rank)-1)*6;
                if(finale) flowing=tick>=10+slot*10&&tick<140;
                if(flowing) {
                    Vec3 destination=Vec3.atLowerCornerOf(BlockPos.of(data.getLong("Heart")).subtract(n.getBlockPos())).add(heart);
                    Vec3 previousPoint=new Vec3(0,1.12,0);
                    for(int segment=1;segment<=24;segment++) {
                        double u=segment/24.0;
                        Vec3 p=new Vec3(0,1.12,0).lerp(destination,u).add(0,Math.sin(Math.PI*u)*1.4,0);
                        g.line(previousPoint,p,finale?.055:.025,COLORS[slot],.38);previousPoint=p;
                    }
                    int sparks=finale&&tick>=60?40:finale||stage.equals("FOURTH_CONVERGENCE")&&tick>38?28:10;
                    for(int i=0;i<sparks;i++) {
                        double u=(t*(finale?.04:.012)+i/(double)sparks)%1;
                        Vec3 p=new Vec3(0,1.12,0).lerp(destination,u).add(0,Math.sin(Math.PI*u)*.8,0);
                        g.diamond(p,slot==1?.025:.04,COLORS[slot],.9);
                        Vec3 tail=p.subtract(destination.subtract(new Vec3(0,1.12,0)).normalize().scale(.22));
                        g.line(tail,p,.013,COLORS[slot],.55);
                    }
                }
            }
        }
        boolean offered=((mask|data.getInt("Pending"))&(1<<slot))!=0;
        if(offered) {
            int[] times=data.getIntArray("OfferingTicks"); double a=slot<4&&slot<times.length?times[slot]+n.timelineAge(t):0;
            boolean pending=(data.getInt("Pending")&(1<<slot))!=0;
            double rotation=slot==4?t*.015:pending?switch(slot) {case 0->a<20?0:(a-20)*(.01+a*.0004);case 1->a<16?0:(a-16)*.3;case 2->a*.025;default->a*.008;}:t*.02;
            var item=slot==4?ZhenyuanRitualContent.TIANMING_JADE.get():ForgeRegistries.ITEMS.getValue(new ResourceLocation("dynasty",OFFERINGS[slot]));
            pose.pushPose(); pose.translate(0,slot==4?1.5:1.12+Math.sin(t*.04)*.03,0);pose.mulPose(Axis.YP.rotation((float)rotation));pose.scale(.65f,.65f,.65f);
            Minecraft.getInstance().getItemRenderer().renderStatic(new ItemStack(item),ItemDisplayContext.GROUND,LightTexture.FULL_BRIGHT,OverlayTexture.NO_OVERLAY,pose,buffers,n.getLevel(),slot);
            pose.popPose();
        }
        renderLabel(n,pose,buffers); pose.popPose();
    }
    private static double clamp(double v) { return Math.max(0,Math.min(1,v)); }
    /** Completion marker is derived only from the saved, server-synchronized offering mask.
     * Pending offerings never get a marker; no client timer or extra persistent entity is needed. */
    private static void drawElementMarker(Geometry g,int slot,double time,double activation) {
        float[] color=COLORS[slot];
        Vec3 center=new Vec3(0,2.15+Math.sin(time*.025+slot)*.035,0);
        double radius=.30*(1+Math.sin(time*.045+slot)*.04);
        g.rotatedSphere(center,radius,color,.68*activation,time*.008,10,20);
        beast(g,slot,center,.43,time,.30*activation);
        for(int i=0;i<5;i++) {
            double a=time*(slot==3?.009:.018)+i*Math.PI*2/5;
            double y=switch(slot) {
                case 0 -> Math.sin(a*2)*.17;
                case 1 -> (i%2==0?.10:-.10);
                case 2 -> ((time*.012+i*.2)%1)*.38;
                default -> Math.sin(a)*.045;
            };
            g.diamond(center.add(Math.cos(a)*.43,y,Math.sin(a)*.43),slot==1?.018:.025,color,.7*activation);
        }
    }
    private static void wave(Geometry g,Vec3 center,double age,double duration,double radius,float[] color) {
        if(age<0||age>=duration)return;
        double u=age/duration;
        g.ring(center,X,Z,.3+radius*u,.035*(1-u)+.008,color,.9*(1-u),0,Math.PI*2);
        for(int i=0;i<32;i++) { double a=i*Math.PI/16;g.diamond(center.add(Math.cos(a)*radius*u,.08*Math.sin(i+age),Math.sin(a)*radius*u),.04,color,1-u); }
    }
    private static void offeringAnimation(Geometry g,int slot,double age,double progress,double time) {
        double form=smooth(clamp(progress/.28));
        double collapse=1-smooth(clamp((progress-.70)/.30));
        double scale=(.12+1.8*collapse)*form;
        beast(g,slot,new Vec3(0,2.15,0),scale,time,.72*form);
    }

    /** Original low-poly silhouettes: coiling dragon, carved tiger, feather wings and plated turtle. */
    private static void beast(Geometry g,int slot,Vec3 center,double scale,double time,double alpha) {
        if(scale<.001)return;
        float[] c=COLORS[slot];
        if(slot==0) {
            Vec3 last=null;
            for(int i=0;i<=40;i++) {
                double u=i/40.0,a=u*Math.PI*3.3+time*.025;
                Vec3 p=center.add(Math.cos(a)*scale*.8,(u-.5)*scale*1.6,Math.sin(a)*scale*.8);
                if(last!=null)g.line(last,p,scale*(.045+.13*u),c,alpha);
                if(i%4==0)g.diamond(p.add(0,scale*.13,0),scale*.10,COLORS[4],alpha*.8);
                last=p;
            }
            // Forward muzzle, brow and swept horns attach to the leading end of the coil.
            g.sphere(last,scale*.22,c,alpha,false,5,8);
            g.line(last,last.add(scale*.32,-scale*.05,0),scale*.13,c,alpha);
            for(int side:new int[]{-1,1}) {
                Vec3 brow=last.add(0,scale*.14,side*scale*.13);
                g.line(brow,brow.add(-scale*.18,scale*.36,side*scale*.09),scale*.035,COLORS[4],alpha);
                g.diamond(last.add(scale*.14,scale*.06,side*scale*.17),scale*.035,COLORS[4],alpha);
            }
        } else if(slot==1) {
            // Shallow sculpted mask, broad cheeks, two incisors; claw cuts frame the face.
            g.sphere(center,scale*.48,c,alpha,false,5,8);
            for(int side:new int[]{-1,1}) {
                g.diamond(center.add(side*scale*.38,scale*.42,0),scale*.19,c,alpha);
                g.line(center.add(side*scale*.12,scale*.13,-scale*.43),center.add(side*scale*.34,scale*.19,-scale*.35),scale*.04,COLORS[4],alpha);
                g.line(center.add(side*scale*.22,-scale*.10,-scale*.39),center.add(side*scale*.16,-scale*.48,-scale*.46),scale*.065,COLORS[4],alpha);
                for(int i=0;i<3;i++) {
                    Vec3 root=center.add(side*(.6+i*.16)*scale,.7*scale,-.18*scale);
                    g.line(root,root.add(-side*.24*scale,-1.3*scale,-.1*scale),scale*.025,c,alpha*.7);
                }
            }
            g.diamond(center.add(0,0,-scale*.49),scale*.13,COLORS[4],alpha);
        } else if(slot==2) {
            g.diamond(center,scale*.29,COLORS[4],alpha);
            for(int side:new int[]{-1,1})for(int i=0;i<7;i++) {
                double fan=.35+i*.15;
                Vec3 root=center.add(side*scale*.15,scale*.1,0);
                Vec3 tip=center.add(side*scale*(.65+fan),scale*(1.2-i*.16),scale*.12*i);
                Vec3 mid=root.lerp(tip,.55);
                g.quad(root,mid.add(0,scale*.11,scale*.09),tip,mid.add(0,-scale*.11,-scale*.09),c,alpha);
                g.line(root,tip,scale*.012,COLORS[4],alpha);
            }
            for(int i=-1;i<=1;i++)g.line(center,center.add(i*scale*.45,-scale*(1.1+Math.abs(i)*.2),scale*.3),scale*.065,c,alpha*.8);
        } else {
            // Six thick faceted carapace plates, low head and a serpentine rim.
            for(int i=0;i<6;i++) {
                double a=i*Math.PI/3;
                Vec3 p=center.add(Math.cos(a)*scale*.42,scale*.10,Math.sin(a)*scale*.42);
                g.sphere(p,scale*.34,c,alpha,false,3,6);
                g.line(p,p.add(0,scale*.22,0),scale*.025,COLORS[4],alpha);
            }
            g.sphere(center.add(0,-scale*.18,-scale*.8),scale*.21,c,alpha,false,4,8);
            for(int x:new int[]{-1,1})for(int z:new int[]{-1,1})g.line(center.add(x*scale*.3,-scale*.2,z*scale*.3),center.add(x*scale*.72,-scale*.4,z*scale*.6),scale*.09,c,alpha);
            Vec3 prev=null;
            for(int i=0;i<=28;i++) {
                double a=i*Math.PI*2/28+time*.009;
                Vec3 p=center.add(Math.cos(a)*scale*.91,Math.sin(a*2)*scale*.16,Math.sin(a)*scale*.91);
                if(prev!=null)g.line(prev,p,scale*.045,COLORS[4],alpha*.65);prev=p;
            }
        }
    }

    private static Vec3 heartDestination(ZhenyuanNodeBlockEntity node,double time) {
        BlockPos core=node.getCorePos();
        // The ritual core is the return-feet position, not necessarily the elevated central pedestal.
        // Read only the already loaded client column; never request or generate chunks from rendering.
        BlockPos heart=new BlockPos(core.getX(),node.getBlockPos().getY(),core.getZ());
        var level=node.getLevel();
        if(level!=null&&level.hasChunkAt(core)) {
            for(int dy=0;dy<=64;dy++) {
                BlockPos candidate=core.above(dy);
                if(level.isOutsideBuildHeight(candidate))break;
                if(level.getBlockEntity(candidate) instanceof ZhenyuanNodeBlockEntity center
                        &&center.getSlot()==4&&center.getCorePos().equals(core)) {
                    heart=candidate;break;
                }
            }
        }
        return Vec3.atLowerCornerOf(heart.subtract(node.getBlockPos()))
                .add(0,5.5+Math.sin(time*.022)*.055,0);
    }

    private void drawHeart(Geometry g, ZhenyuanNodeBlockEntity node, double t, double transition) {
        int mask=node.getOfferingMask(), oldMask=node.getPreviousVisualMask();
        boolean charging=node.getStage()==1;
        double power=heartPower(node,transition);
        double breath=1 + Math.sin(t*(charging?.09:.025))*.025;
        double radius=stageRadius(power*4)*breath;
        Vec3 center=new Vec3(0,5.5+Math.sin(t*.022)*.055,0);
        g.sphere(center,radius*1.045,COLORS[4],.035,true,10,24);
        for(int i=0;i<3;i++) {
            double angle=t*.012*(i%2==0?1:-1)+i*Math.PI/3;
            Vec3 horizontal=new Vec3(Math.cos(angle),0,Math.sin(angle));
            Vec3 tilted=Y.scale(.68).add(new Vec3(-Math.sin(angle),0,Math.cos(angle)).scale(.73));
            g.ring(center,horizontal,tilted,radius*(1.14+i*.07),.020,COLORS[4],.64,0,Math.PI*2);
        }
        // Each tribute contributes its own colored, differently inclined armillary orbit.
        for(int i=0;i<4;i++) if((mask&(1<<i))!=0) {
            double formed=(oldMask&(1<<i))!=0?1:transition;
            double angle=t*(.008+i*.0015)*(i%2==0?1:-1)+i*Math.PI/2;
            Vec3 a=new Vec3(Math.cos(angle),.20*Math.sin(i+1),Math.sin(angle)).normalize();
            // Shallower inclination keeps the enlarged armillary orbits above the floor.
            Vec3 b=new Vec3(-Math.sin(angle)*.785,.62,Math.cos(angle)*.785).normalize();
            double orbit=radius*(1.15+i*.05);
            g.ring(center,a,b,orbit,.012,COLORS[i],.68*formed,0,Math.PI*2*formed);
            Vec3 satellite=center.add(a.scale(Math.cos(t*.028+i)*orbit)).add(b.scale(Math.sin(t*.028+i)*orbit));
            g.diamond(satellite,.12,COLORS[i],.95*formed);
        }
        g.sigil(new Vec3(0,.79,0),1.50+power*1.08,COLORS[4],-t*.003,.60,4);
        if(power>.24)g.sigil(new Vec3(0,10.0+power*.30,0),1.35+power*.825,COLORS[4],t*.004,.24+power*.25,8);
        if(charging) {
            // Formation ascends in four counter-rotating spirals while the server prepares the arena.
            for(int strand=0;strand<4;strand++) {
                Vec3 previous=null;
                for(int j=0;j<48;j++) {
                    double u=j/47.0, a=t*.04+u*Math.PI*4+strand*Math.PI/2;
                    double r=(2.7-u*1.05)*(1+.05*Math.sin(t*.06));
                    Vec3 p=new Vec3(Math.cos(a)*r,.8+u*5.4,Math.sin(a)*r);
                    if(previous!=null)g.line(previous,p,.016,COLORS[strand],.57*(1-u*.55));
                    previous=p;
                }
            }
        }
    }

    private static double heartPower(ZhenyuanNodeBlockEntity node,double transition) {
        double contribution=0;
        for(int i=0;i<4;i++) if((node.getOfferingMask()&(1<<i))!=0)
            contribution+=(node.getPreviousVisualMask()&(1<<i))!=0?1:transition;
        return contribution/4;
    }

    private void renderOffering(ZhenyuanNodeBlockEntity node, double time, PoseStack pose,
                                MultiBufferSource buffers, double activation) {
        var item=ForgeRegistries.ITEMS.getValue(new ResourceLocation(Dynasty.MODID,OFFERINGS[node.getSlot()]));
        if(item==null)return;
        pose.pushPose();
        // The central offering orbits outside the opaque gold heart so it remains visible.
        if(node.getSlot()==4) {
            double a=time*.025;
            pose.translate(Math.cos(a)*4.8,5.5,Math.sin(a)*4.8);
        } else pose.translate(0,1.06+Math.sin(time*.045)*.025,0);
        pose.mulPose(Axis.YP.rotation((float)(time*.02)));
        float size=(float)((node.getSlot()==4?.975:.65)*Math.max(.08,activation));
        pose.scale(size,size,size);
        Minecraft.getInstance().getItemRenderer().renderStatic(new ItemStack(item),ItemDisplayContext.GROUND,
                LightTexture.FULL_BRIGHT,OverlayTexture.NO_OVERLAY,pose,buffers,node.getLevel(),node.getBlockPos().hashCode());
        pose.popPose();
    }

    private void renderLabel(ZhenyuanNodeBlockEntity node, PoseStack pose, MultiBufferSource buffers) {
        Minecraft mc=Minecraft.getInstance();
        if(mc.player==null || mc.player.distanceToSqr(Vec3.atCenterOf(node.getBlockPos()))>144)return;
        Component title=node.getSlot()==4&&node.timeline().getBoolean("Enabled")?Component.literal("中央 · 天命玉"):Component.translatable("ritual.dynasty.zhenyuan.slot."+node.getSlot());
        boolean offered=(node.getOfferingMask()&(1<<node.getSlot()))!=0;
        boolean pending=(node.timeline().getInt("Pending")&(1<<node.getSlot()))!=0;
        Component line=pending?Component.literal("正在献祭 · 请勿重复投放"):Component.translatable(offered?"ritual.dynasty.zhenyuan.offered":"ritual.dynasty.zhenyuan.place_hint");
        pose.pushPose();
        // Keep the existing interaction text below, not inside, the enlarged opaque sphere.
        pose.translate(0,node.getSlot()==4?1.1:1.85,0);
        pose.mulPose(mc.getEntityRenderDispatcher().cameraOrientation());
        pose.scale(-.015F,-.015F,.015F);
        int color=offered?0xAAFFCF:0xF8EACA;
        font.drawInBatch(title,-font.width(title)/2F,0,color,false,pose.last().pose(),buffers,
                Font.DisplayMode.NORMAL,0x660A1015,LightTexture.FULL_BRIGHT);
        font.drawInBatch(line,-font.width(line)/2F,11,0xCCDDE5,false,pose.last().pose(),buffers,
                Font.DisplayMode.NORMAL,0x660A1015,LightTexture.FULL_BRIGHT);
        pose.popPose();
    }
    @Override public boolean shouldRenderOffScreen(ZhenyuanNodeBlockEntity node) { return true; }
    @Override public int getViewDistance() { return 128; }
    private static double smooth(double t) { return t*t*(3-2*t); }

    /** Render-state encapsulation keeps depth testing and prevents ghost geometry through walls. */
    private static final class MagicType extends RenderType {
        private MagicType(String name,VertexFormat format,VertexFormat.Mode mode,int size,boolean crumbling,
                          boolean sort,Runnable setup,Runnable clear) { super(name,format,mode,size,crumbling,sort,setup,clear); }
        private static final RenderType TRANSLUCENT=create("dynasty_zhenyuan_magic",DefaultVertexFormat.POSITION_COLOR,
                VertexFormat.Mode.QUADS,65536,false,true,CompositeState.builder()
                        .setShaderState(POSITION_COLOR_SHADER).setTransparencyState(TRANSLUCENT_TRANSPARENCY)
                        .setCullState(NO_CULL).setWriteMaskState(COLOR_WRITE).createCompositeState(false));
        private static final RenderType SOLID=create("dynasty_zhenyuan_gold",DefaultVertexFormat.POSITION_COLOR,
                VertexFormat.Mode.QUADS,65536,false,false,CompositeState.builder()
                        .setShaderState(POSITION_COLOR_SHADER).setTransparencyState(NO_TRANSPARENCY)
                        .setCullState(CULL).setWriteMaskState(COLOR_DEPTH_WRITE).createCompositeState(false));
    }

    /** Untextured geometry uses radial normals for gold shading; emissive strokes use bounded alpha. */
    private static final class Geometry {
        final Matrix4f matrix; final VertexConsumer buffer;
        Geometry(Matrix4f matrix,VertexConsumer buffer){this.matrix=matrix;this.buffer=buffer;}
        void vertex(Vec3 p,float[] c,double alpha) {
            buffer.vertex(matrix,(float)p.x,(float)p.y,(float)p.z).color(c[0],c[1],c[2],(float)alpha).endVertex();
        }
        void quad(Vec3 a,Vec3 b,Vec3 c,Vec3 d,float[] color,double alpha) {
            vertex(a,color,alpha);vertex(b,color,alpha);vertex(c,color,alpha);vertex(d,color,alpha);
        }
        void line(Vec3 a,Vec3 b,double width,float[] color,double alpha) {
            Vec3 direction=b.subtract(a).normalize();
            Vec3 side=direction.cross(Math.abs(direction.y)>.9?X:Y).normalize().scale(width);
            quad(a.add(side),a.subtract(side),b.subtract(side),b.add(side),color,alpha);
            // Crossed ribbons remain visible edge-on without making oversized solid tubes.
            Vec3 second=direction.cross(side).normalize().scale(width);
            quad(a.add(second),a.subtract(second),b.subtract(second),b.add(second),color,alpha);
        }
        void ring(Vec3 center,Vec3 a,Vec3 b,double radius,double width,float[] color,double alpha,double offset,double sweep) {
            int segments=Math.max(12,(int)(64*Math.abs(sweep)/(Math.PI*2)));
            for(int i=0;i<segments;i++) {
                double t=offset+sweep*i/segments, next=offset+sweep*(i+1)/segments;
                Vec3 p=a.scale(Math.cos(t)).add(b.scale(Math.sin(t)));
                Vec3 q=a.scale(Math.cos(next)).add(b.scale(Math.sin(next)));
                quad(center.add(p.scale(radius-width)),center.add(p.scale(radius+width)),
                        center.add(q.scale(radius+width)),center.add(q.scale(radius-width)),color,alpha);
            }
        }
        void diamond(Vec3 center,double radius,float[] color,double alpha) {
            Vec3 top=center.add(0,radius*1.4,0), bottom=center.add(0,-radius*1.4,0);
            for(int i=0;i<4;i++) {
                Vec3 a=center.add(Math.cos(i*Math.PI/2)*radius,0,Math.sin(i*Math.PI/2)*radius);
                Vec3 b=center.add(Math.cos((i+1)*Math.PI/2)*radius,0,Math.sin((i+1)*Math.PI/2)*radius);
                quad(top,a,b,top,color,alpha);quad(bottom,b,a,bottom,color,alpha);
            }
        }
        void sigil(Vec3 center,double radius,float[] color,double angle,double alpha,int order) {
            ring(center,X,Z,radius,.010,color,alpha,angle,Math.PI*2);
            ring(center,X,Z,radius*.82,.005,color,alpha*.65,-angle,Math.PI*2);
            for(int i=0;i<24;i++) {
                double a=angle+i*Math.PI/12;
                Vec3 radial=new Vec3(Math.cos(a),0,Math.sin(a));
                line(center.add(radial.scale(radius*.88)),center.add(radial.scale(radius*(i%3==0?1.10:1.04))),.007,color,alpha);
            }
            for(int i=0;i<8;i++) {
                double a=-angle+i*Math.PI/4;
                Vec3 radial=new Vec3(Math.cos(a),0,Math.sin(a)), tangent=new Vec3(-Math.sin(a),0,Math.cos(a));
                for(int row=0;row<3;row++) {
                    Vec3 p=center.add(radial.scale(radius*(.52+row*.075)));
                    double w=radius*.11;
                    if(((i+order)>>(row%3)&1)==0)line(p.add(tangent.scale(-w)),p.add(tangent.scale(w)),.009,color,alpha);
                    else {
                        line(p.add(tangent.scale(-w)),p.add(tangent.scale(-w*.28)),.009,color,alpha);
                        line(p.add(tangent.scale(w*.28)),p.add(tangent.scale(w)),.009,color,alpha);
                    }
                }
            }
        }
        void sphere(Vec3 center,double radius,float[] color,double alpha,boolean clear,int lat,int lon) {
            sphereImpl(center,radius,color,alpha,clear,0,lat,lon);
        }
        void rotatedSphere(Vec3 center,double radius,float[] color,double alpha,double rotation,int lat,int lon) {
            sphereImpl(center,radius,color,alpha,false,rotation,lat,lon);
        }
        void sphereImpl(Vec3 center,double radius,float[] color,double alpha,boolean clear,double rotation,int lat,int lon) {
            for(int y=0;y<lat;y++) for(int x=0;x<lon;x++) {
                // Outward counter-clockwise winding; keep the solid gold sphere back-face culled.
                Vec3[] normals={normal(y,x,lat,lon,rotation),normal(y,x+1,lat,lon,rotation),
                        normal(y+1,x+1,lat,lon,rotation),normal(y+1,x,lat,lon,rotation)};
                for(Vec3 n:normals) {
                    double light=clear?1:.32+.68*Math.max(0,n.dot(new Vec3(-.45,.72,.53).normalize()));
                    // A moving engraved meridian subtly modulates the gold, making rotation readable.
                    if(!clear)light*=.88+.12*Math.cos(Math.atan2(n.z,n.x)*12-rotation*12);
                    float[] shaded={(float)(color[0]*light),(float)(color[1]*light),(float)(color[2]*light)};
                    vertex(center.add(n.scale(radius)),shaded,alpha);
                }
            }
        }
        static Vec3 normal(int y,int x,int lat,int lon,double rotation) {
            double v=Math.PI*y/lat,u=Math.PI*2*x/lon+rotation;
            return new Vec3(Math.sin(v)*Math.cos(u),Math.cos(v),Math.sin(v)*Math.sin(u));
        }
    }
}
