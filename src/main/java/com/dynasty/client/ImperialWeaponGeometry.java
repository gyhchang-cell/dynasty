package com.dynasty.client;

/** Pure geometry shared by the game renderer and offline previews; no particle sprites. */
public final class ImperialWeaponGeometry {
    public static final double DESCENT_SEAL_RADIUS=2.35;
    /** Three times the preceding release's linear dimensions, not a damage multiplier. */
    public static final double DRAGON_ENLARGEMENT=3.0;
    // Independent attack scale: leave the paired imperial guardians unchanged.
    public static final double DESCENT_DRAGON_SIZE=2.7*1.5;
    public static final double DESCENT_START_HEIGHT=12.0;
    public static final int SEAL_FORMATION_TICKS=8;
    public record DescentPhase(double charge,double connection,double travel,double dragonAlpha) {}
    /** Server timing is supplied by the caller so previews and rendering use the same phase math. */
    public static DescentPhase descentPhase(double age,int dragonStart,int impactTick) {
        return descentPhase(age,dragonStart,impactTick,false);
    }
    /** A confirmed server hit always wins over the client's interpolated clock. */
    public static DescentPhase descentPhase(double age,int dragonStart,int impactTick,boolean landed) {
        if(landed)age=Math.max(age,impactTick);
        return new DescentPhase(clamp(age/SEAL_FORMATION_TICKS),
                clamp((age-SEAL_FORMATION_TICKS)/Math.max(1,dragonStart-SEAL_FORMATION_TICKS)),
                clamp((age-dragonStart)/Math.max(1,impactTick-dragonStart)),clamp((age-dragonStart)/3));
    }
    /** A rigid model-space transform, shared by the cached mesh and diagnostics. */
    public record DescentPose(P origin,P x,P y,P z) {
        public P direction(P value){return x.scale(value.x).add(y.scale(value.y)).add(z.scale(value.z));}
        public P point(P value){return origin.add(direction(value).scale(DESCENT_DRAGON_SIZE));}
    }
    private static final class DiveAxes {
        // The sculpted head has its own sideways yaw: rotateZ(135 degrees) alone never makes
        // its actual snout point down. Build a full orthonormal frame from the real landmarks.
        static final P FRONT=unit(ImperialDragonMesh.MUZZLE.add(ImperialDragonMesh.HEAD_CENTER.scale(-1)));
        static final P UP=unit(new P(0,1,0).add(FRONT.scale(-FRONT.y)));
        static final P RIGHT=cross(FRONT,UP);
        // Snout -> -Y; original body-up -> -Z, leaving the long body trailing away from the caster.
        static final P X=new P(RIGHT.x,-FRONT.x,-UP.x);
        static final P Y=new P(RIGHT.y,-FRONT.y,-UP.y);
        static final P Z=new P(RIGHT.z,-FRONT.z,-UP.z);
    }
    private static P cross(P a,P b){return new P(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x);}
    private static P unit(P p){return p.scale(1/Math.sqrt(p.x*p.x+p.y*p.y+p.z*p.z));}
    /** Nose-first descent through the upper seal's centre; endpoint is the authoritative hit point. */
    public static DescentPose descentDragonPose(double headOffset,double travel) {
        var rotation=new DescentPose(new P(0,0,0),DiveAxes.X,DiveAxes.Y,DiveAxes.Z);
        P hit=rotation.direction(ImperialDragonMesh.MUZZLE).scale(DESCENT_DRAGON_SIZE);
        double t=clamp(travel),lift=(headOffset+DESCENT_START_HEIGHT)*(1-t*t);
        return new DescentPose(new P(-hit.x,lift-hit.y,-hit.z),DiveAxes.X,DiveAxes.Y,DiveAxes.Z);
    }
    /** Compatibility accessor; callers drawing a dragon must also apply descentDragonPose axes. */
    public static P descentDragonOrigin(double headOffset,double travel) {
        return descentDragonPose(headOffset,travel).origin;
    }
    public record P(double x, double y, double z) {
        public P add(P p) { return new P(x+p.x,y+p.y,z+p.z); }
        public P scale(double s) { return new P(x*s,y*s,z*s); }
    }
    @FunctionalInterface public interface Stroke { void line(P a, P b, double width, int color, double alpha); }
    @FunctionalInterface public interface Surface {
        void face(P a,P b,P c,P d,int color,double alpha);
        default void normalFace(P a,P b,P c,P d,int color,double alpha,P na,P nb,P nc,P nd) {
            face(a,b,c,d,color,alpha);
        }
        /** Runtime may draw one cached mesh; offline consumers keep the expanded-face fallback. */
        default boolean dragonInstance(P origin,double size,double angle,int color,double alpha,boolean mirrored) {return false;}
    }
    private final Stroke out;
    private final Surface mesh;
    public ImperialWeaponGeometry(Stroke out) { this(out,(a,b,c,d,color,alpha)->{}); }
    public ImperialWeaponGeometry(Stroke out,Surface mesh) { this.out=out; this.mesh=mesh; }
    private void line(double x,double y,double xx,double yy,double z,double width,int color,double alpha) {
        out.line(new P(x,y,z),new P(xx,yy,z),width,color,alpha);
    }
    private void ring(double radius,double z,double angle,int sides,int color,double alpha) {
        for(int i=0;i<sides;i++) {
            double a=angle+i*Math.PI*2/sides,b=angle+(i+1)*Math.PI*2/sides;
            line(Math.cos(a)*radius,Math.sin(a)*radius,Math.cos(b)*radius,Math.sin(b)*radius,z,.012,color,alpha);
        }
    }

