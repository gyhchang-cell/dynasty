package com.dynasty;

import com.dynasty.HouyiAvatarShape.Face;
import com.dynasty.HouyiAvatarShape.Material;
import com.dynasty.HouyiAvatarShape.P;
import net.minecraft.world.phys.Vec3;
import java.util.List;
import static com.dynasty.GuanYuSculptor.*;
import static com.dynasty.HouyiAvatarShape.Material.*;

/** Anatomical control surfaces, fitted armor and a connected exterior guandao, all real mesh. */
public final class GuanYuAvatarShape {
    public static final double HEIGHT=9;
    public static final P GRIP=p(-2.42,5.38,1.0);
    public static final P WEAPON_UP=p(-Math.tan(Math.toRadians(12)),1,Math.tan(Math.toRadians(7))).unit();
    private static final P WEAPON_ACROSS=p(1,Math.tan(Math.toRadians(12)),0).unit();
    private static final P WEAPON_NORMAL=WEAPON_ACROSS.cross(WEAPON_UP).unit();
    public static final P SHAFT_BOTTOM=GRIP.sub(WEAPON_UP.scale(3.90)),SHAFT_TOP=GRIP.add(WEAPON_UP.scale(1.50));
    private static final P SCULPT_BOTTOM=p(-2.59+.77*(1.98-.91)/7.32,1.98,.83),SCULPT_TOP=p(-1.82,8.23,.83);
    // Manual trace of the user's third photograph (474 x 316), in SOURCE PIXELS.
    // Each row is one cubic: end of previous row -> two controls -> endpoint.
    // Only the short heel behind the photographed gold socket is inferred.
    // Do not replace this asymmetric outline with the retired procedural leaf curves.
    private static final double[][] BLADE_PHOTO_CURVES={
        {280,151},
        {256,152,209,173,172,165},
        {173,175,181,183,191,187},
        {176,188,150,185,135,180},
        {111,189,79,199,50,190},
        {62,214,88,249,111,255},
        {120,259,131,258,140,253},
        {171,237,198,224,222,211},
        {246,197,265,186,281,179},
        {281,170,280,159,280,151}
    };
    private static final double PHOTO_SCALE=.014, PHOTO_AXIS_X=-.9138115486, PHOTO_AXIS_Y=.4061384661;
    private record Volume(P c,P r) {}
    // Only major anatomical volumes clear blocks; fine ornament must never enlarge the clearing area.
    private static final List<Volume> VOLUMES=List.of(
        new Volume(p(0,5.54,0),p(1.25,1.53,.75)),new Volume(p(0,7.95,0),p(.59,.86,.67)),
        new Volume(p(0,3,-.20),p(1.42,1.6,.77)),new Volume(p(-.77,1.34,.18),p(.50,1.30,.63)),
        new Volume(p(.82,1.35,.19),p(.50,1.30,.63)),new Volume(p(-1.62,6.20,.18),p(.48,.85,.55)),
        new Volume(p(1.70,6.30,.37),p(.49,.76,.60)),new Volume(p(-2.03,5.51,.69),p(.28,.48,.36)),
        new Volume(p(1.60,7,.89),p(.25,.62,.24)),new Volume(p(0,4.65,-.88),p(1.82,2.15,.42)),
        new Volume(p(-2.15,5.105,.83),p(.43,3.125,.13)),new Volume(p(-3.13,1.23,.83),p(.73,1.05,.15)));
    private static final List<P> BLADE_BOUNDARY=photoOutline();
    public static final List<Face> MESH=create();
    private static List<Face> create() {
        GuanYuSculptor m=new GuanYuSculptor();
        legs(m);body(m);cape(m);armor(m);arms(m);head(m);weapon(m);
        return List.copyOf(m.faces);
    }
    private static void legs(GuanYuSculptor m) {
        GuanYuSculptor local=new GuanYuSculptor();legSculpt(local);
        for(Face f:local.faces)m.quad(legVolume(f.a()),legVolume(f.b()),legVolume(f.c()),legVolume(f.d()),f.material());
    }
    private static P legVolume(P q) {
        double center=Math.copySign(.84,q.x());
        return p(center+(q.x()-center)*1.14,q.y(),.08+(q.z()-.08)*1.08);
    }
    private static void legSculpt(GuanYuSculptor m) {
        for(int s:new int[]{-1,1}) {
            m.sweep(new P[]{p(s*.52,4.49,-.04),p(s*.72,3.35,-.05),p(s*.80,2.13,.05)},new double[]{.46,.46,.34},new double[]{.40,.44,.33},18,24,CLOTH_GREEN);
            m.profile(new double[][]{{.47,.28,.27,.23,s*.84,.08},{.88,.30,.32,.25,s*.84,.08},{1.52,.37,.37,.29,s*.82,.05},{2.09,.33,.30,.27,s*.80,.05}},32,18,JADE_DARK);
            m.profile(new double[][]{{.09,.30,.53,.30,s*.86,.26},{.20,.41,.66,.33,s*.86,.26},{.43,.40,.61,.32,s*.86,.26},{.67,.28,.32,.25,s*.84,.13}},32,12,JADE_DARK);
            m.sweep(new P[]{p(s*.86,.28,.62),p(s*.86,.32,.93),p(s*.86,.48,1.05)},new double[]{.30,.22,.04},new double[]{.14,.11,.035},10,16,CLOTH_GREEN);
            m.surface(36,3,(u,v)->{double a=u*Math.PI*2;return p(s*.86+.405*Math.sin(a),.11+v*.085,.26+(.33+.34*Math.max(0,Math.cos(a)))*Math.cos(a));},GOLD_OLD);
            m.plate(p(s*.82,2.21,.39),p(1,0,0),p(0,-1,.05),.74,.48,.11,GOLD_OLD);
            m.plate(p(s*.82,1.84,.405),p(1,0,0),p(0,-1,.02),.51,1.05,.07,GOLD_OLD);
            m.plate(p(s*.82,1.77,.49),p(1,0,0),p(0,-1,0),.32,.76,.04,EMERALD);
            flourish(m,p(s*.82,1.45,.555),.30,.48,s,GOLD_PALE);
            for(int j=0;j<6;j++)for(int k=0;k<3;k++)m.plate(p(s*.82+(k-1)*.17,1.93-j*.20,.40),p(1,0,0),p(0,-1,0),.19,.25,.025,j%2==0?GOLD_OLD:BRONZE);
            flourish(m,p(s*.86,.43,.88),.30,.19,s,GOLD_PALE);
        }
    }
    private static void body(GuanYuSculptor m) {
        m.profile(new double[][]{{4.24,.90,.49,.44,0,0},{4.68,.94,.55,.49,0,0},{5.23,1.10,.63,.59,0,0},{5.98,1.30,.70,.66,0,0},{6.56,1.36,.64,.60,0,0},{6.84,1.03,.47,.44,0,0},{7.20,.37,.29,.28,0,0}},32,22,JADE_DARK);
        // Short under-tunic; the long silhouette is made by separated front/side/rear lames.
        m.profile(new double[][]{{3.10,1.06,.49,.50,0,-.08},{3.70,1.04,.52,.51,0,-.06},{4.49,.89,.49,.45,0,0}},24,10,CLOTH_GREEN);
        for(int s:new int[]{-1,1}) {
            panel(m,new P[]{p(s*.51,4.45,-.57),p(s*.67,3.65,-.72),p(s*.77,2.80,-.78),p(s*.88,2.28,-.68)},.40,.32,JADE_DARK);
        }
        for(int s:new int[]{-1,1}) {
            panel(m,new P[]{p(s*.68,4.50,.47),p(s*1.07,3.78,.72),p(s*1.15,2.82,.67),p(s*1.28,2.40,.25)},.48,.35,JADE_DARK);
            m.shell(10,12,(u,v)->{
                double a=(.25+u*.50)*Math.PI,flare=.98+.72*Math.sin(v*Math.PI*.49);
                return p(s*flare*Math.sin(a),4.45-v*(1.93+.17*Math.sin(u*Math.PI)),.61*Math.cos(a)-.06);
            },p(-s*.075,0,0),JADE_DARK,JADE_DARK);
            P[] rim=new P[17];for(int k=0;k<17;k++){double a=(.25+k/32.)*Math.PI;rim[k]=p(s*1.70*Math.sin(a),2.52-.17*Math.sin(k/16.*Math.PI),.61*Math.cos(a)-.07);}
            m.wire(rim,.020,GOLD_OLD,16);
            for(int j=0;j<8;j++)for(int k=0;k<4;k++)m.plate(p(s*(.68+k*.16+j*.037),4.24-j*.20,.74-.035*k),p(1,0,0),p(s*.12,-1,0),.18,.27,.018,(j+k)%3==0?GOLD_OLD:BRONZE);
        }
        panel(m,new P[]{p(0,4.49,.67),p(.03,3.48,.89),p(.02,2.42,.94),p(.32,1.83,.82)},.53,.37,JADE_DARK);
        for(int j=0;j<4;j++)for(int s:new int[]{-1,1})flourish(m,p(s*.21,3.96-j*.49,.95),.22,.24,s,GOLD_OLD);
        for(int s:new int[]{-1,1}) {
            m.wire(new P[]{p(s*.48,4.53,.77),p(s*.62,3.90,.91),p(s*.47,3.12,.96),p(s*.08,2.76,.97)},.038,SILK_RED,30);
            m.wire(new P[]{p(s*.50,4.53,.80),p(s*.64,3.90,.94),p(s*.50,3.12,.99),p(s*.10,2.73,1)},.009,GOLD_PALE,30);
            for(int k=0;k<7;k++)m.strand(new P[]{p(s*.075+k*.011,2.80,1),p(s*.17+k*.011,2.29,1.04),p(s*.27+k*.012,1.90,.92)},.012,GOLD_PALE,14);
        }
    }
    private static void cape(GuanYuSculptor m) {
        for(int s:new int[]{-1,1}) {
            m.sweep(new P[]{p(s*.90,6.91,-.38),p(s*.91,6.89,-.60),p(s*.91,6.76,-.75)},new double[]{.065,.065,.05},new double[]{.040,.042,.035},8,8,GOLD_OLD);
            m.ellipsoid(p(s*.91,6.76,-.755),p(.115,.10,.048),GOLD_OLD,10,6);
            m.ellipsoid(p(s*.91,6.76,-.794),p(.046,.040,.016),JADE_DARK,8,5);
        }
        m.shell(6,14,(u,v)->p((u-.5)*.34,6.88-v*3.10,-.69-.62*Math.sin(v*.67*Math.PI)),p(0,0,-.08),SILK_RED,CRIMSON);
        for(int s:new int[]{-1,1}) {
            // Mantle, mid-drape, then three separated tails per side: visible even in clay review.
            m.shell(10,8,(u,v)->capePoint(s,u,v*.30),p(0,0,-.085),SILK_RED,CRIMSON);
            m.shell(10,10,(u,v)->capePoint(s,u,.30+v*.36),p(0,0,-.075),SILK_RED,CRIMSON);
            for(int tail=0;tail<3;tail++) {
                final int t=tail;
                m.shell(4,10,(u,v)->capePoint(s,(t+.025+u*.95)/3.,.66+v*(.34-.025*t)),p(0,0,-.065),SILK_RED,CRIMSON);
            }
            P[] edge=new P[25];for(int j=0;j<=24;j++)edge[j]=capePoint(s,1,j/24.).add(p(0,0,-.09));
            m.wire(edge,.026,GOLD_OLD,24);
        }
    }
    private static P capePoint(int side,double u,double v) {
        return p(side*(.14+u*(1.06+.74*Math.sin(v*Math.PI*.65))),
                6.89-v*(4.72-.28*u)+.09*Math.sin(u*4+v*3)*v,
                -.65-.61*Math.sin(v*Math.PI*.67)-.11*Math.cos(u*Math.PI*6)*(.3+.7*v));
    }
    private static void armor(GuanYuSculptor m) {
        for(int s:new int[]{-1,1}) {
            // Cast pectoral plates over the underlayer; separate breast, flank and abdominal volumes.
            m.shell(6,8,(u,v)->p(s*(.10+u*1.02),6.69-v*1.10,
                    .70-.24*u*u+.09*Math.sin(v*Math.PI)+.065*Math.sin(u*Math.PI)),p(0,0,-.09),JADE_DARK,BRONZE);
            m.sweep(new P[]{p(s*1.13,6.34,.25),p(s*1.15,5.84,.20),p(s*.97,5.20,.12)},new double[]{.20,.21,.15},new double[]{.40,.42,.36},10,10,JADE_DARK);
        }
        for(int row=0;row<7;row++)for(int col=-7;col<=7;col++) {
            double x=col*.143+(row%2)*.04,y=6.51-row*.233;if(Math.abs(x)>1.07)continue;
            double z=.70*Math.sqrt(Math.max(.01,1-x*x/1.80))+.075;
            m.plate(p(x,y,z),p(1,0,-x*.38),p(0,-1,.02),.17,.31,.028,(row+col)%5==0?GOLD_OLD:JADE_DARK);
        }
        for(int side:new int[]{-1,1})for(int layer=0;layer<4;layer++) {
            final int s=side,l=layer;
            m.shell(12,4,(u,v)->{double a=(u-.5)*Math.PI;return p(s*(1.04+l*.13+v*.42),6.73-l*.14+.32*Math.cos(a)-v*.20,(.66-l*.028)*Math.sin(a));},p(0,-.065,0),layer%2==0?GOLD_OLD:JADE_DARK,BRONZE);
            P[] border=new P[25];for(int k=0;k<=24;k++){double a=(k/24.-.5)*Math.PI;border[k]=p(s*(1.46+l*.13),6.53-l*.14+.32*Math.cos(a),(.66-l*.028)*Math.sin(a));}m.wire(border,.022,GOLD_PALE,28);
            for(int k=0;k<7;k++){double a=(k/6.-.5)*2.7;m.ellipsoid(p(s*(1.39+l*.13),6.58-l*.14+.32*Math.cos(a),(.67-l*.028)*Math.sin(a)),p(.027,.027,.027),GOLD_PALE,8,4);}
        }
        for(int s:new int[]{-1,1}) {
            m.wire(new P[]{p(s*.38,7.02,.18),p(s*.58,6.82,.59),p(s*.74,6.58,.78),p(s*.61,6.37,.88)},.044,GOLD_PALE,24);
            m.wire(new P[]{p(s*.98,6.78,.38),p(s*.93,5.98,.74),p(s*.78,5.13,.75),p(s*.41,4.58,.73)},.055,SILK_RED,34);
            m.wire(new P[]{p(s*1.03,6.78,.39),p(s*.98,5.98,.75),p(s*.83,5.13,.76),p(s*.46,4.58,.74)},.013,GOLD_PALE,34);
        }
        breastplateRelief(m);
        shoulderLames(m);
        m.profile(new double[][]{{4.40,1.00,.60,.47,0,0},{4.47,1.035,.64,.50,0,0},{4.67,1.045,.64,.49,0,0},{4.73,1.02,.58,.47,0,0}},48,7,GOLD_OLD);
        m.plate(p(0,4.76,.68),p(1,0,0),p(0,-1,0),.64,.40,.10,GOLD_PALE);m.ellipsoid(p(0,4.56,.805),p(.13,.15,.047),CRIMSON,20,12);
        for(int s:new int[]{-1,1})for(int k=0;k<3;k++)m.plate(p(s*(.37+k*.18),4.68,.63-.05*k),p(1,0,-s*.30),p(0,-1,0),.15,.24,.035,JADE_DARK);
    }
    /** Cast dragon-mask relief: separate brow, muzzle, fangs and flame leaves, not a flat medallion. */
    private static void breastplateRelief(GuanYuSculptor m) {
        m.profile(new double[][]{{5.42,.16,.06,.025,0,.80},{5.56,.28,.11,.035,0,.81},{5.78,.31,.17,.04,0,.81},{6.02,.23,.14,.035,0,.78},{6.19,.13,.08,.03,0,.76}},28,18,GOLD_OLD);
        m.ellipsoid(p(0,5.52,.964),p(.205,.125,.028),JADE_DARK,20,10);
        m.sweep(new P[]{p(-.23,5.46,.945),p(-.11,5.38,.966),p(0,5.35,.971),p(.12,5.38,.966),p(.23,5.46,.945)},new double[]{.035,.045,.045,.035},new double[]{.023,.032,.032,.023},24,10,GOLD_PALE);
        m.profile(new double[][]{{5.57,.16,.06,.025,0,.982},{5.64,.23,.09,.035,0,.975},{5.74,.22,.10,.04,0,.95},{5.81,.12,.07,.03,0,.94}},24,12,GOLD_OLD);
        m.strand(new P[]{p(0,5.73,1.055),p(0,5.92,.982),p(0,6.12,.893)},.025,GOLD_PALE,18);
        for(int s:new int[]{-1,1}) {
            m.ellipsoid(p(s*.125,5.685,1.059),p(.045,.026,.010),JADE_DARK,12,6);
            m.strand(new P[]{p(s*.075,5.70,1.062),p(s*.126,5.735,1.061),p(s*.181,5.712,1.042)},.016,GOLD_PALE,12);
            m.ellipsoid(p(s*.192,5.927,.970),p(.080,.035,.024),JADE_DARK,12,6);
            m.ellipsoid(p(s*.192,5.931,.992),p(.026,.027,.009),EMERALD,10,6);
            m.sweep(new P[]{p(s*.065,5.944,.992),p(s*.18,6.025,.992),p(s*.30,6.045,.918),p(s*.41,6.104,.790)},new double[]{.025,.045,.042,.003},new double[]{.023,.032,.029,.002},20,10,GOLD_PALE);
            m.sweep(new P[]{p(s*.19,6.092,.849),p(s*.28,6.28,.80),p(s*.47,6.42,.717),p(s*.50,6.56,.640)},new double[]{.047,.038,.023,.0015},new double[]{.039,.03,.016,.0015},22,10,GOLD_OLD);
            m.sweep(new P[]{p(s*.215,5.572,1.028),p(s*.209,5.491,1.013),p(s*.163,5.451,.995)},new double[]{.038,.026,.002},new double[]{.025,.017,.002},12,10,GOLD_PALE);
            for(int k=0;k<3;k++)m.sweep(new P[]{p(s*(.05+k*.047),5.575,1.047),p(s*(.05+k*.047),5.526,1.024)},new double[]{.020,.001},new double[]{.014,.001},5,8,GOLD_PALE);
            m.strand(new P[]{p(s*.19,5.695,1.051),p(s*.39,5.708,.967),p(s*.62,5.922,.793),p(s*.75,6.165,.623)},.017,GOLD_PALE,28);
            m.strand(new P[]{p(s*.19,5.695,1.051),p(s*.42,5.61,.930),p(s*.70,5.727,.737),p(s*.79,5.914,.619)},.012,GOLD_PALE,26);
            for(int k=0;k<5;k++) {
                double y=5.42+k*.123,spread=.11*Math.sin((k+1)*.53);
                m.sweep(new P[]{p(s*.23,y,.881),p(s*(.39+spread),y-.04,.875),p(s*(.53+spread),y+.08,.747),p(s*(.59+spread),y+.23,.68)},new double[]{.024,.046,.036,.002},new double[]{.012,.019,.017,.001},17,8,k%2==0?GOLD_OLD:GOLD_PALE);
            }
            m.strand(new P[]{p(s*.24,5.40,.847),p(s*.39,5.24,.817),p(s*.61,5.25,.744),p(s*.70,5.40,.65)},.017,GOLD_OLD,24);
            flourish(m,p(s*.64,5.055,.68),.115,.17,s,GOLD_OLD);
        }
    }
    /** Scale lames follow the outside of each upper arm; they do not bridge the elbow or weapon grip. */
    private static void shoulderLames(GuanYuSculptor m) {
        for(int s:new int[]{-1,1})for(int row=0;row<3;row++)for(int col=0;col<5;col++) {
            double a=(col-2)*.27,x=s*(1.35+row*.16+.34*Math.sin(a)),y=6.60-row*.17;
            double z=.40+.12*Math.cos(a);
            m.plate(p(x,y,z),p(Math.cos(a),0,-s*Math.sin(a)),p(s*.16,-1,.10),.18,.29,.038,row%2==0?GOLD_OLD:JADE_DARK);
            m.ellipsoid(p(x,y-.045,z+.035),p(.020,.020,.012),GOLD_PALE,8,4);
        }
    }
    private static void arms(GuanYuSculptor m) {
        m.sweep(new P[]{p(-1.18,6.54,0),p(-1.64,6.08,.20),p(-1.84,5.67,.48)},new double[]{.37,.42,.28},new double[]{.37,.39,.27},18,24,CLOTH_GREEN);
        m.sweep(new P[]{p(-1.84,5.67,.48),p(-2.02,5.48,.67),gripPoint(.29,0,-.11)},new double[]{.25,.21,.125},new double[]{.25,.20,.115},14,16,GOLD_OLD);
        m.sweep(new P[]{p(1.18,6.65,0),p(1.65,6.15,.16),p(1.86,5.94,.38)},new double[]{.37,.43,.32},new double[]{.37,.43,.29},18,24,CLOTH_GREEN);
        m.sweep(new P[]{p(1.86,5.94,.38),p(1.72,6.34,.67),p(1.58,6.69,.87)},new double[]{.29,.25,.17},new double[]{.27,.23,.16},16,24,GOLD_OLD);
        for(int s:new int[]{-1,1}) {
            P[] controls=s<0?new P[]{p(-1.84,5.67,.48),p(-2.02,5.48,.67),gripPoint(.29,0,-.11)}:new P[]{p(1.86,5.94,.38),p(1.72,6.34,.67),p(1.58,6.69,.87)};
            for(int k=1;k<(s<0?4:7);k++)flourish(m,path(controls,k/8.).add(p(0,.025,.23)),.14,.058,s,GOLD_PALE);
        }
        // Palm stays beside the shaft. Four closed fingers wrap a clear bore aligned to its final axis.
        m.sweep(new P[]{gripPoint(.22,-.18,-.10),gripPoint(.22,0,-.10),gripPoint(.21,.19,-.10)},new double[]{.07,.10,.075},new double[]{.075,.09,.07},10,12,GUAN_SKIN);
        for(int k=0;k<4;k++) {
            double y=-.16+k*.106;
            m.sweep(new P[]{gripPoint(.20,y,-.12),gripPoint(-.11,y,-.13),gripPoint(-.17,y,.04),gripPoint(-.07,y,.175),gripPoint(.11,y,.145)},new double[]{.047,.047,.041,.03},new double[]{.043,.043,.036,.028},20,10,GUAN_SKIN);
            m.ellipsoid(gripPoint(.105,y,.169),p(.025,.032,.012),GUAN_HIGHLIGHT,8,5);
        }
        m.sweep(new P[]{gripPoint(.24,.10,-.04),gripPoint(.18,.23,.11),gripPoint(.015,.18,.19)},new double[]{.067,.054,.035},new double[]{.058,.047,.031},14,10,GUAN_SKIN);
        m.profile(new double[][]{{6.65,.12,.10,.09,1.58,.89},{6.82,.20,.13,.10,1.56,.89},{7.02,.18,.13,.10,1.53,.89},{7.10,.13,.10,.08,1.50,.89}},24,12,GUAN_SKIN);
        m.sweep(new P[]{p(1.43,7.04,.88),p(1.405,7.25,.87),p(1.38,7.40,.835),p(1.40,7.54,.84)},new double[]{.068,.061,.046,.028},new double[]{.06,.057,.043,.025},15,10,GUAN_SKIN);
        for(int k=0;k<3;k++) {
            double x=1.53+k*.10;m.sweep(new P[]{p(x,7.04,.88),p(x+.02,7.11,1.03),p(x+.015,6.95,1.12),p(x,6.84,1.035)},new double[]{.055,.055,.049,.035},new double[]{.05,.053,.043,.031},14,10,GUAN_SKIN);
            m.ellipsoid(p(x+.006,6.87,1.083),p(.034,.046,.014),GUAN_HIGHLIGHT,8,5);
        }
        m.sweep(new P[]{p(1.34,6.81,.89),p(1.33,6.91,1.07),p(1.48,6.94,1.145)},new double[]{.078,.061,.04},new double[]{.07,.055,.034},14,12,GUAN_SKIN);
    }
    private static P gripPoint(double across,double up,double normal) {
        return GRIP.add(WEAPON_ACROSS.scale(across)).add(WEAPON_UP.scale(up)).add(WEAPON_NORMAL.scale(normal));
    }
    private static void head(GuanYuSculptor m) {
        m.profile(new double[][]{{6.88,.32,.29,.28,0,0},{7.25,.34,.32,.29,0,0},{7.43,.30,.30,.26,0,0}},32,10,GUAN_SKIN);
        m.profile(new double[][]{{6.90,.38,.32,.30,0,0},{7.13,.37,.33,.31,0,0},{7.36,.33,.27,.29,0,0}},36,10,JADE_DARK);
        double[][] skull={{7.25,.20,.29,.24,0,0},{7.37,.31,.37,.32,0,0},{7.55,.43,.41,.37,0,0},{7.77,.48,.42,.40,0,0},{7.97,.49,.40,.41,0,0},{8.19,.48,.37,.40,0,0},{8.36,.42,.30,.33,0,0},{8.48,.26,.19,.22,0,0},{8.52,.008,.015,.015,0,0}};
        m.surface(48,40,(u,v)-> {
            P q=profilePoint(skull,u,v);double front=Math.max(0,Math.cos(u*Math.PI*2));
            double eyes=(gauss(q.x(),.235,.125)+gauss(q.x(),-.235,.125))*gauss(q.y(),7.93,.085);
            double cheek=(gauss(q.x(),.31,.12)+gauss(q.x(),-.31,.12))*gauss(q.y(),7.70,.12);
            double brow=(gauss(q.x(),.24,.19)+gauss(q.x(),-.24,.19))*gauss(q.y(),8.015,.056);
            double bridge=.155*gauss(q.x(),0,.073)*gauss(q.y(),7.82,.245);
            double tip=.188*gauss(q.x(),0,.10)*gauss(q.y(),7.636,.068);
            double alar=.072*(gauss(q.x(),.105,.048)+gauss(q.x(),-.105,.048))*gauss(q.y(),7.634,.054);
            double mouth=.025*gauss(q.x(),0,.21)*gauss(q.y(),7.48,.10);
            return q.add(p(0,0,front*front*(-.088*eyes+.070*cheek+.049*brow+bridge+tip+alar+mouth)));
        },GUAN_SKIN);
        for(int s:new int[]{-1,1}) {
            m.sweep(new P[]{p(s*.49,7.99,-.018),p(s*.565,7.91,.045),p(s*.57,7.72,.06),p(s*.49,7.61,.02)},new double[]{.06,.079,.069,.022},new double[]{.059,.07,.057,.023},16,12,GUAN_SKIN);
            m.strand(new P[]{p(s*.53,7.89,.105),p(s*.546,7.77,.121),p(s*.505,7.70,.096)},.018,GUAN_SHADOW,12);
            eye(m,s);
            m.sweep(new P[]{p(s*.065,7.992,.441),p(s*.19,8.041,.459),p(s*.33,8.066,.395),p(s*.448,8.025,.275)},new double[]{.022,.053,.041,.002},new double[]{.018,.034,.030,.002},16,8,BEARD);
            for(int k=0;k<7;k++){double a=k/6.;m.strand(new P[]{p(s*(.086+.28*a),8.002+.047*Math.sin(a*Math.PI),.450-.15*a*a),p(s*(.11+.29*a),8.032+.043*Math.sin(a*Math.PI),.460-.155*a*a)},.004,BEARD_GLEAM,5);}
            m.strand(new P[]{p(s*.09,8.024,.451),p(s*.25,8.075,.427),p(s*.43,8.035,.287)},.01,BEARD_GLEAM,16);
            m.ellipsoid(p(s*.093,7.613,.502),p(.036,.013,.012),GUAN_SHADOW,12,6);
            m.strand(new P[]{p(s*.142,7.646,.475),p(s*.18,7.55,.432),p(s*.22,7.478,.399)},.007,GUAN_SHADOW,15);
        }
        m.sweep(new P[]{p(-.20,7.472,.463),p(-.09,7.482,.503),p(0,7.47,.519),p(.10,7.482,.503),p(.20,7.472,.463)},new double[]{.012,.027,.024,.012},new double[]{.012,.018,.017,.01},24,8,GUAN_SHADOW);
        m.strand(new P[]{p(-.16,7.43,.467),p(0,7.424,.498),p(.16,7.43,.467)},.027,GUAN_HIGHLIGHT,18);
        beard(m);crown(m);
    }
    private static void eye(GuanYuSculptor m,int s) {
        // Narrow phoenix-eye aperture: the outer canthus rises, rather than a round staring eye.
        m.surface(24,6,(u,v)->p(s*(.083+.302*u),7.905+.094*u+.012*Math.sin(u*Math.PI)+(v-.5)*.063*Math.sin(u*Math.PI),.435-.118*Math.pow(u,1.8)),EYE_DARK);
        m.surface(20,5,(u,v)->{double t=.08+.78*u;return p(s*(.083+.302*t),7.905+.094*t+.012*Math.sin(t*Math.PI)+(v-.5)*.030*Math.sin(u*Math.PI),.439-.118*Math.pow(t,1.8));},GOLD_PALE);
        m.ellipsoid(p(s*.206,7.955,.429),p(.023,.021,.010),EYE_DARK,16,10);
        m.ellipsoid(p(s*.198,7.963,.439),p(.005,.005,.002),IVORY,8,4);
        P[] upper=new P[25],lower=new P[25];
        for(int k=0;k<=24;k++){double t=k/24.,y=7.905+.094*t+.012*Math.sin(t*Math.PI),z=.440-.118*Math.pow(t,1.8);upper[k]=p(s*(.083+.302*t),y+.030*Math.sin(t*Math.PI),z);lower[k]=p(s*(.083+.302*t),y-.020*Math.sin(t*Math.PI),z);}
        m.wire(upper,.012,EYE_DARK,28);m.wire(lower,.009,GUAN_SHADOW,28);
        m.strand(new P[]{p(s*.338,7.986,.357),p(s*.387,8.003,.320),p(s*.417,8.034,.286)},.012,EYE_DARK,14);
    }
    private static void beard(GuanYuSculptor m) {
        m.sweep(new P[]{p(0,7.36,.48),p(.012,7.20,.61),p(.008,7.03,.75)},new double[]{.35,.35,.29},new double[]{.095,.105,.08},8,12,BEARD);
        // Five closed oval locks, not a black sheet. Central lock is longest; every lock has an S bend.
        for(int lock=-2;lock<=2;lock++) {
            double x=lock*.13,length=1.79-Math.abs(lock)*.24;
            P[] q={p(x,7.38-Math.abs(lock)*.018,.48),p(x*1.17-.022,7.02,.77-Math.abs(lock)*.018),
                    p(x*1.28+.04,6.54+Math.abs(lock)*.07,1.02-Math.abs(lock)*.04),p(x*1.17+.035,7.39-length,1.12-Math.abs(lock)*.065)};
            double w=lock==0?.137:lock%2==0?.085:.105;
            m.sweep(q,new double[]{w*1.1,w,w*.76,.009},new double[]{.10,.12,.088,.009},18,10,BEARD);
            for(int ridge=-1;ridge<=1;ridge++) {
                P[] line=new P[13];for(int j=0;j<line.length;j++) {
                    double t=j/12.;line[j]=path(q,t).add(p(ridge*.042*(1-t),0,.09*(1-t)+.016));
                }
                m.strand(line,.006,BEARD_GLEAM,14);
            }
        }
        for(int s:new int[]{-1,1}) {
            m.sweep(new P[]{p(s*.035,7.556,.553),p(s*.17,7.53,.552),p(s*.31,7.45,.493),p(s*.39,7.24,.464)},new double[]{.037,.058,.044,.004},new double[]{.025,.030,.026,.004},26,10,BEARD);
            for(int j=0;j<4;j++)m.strand(new P[]{p(s*.055,7.565-j*.014,.579),p(s*.20,7.522-j*.011,.576),p(s*.34,7.37-j*.028,.503)},.005,BEARD_GLEAM,20);
            m.strand(new P[]{p(s*.44,7.73,.247),p(s*.43,7.52,.307),p(s*.36,7.28,.437),p(s*.26,7.02,.58)},.049,BEARD,25);
        }
    }
    private static P beardPoint(double u,double v,double offset) {
        double w=.40*Math.pow(1-v,.62)+.003;
        return p((u-.5)*2*w+.23*Math.sin(v*2.8)*v,7.39-v*1.65+.07*Math.cos(u*Math.PI*2)*(1-v),.445+.46*Math.sin(v*Math.PI*.63)+.029*Math.cos(u*Math.PI*22)*(1-v)+offset);
    }
    private static void crown(GuanYuSculptor m) {
        // Fitted rear crown cloth covers the occiput; the paired ribbons remain separate.
        m.shell(12,10,(u,v)->p((u-.5)*.67,8.31-v*1.15,-.32-.115*Math.sin(v*Math.PI)),p(0,0,-.045),JADE_DARK,CLOTH_GREEN);
        m.profile(new double[][]{{8.24,.49,.34,.41,0,-.01},{8.38,.48,.32,.41,0,-.02},{8.56,.38,.25,.32,0,-.04},{8.68,.17,.11,.18,0,-.08},{8.73,.01,.02,.02,0,-.08}},48,16,JADE_DARK);
        m.surface(56,4,(u,v)->{double a=u*Math.PI*2;return p(.491*Math.sin(a),8.255+v*.103+.035*Math.cos(a),-.012+(.41-.058*Math.max(0,Math.cos(a)))*Math.cos(a));},GOLD_OLD);
        for(int s:new int[]{-1,1}){m.strand(new P[]{p(s*.06,8.37,.352),p(s*.24,8.43,.309),p(s*.41,8.36,.206),p(s*.485,8.32,.03)},.021,GOLD_PALE,25);flourish(m,p(s*.24,8.335,.327),.115,.05,s,GOLD_PALE);}
        m.plate(p(0,8.54,.343),p(1,0,0),p(0,-1,.12),.29,.28,.041,GOLD_PALE);m.ellipsoid(p(0,8.393,.398),p(.075,.095,.032),CRIMSON,20,10);
        m.sweep(new P[]{p(0,8.57,-.035),p(0,8.78,-.06),p(0,8.91,-.045)},new double[]{.045,.037,.015},new double[]{.04,.031,.011},16,10,GOLD_OLD);m.ellipsoid(p(0,8.93,-.045),p(.056,.060,.044),GOLD_PALE,14,8);
        for(int s:new int[]{-1,1}){m.wire(new P[]{p(s*.055,8.66,-.02),p(s*.145,8.74,-.03),p(s*.16,8.62,.015),p(s*.085,8.56,.035)},.019,GOLD_PALE,25);panel(m,new P[]{p(s*.22,8.49,-.31),p(s*.35,7.89,-.47),p(s*.44,7.11,-.44),p(s*.56,6.81,-.32)},.115,.07,CLOTH_GREEN);}
    }
    private static void weapon(GuanYuSculptor m) {
        GuanYuSculptor local=new GuanYuSculptor();weaponSculpt(local);
        for(Face f:local.faces)m.quad(weaponPose(f.a()),weaponPose(f.b()),weaponPose(f.c()),weaponPose(f.d()),f.material());
        GuanYuSculptor blade=new GuanYuSculptor();guandaoBlade(blade);
        for(Face f:blade.faces)m.quad(bladePose(f.a()),bladePose(f.b()),bladePose(f.c()),bladePose(f.d()),f.material());
        // Tassels follow gravity after posing the weapon, rather than inheriting its inverted sculpt frame.
        P knot=SHAFT_TOP.add(WEAPON_ACROSS.scale(.19)).add(WEAPON_NORMAL.scale(.21));
        m.wire(new P[]{SHAFT_TOP.add(WEAPON_NORMAL.scale(.15)),knot},.021,GOLD_OLD,5);
        m.ellipsoid(knot,p(.06,.06,.045),GOLD_OLD,10,6);
        for(int k=0;k<3;k++) {
            P root=knot.add(WEAPON_ACROSS.scale((k-1)*.075));
            m.sweep(new P[]{root,root.add(p(.04,-.22,.025)),root.add(p(.015,-.43+k*.025,.07))},new double[]{.034,.027,.003},new double[]{.025,.022,.003},10,8,k==1?CRIMSON:SILK_RED);
        }
    }
    private static P bladePose(P q) {
        return SHAFT_TOP.add(WEAPON_ACROSS.scale(q.x())).add(WEAPON_UP.scale(q.y())).add(WEAPON_NORMAL.scale(q.z()));
    }
    private static P weaponPose(P q) {
        double axial=(SCULPT_BOTTOM.y()-q.y());
        if(axial<0)axial*=5.40/(SCULPT_TOP.y()-SCULPT_BOTTOM.y());
        double oldX=SCULPT_BOTTOM.x()+(q.y()-SCULPT_BOTTOM.y())*(SCULPT_TOP.x()-SCULPT_BOTTOM.x())/(SCULPT_TOP.y()-SCULPT_BOTTOM.y());
        return SHAFT_TOP.add(WEAPON_UP.scale(axial)).add(WEAPON_ACROSS.scale(q.x()-oldX)).add(WEAPON_NORMAL.scale(q.z()-.83));
    }
    private static void weaponSculpt(GuanYuSculptor m) {
        m.sweep(new P[]{SCULPT_BOTTOM,SCULPT_TOP},new double[]{.096,.078,.056,.072},new double[]{.096,.078,.056,.072},32,12,GUAN_SHAFT);
        P axis=SCULPT_TOP.sub(SCULPT_BOTTOM).unit();
        // Grip reinforcement stays within the existing 0.096-radius hand bore.
        P across=p(0,0,1),normal=axis.cross(across).unit();
        P[] wrap=new P[145];
        for(int i=0;i<wrap.length;i++){
            double t=i/(double)(wrap.length-1),a=t*Math.PI*24,axial=1.02+t*1.55;
            wrap[i]=SCULPT_BOTTOM.add(axis.scale(axial)).add(across.scale(.078*Math.cos(a))).add(normal.scale(.078*Math.sin(a)));
        }
        m.sweep(wrap,new double[]{.0055,.0055},new double[]{.0055,.0055},144,5,GUAN_SHAFT);
        for(double offset:new double[]{.16,.45,2.15,4.62,5.98}){
            P c=SCULPT_BOTTOM.add(axis.scale(offset));
            m.sweep(new P[]{c,c.add(axis.scale(.09))},new double[]{.099,.099},new double[]{.099,.099},2,12,GOLD_OLD);
        }
        // Restore the upper handle. Only the lower protrusion under the blade/tassel is removed.
        m.sweep(new P[]{p(-1.82,8.19,.83),p(-1.805,8.34,.83),p(-1.793,8.43,.83)},new double[]{.095,.13,.07},new double[]{.095,.13,.07},6,10,GOLD_OLD);
    }
    private static void guandaoBlade(GuanYuSculptor m) {
        // Fixed centerline; stepped bronze socket encloses the same heel, never a floating plate.
        m.sweep(new P[]{p(0,-.19,0),p(0,-.12,0),p(0,.10,0),p(0,.26,0)},new double[]{.112,.173,.18,.15},new double[]{.112,.173,.18,.15},12,16,GUAN_SOCKET);
        for(double y:new double[]{-.12,.055,.23})m.sweep(new P[]{p(0,y,0),p(0,y+.033,0)},new double[]{.178,.178},new double[]{.178,.178},1,16,GOLD_OLD);
        photoBladeMesh(m);
    }
    /** Single source of truth for the 2D study, runtime mesh and geometry tests. */
    private static List<P> photoOutline() {
        var result=new java.util.ArrayList<P>();
        double x=BLADE_PHOTO_CURVES[0][0],y=BLADE_PHOTO_CURVES[0][1];
        for(int row=1;row<BLADE_PHOTO_CURVES.length;row++) {
            double[] c=BLADE_PHOTO_CURVES[row];
            for(int step=0;step<16;step++) {
                double t=step/16.,r=1-t;
                result.add(photoToBlade(x*r*r*r+3*c[0]*r*r*t+3*c[2]*r*t*t+c[4]*t*t*t,
                        y*r*r*r+3*c[1]*r*r*t+3*c[3]*r*t*t+c[5]*t*t*t));
            }
            x=c[4];y=c[5];
        }
        return List.copyOf(result);
    }
    private static P photoToBlade(double x,double y) {
        x-=280;y-=165;
        return p((PHOTO_AXIS_Y*x-PHOTO_AXIS_X*y)*PHOTO_SCALE,
                (PHOTO_AXIS_X*x+PHOTO_AXIS_Y*y)*PHOTO_SCALE,0);
    }
    /** New closed extrusion, triangulated for the concave photographed heel/notch. */
    private static void photoBladeMesh(GuanYuSculptor m) {
        List<P> boundary=photoOutline();
        var q=new java.util.ArrayList<>(boundary);
        double signed=0;for(int i=0;i<q.size();i++)signed+=cross2(q.get(i),q.get((i+1)%q.size()));
        double winding=Math.signum(signed);
        // Only move the interior shoulder of the bevel. Approved exterior XY coordinates stay exact.
        for(int i=65;i<128;i++) {
            P a=boundary.get(i-1),b=boundary.get(i+1),v=boundary.get(i),t=b.sub(a).unit();
            double fade=Math.min(1,Math.min(length(v.sub(boundary.get(64)))/.28,length(v.sub(boundary.get(128)))/.22));
            q.set(i,v.add(p(-t.y()*winding,t.x()*winding,0).scale(.105*fade)));
        }
        List<P> shoulder=List.copyOf(q);
        if(signed<0)java.util.Collections.reverse(q);
        var remaining=new java.util.ArrayList<Integer>();
        for(int i=0;i<q.size();i++)remaining.add(i);
        while(remaining.size()>2) {
            boolean clipped=false;
            for(int j=0;j<remaining.size();j++) {
                P a=q.get(remaining.get((j+remaining.size()-1)%remaining.size())),b=q.get(remaining.get(j)),c=q.get(remaining.get((j+1)%remaining.size()));
                if(cross2(b.sub(a),c.sub(b))<=1e-12)continue;
                boolean occupied=false;
                for(int k:remaining) {
                    P v=q.get(k);if(v==a||v==b||v==c)continue;
                    if(cross2(b.sub(a),v.sub(a))>=-1e-12&&cross2(c.sub(b),v.sub(b))>=-1e-12&&cross2(a.sub(c),v.sub(c))>=-1e-12){occupied=true;break;}
                }
                if(occupied)continue;
                bladeTriangle(m,a,b,c,1);
                remaining.remove(j);clipped=true;break;
            }
            if(!clipped)throw new IllegalStateException("Photograph outline could not be triangulated");
        }
        for(int i=0;i<boundary.size();i++)for(int k=0;k<2;k++) {
            int j=(i+1)%boundary.size();double t=k*.5;
            P a=lerp(boundary.get(i),boundary.get(j),t),b=lerp(boundary.get(i),boundary.get(j),t+.5);
            P ia=lerp(shoulder.get(i),shoulder.get(j),t),ib=lerp(shoulder.get(i),shoulder.get(j),t+.5);
            boolean edge=i>=64&&i<128;
            for(int side:new int[]{-1,1})if(edge) {
                P ao=a.add(p(0,0,side*cutDepth(a))),bo=b.add(p(0,0,side*cutDepth(b)));
                P ai=bladeDepth(ia,side),bi=bladeDepth(ib,side),am=lerp(ao,ai,.20),bm=lerp(bo,bi,.20);
                bladeQuad(m,ao,bo,bm,am,side*winding,GUAN_EDGE);
                bladeQuad(m,am,bm,bi,ai,side*winding,GUAN_BEVEL);
            }
            P af=edge?a.add(p(0,0,cutDepth(a))):bladeDepth(a,1),bf=edge?b.add(p(0,0,cutDepth(b))):bladeDepth(b,1);
            P ab=p(af.x(),af.y(),-af.z()),bb=p(bf.x(),bf.y(),-bf.z());
            bladeQuad(m,ab,bb,bf,af,winding,edge?GUAN_EDGE:GUAN_BLADE);
        }
        // Relief projects onto these exact surface triangles, not an unrelated display surface.
        bladeRelief(m,List.copyOf(m.faces));
    }
    private static double length(P q){return Math.sqrt(q.dot(q));}
    private static P lerp(P a,P b,double t){return a.scale(1-t).add(b.scale(t));}
    private static void bladeQuad(GuanYuSculptor m,P a,P b,P c,P d,double sign,Material mat){if(sign>0)m.quad(a,b,c,d,mat);else m.quad(d,c,b,a,mat);}
    private static void bladeTriangle(GuanYuSculptor m,P a,P b,P c,int split) {
        if(split>0){P ab=lerp(a,b,.5),bc=lerp(b,c,.5),ca=lerp(c,a,.5);bladeTriangle(m,a,ab,ca,split-1);bladeTriangle(m,ab,b,bc,split-1);bladeTriangle(m,ca,bc,c,split-1);bladeTriangle(m,ab,bc,ca,split-1);return;}
        for(int side:new int[]{-1,1}){P af=bladeDepth(a,side),bf=bladeDepth(b,side),cf=bladeDepth(c,side);bladeQuad(m,af,bf,cf,af,side,GUAN_BLADE);}
    }
    private static double cross2(P a,P b){return a.x()*b.y()-a.y()*b.x();}
    private static double cutDepth(P q){return .002+.063*Math.max(0,1-length(q.sub(BLADE_BOUNDARY.get(128)))/.15);}
    private static P bladeDepth(P q,int side) {
        List<P> boundary=BLADE_BOUNDARY;double edge=Double.POSITIVE_INFINITY,back=edge;
        for(int i=0;i<128;i++){P a=boundary.get(i),b=boundary.get(i+1),d=b.sub(a);double t=Math.max(0,Math.min(1,q.sub(a).dot(d)/Math.max(1e-12,d.dot(d))));double distance=length(q.sub(a.add(d.scale(t))));if(i>=64)edge=Math.min(edge,distance);else back=Math.min(back,distance);}
        double stock=.065+.065*edge/Math.max(1e-9,edge+back);
        double tip=Math.min(1,length(q.sub(photoToBlade(50,190)))/.28);
        return q.add(p(0,0,side*(.002+(stock-.002)*tip)));
    }
    private static void bladeRelief(GuanYuSculptor m,List<Face> surface) {
        for(int side:new int[]{-1,1}) {
            // One sinuous dragon, its low head lying within the blade rather than on its silhouette.
            reliefLine(m,surface,new double[][]{{105,218},{123,217},{143,207},{164,207},{176,219},{157,233},{149,239},{176,230},{205,211},{238,188}},.025,side,GUAN_RELIEF);
            reliefLine(m,surface,new double[][]{{101,218},{98,213},{103,207},{112,207},{118,211},{113,216}},.036,side,GUAN_RELIEF);
            reliefLine(m,surface,new double[][]{{98,212},{92,211},{91,216},{98,218}},.014,side,GUAN_RELIEF);
            reliefLine(m,surface,new double[][]{{106,208},{108,202},{103,199}},.009,side,GUAN_RELIEF);
            reliefLine(m,surface,new double[][]{{114,210},{120,203},{117,200}},.008,side,GUAN_RELIEF);
            reliefLine(m,surface,new double[][]{{94,216},{87,213},{82,214}},.005,side,GUAN_RELIEF);
            reliefLine(m,surface,new double[][]{{103,211},{107,210}},.007,side,GOLD_OLD);
            for(double[] leg:new double[][]{{134,212,-7,11},{165,211,12,-10},{172,223,12,7},{192,219,11,3}}) {
                double x=leg[0],y=leg[1],dx=leg[2],dy=leg[3];
                reliefLine(m,surface,new double[][]{{x,y},{x+dx*.45,y+dy*.9},{x+dx,y+dy}},.011,side,GUAN_RELIEF);
                for(int k=0;k<3;k++)reliefLine(m,surface,new double[][]{{x+dx,y+dy},{x+dx+3+k*1.6,y+dy-3+k*2}},.004,side,GUAN_RELIEF);
            }
            for(int k=0;k<8;k++){double x=182+k*5,y=226-k*4;reliefLine(m,surface,new double[][]{{x-2,y-2},{x,y},{x+3,y-1}},.004,side,GUAN_RELIEF);}
            reliefLine(m,surface,new double[][]{{133,242},{126,244},{120,240},{123,237},{128,239}},.006,side,GUAN_RELIEF);
            reliefLine(m,surface,new double[][]{{197,193},{204,188},{212,189},{212,193},{206,194}},.006,side,GUAN_RELIEF);
            // Subtle interior spine rib follows the stable back, remaining inside the silhouette.
            reliefLine(m,surface,new double[][]{{267,161},{236,169},{205,176},{189,178}},.009,side,GUAN_RELIEF);
        }
    }
    private static void reliefLine(GuanYuSculptor m,List<Face> surface,double[][] pixels,double width,int side,Material material) {
        P[] control=new P[pixels.length];for(int i=0;i<control.length;i++)control[i]=photoToBlade(pixels[i][0],pixels[i][1]);
        int steps=Math.max(6,(control.length-1)*8);
        for(int k=0;k<steps;k++) {
            double t=k/(double)steps,v=(k+1.)/steps;P a=path(control,t),b=path(control,v),d=b.sub(a).unit(),n=p(-d.y(),d.x(),0);
            double wa=width*(.20+.80*Math.sin(Math.PI*(.06+.88*t))),wb=width*(.20+.80*Math.sin(Math.PI*(.06+.88*v)));
            P[] ring={a.sub(n.scale(wa)),b.sub(n.scale(wb)),b.add(n.scale(wb)),a.add(n.scale(wa))};
            P[] edge=new P[4];boolean valid=true;
            for(int j=0;j<4;j++){double z=surfaceHeight(surface,ring[j]);if(!Double.isFinite(z)){valid=false;break;}edge[j]=ring[j].add(p(0,0,side*(z+.0015)));}
            if(!valid)continue;double az=surfaceHeight(surface,a),bz=surfaceHeight(surface,b);if(!Double.isFinite(az+bz))continue;
            P ac=a.add(p(0,0,side*(az+.010))),bc=b.add(p(0,0,side*(bz+.010)));
            bladeQuad(m,edge[0],edge[1],bc,ac,side,material);bladeQuad(m,ac,bc,edge[2],edge[3],side,material);
        }
    }
    private static double surfaceHeight(List<Face> surface,P q) {
        for(Face f:surface)if(f.material()==GUAN_BLADE&&f.a().z()>0&&f.b().z()>0&&f.c().z()>0) {
            P a=f.a(),b=f.b(),c=f.c();double den=cross2(b.sub(a),c.sub(a));if(Math.abs(den)<1e-12)continue;
            double v=cross2(q.sub(a),c.sub(a))/den,w=cross2(b.sub(a),q.sub(a))/den;
            if(v>=-1e-8&&w>=-1e-8&&v+w<=1+1e-8)return a.z()*(1-v-w)+b.z()*v+c.z()*w;
        }
        return Double.NaN;
    }
    private static P bladeCurve(P[] q,double t) {
        double a=Math.max(0,Math.min(1,t))*((q.length-1)/3);int segment=Math.min((q.length-1)/3-1,(int)a);double f=a-segment,r=1-f;int i=segment*3;
        return q[i].scale(r*r*r).add(q[i+1].scale(3*r*r*f)).add(q[i+2].scale(3*r*f*f)).add(q[i+3].scale(f*f*f));
    }
    private static P bladePoint(P[] spine,P[] edge,double u,double v,double side,double lift) {
        double thickness=(.115*(1-u)+.065*Math.sin(u*Math.PI)+.004)*Math.min(1,(1-v)*10);
        return bladeCurve(spine,v).scale(1-u).add(bladeCurve(edge,v).scale(u)).add(p(0,0,side*(thickness+lift)));
    }
    private static void dragonSocket(GuanYuSculptor m) {
        P c=p(-2.55,1.94,.83);
        m.ellipsoid(c,p(.23,.24,.20),JADE_METAL,12,8);
        m.sweep(new P[]{c.add(p(-.08,-.08,0)),c.add(p(-.24,-.18,0)),c.add(p(-.37,-.22,0))},new double[]{.17,.18,.12},new double[]{.19,.17,.14},8,10,JADE_METAL);
        m.sweep(new P[]{c.add(p(.03,.07,0)),c.add(p(-.20,.04,0)),c.add(p(-.34,-.04,0))},new double[]{.095,.105,.045},new double[]{.18,.19,.13},8,10,JADE_DARK);
        for(int s:new int[]{-1,1}) {
            m.sweep(new P[]{c.add(p(.11,-.10,s*.10)),c.add(p(.16,.18,s*.19)),c.add(p(.01,.36,s*.22))},new double[]{.055,.038,.002},new double[]{.05,.031,.002},9,8,GOLD_OLD);
            m.sweep(new P[]{c.add(p(.025,-.07,s*.19)),c.add(p(-.09,-.12,s*.23)),c.add(p(-.19,-.08,s*.19))},new double[]{.032,.050,.017},new double[]{.024,.034,.018},8,8,JADE_DARK);
            m.ellipsoid(c.add(p(-.09,-.055,s*.205)),p(.032,.019,.018),LIGHT,8,5);
            for(int k=0;k<2;k++)m.strand(new P[]{c.add(p(-.20-k*.095,-.07,s*.14)),c.add(p(-.21-k*.095,-.14,s*.13))},.023,GOLD_OLD,5);
        }
    }
    /** A raised serpentine gold dragon on each green blade face; not a generic decorative curl. */
    private static void bladeDragonRelief(GuanYuSculptor m,P[] spine,P[] edge,int side) {
        P[] body=new P[37];
        for(int k=0;k<=36;k++){double t=k/36.;body[k]=bladePoint(spine,edge,.34+.13*Math.sin(t*Math.PI*3.4),.17+.66*t,side,.028);}
        m.sweep(body,new double[]{.039,.034,.026,.003},new double[]{.018,.017,.013,.002},48,10,GOLD_OLD);
        for(int k=1;k<30;k++){
            double t=k/36.,u=.34+.13*Math.sin(t*Math.PI*3.4),v=.17+.66*t;
            m.ellipsoid(bladePoint(spine,edge,u,v,side,.050),p(.019,.014,.005),GOLD_PALE,8,5);
            if(k%2==0)m.strand(new P[]{bladePoint(spine,edge,u-.02,v,side,.041),bladePoint(spine,edge,u-.13,v-.015,side,.052),bladePoint(spine,edge,u-.09,v-.044,side,.034)},.012,GOLD_PALE,8);
        }
        P head=bladePoint(spine,edge,.34,.165,side,.047);
        m.ellipsoid(head,p(.070,.053,.021),GOLD_OLD,20,12);
        m.ellipsoid(head.add(p(-.047,.029,side*.022)),p(.010,.010,.005),EYE_DARK,10,6);
        m.strand(new P[]{head.add(p(.026,.040,0)),head.add(p(.065,.094,side*.01)),head.add(p(.035,.143,0))},.017,GOLD_PALE,14);
        m.strand(new P[]{head.add(p(-.018,.04,0)),head.add(p(-.028,.11,side*.01)),head.add(p(-.078,.13,0))},.015,GOLD_PALE,14);
        m.strand(new P[]{head.add(p(-.066,-.015,0)),head.add(p(-.10,-.03,side*.02)),head.add(p(-.14,.023,0))},.009,GOLD_PALE,16);
        for(double v:new double[]{.32,.59})for(int s:new int[]{-1,1}) {
            double t=(v-.17)/.66,u=.34+.13*Math.sin(t*Math.PI*3.4);
            m.strand(new P[]{bladePoint(spine,edge,u,v,side,.038),bladePoint(spine,edge,u+s*.13,v+.019,side,.042),bladePoint(spine,edge,u+s*.19,v-.014,side,.032)},.017,GOLD_PALE,12);
            for(int claw=0;claw<3;claw++)m.strand(new P[]{bladePoint(spine,edge,u+s*.17,v-.007,side,.038),bladePoint(spine,edge,u+s*(.19+claw*.025),v-.04+claw*.014,side,.032)},.007,GOLD_PALE,5);
        }
    }
    private static void panel(GuanYuSculptor m,P[] q,double top,double bottom,Material color) {
        m.shell(8,16,(u,v)->path(q,v).add(p((u-.5)*2*(top*(1-v)+bottom*v),.03*Math.sin(u*Math.PI*2)*v,.035*Math.sin(u*Math.PI*6)*(1-v*.45))),p(0,0,-.07),color,JADE_DARK);
        for(int s:new int[]{-1,1}){P[] edge=new P[25];for(int i=0;i<=24;i++){double t=i/24.;edge[i]=path(q,t).add(p(s*(top*(1-t)+bottom*t),0,.01));}m.wire(edge,.021,GOLD_OLD,28);}
    }
    private static void flourish(GuanYuSculptor m,P c,double width,double height,int side,Material color) {
        P[] q=new P[19];for(int k=0;k<=18;k++){double t=k/18.,a=t*Math.PI*2.20,r=1-.77*t;q[k]=c.add(p(side*width*Math.sin(a)*r,height*Math.cos(a)*r,.012*Math.sin(t*Math.PI)));}m.strand(q,.010,color,14);
        m.strand(new P[]{c.add(p(0,-height,0)),c.add(p(side*width*.7,-height*.8,.01)),c.add(p(side*width*1.03,-height*.05,0))},.012,color,10);
    }
    private static double gauss(double x,double c,double s){return Math.exp(-Math.pow((x-c)/s,2));}
    public static Vec3 origin(Vec3 player,float yaw){return player.subtract(HouyiAvatarShape.forward(yaw).scale(4));}
    public static boolean contains(double x,double y,double z,double formed) {
        if(y<0||y>HEIGHT*Math.max(0,Math.min(1,formed)))return false;
        for(Volume v:VOLUMES){double a=(x-v.c.x())/(v.r.x()+.30),b=(y-v.c.y())/(v.r.y()+.30),c=(z-v.c.z())/(v.r.z()+.30);if(a*a+b*b+c*c<=1)return true;}return false;
    }
    private GuanYuAvatarShape(){}
}
