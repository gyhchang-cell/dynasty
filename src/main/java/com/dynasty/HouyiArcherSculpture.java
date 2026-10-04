package com.dynasty;

import com.dynasty.HouyiAvatarShape.Face;
import com.dynasty.HouyiAvatarShape.Material;
import com.dynasty.HouyiAvatarShape.P;
import java.util.List;
import static com.dynasty.GuanYuSculptor.p;
import static com.dynasty.HouyiAvatarShape.Material.*;

/** Authoring helpers for the existing Houyi mesh, not an entity, animation or ritual system.
 * Local -X is the arrow/aim direction; +Z is the viewer-facing breastplate side.
 * Grip, nock, string and facial gaze share the same explicit landmarks. */
final class HouyiArcherSculpture {
    static final P GRIP=p(-3.78,7.78,.78), NOCK=p(.12,7.88,.78);
    static final P BOW_TOP=p(-3.0,9.82,.78), BOW_BOTTOM=p(-3.0,5.74,.78);
    static final P HOLD_SHOULDER=p(-1.02,6.98,.22), HOLD_ELBOW=p(-2.39,7.37,.60);
    static final P DRAW_SHOULDER=p(1.00,7.01,-.22), DRAW_ELBOW=p(2.13,7.80,-.44);
    static final P HOLD_WRIST=p(-3.48,7.76,.77), DRAW_WRIST=p(.43,7.91,.74);
    static final P HEAD=p(-.02,8.20,.08);
    private HouyiArcherSculpture() {}