    /** Curving celestial dragon with a tapered body, dorsal spines, jaw, antlers and whiskers. */
    public void dragon(P origin,double size,double angle,double time,int color,double alpha) {
        if(mesh.dragonInstance(origin,size,angle,color,alpha,false))return;
        boolean jade=((color>>16)&255)<150;
        for(int i=0;i<ImperialDragonMesh.FACES.size();i++) {
            var face=ImperialDragonMesh.FACES.get(i);
            var normals=DragonNormals.VALUE.get(i);
            mesh.normalFace(transform(face.a(),origin,size,angle),transform(face.b(),origin,size,angle),
                    transform(face.c(),origin,size,angle),transform(face.d(),origin,size,angle),
                    ImperialDragonMesh.color(face.material(),jade),alpha,normal(normals.a(),angle),
                    normal(normals.b(),angle),normal(normals.c(),angle),normal(normals.d(),angle));
        }
    }
    // Loaded once, not welded/smoothed every render frame; lazy avoids a mesh/static-initializer cycle.
    private static final class DragonNormals {
        static final java.util.List<ImperialMeshNormals.Normals> VALUE=ImperialMeshNormals.build(
                ImperialDragonMesh.FACES.stream().map(f->new ImperialMeshNormals.Quad(
                        point(f.a()),point(f.b()),point(f.c()),point(f.d()),f.material())).toList());
    }
    static java.util.List<ImperialMeshNormals.Normals> dragonNormals(){return DragonNormals.VALUE;}
    private static ImperialMeshNormals.Point point(P p){return new ImperialMeshNormals.Point(p.x,p.y,p.z);}
    private static P normal(ImperialMeshNormals.Point p,double a) {
        return new P(p.x()*Math.cos(a)-p.y()*Math.sin(a),p.x()*Math.sin(a)+p.y()*Math.cos(a),p.z());
    }
    private static P transform(P p,P origin,double size,double a) {
        return new P((p.x*Math.cos(a)-p.y*Math.sin(a))*size,
                (p.x*Math.sin(a)+p.y*Math.cos(a))*size,p.z*size).add(origin);
    }

