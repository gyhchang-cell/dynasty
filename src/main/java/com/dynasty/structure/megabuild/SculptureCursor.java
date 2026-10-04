package com.dynasty.structure.megabuild;

/** Chunk-major iterator; each returned cell remains in one world chunk until that tile is finished. */
public final class SculptureCursor {
    public final int originX,originY,originZ,width,height,length,firstChunkX,firstChunkZ,chunksX,chunksZ;
    public int chunk,cell;
    public SculptureCursor(int x,int y,int z,int width,int height,int length){
        originX=x;originY=y;originZ=z;this.width=width;this.height=height;this.length=length;
        firstChunkX=Math.floorDiv(x,16);firstChunkZ=Math.floorDiv(z,16);
        chunksX=Math.floorDiv(x+width-1,16)-firstChunkX+1;chunksZ=Math.floorDiv(z+length-1,16)-firstChunkZ+1;
    }
    public boolean done(){return chunk>=chunksX*chunksZ;}
    public int chunkX(){return firstChunkX+chunk%chunksX;}
    public int chunkZ(){return firstChunkZ+chunk/chunksX;}
    private int minX(){return Math.max(originX,chunkX()*16);}
    private int minZ(){return Math.max(originZ,chunkZ()*16);}
    private int spanX(){return Math.min(originX+width,chunkX()*16+16)-minX();}
    private int spanZ(){return Math.min(originZ+length,chunkZ()*16+16)-minZ();}
    public int x(){return minX()+(cell/height)%spanX();}
    public int y(){return originY+cell%height;}
    public int z(){return minZ()+cell/(height*spanX());}
    public void next(){if(++cell>=height*spanX()*spanZ()){cell=0;chunk++;}}
    public boolean valid(){return chunk>=0&&chunk<=chunksX*chunksZ&&cell>=0&&(done()?cell==0:cell<height*spanX()*spanZ());}
    public double progress(){return Math.min(1,(chunk+(done()?0:(double)cell/(height*spanX()*spanZ())))/(chunksX*chunksZ));}
}
