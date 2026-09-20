'use strict';
// No remote dependencies. This viewer consumes only the exact runtime mesh exporter schema.
const $=s=>document.querySelector(s), canvas=$('#canvas'), status=$('#status');
window.addEventListener('error',e=>{$('#error').textContent=`预览渲染出错：${e.message}`;});
const params=new URLSearchParams(location.search);
const gl=canvas.getContext('webgl2',{antialias:true,alpha:false,preserveDrawingBuffer:true});
if(!gl) throw new Error('This preview requires WebGL 2.');
const V={add:(a,b)=>a.map((v,i)=>v+b[i]),sub:(a,b)=>a.map((v,i)=>v-b[i]),scale:(a,t)=>a.map(v=>v*t),dot:(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),cross:(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]};
V.unit=a=>V.scale(a,1/Math.max(1e-12,Math.hypot(...a)));
function mul(a,b){let o=new Float32Array(16);for(let c=0;c<4;c++)for(let r=0;r<4;r++)for(let k=0;k<4;k++)o[c*4+r]+=a[k*4+r]*b[c*4+k];return o;}
function lookAt(eye,target,up=[0,1,0]){const z=V.unit(V.sub(eye,target)),x=V.unit(V.cross(up,z)),y=V.cross(z,x);return new Float32Array([x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-V.dot(x,eye),-V.dot(y,eye),-V.dot(z,eye),1]);}
function perspective(fov,aspect,near,far){const f=1/Math.tan(fov/2);return new Float32Array([f/aspect,0,0,0,0,f,0,0,0,0,(far+near)/(near-far),-1,0,0,2*far*near/(near-far),0]);}
function ortho(l,r,b,t,n,f){return new Float32Array([2/(r-l),0,0,0,0,2/(t-b),0,0,0,0,-2/(f-n),0,-(r+l)/(r-l),-(t+b)/(t-b),-(f+n)/(f-n),1]);}
function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));return s;}
function program(v,f){const p=gl.createProgram();gl.attachShader(p,shader(gl.VERTEX_SHADER,v));gl.attachShader(p,shader(gl.FRAGMENT_SHADER,f));gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(p));return p;}
const vertex=`#version 300 es
precision highp float;
layout(location=0) in vec3 position;layout(location=1) in vec3 normal;layout(location=2) in vec3 color;layout(location=3) in vec3 material;
uniform mat4 viewProjection;uniform mat4 shadowMatrix;
out vec3 vPosition;out vec3 vNormal;out vec3 vColor;out vec3 vMaterial;out vec4 vShadow;
void main(){vPosition=position;vNormal=normal;vColor=color;vMaterial=material;vShadow=shadowMatrix*vec4(position,1.0);gl_Position=viewProjection*vec4(position,1.0);}`;
const fragment=`#version 300 es
precision highp float;
in vec3 vPosition;in vec3 vNormal;in vec3 vColor;in vec3 vMaterial;in vec4 vShadow;
uniform vec3 eye;uniform sampler2D shadowMap;uniform float clipY;uniform float floorY;uniform float modelHeight;uniform bool debugNormals;uniform bool studio;uniform bool ground;
out vec4 outputColor;
float visibility(vec3 n,vec3 light){vec3 q=vShadow.xyz/vShadow.w*.5+.5;if(q.x<0.0||q.x>1.0||q.y<0.0||q.y>1.0||q.z>1.0)return 1.0;float sum=0.0;float bias=max(.0004,.0017*(1.0-dot(n,light)));for(int x=-1;x<=1;x++)for(int y=-1;y<=1;y++){float d=texture(shadowMap,q.xy+vec2(x,y)/1536.0).r;sum+=q.z-bias<=d?1.0:.24;}return sum/9.0;}
void main(){
 if(!ground&&vPosition.y>clipY)discard;
 vec3 N=normalize(vNormal),view=normalize(eye-vPosition);if(dot(N,view)<0.0)N=-N;
 if(debugNormals&&!ground){outputColor=vec4(N*.5+.5,1);return;}
 vec3 key=normalize(vec3(-.45,.8,.6)),fill=normalize(vec3(.7,.35,-.45));
 if(!studio&&!ground){
  float warm=smoothstep(.09,.27,vColor.r-vColor.b)*smoothstep(.23,.55,vColor.g);
  float pale=smoothstep(.66,.86,min(vColor.r,min(vColor.g,vColor.b)));
  float metal=max(warm,pale*.55);
  float diffuse=.28+.64*max(0.0,dot(N,key))+.16*max(0.0,dot(N,fill));
  float highlight=pow(max(0.0,dot(N,normalize(key+view))),mix(26.,80.,metal));
  float rim=pow(1.-max(0.,dot(N,view)),3.);
  vec3 light=vColor*diffuse+mix(vec3(.8,.88,1.),vec3(1.,.87,.64),metal)*highlight*mix(.055,.42,metal);
  light+=vColor*vec3(.13,.17,.20)*rim;
  outputColor=vec4(clamp(light,0.,1.),1.);return;
 }
 vec3 base=pow(vColor,vec3(2.2));float metal=vMaterial.x,rough=vMaterial.y,emission=vMaterial.z;
 float shadow=studio?visibility(N,key):1.0;
 float k=max(0.0,dot(N,key)),f=max(0.0,dot(N,fill));
 vec3 shade=base*(vec3(.38)+vec3(.94,.84,.68)*k*shadow+vec3(.25,.35,.48)*f);
 vec3 halfV=normalize(key+view);float shine=pow(max(0.0,dot(N,halfV)),mix(95.0,13.0,rough));
 vec3 specColor=mix(vec3(.06),base*.75+vec3(.14),metal);
 if(studio)shade+=specColor*shine*.60*shadow;
 float rim=pow(1.0-abs(dot(N,view)),3.0);
 shade+=vec3(.07,.10,.12)*rim*(.3+.7*max(0.0,N.y));
 shade+=base*emission*.55;
 if(ground){float coordScale=modelHeight*.20;vec2 uv=vPosition.xz/coordScale;vec2 grid=abs(fract(uv-.5)-.5)/fwidth(uv);float line=1.0-min(min(grid.x,grid.y),1.0);shade=mix(shade,shade*1.30,line*.22);float fade=clamp(length(vPosition.xz)/modelHeight/2.7,0.,1.);shade=mix(shade,vec3(.026,.036,.052),fade);}
 shade=shade/(shade+vec3(.78));outputColor=vec4(pow(max(shade,vec3(0)),vec3(1.0/2.2)),1);
}`;
const mainProgram=program(vertex,fragment);
const depthProgram=program(`#version 300 es
precision highp float;layout(location=0) in vec3 position;uniform mat4 viewProjection;out float height;void main(){height=position.y;gl_Position=viewProjection*vec4(position,1.0);}`,`#version 300 es
precision highp float;in float height;uniform float clipY;out vec4 color;void main(){if(height>clipY)discard;color=vec4(1);}`);
function uniforms(p,names){return Object.fromEntries(names.map(n=>[n,gl.getUniformLocation(p,n)]));}
const mainU=uniforms(mainProgram,['viewProjection','shadowMatrix','eye','shadowMap','clipY','floorY','modelHeight','debugNormals','studio','ground']);
const depthU=uniforms(depthProgram,['viewProjection','clipY']);
const depthTexture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,depthTexture);gl.texImage2D(gl.TEXTURE_2D,0,gl.DEPTH_COMPONENT24,1536,1536,0,gl.DEPTH_COMPONENT,gl.UNSIGNED_INT,null);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
const depthFramebuffer=gl.createFramebuffer();gl.bindFramebuffer(gl.FRAMEBUFFER,depthFramebuffer);gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.DEPTH_ATTACHMENT,gl.TEXTURE_2D,depthTexture,0);gl.drawBuffers([gl.NONE]);gl.readBuffer(gl.NONE);if(gl.checkFramebufferStatus(gl.FRAMEBUFFER)!==gl.FRAMEBUFFER_COMPLETE)throw new Error('Shadow depth framebuffer is incomplete');gl.bindFramebuffer(gl.FRAMEBUFFER,null);
function geometry(values){const vao=gl.createVertexArray();gl.bindVertexArray(vao);const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(values),gl.STATIC_DRAW);for(let i=0;i<4;i++){gl.enableVertexAttribArray(i);gl.vertexAttribPointer(i,3,gl.FLOAT,false,48,i*12);}gl.bindVertexArray(null);return {vao,buffer,count:values.length/12};}
function prepare(model){const d=[];for(let f=0;f<model.materialIndices.length;f++){const m=model.materials[model.materialIndices[f]];for(const v of [0,1,2,0,2,3]){const o=f*12+v*3;d.push(...model.positions.slice(o,o+3),...model.normals.slice(o,o+3),...m.rgb,m.metalness,m.roughness,m.emission);}}model.gpu=geometry(d);return model;}
let models,model,groundMesh,center,height,distance,yaw=.32,pitch=.10,viewMode=params.get('view')||'threequarter',isNormals=false,isStudio=params.get('lighting')==='studio',dirty=true,drag=null;
function updateLabels(){const panel=$('#panels');panel.className=viewMode==='four'?'':'single';panel.innerHTML=(viewMode==='four'?['正面 FRONT','右侧 SIDE','背面 BACK','四分之三 THREE-QUARTER']:[viewMode==='portrait'?'头部细节 · 检查比例 / 遮挡':'实际运行时网格 · 可拖动旋转']).map(x=>`<span>${x}</span>`).join('');document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===viewMode));}
function selectModel(id){model=models.find(m=>m.id===id)||models[0];$('#model').value=model.id;const b=model.bounds;height=b.max[1]-b.min[1];center=b.min.map((v,i)=>(v+b.max[i])/2);distance=Math.max(height,b.max[0]-b.min[0])*1.80;const y=b.min[1]-.025*height,s=height*5;const g=[];for(const p of [[-s,y,-s],[-s,y,s],[s,y,s],[-s,y,-s],[s,y,s],[s,y,-s]])g.push(...p,0,1,0,.13,.17,.22,0,.96,0);if(groundMesh){gl.deleteBuffer(groundMesh.buffer);gl.deleteVertexArray(groundMesh.vao);}groundMesh=geometry(g);setView(viewMode);status.textContent=`${model.name}   |   ${model.qa.quads.toLocaleString()} 四边面   |   有限顶点检查通过\n摄影棚预览只用于检查实际几何；游戏中的光照、法阵及动态表现需另行验证。`;document.title=`${model.name} · Dynasty 真实网格检视`;dirty=true;}
function setView(name){viewMode=name;const presets={front:[0,0],side:[Math.PI/2,0],back:[Math.PI,0],threequarter:[.43,.10],portrait:[.12,.03],four:[.30,.08]};[yaw,pitch]=presets[name]||presets.threequarter;distance=Math.max(height,model.bounds.max[0]-model.bounds.min[0])*(name==='portrait'?(model.id.endsWith('_dragon')?.95:.73):1.80);updateLabels();dirty=true;}
function camera(w,h,override){const y=override?override[0]:yaw,p=override?override[1]:pitch;let target=[...center],dist=distance;if(viewMode==='portrait')target[1]=model.bounds.min[1]+height*(model.id.endsWith('_dragon')?.73:.82);const e=V.add(target,[Math.sin(y)*Math.cos(p)*dist,Math.sin(p)*dist,Math.cos(y)*Math.cos(p)*dist]);return {eye:e,matrix:mul(perspective(.57,w/h,height*.004,height*25),lookAt(e,target))};}
function drawGeo(g){gl.bindVertexArray(g.vao);gl.drawArrays(gl.TRIANGLES,0,g.count);}
function render(){if(!model||!dirty)return;dirty=false;const dpr=Math.min(devicePixelRatio||1,2),width=Math.floor(canvas.clientWidth*dpr),h=Math.floor(canvas.clientHeight*dpr);if(canvas.width!==width||canvas.height!==h){canvas.width=width;canvas.height=h;}const clip=model.bounds.min[1]+height*Number($('#formed').value)+.0001;const lightEye=V.add(center,V.scale(V.unit([-.45,.8,.6]),height*3));const shadowMatrix=mul(ortho(-height,height,-height,height,height*.01,height*8),lookAt(lightEye,center));
 gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);gl.depthMask(true);gl.disable(gl.BLEND);gl.disable(gl.CULL_FACE);gl.disable(gl.SCISSOR_TEST);
 gl.bindFramebuffer(gl.FRAMEBUFFER,depthFramebuffer);gl.viewport(0,0,1536,1536);gl.clear(gl.DEPTH_BUFFER_BIT);gl.useProgram(depthProgram);gl.uniformMatrix4fv(depthU.viewProjection,false,shadowMatrix);gl.uniform1f(depthU.clipY,clip);drawGeo(model.gpu);gl.bindFramebuffer(gl.FRAMEBUFFER,null);
 gl.useProgram(mainProgram);gl.uniformMatrix4fv(mainU.shadowMatrix,false,shadowMatrix);gl.uniform1f(mainU.clipY,clip);gl.uniform1f(mainU.floorY,model.bounds.min[1]);gl.uniform1f(mainU.modelHeight,height);gl.uniform1i(mainU.debugNormals,isNormals);gl.uniform1i(mainU.studio,isStudio);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,depthTexture);gl.uniform1i(mainU.shadowMap,0);
 const panes=viewMode==='four'?[[0,h/2,width/2,h/2,[0,.02]],[width/2,h/2,width/2,h/2,[Math.PI/2,.02]],[0,0,width/2,h/2,[Math.PI,.02]],[width/2,0,width/2,h/2,[.50,.12]]]:[[0,0,width,h,null]];
 gl.enable(gl.SCISSOR_TEST);for(const [x,y,w,ph,angle]of panes){gl.viewport(x,y,w,ph);gl.scissor(x,y,w,ph);gl.clearColor(.055,.075,.103,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);const cam=camera(w,ph,angle);gl.uniformMatrix4fv(mainU.viewProjection,false,cam.matrix);gl.uniform3fv(mainU.eye,cam.eye);gl.uniform1i(mainU.ground,1);drawGeo(groundMesh);gl.uniform1i(mainU.ground,0);drawGeo(model.gpu);}gl.disable(gl.SCISSOR_TEST);gl.bindVertexArray(null);window.imperialPreviewReady=true;
}
function frame(){try{render();}catch(e){$('#error').textContent=e.stack;}requestAnimationFrame(frame);}requestAnimationFrame(frame);
window.addEventListener('resize',()=>dirty=true);
$('#model').addEventListener('change',e=>selectModel(e.target.value));document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>setView(b.dataset.view));$('#formed').oninput=()=>dirty=true;$('#normals').onclick=()=>{isNormals=!isNormals;$('#normals').classList.toggle('active',isNormals);dirty=true;};$('#lighting').textContent=isStudio?'摄影棚灯光':'游戏材质预览';$('#lighting').onclick=()=>{isStudio=!isStudio;$('#lighting').textContent=isStudio?'摄影棚灯光':'游戏材质预览';dirty=true;};
canvas.onpointerdown=e=>{drag={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);};canvas.onpointermove=e=>{if(!drag)return;if(viewMode==='four'){setView('threequarter');}yaw+=(e.clientX-drag.x)*.007;pitch=Math.max(-1.25,Math.min(1.25,pitch+(e.clientY-drag.y)*.006));drag={x:e.clientX,y:e.clientY};dirty=true;};canvas.onpointerup=()=>drag=null;canvas.onpointercancel=()=>drag=null;canvas.onwheel=e=>{e.preventDefault();distance=Math.max(height*.2,Math.min(height*8,distance*Math.exp(e.deltaY*.001)));dirty=true;};canvas.ondblclick=()=>setView('threequarter');
(async()=>{try{const url=params.get('data')||'../../build/imperial-mesh-preview/after/meshes.json';const response=await fetch(url,{cache:'no-store'});if(!response.ok)throw new Error(`Mesh JSON ${response.status}: ${url}`);const data=await response.json();if(data.schema!==1)throw new Error('Unsupported mesh JSON schema');models=data.models.map(prepare);selectModel(params.get('model')||'guanyu');}catch(e){$('#error').textContent=`无法加载模型。请先导出网格，再从项目根目录启动本地静态服务器。\n${e.stack}`;status.textContent='';}})();
