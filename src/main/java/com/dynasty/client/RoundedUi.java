package com.dynasty.client;
import net.minecraft.client.gui.GuiGraphics;
/** Rounded geometry in logical GUI pixels; no external UI library or shader. */
public final class RoundedUi {
 public static void fill(GuiGraphics g,int x,int y,int w,int h,int r,int color){
  r=Math.max(0,Math.min(r,Math.min(w,h)/2));
  for(int row=0;row<h;row++){double dy=row<r?r-row-.5:row>=h-r?row-(h-r)+.5:0;int inset=dy==0?0:(int)Math.ceil(r-Math.sqrt(Math.max(0,r*r-dy*dy)));g.fill(x+inset,y+row,x+w-inset,y+row+1,color);}
 }
 private RoundedUi(){}
}