    public void aura(int style,double time,double alpha) {
        if(style==1) {
            // Square imperial seal, not another generic circular magic array.
            ring(1.06,0,Math.PI/4,4,0xffb83d,alpha);
            ring(.94,0,Math.PI/4,4,0xffe5a5,alpha*.65);
            edict(.63,0,alpha);
            for(int i=0;i<8;i++) {
                double a=i*Math.PI/4+time*.006;
                double x=Math.cos(a)*1.2,y=Math.sin(a)*1.2;
                line(x,y,x*1.09,y*1.09,0,.018,0xffd274,alpha);
            }
            dragon(new P(1.05,0,.08).scale(DRAGON_ENLARGEMENT),1.18*DRAGON_ENLARGEMENT,-.18+Math.sin(time*.015)*.04,time,0xffb938,alpha);
            // Mirrored guardian faces inward; both heads stay upright rather than orbiting upside down.
            new ImperialWeaponGeometry(out,new Surface() {
                private P mirror(P p){return new P(-p.x,p.y,p.z);}
                public void face(P a,P b,P c,P d,int col,double v) {
                    mesh.face(mirror(a),mirror(b),mirror(c),mirror(d),col,v);
                }
                public void normalFace(P a,P b,P c,P d,int col,double v,P na,P nb,P nc,P nd) {
                    mesh.normalFace(mirror(a),mirror(b),mirror(c),mirror(d),col,v,
                            mirror(na),mirror(nb),mirror(nc),mirror(nd));
                }
                public boolean dragonInstance(P origin,double size,double angle,int color,double alpha,boolean mirrored) {
                    return mesh.dragonInstance(mirror(origin),size,-angle,color,alpha,!mirrored);
                }
            })
                    .dragon(new P(1.05,0,-.08).scale(DRAGON_ENLARGEMENT),1.18*DRAGON_ENLARGEMENT,-.18+Math.sin(time*.015)*.04,time,0xffdc83,alpha);
        } else {
            dragon(new P(.15,-.02,0).scale(DRAGON_ENLARGEMENT),1.30*DRAGON_ENLARGEMENT,-.15+Math.sin(time*.015)*.07,time,0x22dcb2,alpha);
            for(int k=0;k<3;k++) {
                P last=null;
                for(int i=0;i<36;i++) {
                    double a=i*.1+time*.01+k*.3;
                    P p=new P(Math.cos(a)*(1.95+k*.09),Math.sin(a)*(1.95+k*.09),-.10);
                    if(last!=null)out.line(last,p,.008,0x80ffe3,alpha*.28); last=p;
                }
            }
        }
    }

    public void slash(int style,double progress,double alpha) {
        int color=style==1?0xffcf67:0x37efc2;
        for(int layer=0;layer<3;layer++) {
            P last=null;
            for(int i=0;i<=56;i++) {
                double t=i/56.0,a=-2.5+t*2.75+progress*.8;
                double radius=1.7+layer*.18+progress*.5;
                P p=new P(Math.cos(a)*radius,Math.sin(a)*radius*.55,.20*Math.sin(a));
                if(last!=null)out.line(last,p,(layer==0?.09:.022)*Math.sin(t*Math.PI),color,alpha*(1-layer*.23));
                last=p;
            }
        }
        if(style==1) for(int k=0;k<5;k++) {
            double x=-1.2+k*.6;
            out.line(new P(x,-.20,0),new P(x+.15,.25,0),.016,0xfff2cd,alpha*.6);
        }
    }

    public void summonSeal(double time,double alpha) {
        new BowSigilGeometry(Math.min(1,alpha),(x1,y1,x2,y2,w)->
                line(x1,y1,x2,y2,0,w,0x79ffe2,alpha)).draw(3,time);
    }

