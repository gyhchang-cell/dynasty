package com.dynasty.client;

import java.util.ArrayList;
import java.util.List;
import com.dynasty.client.ImperialWeaponGeometry.P;

/** Closed-volume Chinese dragon: swept skin/scales, sculpted jaw, antlers, toes and hair locks. */
public final class ImperialDragonMesh {
    public record Face(P a,P b,P c,P d,int material) {}
    private record Frame(P center,P tangent,P back,P side,double radius) {}
    private static final List<Face> BUILD=new ArrayList<>();
    // A relaxed S: reduce lateral bends without stretching the head or detaching the legs.
    private static final P[] SPINE={p(.34,-1.45,-.09),p(.18,-1.36,-.035),p(-.20,-1.18,.065),
            p(-.34,-.87,.135),p(-.17,-.54,.18),p(.20,-.25,.17),p(.36,.10,.09),
            p(.32,.48,.020),p(.18,.78,0),p(.06,.94,.02)};
    public static final int BODY_ROWS=144,BODY_SIDES=36,MANE_LOCKS_PER_GROUP=7;
    private static final double[] RADII={.008,.047,.091,.129,.153,.176,.189,.18,.157,.153};
    private static final P HEAD=SPINE[SPINE.length-1];
    // x, y center, vertical half-height, lateral half-width; one coherent skull, not intersecting spheres.
    private static final double[][] CRANIUM={{.22,.025,.148,.148},{.14,.060,.240,.228},{.015,.064,.242,.260},
            {-.12,.040,.214,.233},{-.245,.018,.137,.190},{-.36,.009,.115,.167},{-.47,-.004,.100,.164},
            {-.58,-.020,.102,.178},{-.65,-.033,.075,.150},{-.673,-.038,.024,.085}};
    private static final double[][] JAW={{.135,-.09,.058,.120},{.065,-.136,.058,.139},{-.045,-.226,.055,.133},
            {-.19,-.287,.045,.139},{-.36,-.343,.047,.141},{-.52,-.394,.050,.146},{-.625,-.399,.045,.125},{-.65,-.375,.009,.033}};
    /** Actual capped nose vertex, not the model origin or an estimated bounding-box center. */
    public static final P MUZZLE=headPose(p(CRANIUM[CRANIUM.length-1][0]-.013,CRANIUM[CRANIUM.length-1][1],0));
    public static final P IMPACT_POINT=MUZZLE;
    public static final P HEAD_CENTER=HEAD;
    public static final List<Face> FACES=create();
    private static P p(double x,double y,double z){return new P(x,y,z);}
    private static P sub(P a,P b){return a.add(b.scale(-1));}
    private static double dot(P a,P b){return a.x()*b.x()+a.y()*b.y()+a.z()*b.z();}
    private static P cross(P a,P b){return p(a.y()*b.z()-a.z()*b.y(),a.z()*b.x()-a.x()*b.z(),a.x()*b.y()-a.y()*b.x());}
    private static P unit(P a){return a.scale(1/Math.max(1e-10,Math.sqrt(dot(a,a))));}
    private static double clamp(double v,double a,double b){return Math.max(a,Math.min(b,v));}
    private static P mix(P a,P b,double t){return a.scale(1-t).add(b.scale(t));}
    private static void quad(P a,P b,P c,P d,int m){BUILD.add(new Face(a,b,c,d,m));}
    private static double cat(double a,double b,double c,double d,double t){return .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t);}
    private static P cat(P a,P b,P c,P d,double t){return p(cat(a.x(),b.x(),c.x(),d.x(),t),cat(a.y(),b.y(),c.y(),d.y(),t),cat(a.z(),b.z(),c.z(),d.z(),t));}
    private static P curve(P[] pts,double t){
        double q=clamp(t,0,1)*(pts.length-1);int i=Math.min(pts.length-2,(int)q);
        return cat(pts[Math.max(0,i-1)],pts[i],pts[i+1],pts[Math.min(pts.length-1,i+2)],q-i);
    }
    private static double radius(double t){
        double q=clamp(t,0,1)*(RADII.length-1);int i=Math.min(RADII.length-2,(int)q);
        return cat(RADII[Math.max(0,i-1)],RADII[i],RADII[i+1],RADII[Math.min(RADII.length-1,i+2)],q-i);
    }
    private static Frame frame(double t){
        P center=curve(SPINE,t),tangent=unit(sub(curve(SPINE,t+.001),curve(SPINE,t-.001)));
        P back=unit(cross(tangent,p(0,0,1))),side=unit(cross(back,tangent));
        return new Frame(center,tangent,back,side,radius(t));
    }
    private static P skin(double t,double angle,double lift){
        Frame f=frame(t);return f.center.add(f.back.scale(Math.cos(angle)*(f.radius+lift)))
                .add(f.side.scale(Math.sin(angle)*(f.radius*.89+lift)));
    }

    /** A transported cross-section frame prevents twists at vertical tangents. */
    private static void sweep(P[] path,double[] widths,double[] depths,int steps,int sides,int material){
        P lastU=null;P[][] rings=new P[steps+1][sides];
        for(int j=0;j<=steps;j++){
            double t=j/(double)steps;P center=curve(path,t),tangent=unit(sub(curve(path,t+.001),curve(path,t-.001)));
            P u=lastU==null?unit(cross(tangent,Math.abs(tangent.z())<.90?p(0,0,1):p(0,1,0)))
                    :unit(sub(lastU,tangent.scale(dot(lastU,tangent))));
            P v=unit(cross(tangent,u));lastU=u;
            double k=t*(widths.length-1);int n=Math.min(widths.length-2,(int)k);
            double w=widths[n]*(1-(k-n))+widths[n+1]*(k-n),d=depths[n]*(1-(k-n))+depths[n+1]*(k-n);
            for(int s=0;s<sides;s++){double a=s*Math.PI*2/sides;rings[j][s]=center.add(u.scale(w*Math.cos(a))).add(v.scale(d*Math.sin(a)));}
        }
        for(int j=0;j<steps;j++)for(int s=0;s<sides;s++){int ss=(s+1)%sides;quad(rings[j][s],rings[j][ss],rings[j+1][ss],rings[j+1][s],material);}
        for(int s=0;s<sides;s++){int ss=(s+1)%sides;quad(path[0],rings[0][ss],rings[0][s],path[0],material);
            quad(path[path.length-1],rings[steps][s],rings[steps][ss],path[path.length-1],material);}
    }
    private static void branch(P[] pts,double width,int material,int steps){
        sweep(pts,new double[]{width,width*.85,width*.47,.0001},new double[]{width,width*.85,width*.47,.0001},steps,10,material);
    }
    /** Staggered shield scales point toward the tail; relief is confined to the free edge. */
    private static void scale(double t,double a,double dt,double da,int material){
        double[][] border={{-.80,-.46},{-.90,0},{-.80,.46},{-.05,.62},{.76,.40},{1,0},{.76,-.40},{-.05,-.62}};
        P[] rim=new P[8],inner=new P[8];
        for(int k=0;k<8;k++){
            // Reverse the shield: its pointed free end trails toward the tail, not the head.
            rim[k]=skin(clamp(t-border[k][0]*dt,0,1),a+border[k][1]*da,.0012);
            inner[k]=skin(t-border[k][0]*dt*.87,a+border[k][1]*da*.87,.0042+radius(t)*.012);
        }
        for(int k=0;k<8;k++){int kk=(k+1)%8;quad(rim[k],rim[kk],inner[kk],inner[k],k==4||k==5?10:8);}
        quad(inner[0],inner[1],inner[2],inner[3],material);
        quad(inner[0],inner[3],inner[4],inner[7],material);
        quad(inner[7],inner[4],inner[5],inner[6],material);
    }
    private static void body(){
        for(int i=0;i<BODY_ROWS;i++)for(int j=0;j<BODY_SIDES;j++){
            double t=i/(double)BODY_ROWS,tt=(i+1)/(double)BODY_ROWS;
            double a=j*Math.PI*2/BODY_SIDES,aa=(j+1)*Math.PI*2/BODY_SIDES;
            quad(skin(t,a,0),skin(t,aa,0),skin(tt,aa,0),skin(tt,a,0),8);
        }
        for(int row=0;row<74;row++){
            double t=.102+row*.0118;
            for(int j=0;j<22;j++){
                double a=(j+(row%2)*.5)*Math.PI/11+.012*Math.sin(row*.43);
                if(Math.cos(a)<-.57)continue;
                double varied=.97+.035*Math.sin(j*2.1+row*.71);
                // Staggered shields fit between neighbors. The former 1.31 angular span
                // let same-height tiles slice through one another along their edges.
                // Sparse neighboring hues keep the enlarged relief readable without a checkerboard.
                int tone=(row+j)%9==0?17:(row*3+j)%11==0?18:0;
                scale(t,a,.0054*varied,Math.PI/11*.78,tone);
            }
        }
        // Broad articulated ventral plates, not thin painted belly lines.
        for(int row=0;row<69;row++){
            double t=.035+row*.0138,tt=t+.0126;
            for(int j=0;j<9;j++){double a=Math.PI-.99+j*.22,aa=a+.22;quad(skin(t,a,.003),skin(t,aa,.003),skin(tt,aa,.0045),skin(tt,a,.0045),6);}
        }
        // Swept dorsal locks are curved tapered volumes rather than flat triangles.
        for(int row=0;row<26;row++){
            double t=.13+row*.0315;Frame f=frame(t);P root=skin(t,0,.001);double len=.045+.12*Math.sin(t*Math.PI*.65);
            P[] strand={root,root.add(f.back.scale(len*.42)).add(f.tangent.scale(-.025)),
                    root.add(f.back.scale(len*.79)).add(f.tangent.scale(-.065)),root.add(f.back.scale(len)).add(f.tangent.scale(-.14))};
            sweep(strand,new double[]{.016,.028,.019,.0001},new double[]{.009,.011,.008,.0001},9,6,row%3==0?3:1);
        }
        Frame tail=frame(.015);
        for(int k=-3;k<=3;k++){
            P root=tail.center.add(tail.side.scale(k*.006));
            P[] lock={root,root.add(tail.tangent.scale(-.08)).add(tail.back.scale(k*.016)),root.add(tail.tangent.scale(-.20)).add(tail.back.scale(k*.036)),
                    root.add(tail.tangent.scale(-.34+Math.abs(k)*.024)).add(tail.back.scale(k*.037))};
            sweep(lock,new double[]{.018,.025,.016,.0001},new double[]{.008,.010,.006,.0001},12,6,k%2==0?1:3);
        }
    }
    private static void limbs(){
        for(int pair=0;pair<2;pair++)for(int side:new int[]{-1,1}){
            double t=pair==0?.445:.785;Frame f=frame(t);P ventral=f.back.scale(-1),lateral=f.side.scale(side),root=skin(t,side*1.90,0);
            P elbow=root.add(ventral.scale(.165)).add(f.tangent.scale(pair==0?.08:-.14)).add(lateral.scale(.072));
            P wrist=elbow.add(ventral.scale(.145)).add(f.tangent.scale(pair==0?-.17:.13)).add(lateral.scale(.068));
            P palm=wrist.add(ventral.scale(.055)).add(f.tangent.scale(pair==0?-.04:.015));
            sweep(new P[]{root,mix(root,elbow,.45),elbow,wrist,palm},new double[]{.072,.071,.040,.031,.032},
                    new double[]{.065,.059,.039,.028,.025},15,12,0);
            for(int n=0;n<3;n++){
                double u=.17+n*.19;P a=mix(root,elbow,u),b=mix(root,elbow,u+.12);
                sweep(new P[]{a,b},new double[]{.071-n*.009,.065-n*.009},new double[]{.058-n*.005,.054-n*.005},1,10,n%2==0?5:0);
            }
            P direction=unit(ventral.add(f.tangent.scale(pair==0?-.6:.5))),spread=unit(cross(direction,lateral));
            for(int digit=0;digit<4;digit++){
                double fan=(digit-1)*.038;P start=palm.add(spread.scale(fan*.60));
                P digitDirection=direction;
                if(digit==3){start=palm.add(spread.scale(-.022));digitDirection=unit(direction.scale(-.50).add(spread.scale(-1)));fan=-.010;}
                P knuckle=start.add(digitDirection.scale(digit==1?.063:.051)).add(spread.scale(fan));
                P end=knuckle.add(digitDirection.scale(.042)).add(lateral.scale(.012));
                sweep(new P[]{start,knuckle,end},new double[]{.017,.014,.008},new double[]{.014,.013,.007},5,8,0);
                branch(new P[]{end,end.add(digitDirection.scale(.025)).add(lateral.scale(.013)),end.add(digitDirection.scale(.036)).add(lateral.scale(.042))},.010,3,6);
            }
        }
    }
    private static double section(double[][] s,double t,int value){
        double q=clamp(t,0,1)*(s.length-1);int i=Math.min(s.length-2,(int)q);
        return cat(s[Math.max(0,i-1)][value],s[i][value],s[i+1][value],s[Math.min(s.length-1,i+2)][value],q-i);
    }
    private static P sectionPoint(double[][] s,double t,double a,double inflate){
        double x=section(s,t,0),y=section(s,t,1),h=section(s,t,2),w=section(s,t,3),sy=Math.sin(a),cz=Math.cos(a);
        double ridge=s==CRANIUM?.011*Math.exp(-Math.pow((x+.27)/.23,2))*Math.max(0,sy):0;
        return p(x,y+(h+inflate)*sy+ridge,(w+inflate)*cz);
    }
    private static void loft(double[][] sections,int steps,int material){
        for(int i=0;i<steps;i++)for(int j=0;j<32;j++){
            double t=i/(double)steps,tt=(i+1)/(double)steps,a=j*Math.PI/16,aa=(j+1)*Math.PI/16;
            quad(sectionPoint(sections,t,a,0),sectionPoint(sections,t,aa,0),sectionPoint(sections,tt,aa,0),sectionPoint(sections,tt,a,0),material);
        }
        for(int j=0;j<32;j++){
            double a=j*Math.PI/16,aa=(j+1)*Math.PI/16;
            P first=p(sections[0][0]+.010,sections[0][1],0),last=p(sections[sections.length-1][0]-.013,sections[sections.length-1][1],0);
            quad(first,sectionPoint(sections,0,aa,0),sectionPoint(sections,0,a,0),first,material);
            quad(last,sectionPoint(sections,1,a,0),sectionPoint(sections,1,aa,0),last,material);
        }
    }
    private static void patch(P center,P u,P v,P normal,double width,double height,double depth,int material){
        for(int r=0;r<3;r++)for(int i=0;i<24;i++){
            double a=i*Math.PI/12,b=(i+1)*Math.PI/12,rr=r/3.0,ss=(r+1)/3.0;
            quad(patchPoint(center,u,v,normal,width,height,depth,rr,a),patchPoint(center,u,v,normal,width,height,depth,rr,b),
                    patchPoint(center,u,v,normal,width,height,depth,ss,b),patchPoint(center,u,v,normal,width,height,depth,ss,a),material);
        }
    }
    private static P patchPoint(P c,P u,P v,P n,double w,double h,double d,double r,double a){
        double x=Math.cos(a),y=Math.sin(a)*(1-.22*Math.abs(Math.cos(a)));
        return c.add(u.scale(x*r*w)).add(v.scale(y*r*h)).add(n.scale(d*(1-r*r)));
    }
    private static void head(){
        int first=BUILD.size();loft(CRANIUM,64,0);loft(JAW,48,0);
        sweep(new P[]{p(-.51,-.234,0),p(-.35,-.207,0),p(-.17,-.155,0),p(-.075,-.107,0)},
                new double[]{.129,.112,.083,.040},new double[]{.101,.111,.106,.075},12,16,2);
        sweep(new P[]{p(-.56,-.352,0),p(-.43,-.322,0),p(-.30,-.277,0),p(-.20,-.247,0)},
                new double[]{.009,.014,.015,.009},new double[]{.057,.066,.060,.036},10,10,7);
        for(int side:new int[]{-1,1}){
            P[] upper={p(-.605,-.091,side*.118),p(-.48,-.103,side*.124),p(-.31,-.100,side*.126),p(-.16,-.096,side*.146)};
            P[] lower={p(-.585,-.349,side*.102),p(-.48,-.341,side*.119),p(-.32,-.299,side*.119),p(-.16,-.230,side*.123)};
            sweep(upper,new double[]{.006,.008,.009,.005},new double[]{.008,.009,.008,.005},15,8,7);
            sweep(lower,new double[]{.005,.008,.008,.004},new double[]{.006,.009,.007,.004},15,8,7);
            for(int k=0;k<8;k++){
                double t=.06+k*.117+.012*Math.sin(k*1.8);P top=curve(upper,t),bottom=curve(lower,t);
                double len=k==1?.129:k==6?.095:.031+(Math.sin(k*2.4)+1)*.015;
                branch(new P[]{top,top.add(p(-.006,-len*.53,-side*.006)),top.add(p(.012,-len,-side*.011))},k==1?.019:.0105,3,5);
                double lowerLen=k==2?.073:.029+(Math.sin(k*1.7)+1)*.011;
                branch(new P[]{bottom,bottom.add(p(-.011,lowerLen*.62,-side*.005)),bottom.add(p(-.002,lowerLen,-side*.014))},k==2?.013:.009,3,5);
            }
            P ec=p(-.146,.098,side*.210),eu=unit(p(1,.33,0)),ev=unit(p(-.33,1,0)),en=p(-.10,.10,side);
            patch(ec,eu,ev,en,.063,.026,.012,2);patch(ec.add(eu.scale(-.012)).add(en.scale(.011)),eu,ev,en,.025,.019,.006,4);
            patch(ec.add(eu.scale(-.012)).add(en.scale(.018)),eu,ev,en,.005,.017,.002,2);
            patch(ec.add(eu.scale(-.022)).add(ev.scale(.007)).add(en.scale(.023)),eu,ev,en,.005,.003,.001,12);
            P[] brow={p(-.247,.112,side*.184),p(-.181,.143,side*.223),p(-.105,.177,side*.232),p(-.021,.185,side*.236)};
            sweep(brow,new double[]{.006,.028,.042,.014},new double[]{.005,.025,.031,.012},12,10,0);
            branch(new P[]{p(-.105,.175,side*.236),p(.010,.245,side*.276),p(.143,.275,side*.249)},.016,1,9);
            P[] cheek={p(-.212,-.015,side*.193),p(-.114,-.020,side*.245),p(-.029,-.052,side*.273),p(.087,-.126,side*.225)};
            sweep(cheek,new double[]{.016,.034,.046,.007},new double[]{.012,.024,.026,.005},12,8,0);
            for(int k=0;k<3;k++){
                P root=p(-.105+k*.060,-.075-k*.012,side*(.210+k*.012));
                sweep(new P[]{root,root.add(p(.060,-.045,side*.045)),root.add(p(.160,-.130,side*.083)),
                        root.add(p(.255,-.178-k*.038,side*.091))},new double[]{.010,.023,.014,.0001},
                        new double[]{.008,.012,.009,.0001},8,6,k==0?1:13);
            }
            P nc=p(-.616,.006,side*.164);
            patch(nc,unit(p(1,.15,0)),p(0,1,0),p(-.12,.12,side),.030,.025,.001,2);
            sweep(new P[]{p(-.651,-.060,side*.123),p(-.640,-.001,side*.164),p(-.589,.027,side*.177),p(-.535,-.001,side*.153)},
                    new double[]{.006,.012,.016,.005},new double[]{.006,.012,.013,.005},10,8,0);
            antler(side);mane(side);
            for(int k=0;k<2;k++){
                P[] whisker={p(-.602,-.080,side*.137),p(-.79,-.065+k*.019,side*.199),p(-.96,.054-k*.11,side*.279),
                        p(-1.11,.117-k*.14,side*.307),p(-1.18,.065-k*.19,side*.354)};
                sweep(whisker,new double[]{.0085,.008,.005,.0004},new double[]{.0085,.008,.005,.0004},24,6,k==0?3:1);
            }
        }
        for(int row=0;row<17;row++)for(int col=0;col<21;col++){
            double t=.060+row*.047,a=-.165+col*.17+(row%2)*.079+.009*Math.sin(row*.71);
            double x=section(CRANIUM,t,0);
            if(x>-.26&&x<-.065&&(a<.65||a>Math.PI-.65))continue;
            P[] tile={sectionPoint(CRANIUM,t-.022,a,.0015),sectionPoint(CRANIUM,t-.015,a+.091,.0015),
                    sectionPoint(CRANIUM,t+.016,a+.091,.0015),sectionPoint(CRANIUM,t+.026,a,.0015),
                    sectionPoint(CRANIUM,t+.016,a-.091,.0015),sectionPoint(CRANIUM,t-.015,a-.091,.0015)};
            P crown=sectionPoint(CRANIUM,t,a,.006);
            // All facets share skin color; only actual relief shades the fine scales.
            // Darkening a third of every tile made the forehead look like an industrial zigzag grid.
            for(int k=0;k<6;k++)quad(tile[k],tile[(k+1)%6],crown,crown,0);
        }
        for(int k=-5;k<=5;k++){
            double z=k*.016;P root=p(-.44+Math.abs(k)*.014,-.403,z);
            P[] lock={root,root.add(p(.025,-.093,z*.15)),root.add(p(.100,-.190,z*.30)),root.add(p(.181,-.225-Math.cos(k*.4)*.045,z*.38))};
            sweep(lock,new double[]{.013,.018,.012,.0001},new double[]{.007,.009,.006,.0001},14,6,k%3==0?3:1);
        }
        for(int i=first;i<BUILD.size();i++){Face f=BUILD.get(i);BUILD.set(i,new Face(headPose(f.a),headPose(f.b),headPose(f.c),headPose(f.d),f.material));}
    }
    private static void antler(int side){
        P[] main={p(.035,.256,side*.152),p(.113,.370,side*.187),p(.254,.483,side*.218),p(.357,.650,side*.241),p(.325,.811,side*.264)};
        sweep(main,new double[]{.048,.040,.029,.018,.0001},new double[]{.042,.036,.027,.017,.0001},24,12,1);
        // Forks originate on the actual curved trunk, so editing its profile cannot leave floating stubs.
        P lower=curve(main,.29),middle=curve(main,.52),upper=curve(main,.77);
        branch(new P[]{lower,lower.add(p(-.051,.117,-side*.015)),lower.add(p(-.116,.216,side*.003))},.023,3,12);
        branch(new P[]{middle,middle.add(p(.121,.022,side*.038)),middle.add(p(.199,.121,side*.076))},.022,3,12);
        branch(new P[]{upper,upper.add(p(.109,.049,side*.031)),upper.add(p(.162,.144,side*.071))},.016,3,10);
        for(int k=0;k<3;k++){
            P a=mix(main[0],main[1],.10+k*.14),b=mix(main[0],main[1],.14+k*.14);
            sweep(new P[]{a,b},new double[]{.045-k*.003,.043-k*.003},new double[]{.040-k*.002,.038-k*.002},1,12,6);
        }
    }
    private static void mane(int side){
        sweep(new P[]{p(.065,.090,side*.233),p(.214,.156,side*.316),p(.337,.166,side*.345),p(.388,.229,side*.322)},
                new double[]{.045,.068,.035,.0001},new double[]{.016,.019,.012,.0001},14,8,0);
        // Three hair groups have different root directions and curls: a crown, cheek ruff and throat mane.
        // Fine ridges follow each bundle instead of becoming parallel comb teeth.
        for(int group=0;group<3;group++)for(int k=0;k<MANE_LOCKS_PER_GROUP;k++){
            double f=k/(double)(MANE_LOCKS_PER_GROUP-1);P root;P[] lock;
            if(group==0){
                root=p(.015+f*.105,.255-f*.085,side*(.170+f*.054));
                lock=new P[]{root,root.add(p(.078,.105-f*.055,side*.027)),root.add(p(.223,.126-f*.049,side*.047)),
                        root.add(p(.326,.163-f*.134,side*.079)),root.add(p(.384,.101-f*.179,side*.070))};
            }else if(group==1){
                root=p(-.018+f*.086,.126-f*.198,side*(.244-f*.018));
                lock=new P[]{root,root.add(p(.112,.024-f*.043,side*.058)),root.add(p(.255,.076-f*.185,side*.105)),
                        root.add(p(.372,.085-f*.233,side*.127)),root.add(p(.438,.137-f*.357,side*.072))};
            }else{
                root=p(-.080+f*.108,-.061-f*.078,side*(.210+f*.019));
                lock=new P[]{root,root.add(p(.088,-.085,side*.055)),root.add(p(.178,-.223+f*.042,side*.091)),
                        root.add(p(.260,-.277+f*.061,side*.073)),root.add(p(.309,-.224+f*.053,side*.102))};
            }
            double width=.014+.004*Math.sin(k*2.0+group);
            // Thin, flattened hair bundles, with longer free wisps rather than thick sausage curls.
            lock[lock.length-1]=lock[lock.length-1].add(p(.035+.018*Math.sin(k*1.7),
                    .055*Math.sin(k*2.1+group),side*.014*Math.cos(k*.9)));
            sweep(lock,new double[]{.008,width,width*.80,.008,.0001},new double[]{.005,.009,.007,.004,.0001},14,8,group==0&&k==0?1:13);
            for(int strand=-1;strand<=1;strand++){
                P[] fine=new P[lock.length];
                for(int j=0;j<lock.length;j++){
                    double phase=j/(double)(lock.length-1),offset=strand*.009*Math.sin(Math.PI*phase);
                    fine[j]=lock[j].add(p(-.003,offset+.003,side*(.008-.004*phase)));
                }
                sweep(fine,new double[]{.0015,.0022,.0015,.0001},new double[]{.0015,.0022,.0015,.0001},10,4,strand==0?15:16);
            }
        }
    }
    private static P headPose(P point){
        // Broad feline muzzle rather than an excessively long crocodile-like parallel snout.
        double x=point.x()<-.20?-.20+(point.x()+.20)*.79:point.x();
        double c=Math.cos(.67),s=Math.sin(.67);return HEAD.add(p(x*c+point.z()*s,point.y(),-x*s+point.z()*c));
    }
    /** Subtract this rotated/scaled offset from a target to make the nose touch it exactly. */
    public static P impactOffset(double size,double angle){
        double c=Math.cos(angle),s=Math.sin(angle);
        return p((IMPACT_POINT.x()*c-IMPACT_POINT.y()*s)*size,
                (IMPACT_POINT.x()*s+IMPACT_POINT.y()*c)*size,IMPACT_POINT.z()*size);
    }
    private static List<Face> create(){
        body();limbs();head();
        if(BUILD.size()>56000)throw new IllegalStateException("Dragon geometry exceeded 56k face budget: "+BUILD.size());
        for(Face f:BUILD)for(P v:new P[]{f.a,f.b,f.c,f.d})if(!Double.isFinite(v.x()+v.y()+v.z()))throw new IllegalStateException("Non-finite dragon vertex");
        List<Face> mesh=List.copyOf(BUILD);BUILD.clear();return mesh;
    }
    public static int color(int material,boolean jade){
        return switch(material){case 1->jade?0xcbb478:0xd8ac54;case 2->0x152022;case 3->0xf2dfb7;case 4->0xffcf61;
            case 5->jade?0x579c90:0xd3a44c;case 6->jade?0xd1c598:0xdcc58b;case 7->0x482824;case 8->jade?0x265b56:0x886023;
            case 10->jade?0x518f84:0xc69642;case 12->0xd4ffff;case 13->jade?0x497b68:0xb99d58;
            case 15->jade?0x7ba58c:0xe1c887;case 16->jade?0x34594c:0x907538;
            case 17->jade?0x448a7c:0xc59744;case 18->jade?0x327166:0xa57930;default->jade?0x397c71:0xb78736;};
    }
    private ImperialDragonMesh(){}
}
