package com.dynasty;

/** Shared deterministic five-segment lag: no entities or physics chain per thread of silk. */
public final class WhiskPose {
    public static final int SEGMENTS=5;
    public static float bend(double age,int windup,int segment){
        if(segment<0||segment>=SEGMENTS||!Double.isFinite(age)||age<0||age>windup+16)return 0;
        double delayed=age-segment*1.2;
        if(delayed<0)return 0;
        double charge=Math.min(1,delayed/Math.max(1,windup));
        double recoil=delayed<windup?0:Math.sin(Math.min(Math.PI,(delayed-windup)*Math.PI/12))*Math.exp(-(delayed-windup)/9);
        double recovery=delayed<=windup?1:Math.max(0,1-(delayed-windup)/12);
        return (float)(-.11*charge*recovery+.48*recoil);
    }
    private WhiskPose(){}
}