    /** Two identical horizontal arrays; twelve rising rune pillars join them into a readable cage. */
    public void sealCage(double time,double charge,double connection,double bottom,double top,double radius,double alpha) {
        charge=clamp(charge);connection=clamp(connection);alpha=clamp(alpha);
        if(charge<=0||alpha<=0||radius<=0||top<=bottom)return;
        final double visibility=alpha;
        // Formation is separate from opacity: fading must not unwind/retrace the seal's geometry.
        for(double height:new double[]{bottom,top}) {
            new BowSigilGeometry(charge,(x1,y1,x2,y2,w)->out.line(
                    new P(x1*radius,height,y1*radius),new P(x2*radius,height,y2*radius),
                    w*radius,0x79ffe2,visibility)).draw(3,time);
        }
        if(connection<=0)return;
        double rise=ease(connection),height=top-bottom,tip=bottom+height*rise;
        double orbit=radius*.955,spin=time*.007;
        for(int i=0;i<12;i++) {
            double angle=spin+i*Math.PI/6,c=Math.cos(angle),s=Math.sin(angle);
            P base=new P(c*orbit,bottom,s*orbit),end=new P(c*orbit,tip,s*orbit);
            out.line(base,end,.012,0x8cffe6,alpha*.86);
            // Twin fine rails and small diamond clasps read as a seal, not a solid prison wall.
            for(int side:new int[]{-1,1}) {
                double offset=side*.045;
                out.line(new P(base.x-s*offset,bottom,base.z+c*offset),
                        new P(end.x-s*offset,tip,end.z+c*offset),.0035,0x47baac,alpha*.5);
            }
            for(double fraction:new double[]{.32,.68}) {
                double y=bottom+height*fraction;
                if(tip<y+.09)continue;
                P low=new P(base.x,y-.09,base.z),high=new P(base.x,y+.09,base.z);
                P left=new P(base.x-s*.065,y,base.z+c*.065),right=new P(base.x+s*.065,y,base.z-c*.065);
                out.line(low,left,.006,0xf6dda1,alpha*.7);out.line(left,high,.006,0xf6dda1,alpha*.7);
                out.line(high,right,.006,0xf6dda1,alpha*.7);out.line(right,low,.006,0xf6dda1,alpha*.7);
            }
        }
        // A faint travelling collar makes the upward connection front visible; two completed
        // collars stay behind it. They remain thin and never fill the enclosed target's silhouette.
        cageCollar(orbit,tip,spin,alpha*.62);
        for(double fraction:new double[]{.32,.68})if(rise>fraction)
            cageCollar(orbit,bottom+height*fraction,spin,alpha*.27);
    }
    private void cageCollar(double radius,double height,double spin,double alpha) {
        for(int i=0;i<72;i++) {
            double a=spin+i*Math.PI/36,b=spin+(i+1)*Math.PI/36;
            out.line(new P(Math.cos(a)*radius,height,Math.sin(a)*radius),
                    new P(Math.cos(b)*radius,height,Math.sin(b)*radius),.0045,0x63dccc,alpha);
        }
    }
    private static double clamp(double value){return Math.max(0,Math.min(1,value));}
    private static double ease(double value){return value*value*(3-2*value);}

    public void impact(int style,double progress,double alpha) {
        if(style==1) {
            // Narrow imperial blade sigil with swept cloud filigree, no square box or bulky glyph.
            double length=1.25+progress*.3;
            line(0,-.65,0,length,0,.022,0xfff2c5,alpha);
            for(int side:new int[]{-1,1}) {
                line(0,length,side*.12,.12,0,.016,0xffd579,alpha);
                line(side*.12,.12,0,-.14,0,.016,0xffd579,alpha);
                line(0,-.18,side*.48,-.02,0,.022,0xffcf70,alpha);
                line(side*.48,-.02,side*.29,-.26,0,.012,0xffe7a5,alpha);
                for(int k=0;k<3;k++) {
                    P last=null;
                    for(int i=0;i<=28;i++) {
                        double t=i/28.0;
                        P p=new P(side*(.22+Math.sin(t*3.4)*(.45+k*.15)),.88-t*1.8-k*.04,-.04);
                        if(last!=null)out.line(last,p,.008,0xffc967,alpha*(.7-k*.15));last=p;
                    }
                }
            }
            ring(.08,0,Math.PI/4,4,0xffecb1,alpha);
        } else {
            dragon(new P(0,0,0),(.8+progress*.7)*DRAGON_ENLARGEMENT,-progress*1.2,progress*25,0x35edbd,alpha);
            for(int k=0;k<3;k++)line(-.55+k*.32,.65,.1+k*.32,-.55,0,.028,0xb5ffe6,alpha);
        }
    }

    /** Hand-drawn strokes for 敕, kept upright and separate from the rotating dragons. */
    private void edict(double s,double z,double alpha) {
        double[][] strokes={{-.85,.62,-.08,.62},{-.72,.32,-.2,.32},{-.72,.32,-.72,-.05},{-.72,-.05,-.2,-.05},
                {-.2,-.05,-.2,.32},{-.46,.85,-.46,-.8},{-.46,-.12,-.88,-.62},{-.46,-.12,-.05,-.52},
                {.35,.83,.10,.23},{.22,.42,.87,.42},{.67,.42,.56,-.13},{.56,-.13,.18,-.77},
                {.22,.23,.42,-.28},{.42,-.28,.88,-.77}};
        for(double[] a:strokes)line(a[0]*s,a[1]*s,a[2]*s,a[3]*s,z,.025,0xffe6ab,alpha);
    }
}