    static List<Face> create() {
        var m=new GuanYuSculptor();
        // 1–2. Long-legged athletic anatomy, sternum/back volume and stable pelvis.
        proportions(m);
        // 3. Scapulae, independent joints and an opened drawing elbow determine the pose.
        drawAnatomy(m);
        // 4–6. A narrow, aim-facing carved face; focused eyes and bundled hair.
        head(m);eyes(m);hair(m);
        // 7–8. Layered light armor and functional asymmetry, not Guan Yu's heavy armor.
        clothing(m);asymmetry(m);
        // 9–10. Forearm guards and two different functional hands.
        armArmor(m);hands(m);
        // 11–12. Existing tall golden recurved bow, now joined to the actual grip/nock.
        bow(m);
        return List.copyOf(m.faces);
    }
    private static void proportions(GuanYuSculptor m) {
        m.profile(new double[][]{
            {4.03,.59,.44,.48,0,-.02},
            {4.40,.78,.51,.53,0,-.02},{4.73,.66,.47,.48,0,0},
            {5.15,.56,.44,.43,0,.02},{5.65,.66,.53,.50,-.04,.04},
            {6.12,.90,.67,.63,-.08,.04},{6.65,1.08,.73,.64,-.09,.04},
            {6.98,1.04,.65,.57,-.05,0},{7.23,.59,.45,.41,0,0},
            {7.30,.31,.29,.27,0,0}},16,26,CLOTH);
        // Separate legs below pelvis; no pillar connecting the knees.
        m.sweep(new P[]{p(-.01,7.10,0),p(-.06,7.42,.08),p(-.04,7.67,.10)},
                new double[]{.32,.28,.27},new double[]{.31,.27,.26},7,12,SKIN);
        for(int s:new int[]{-1,1}) {
            P hip=p(s*.47,4.30,-.01),knee=p(s*.66,2.42,s<0?.26:-.12),ankle=p(s*.82,.52,s<0?.32:-.10);
            m.sweep(new P[]{hip,p(s*.58,3.48,s<0?.18:-.08),knee},new double[]{.44,.39,.28},new double[]{.44,.36,.29},13,12,CLOTH);
            m.ellipsoid(knee,p(.29,.31,.30),ARMOR,12,7);
            m.sweep(new P[]{knee,p(s*.73,1.56,s<0?.28:-.10),ankle},new double[]{.27,.31,.20},new double[]{.28,.28,.20},12,12,CLOTH);
            m.sweep(new P[]{ankle.add(p(0,.14,0)),ankle.add(p(0,-.18,.11)),ankle.add(p(-.07,-.30,.49))},new double[]{.23,.29,.28},new double[]{.22,.26,.17},8,10,ARMOR);
            m.ellipsoid(ankle.add(p(-.04,-.36,.25)),p(.33,.12,.55),HAIR,12,6);
        }
    }
    private static void drawAnatomy(GuanYuSculptor m) {
        // Sternum is forward; the drawing-side scapula opens backwards.
        m.ellipsoid(p(.45,6.81,-.53),p(.54,.45,.21),CLOTH,12,8);
        arm(m,HOLD_SHOULDER,HOLD_ELBOW,HOLD_WRIST);
        arm(m,DRAW_SHOULDER,DRAW_ELBOW,DRAW_WRIST);
    }
    private static void arm(GuanYuSculptor m,P shoulder,P elbow,P wrist) {
        P mid=shoulder.add(elbow).scale(.5);
        m.ellipsoid(shoulder,p(.41,.42,.40),CLOTH,12,8);
        m.sweep(new P[]{shoulder,mid.add(p(0,-.03,0)),elbow},new double[]{.35,.32,.24},new double[]{.34,.30,.24},10,12,SKIN);
        m.ellipsoid(elbow,p(.25,.25,.25),SKIN,12,7);
        m.sweep(new P[]{elbow,elbow.scale(.56).add(wrist.scale(.44)),wrist},new double[]{.25,.28,.16},new double[]{.24,.25,.15},10,12,SKIN);
    }
    // Facial surface: local u runs across the face, depth points down the arrow's -X axis.
    static P face(double u,double y,double depth) {
        return HEAD.add(p(-depth,y,u));
    }
    private static void head(GuanYuSculptor m) {
        int start=m.faces.size();
        m.profile(new double[][]{
            {-.66,.09,.13,.16,0,0},{-.56,.25,.34,.30,0,0},
            {-.34,.39,.40,.36,0,0},{-.07,.47,.44,.42,0,0},
            {.20,.48,.42,.43,0,0},{.48,.43,.36,.38,0,0},
            {.64,.25,.20,.25,0,0},{.70,.005,.005,.005,0,0}},12,18,SKIN);
        // Transform only the newly authored head profile, leaving world-space body intact.
        for(int i=start;i<m.faces.size();i++) {
            Face f=m.faces.get(i);P a=face(f.a().x(),f.a().y(),f.a().z()),b=face(f.b().x(),f.b().y(),f.b().z()),c=face(f.c().x(),f.c().y(),f.c().z()),d=face(f.d().x(),f.d().y(),f.d().z());
            m.faces.set(i,new Face(a,b,c,d,f.material(),b.sub(a).cross(c.sub(a)).unit(),a.add(b).add(c).add(d).scale(.25)));
        }
        for(int s:new int[]{-1,1}) {
            m.ellipsoid(face(s*.47,-.03,0),p(.15,.22,.105),SKIN,10,7);
            // Cheek and brow are separate faceted volumes, with recessed orbital gap.
            faceSweep(m,new double[][]{{s*.12,.09,.407},{s*.29,.12,.393},{s*.42,.06,.29}},.055,.075,SKIN);
            faceSweep(m,new double[][]{{s*.17,-.15,.397},{s*.31,-.10,.379},{s*.41,-.18,.27}},.074,.09,SKIN);
        }
        faceSweep(m,new double[][]{{0,.19,.42},{0,-.02,.49},{0,-.16,.58},{0,-.23,.48}},.071,.075,SKIN);
        for(int s:new int[]{-1,1})m.ellipsoid(face(s*.082,-.22,.48),p(.067,.043,.055),SKIN,8,5);
        faceSweep(m,new double[][]{{-.15,-.34,.40},{0,-.36,.47},{.15,-.34,.40}},.012,.018,HAIR);
        m.ellipsoid(face(0,-.49,.33),p(.12,.11,.17),SKIN,10,5);
    }
    private static void faceSweep(GuanYuSculptor m,double[][] q,double w,double d,Material mat) {
        P[] pts=new P[q.length];for(int i=0;i<q.length;i++)pts[i]=face(q[i][0],q[i][1],q[i][2]);
        m.sweep(pts,new double[]{w,w*.9,w*.35},new double[]{d,d*.9,d*.35},10,6,mat);
    }
    private static void eyes(GuanYuSculptor m) {
        for(int s:new int[]{-1,1}) {
            double u=s*.245;
            m.ellipsoid(face(u,.027,.394),p(.025,.049,.153),HAIR,10,6);
            m.ellipsoid(face(u,.029,.416),p(.018,.023,.115),IVORY,10,5);
            m.ellipsoid(face(u,.033,.436),p(.010,.026,.034),HAIR,8,5);
            m.ellipsoid(face(u,.038,.447),p(.006,.010,.012),LIGHT,6,4);
            faceSweep(m,new double[][]{{s*.105,.079,.417},{s*.26,.102,.426},{s*.405,.094,.317}},.019,.028,HAIR);
            faceSweep(m,new double[][]{{s*.09,.174,.418},{s*.25,.222,.407},{s*.42,.236,.282}},.039,.051,HAIR);
        }
    }
    private static void hair(GuanYuSculptor m) {
        m.ellipsoid(HEAD.add(p(.20,.26,0)),p(.32,.51,.49),HAIR,14,10);
        for(int s:new int[]{-1,1}) {
            m.sweep(new P[]{face(s*.38,.56,.05),face(s*.46,.36,.13),face(s*.48,-.08,.20),face(s*.45,-.34,.10)},new double[]{.12,.13,.07,.018},new double[]{.10,.11,.075,.018},12,7,HAIR);
        }
        m.ellipsoid(HEAD.add(p(.06,.78,0)),p(.24,.28,.23),HAIR,12,7);
        m.band(HEAD.add(p(-.03,.65,0)),.25,.07,.035,GOLD);
        // Hair originates at tied crown and flows behind the aiming head (+X), in solid locks.
        for(int i=-2;i<=2;i++) {
            double z=i*.13;
            m.sweep(new P[]{HEAD.add(p(.16,.69,z*.4)),p(.63,8.26,z),p(.88,7.40,z*1.3-.15),p(1.00+i*.035,6.40,z*1.5-.43),p(1.40,5.65+Math.abs(i)*.19,z*1.4-.52)},
                new double[]{.085,.10,.12,.087,.008},new double[]{.095,.12,.13,.075,.008},20,7,HAIR);
        }
        // Low solar diadem, not a heavy royal crown.
        faceSweep(m,new double[][]{{-.45,.40,.17},{-.35,.44,.36},{0,.47,.44},{.35,.44,.36},{.45,.40,.17}},.036,.040,GOLD);
        m.ellipsoid(face(0,.51,.47),p(.052,.10,.07),LIGHT,8,6);
        for(int s:new int[]{-1,1})faceSweep(m,new double[][]{{s*.14,.48,.38},{s*.19,.65,.25},{s*.13,.83,.12}},.030,.040,GOLD);
        for(int i=-1;i<=1;i++)faceSweep(m,new double[][]{{i*.15,.75,.06},{i*.19,1.14,.05},{i*.20,1.59-Math.abs(i)*.17,.02}},.032,.035,GOLD);
    }
    private static void clothing(GuanYuSculptor m) {
        // Curved chest plates have back walls/rims and a real gap over the cloth.
        for(int s:new int[]{-1,1}) {
            final int side=s;
            m.shell(6,7,(u,v)->p(side*(.10+.88*u)*(1-.20*v),6.96-1.02*v,
                    .78+.12*Math.sin(u*Math.PI)*Math.sin(v*Math.PI)-side*.08),p(0,0,-.065),IVORY,ARMOR);
            m.wire(new P[]{p(s*.16,7.02,.79-s*.08),p(s*.69,6.90,.84-s*.08),p(s*.94,6.47,.80-s*.08),p(s*.60,5.97,.79-s*.08)},.028,GOLD,16);
        }
        m.band(p(-.03,6.44,1.01),.21,.23,.028,GOLD);
        m.ellipsoid(p(-.03,6.44,1.005),p(.18,.20,.10),ARMOR,10,6);
        m.ellipsoid(p(-.03,6.44,1.09),p(.105,.13,.05),LIGHT,10,6);
        for(int i=0;i<8;i++) {
            double a=i*Math.PI/4;
            m.wire(new P[]{p(-.03+.24*Math.cos(a),6.44+.26*Math.sin(a),1.00),p(-.03+.31*Math.cos(a),6.44+.33*Math.sin(a),.97)},.017,GOLD,2);
        }
        for(int i=0;i<3;i++) {
            final int row=i;
            m.shell(8,3,(u,v)->p((u-.5)*(1.36-row*.15),5.99-row*.24-.22*v,
                    .57+.06*Math.cos((u-.5)*Math.PI)),p(0,0,-.055),ARMOR,CLOTH);
        }
        // Belt is a closed oval cuff, rather than a painted stripe.
        m.sweep(new P[]{p(0,4.64,0),p(0,4.91,0)},new double[]{.73,.68},new double[]{.53,.50},2,20,HAIR);
        m.ellipsoid(p(0,4.78,.55),p(.21,.15,.09),GOLD,10,6);
        m.ellipsoid(p(0,4.78,.635),p(.085,.073,.025),LIGHT,8,5);
        for(int panel=0;panel<6;panel++) {
            final double a=panel*Math.PI/3;
            final double length=panel%3==0?1.48:1.10;
            m.shell(4,8,(u,v)->{
                double theta=a+(u-.5)*.80, r=.77+.32*v;
                return p(Math.sin(theta)*r,4.64-v*length,Math.cos(theta)*r*.69);
            },p(Math.sin(a)*.045,0,Math.cos(a)*.045),panel%2==0?ARMOR:CLOTH,HAIR);
            m.wire(new P[]{p(Math.sin(a-.4)*.80,4.60,Math.cos(a-.4)*.55),p(Math.sin(a-.36)*.96,4.60-length*.6,Math.cos(a-.36)*.67),p(Math.sin(a-.32)*1.10,4.60-length,Math.cos(a-.32)*.76)},.019,GOLD,10);
        }
        for(int s:new int[]{-1,1}) {
            double kz=s<0?.26:-.12;
            m.ellipsoid(p(s*.66,2.45,kz+.26),p(.27,.25,.13),IVORY,10,7);
            m.ellipsoid(p(s*.75,1.56,kz+.27),p(.22,.60,.105),ARMOR,10,8);
            for(int i=0;i<3;i++)m.sweep(new P[]{p(s*(.70+.025*i),1.93-i*.38,kz),p(s*(.70+.025*i),1.84-i*.38,kz)},new double[]{.31,.30},new double[]{.29,.28},1,12,HAIR);
        }
    }
    private static void asymmetry(GuanYuSculptor m) {
        // Stable bow shoulder has two small lames; drawing shoulder is free to rotate.
        for(int i=0;i<2;i++)m.ellipsoid(HOLD_SHOULDER.add(p(-i*.20,.18-i*.08,0)),p(.45,.19,.44),i==0?IVORY:ARMOR,12,6);
        m.ellipsoid(DRAW_SHOULDER.add(p(0,.13,-.05)),p(.37,.14,.37),ARMOR,12,6);
        // Quiver sits on the drawing hip, away from the bowstring plane.
        m.sweep(new P[]{p(.97,3.58,-.46),p(1.15,4.63,-.50),p(1.22,5.12,-.52)},new double[]{.20,.24,.25},new double[]{.17,.20,.22},9,10,HAIR);
        m.sweep(new P[]{p(1.20,5.01,-.52),p(1.24,5.15,-.52)},new double[]{.265,.265},new double[]{.23,.23},2,10,GOLD);
        for(int i=0;i<3;i++) {
            P base=p(.99+i*.17,4.65,-.52),top=base.add(p(.17,1.26+(i%2)*.13,-.04));
            m.wire(new P[]{base,top},.023,GOLD,3);
            m.sweep(new P[]{top.add(p(-.02,-.32,0)),top.add(p(-.015,-.08,0)),top},new double[]{.07,.07,.009},new double[]{.035,.03,.008},5,6,IVORY);
        }
        m.wire(new P[]{p(-.47,7.07,-.43),p(.06,6.34,-.65),p(.75,5.35,-.52),p(.91,4.82,-.49)},.09,HAIR,15);
        for(int i=0;i<2;i++) {
            final int n=i;
            m.shell(3,14,(u,v)->{
                P c=GuanYuSculptor.path(new P[]{p(-.61,4.76,-.12),p(-1.07,4.02,-.53),p(-1.12,3.05,-.70),p(-1.49,2.63+n*.23,-.35)},v);
                return c.add(p((u-.5)*(.27-.14*v),0,n*.18));
            },p(0,0,.035),i==0?IVORY:CLOTH,CLOTH);
        }
    }
    private static void armArmor(GuanYuSculptor m) {
        forearmGuard(m,HOLD_ELBOW,HOLD_WRIST,.35,IVORY);
        forearmGuard(m,DRAW_ELBOW,DRAW_WRIST,.33,ARMOR);
    }
    private static void forearmGuard(GuanYuSculptor m,P elbow,P wrist,double radius,Material mat) {
        P a=elbow.scale(.70).add(wrist.scale(.30)),b=elbow.scale(.16).add(wrist.scale(.84));
        m.sweep(new P[]{a,a.add(b).scale(.5),b},new double[]{radius,radius*.94,.205},new double[]{radius*.94,radius*.88,.20},8,10,mat);
        for(double t:new double[]{.05,.86}) {
            P c=a.scale(1-t).add(b.scale(t)),d=a.scale(1-t-.07).add(b.scale(t+.07));
            double r=radius*(1-t)+.205*t;
            m.sweep(new P[]{c,d},new double[]{r+.015,r+.015},new double[]{r+.01,r+.01},1,10,GOLD);
        }
    }
    private static void hands(GuanYuSculptor m) {
        // Bow grip runs through the empty fist bore, not through a palm solid.
        m.sweep(new P[]{HOLD_WRIST,GRIP.add(p(.15,0,-.16)),GRIP.add(p(.03,0,-.23))},new double[]{.155,.16,.17},new double[]{.13,.095,.08},6,8,SKIN);
        for(int i=0;i<4;i++) {
            double y=GRIP.y()+.17-i*.11;
            m.sweep(new P[]{p(GRIP.x()+.14,y,GRIP.z()-.09),p(GRIP.x()-.01,y,GRIP.z()-.16),p(GRIP.x()-.17,y,GRIP.z()-.02),p(GRIP.x()-.07,y,GRIP.z()+.15),p(GRIP.x()+.07,y,GRIP.z()+.13)},new double[]{.048,.05,.047,.040},new double[]{.045,.045,.042,.036},10,6,SKIN);
        }
        m.sweep(new P[]{GRIP.add(p(.19,-.11,-.02)),GRIP.add(p(.18,.16,.11)),GRIP.add(p(.01,.25,.14)),GRIP.add(p(-.07,.15,.12))},new double[]{.074,.065,.058,.043},new double[]{.065,.062,.051,.038},9,7,SKIN);
        // Mediterranean draw: three bent fingers hook behind the nock beside the cheek.
        m.sweep(new P[]{DRAW_WRIST,p(.27,7.93,.86),p(.09,7.96,.91)},new double[]{.15,.16,.13},new double[]{.12,.12,.09},6,8,SKIN);
        for(int i=0;i<3;i++) {
            double y=NOCK.y()+.13-i*.12;
            m.sweep(new P[]{p(.17,y,.92),p(-.01,y,.91),p(-.04,y,.75),p(.10,y,.70)},new double[]{.049,.050,.044,.030},new double[]{.045,.045,.04,.026},8,6,SKIN);
        }
        m.wire(new P[]{p(.25,8.04,.84),p(.15,8.10,.83),p(.04,8.08,.89)},.049,SKIN,7);
        m.wire(new P[]{p(.30,7.81,.86),p(.20,7.74,.85),p(.11,7.76,.90)},.045,SKIN,7);
    }
    private static void bow(GuanYuSculptor m) {
        // Preserve the golden recurved design, balancing both limbs around the raised grip.
        // Slightly shorter limbs keep the existing ten-block avatar envelope, not a larger bow.
        P[] center={BOW_BOTTOM,p(-3.28,6.15,.78),p(-3.66,6.90,.78),GRIP,p(-3.66,8.66,.78),p(-3.28,9.41,.78),BOW_TOP};
        m.sweep(center,new double[]{.030,.11,.10,.078,.092,.024},new double[]{.038,.15,.135,.12,.13,.035},38,10,GOLD);
        m.sweep(new P[]{p(-3.04,5.81,.88),p(-3.43,6.44,.90),p(-3.75,7.12,.90),GRIP.add(p(.015,0,.11)),p(-3.51,9.05,.90),p(-3.02,9.78,.81)},new double[]{.022,.041,.035,.03,.026,.008},new double[]{.028,.04,.04,.03,.028,.01},32,7,ARMOR);
        m.sweep(new P[]{GRIP.add(p(0,-.26,0)),GRIP.add(p(0,.28,0))},new double[]{.083,.083},new double[]{.085,.085},3,10,HAIR);
        for(int i=0;i<7;i++)m.sweep(new P[]{GRIP.add(p(0,-.25+i*.074,0)),GRIP.add(p(0,-.224+i*.074,0))},new double[]{.088,.088},new double[]{.091,.091},1,10,GOLD);
        m.wire(new P[]{BOW_TOP,NOCK},.015,LIGHT,2);
        m.wire(new P[]{NOCK,BOW_BOTTOM},.015,LIGHT,2);
        P arrowFront=p(-4.76,7.755,.78);
        m.sweep(new P[]{NOCK,arrowFront},new double[]{.025,.025},new double[]{.025,.025},2,8,GOLD);
        m.sweep(new P[]{arrowFront.add(p(.10,0,0)),arrowFront.add(p(-.32,-.01,0))},new double[]{.11,.001},new double[]{.08,.001},2,6,LIGHT);
        // Restrained solar nimbus behind the head, preserving the apparition's identity.
        m.band(p(.60,8.22,-.62),.92,.92,.016,GOLD);
        m.band(p(.60,8.22,-.65),1.02,1.02,.010,LIGHT);
    }
}
