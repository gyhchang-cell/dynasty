#!/usr/bin/env node
/** Import two generated skin atlases and preview the real HumanoidModel UVs.
 * Requires sharp (NODE_PATH may point to an installed package directory).
 * prepare OUTPUT: exports only the two reviewed textures to OUTPUT.
 * render INPUT OUTPUT INFLATION YAW: CPU rasterization, no AI model mock-up.
 * Model geometry/UVs follow Forge 1.20.1 HumanoidModel.createMesh and ModelPart.Cube.
 */
const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const ROOT = path.resolve(__dirname, '../..');
const ART = path.join(ROOT, 'docs/art/entity-batch-01');

function faceRects(u,v,w,h,d) {
  return {
    top:[u+d,v,w,d], bottom:[u+d+w,v,w,d],
    west:[u,v+d,d,h], front:[u+d,v+d,w,h],
    east:[u+d+w,v+d,d,h], back:[u+d+w+d,v+d,w,h],
  };
}
const UV = {
  head:faceRects(0,0,8,8,8), body:faceRects(16,16,8,12,4),
  arm:faceRects(40,16,4,12,4), leg:faceRects(0,16,4,12,4),
};

async function prepare(destination) {
  fs.mkdirSync(destination,{recursive:true});
  for (const name of ['terracotta_warrior','royal_guard']) {
    const {data} = await sharp(path.join(ART,'sources',name+'.png'))
      .resize(128,128,{fit:'fill',kernel:'nearest'}).ensureAlpha().raw().toBuffer({resolveWithObject:true});
    const out = Buffer.alloc(128*128*4);
    // Re-register the generated guard's head, shifted two logical pixels to the right.
    // Underside caps are sampled from corresponding chin/sole/palm strips.
    const sourceOverride = {
      'head.bottom':name==='royal_guard'?[18,2,6,6]:[8,15,8,1],
      'arm.bottom':[44,31,4,1], 'leg.bottom':[4,31,4,1],
    };
    if(name==='royal_guard') Object.assign(sourceOverride,{
      'head.top':[10,0,8,8], 'head.front':[10,8,8,8],
      'head.west':[0,8,10,8], 'head.east':[18,8,6,8],
    });
    let filled=0;
    for(const [part,faces] of Object.entries(UV)) for(const [face,rect] of Object.entries(faces)) {
      const src=sourceOverride[part+'.'+face]||rect;
      const [sx,sy,sw,sh]=src.map(n=>n*2), [dx,dy,dw,dh]=rect.map(n=>n*2);
      const opaque=[];
      for(let y=sy;y<sy+sh;y++) for(let x=sx;x<sx+sw;x++) {
        const i=(y*128+x)*4;
        if(data[i+3]>=128) opaque.push({x,y,i});
      }
      if(!opaque.length) throw Error(name+' empty source face '+part+'.'+face);
      for(let y=0;y<dh;y++) for(let x=0;x<dw;x++) {
        const ax=sx+Math.min(sw-1,Math.floor((x+.5)*sw/dw));
        const ay=sy+Math.min(sh-1,Math.floor((y+.5)*sh/dh));
        let i=(ay*128+ax)*4;
        if(data[i+3]<128) {
          // Nearest-edge extension inside this face only: closes sampling cracks at UV seams.
          let best=null, dist=Infinity;
          for(const q of opaque){const t=(q.x-ax)**2+(q.y-ay)**2;if(t<dist){best=q;dist=t;}}
          i=best.i; filled++;
        }
        const j=((dy+y)*128+dx+x)*4;
        out[j]=data[i];out[j+1]=data[i+1];out[j+2]=data[i+2];out[j+3]=255;
      }
    }
    // Unused regions including all of the hat overlay stay alpha=0.
    for(const faces of Object.values(UV)) for(const [x,y,w,h] of Object.values(faces))
      for(let v=y*2;v<(y+h)*2;v++) for(let u=x*2;u<(x+w)*2;u++)
        if(out[(v*128+u)*4+3]!==255) throw Error('Hole in base UV');
    await sharp(out,{raw:{width:128,height:128,channels:4}}).png().toFile(path.join(destination,name+'.png'));
    console.log(name+': 128x128 RGBA, all 24 base faces opaque; extended '+filled+' edge pixels.');
  }
}

function mesh(inflate) {
  // Dimensions and poses are the actual definitions in HumanoidModel.createMesh.
  return [
    {p:[-4,-8,-4],s:[8,8,8],uv:[0,0],i:inflate},
    {p:[-4,-8,-4],s:[8,8,8],uv:[32,0],i:inflate+.5},
    {p:[-4,0,-2],s:[8,12,4],uv:[16,16],i:inflate},
    {p:[-8,0,-2],s:[4,12,4],uv:[40,16],i:inflate},
    {p:[4,0,-2],s:[4,12,4],uv:[40,16],i:inflate,mirror:true},
    {p:[-3.9,12,-2],s:[4,12,4],uv:[0,16],i:inflate},
    {p:[-.1,12,-2],s:[4,12,4],uv:[0,16],i:inflate,mirror:true},
  ];
}

