package com.dynasty.client;

/** Solid beveled regalia, in humanoid model coordinates. No particles, entities or collision boxes. */
public final class BossRegaliaGeometry {
    public record P(double x,double y,double z) {}
    @FunctionalInterface public interface Face { void quad(P a,P b,P c,P d,int color); }
    private final Face out;
    public BossRegaliaGeometry(Face out){this.out=out;}
    public void draw(int style,double time) {
        if(style!=1&&style!=2)return;
        if(style==1) {
            // Segmented imperial aureole, jade inside gold; offset behind the shoulders.
            ring(0,-.12,.66,1.03,.074,.055,0xf1c879,time*.08,12,.12);
            ring(0,-.12,.69,.88,.038,.04,0x278f81,-time*.06,48,.01);
            // Six detached seal tablets orbit slowly in a vertical plane.
            for(int i=0;i<6;i++) {
                double a=i*Math.PI/3+time*.006;
                double x=Math.cos(a)*1.29,y=-.12+Math.sin(a)*1.29;
                blade(x,y,.64,.15,.28,.055,a-Math.PI/2,0x23796f,0xffd586);
                blade(x,y,.565,.032,.11,.015,a-Math.PI/2,0xffe5a3,0xc68e42);
            }
            // Three-pronged crown above the head, independent of floating ornaments.
            for(int i=-1;i<=1;i++)blade(i*.17,-.72-Math.abs(i)*.03,0,.08,.18,.055,i*.22,0xa96c2c,0xffdc82);
        } else {
            // Two oblique, physically thick celestial armillary rings.
            ring(0,-.02,.7,1.04,.052,.04,0xa3d7ea,time*.12,16,.07);
            ring(0,-.02,.74,.81,.038,.05,0x417fb6,-time*.17,12,.10);
            // Wing-shaped fan of six levitating thunder blades, not a copy of the golden seal crown.
            for(int side:new int[]{-1,1})for(int i=0;i<3;i++) {
                double bob=Math.sin(time*.04+i*.8)*.045;
                blade(side*(.84+i*.24),-.37+i*.27+bob,.49+i*.06,
                        .12,.48-i*.06,.07,side*(.27+i*.20),0x427da4,0xd9f6ff);
                ring(side*(.84+i*.24),-.37+i*.27+bob,.41+i*.06,.066,.019,.014,0xffdc97,0,8,0);
            }
        }
    }
    private void blade(double x,double y,double z,double width,double height,double depth,double angle,int base,int edge) {
        // Tapered diamond section with a raised central ridge, not a rectangular cuboid.
        P top=point(x,y,z,0,-height,0,angle),right=point(x,y,z,width,0,0,angle);
        P bottom=point(x,y,z,0,height*.66,0,angle),left=point(x,y,z,-width,0,0,angle);
        P front=point(x,y,z,0,0,-depth,angle),back=point(x,y,z,0,0,depth,angle);
        P[] rim={top,right,bottom,left};
        for(int i=0;i<4;i++) {
            out.quad(rim[i],rim[(i+1)%4],front,front,i%2==0?edge:base);
            out.quad(rim[(i+1)%4],rim[i],back,back,base);
        }
    }
    private P point(double x,double y,double z,double a,double b,double c,double angle) {
        return new P(x+a*Math.cos(angle)-b*Math.sin(angle),y+a*Math.sin(angle)+b*Math.cos(angle),z+c);
    }
    private void ring(double x,double y,double z,double radius,double thick,double depth,int color,double rotation,int count,double gap) {
        for(int i=0;i<count;i++) {
            double a=i*Math.PI*2/count+Math.toRadians(rotation)+gap*.5;
            double b=(i+1)*Math.PI*2/count+Math.toRadians(rotation)-gap*.5;
            P of=radial(x,y,z-depth,radius+thick,a),ot=radial(x,y,z-depth,radius+thick,b);
            P in=radial(x,y,z-depth,radius-thick,a),it=radial(x,y,z-depth,radius-thick,b);
            P ob=radial(x,y,z+depth,radius+thick,a),obt=radial(x,y,z+depth,radius+thick,b);
            P ib=radial(x,y,z+depth,radius-thick,a),ibt=radial(x,y,z+depth,radius-thick,b);
            out.quad(of,ot,it,in,color);out.quad(ob,ib,ibt,obt,color);
            out.quad(of,ob,obt,ot,shade(color,.64));out.quad(in,it,ibt,ib,shade(color,.8));
            out.quad(of,in,ib,ob,color);out.quad(ot,obt,ibt,it,color);
        }
    }
    private P radial(double x,double y,double z,double r,double a){return new P(x+Math.cos(a)*r,y+Math.sin(a)*r,z);}
    private int shade(int color,double n){return ((int)(((color>>16)&255)*n)<<16)|((int)(((color>>8)&255)*n)<<8)|(int)((color&255)*n);}
}