async function render(input,output,inflation=0,yaw=-.40) {
  const {data,info}=await sharp(input).ensureAlpha().raw().toBuffer({resolveWithObject:true});
  const W=360,H=470,scale=12,pitch=.13;
  const rgb=Buffer.alloc(W*H*4),depth=new Float64Array(W*H).fill(Infinity);
  for(let i=0;i<W*H;i++){rgb[i*4]=48;rgb[i*4+1]=52;rgb[i*4+2]=63;rgb[i*4+3]=255;}
  function project([x,y,z]) {
    const X=x*Math.cos(yaw)-z*Math.sin(yaw), Z=x*Math.sin(yaw)+z*Math.cos(yaw);
    const Y=(y-8)*Math.cos(pitch)-Z*Math.sin(pitch);
    return [W/2+X*scale,H/2+Y*scale,(y-8)*Math.sin(pitch)+Z*Math.cos(pitch)];
  }
  function triangle(a,b,c,shade) {
    const edge=(a,b,x,y)=>(x-a[0])*(b[1]-a[1])-(y-a[1])*(b[0]-a[0]);
    const area=edge(a,b,c[0],c[1]);if(Math.abs(area)<1e-8)return;
    const x0=Math.max(0,Math.floor(Math.min(a[0],b[0],c[0]))), x1=Math.min(W-1,Math.ceil(Math.max(a[0],b[0],c[0])));
    const y0=Math.max(0,Math.floor(Math.min(a[1],b[1],c[1]))), y1=Math.min(H-1,Math.ceil(Math.max(a[1],b[1],c[1])));
    for(let y=y0;y<=y1;y++) for(let x=x0;x<=x1;x++) {
      const wa=edge(b,c,x+.5,y+.5)/area,wb=edge(c,a,x+.5,y+.5)/area,wc=1-wa-wb;
      if(wa< -1e-8||wb< -1e-8||wc< -1e-8)continue;
      const z=wa*a[2]+wb*b[2]+wc*c[2],idx=y*W+x;if(z>=depth[idx])continue;
      const u=(wa*a[3]+wb*b[3]+wc*c[3])/64,v=(wa*a[4]+wb*b[4]+wc*c[4])/64;
      const tx=Math.max(0,Math.min(info.width-1,Math.floor(u*info.width)));
      const ty=Math.max(0,Math.min(info.height-1,Math.floor(v*info.height)));
      const k=(ty*info.width+tx)*4;if(data[k+3]<128)continue;
      for(let n=0;n<3;n++)rgb[idx*4+n]=Math.round(data[k+n]*shade);
      depth[idx]=z;
    }
  }
  for(const box of mesh(inflation)) {
    const [w,h,d]=box.s,[u,v]=box.uv;
    let [x0,y0,z0]=box.p.map(n=>n-box.i);
    let [x1,y1,z1]=box.p.map((n,j)=>n+box.s[j]+box.i);
    if(box.mirror)[x0,x1]=[x1,x0];
    const pts=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],
               [x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]];
    // Vertex order and UV remapping match ModelPart.Cube/Polygon (including mirrored limbs).
    const faces=[
      [[5,4,0,1],[u+d,v,u+d+w,v+d],1.0],
      [[2,3,7,6],[u+d+w,v+d,u+d+2*w,v],.75],
      [[0,4,7,3],[u,v+d,u+d,v+d+h],.83],
      [[1,0,3,2],[u+d,v+d,u+d+w,v+d+h],1.0],
      [[5,1,2,6],[u+d+w,v+d,u+2*d+w,v+d+h],.90],
      [[4,5,6,7],[u+2*d+w,v+d,u+2*d+2*w,v+d+h],.90],
    ];
    for(const [ids,r,shade] of faces) {
      const [a,b,c,e]=r,uv=[[c,b],[a,b],[a,e],[c,e]];
      const q=ids.map((idx,j)=>[...project(pts[idx]),...uv[j]]);
      triangle(q[0],q[1],q[2],shade);triangle(q[0],q[2],q[3],shade);
    }
  }
  fs.mkdirSync(path.dirname(output),{recursive:true});
  await sharp(rgb,{raw:{width:W,height:H,channels:4}}).png().toFile(output);
}

async function main(){
  const [cmd,...args]=process.argv.slice(2);
  if(cmd==='prepare'&&args[0])return prepare(path.resolve(args[0]));
  if(cmd==='render'&&args[0]&&args[1])return render(args[0],args[1],Number(args[2]||0),Number(args[3]||-.40));
  throw Error('Usage: entity_batch_01.cjs prepare OUTPUT | render INPUT OUTPUT INFLATION YAW');
}
main().catch(e=>{console.error(e);process.exitCode=1;});
