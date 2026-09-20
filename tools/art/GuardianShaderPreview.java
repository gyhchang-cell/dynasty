import com.dynasty.GuanYuAvatarShape;
import com.dynasty.HouyiAvatarShape;
import com.dynasty.client.ImperialMeshNormals;
import java.awt.image.BufferedImage;
import java.nio.*;
import java.nio.file.*;
import javax.imageio.ImageIO;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import org.joml.Vector4f;
import org.lwjgl.BufferUtils;
import org.lwjgl.glfw.GLFW;
import org.lwjgl.glfw.GLFWErrorCallback;
import org.lwjgl.opengl.*;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.VertexFormat;

/** Actual production GLSL + real mesh rendered in a hidden native OpenGL context, not a Minecraft screenshot. */
public class GuardianShaderPreview {
  static int compile(int type,Path path)throws Exception {
    int shader=GL20.glCreateShader(type);GL20.glShaderSource(shader,Files.readString(path));GL20.glCompileShader(shader);
    if(GL20.glGetShaderi(shader,GL20.GL_COMPILE_STATUS)==0)throw new IllegalStateException(path+": "+GL20.glGetShaderInfoLog(shader));return shader;
  }
  static void matrix(int program,String name,Matrix4f value){FloatBuffer b=BufferUtils.createFloatBuffer(16);value.get(b);GL20.glUniformMatrix4fv(GL20.glGetUniformLocation(program,name),false,b);}
  static ImperialMeshNormals.Point point(HouyiAvatarShape.P p){return new ImperialMeshNormals.Point(p.x(),p.y(),p.z());}
  static void pack(BufferBuilder buffer,Matrix4f matrix,HouyiAvatarShape.P p,ImperialMeshNormals.Point n,HouyiAvatarShape.Material material) {
    buffer.vertex(matrix,(float)p.x(),(float)p.y(),(float)p.z()).color(material.r,material.g,material.b,1);
    buffer.normal((float)n.x(),(float)n.y(),(float)n.z());buffer.endVertex();
  }
  static void benchmarkPacking(java.util.List<HouyiAvatarShape.Face> mesh,java.util.List<ImperialMeshNormals.Normals> normals) {
    BufferBuilder buffer=new BufferBuilder(mesh.size()*6*24);Matrix4f matrix=new Matrix4f().rotateY(.52f);
    double[] times=new double[12];
    for(int frame=0;frame<17;frame++) {
      long start=System.nanoTime();buffer.begin(VertexFormat.Mode.TRIANGLES,DefaultVertexFormat.POSITION_COLOR_NORMAL);
      for(int i=0;i<mesh.size();i++){var f=mesh.get(i);var n=normals.get(i);pack(buffer,matrix,f.a(),n.a(),f.material());pack(buffer,matrix,f.b(),n.b(),f.material());pack(buffer,matrix,f.c(),n.c(),f.material());pack(buffer,matrix,f.a(),n.a(),f.material());pack(buffer,matrix,f.c(),n.c(),f.material());pack(buffer,matrix,f.d(),n.d(),f.material());}
      buffer.end().release();if(frame>=5)times[frame-5]=(System.nanoTime()-start)/1e6;
    }
    java.util.Arrays.sort(times);System.out.printf("One guardian CPU dynamic pack: median=%.3f ms, slowest=%.3f ms, %,d vertices/frame (native buffer, no per-face allocations)%n",times[6],times[11],mesh.size()*6);
  }
  static ByteBuffer capture(int vertices,int width,int height) {
    GL11.glClear(GL11.GL_COLOR_BUFFER_BIT|GL11.GL_DEPTH_BUFFER_BIT);GL11.glDrawArrays(GL11.GL_TRIANGLES,0,vertices);GL11.glFinish();
    ByteBuffer pixels=BufferUtils.createByteBuffer(width*height*4);GL11.glReadPixels(0,0,width,height,GL11.GL_RGBA,GL11.GL_UNSIGNED_BYTE,pixels);return pixels;
  }
  static void verifyInstanceTransforms(int program,FloatBuffer original,int width,int height,float playerYaw) {
    Matrix4f world=new Matrix4f().translation(.35f,-.15f,.3f).rotateY(playerYaw);
    Matrix4f pose=new Matrix4f().rotateX(.09f).rotateY(-.16f),worldPose=new Matrix4f(pose).mul(world);
    Matrix4f view=new Matrix4f().lookAt(-.65f,5.25f,23,-.65f,4.5f,0,0,1,0);
    matrix(program,"ModelViewMat",new Matrix4f(view).mul(worldPose));matrix(program,"WorldViewMat",new Matrix4f());matrix(program,"LightViewMat",new Matrix4f(world).invert());matrix(program,"LocalFromPosition",new Matrix4f());
    ByteBuffer cached=capture(original.limit()/10,width,height);
    FloatBuffer transformed=BufferUtils.createFloatBuffer(original.limit());
    for(int at=0;at<original.limit();at+=10) {
      Vector4f p=new Vector4f(original.get(at),original.get(at+1),original.get(at+2),1).mul(worldPose);
      Vector3f n=new Vector3f(original.get(at+7),original.get(at+8),original.get(at+9));world.transformDirection(n);
      transformed.put(p.x).put(p.y).put(p.z);for(int k=3;k<7;k++)transformed.put(original.get(at+k));transformed.put(n.x).put(n.y).put(n.z);
    }transformed.flip();GL15.glBufferData(GL15.GL_ARRAY_BUFFER,transformed,GL15.GL_STATIC_DRAW);
    matrix(program,"ModelViewMat",view);matrix(program,"WorldViewMat",pose);matrix(program,"LightViewMat",pose);matrix(program,"LocalFromPosition",new Matrix4f(worldPose).invert());
    ByteBuffer dynamic=capture(original.limit()/10,width,height);
    long sum=0;int mismatched=0;
    for(int at=0;at<cached.limit();at+=4){int largest=0;for(int k=0;k<3;k++){int delta=Math.abs((cached.get(at+k)&255)-(dynamic.get(at+k)&255));sum+=delta;largest=Math.max(largest,delta);}if(largest>12)mismatched++;}
    double mean=sum/(double)(width*height*3);
    System.out.printf("Cached/local vs streamed/world yaw=%.2f: mean RGB error=%.5f /255, edge-mismatch pixels=%d/%d%n",playerYaw,mean,mismatched,width*height);
    if(mean>.12||mismatched>width*height*.002)throw new IllegalStateException("VBO/world normal, texture or lighting basis mismatch");
    GL15.glBufferData(GL15.GL_ARRAY_BUFFER,original,GL15.GL_STATIC_DRAW);matrix(program,"WorldViewMat",new Matrix4f());matrix(program,"LightViewMat",new Matrix4f());matrix(program,"LocalFromPosition",new Matrix4f());
  }
  public static void main(String[] args)throws Exception {
    int width=960,height=1280;
    GLFWErrorCallback.createPrint(System.err).set();if(!GLFW.glfwInit())throw new IllegalStateException("GLFW unavailable");
    GLFW.glfwWindowHint(GLFW.GLFW_VISIBLE,GLFW.GLFW_FALSE);GLFW.glfwWindowHint(GLFW.GLFW_CONTEXT_VERSION_MAJOR,3);GLFW.glfwWindowHint(GLFW.GLFW_CONTEXT_VERSION_MINOR,2);
    GLFW.glfwWindowHint(GLFW.GLFW_OPENGL_PROFILE,GLFW.GLFW_OPENGL_CORE_PROFILE);GLFW.glfwWindowHint(GLFW.GLFW_OPENGL_FORWARD_COMPAT,GLFW.GLFW_TRUE);
    long window=GLFW.glfwCreateWindow(16,16,"Dynasty shader validation",0,0);if(window==0)throw new IllegalStateException("No hidden OpenGL context");
    GLFW.glfwMakeContextCurrent(window);GL.createCapabilities();
    Path shaders=Path.of("src/main/resources/assets/dynasty/shaders/core");int v=compile(GL20.GL_VERTEX_SHADER,shaders.resolve("imperial_material.vsh")),f=compile(GL20.GL_FRAGMENT_SHADER,shaders.resolve("imperial_material.fsh"));
    int program=GL20.glCreateProgram();GL20.glAttachShader(program,v);GL20.glAttachShader(program,f);GL20.glBindAttribLocation(program,0,"Position");GL20.glBindAttribLocation(program,1,"Color");GL20.glBindAttribLocation(program,2,"Normal");GL20.glLinkProgram(program);
    if(GL20.glGetProgrami(program,GL20.GL_LINK_STATUS)==0)throw new IllegalStateException(GL20.glGetProgramInfoLog(program));GL20.glUseProgram(program);
    int framebuffer=GL30.glGenFramebuffers();GL30.glBindFramebuffer(GL30.GL_FRAMEBUFFER,framebuffer);
    int color=GL11.glGenTextures();GL11.glBindTexture(GL11.GL_TEXTURE_2D,color);GL11.glTexImage2D(GL11.GL_TEXTURE_2D,0,GL11.GL_RGBA8,width,height,0,GL11.GL_RGBA,GL11.GL_UNSIGNED_BYTE,(ByteBuffer)null);GL11.glTexParameteri(GL11.GL_TEXTURE_2D,GL11.GL_TEXTURE_MIN_FILTER,GL11.GL_NEAREST);GL11.glTexParameteri(GL11.GL_TEXTURE_2D,GL11.GL_TEXTURE_MAG_FILTER,GL11.GL_NEAREST);GL30.glFramebufferTexture2D(GL30.GL_FRAMEBUFFER,GL30.GL_COLOR_ATTACHMENT0,GL11.GL_TEXTURE_2D,color,0);
    int depth=GL30.glGenRenderbuffers();GL30.glBindRenderbuffer(GL30.GL_RENDERBUFFER,depth);GL30.glRenderbufferStorage(GL30.GL_RENDERBUFFER,GL14.GL_DEPTH_COMPONENT24,width,height);GL30.glFramebufferRenderbuffer(GL30.GL_FRAMEBUFFER,GL30.GL_DEPTH_ATTACHMENT,GL30.GL_RENDERBUFFER,depth);
    if(GL30.glCheckFramebufferStatus(GL30.GL_FRAMEBUFFER)!=GL30.GL_FRAMEBUFFER_COMPLETE)throw new IllegalStateException("Incomplete framebuffer");
    var mesh=GuanYuAvatarShape.MESH;var normals=ImperialMeshNormals.build(mesh.stream().map(q->new ImperialMeshNormals.Quad(point(q.a()),point(q.b()),point(q.c()),point(q.d()),q.material().ordinal())).toList());
    benchmarkPacking(mesh,normals);
    FloatBuffer vertices=BufferUtils.createFloatBuffer(mesh.size()*6*10);
    for(int i=0;i<mesh.size();i++) {
      var face=mesh.get(i);var n=normals.get(i);var ps=new HouyiAvatarShape.P[]{face.a(),face.b(),face.c(),face.d()};var ns=new ImperialMeshNormals.Point[]{n.a(),n.b(),n.c(),n.d()};
      for(int corner:new int[]{0,1,2,0,2,3}) {var p=ps[corner];var nn=ns[corner];vertices.put((float)p.x()).put((float)p.y()).put((float)p.z());vertices.put(face.material().r).put(face.material().g).put(face.material().b).put(1);vertices.put((float)nn.x()).put((float)nn.y()).put((float)nn.z());}
    }vertices.flip();
    int vao=GL30.glGenVertexArrays();GL30.glBindVertexArray(vao);int buffer=GL15.glGenBuffers();GL15.glBindBuffer(GL15.GL_ARRAY_BUFFER,buffer);GL15.glBufferData(GL15.GL_ARRAY_BUFFER,vertices,GL15.GL_STATIC_DRAW);
    GL20.glEnableVertexAttribArray(0);GL20.glVertexAttribPointer(0,3,GL11.GL_FLOAT,false,40,0);GL20.glEnableVertexAttribArray(1);GL20.glVertexAttribPointer(1,4,GL11.GL_FLOAT,false,40,12);GL20.glEnableVertexAttribArray(2);GL20.glVertexAttribPointer(2,3,GL11.GL_FLOAT,false,40,28);
    matrix(program,"ProjMat",new Matrix4f().perspective((float)Math.toRadians(27),(float)width/height,.1f,100));matrix(program,"WorldViewMat",new Matrix4f());matrix(program,"LightViewMat",new Matrix4f());matrix(program,"LocalFromPosition",new Matrix4f());
    GL20.glUniform4f(GL20.glGetUniformLocation(program,"ColorModulator"),1,1,1,1);GL20.glUniform1f(GL20.glGetUniformLocation(program,"SceneLight"),1);GL20.glUniform1f(GL20.glGetUniformLocation(program,"FogStart"),90);GL20.glUniform1f(GL20.glGetUniformLocation(program,"FogEnd"),100);GL20.glUniform4f(GL20.glGetUniformLocation(program,"FogColor"),0,0,0,0);
    GL20.glUniform1f(GL20.glGetUniformLocation(program,"MeshOpacity"),1);
    GL11.glViewport(0,0,width,height);GL11.glEnable(GL11.GL_DEPTH_TEST);GL11.glDepthMask(true);GL11.glDisable(GL11.GL_BLEND);GL11.glDisable(GL11.GL_CULL_FACE);GL11.glClearColor(.045f,.054f,.061f,1);
    Path tile=args.length>1?Path.of(args[1]):Path.of("src/main/resources/assets/dynasty/textures/effect/guanyu_brocade.png");
    boolean hasTexture=Files.isRegularFile(tile);
    BufferedImage bitmap=hasTexture?ImageIO.read(tile.toFile()):new BufferedImage(1,1,BufferedImage.TYPE_INT_ARGB);
    int tw=bitmap.getWidth(),th=bitmap.getHeight();ByteBuffer texels=BufferUtils.createByteBuffer(tw*th*4);
    for(int y=0;y<th;y++)for(int x=0;x<tw;x++){int rgb=bitmap.getRGB(x,y);texels.put((byte)(rgb>>16)).put((byte)(rgb>>8)).put((byte)rgb).put((byte)255);}texels.flip();
    int brocade=GL11.glGenTextures();GL13.glActiveTexture(GL13.GL_TEXTURE0);GL11.glBindTexture(GL11.GL_TEXTURE_2D,brocade);GL11.glTexImage2D(GL11.GL_TEXTURE_2D,0,GL11.GL_RGBA8,tw,th,0,GL11.GL_RGBA,GL11.GL_UNSIGNED_BYTE,texels);
    GL11.glTexParameteri(GL11.GL_TEXTURE_2D,GL11.GL_TEXTURE_MIN_FILTER,GL11.GL_LINEAR);GL11.glTexParameteri(GL11.GL_TEXTURE_2D,GL11.GL_TEXTURE_MAG_FILTER,GL11.GL_LINEAR);GL11.glTexParameteri(GL11.GL_TEXTURE_2D,GL11.GL_TEXTURE_WRAP_S,GL12.GL_CLAMP_TO_EDGE);GL11.glTexParameteri(GL11.GL_TEXTURE_2D,GL11.GL_TEXTURE_WRAP_T,GL12.GL_CLAMP_TO_EDGE);
    GL20.glUniform1i(GL20.glGetUniformLocation(program,"Sampler0"),0);
    var robeA=HouyiAvatarShape.Material.CLOTH_GREEN;var robeB=HouyiAvatarShape.Material.EMERALD;
    GL20.glUniform3f(GL20.glGetUniformLocation(program,"RobeColorA"),robeA.r,robeA.g,robeA.b);GL20.glUniform3f(GL20.glGetUniformLocation(program,"RobeColorB"),robeB.r,robeB.g,robeB.b);
    GL20.glUniform1f(GL20.glGetUniformLocation(program,"MaterialMode"),hasTexture?1:0);
    for(float playerYaw:new float[]{.71f,-1.31f,2.4f})verifyInstanceTransforms(program,vertices,width,height,playerYaw);
    String stem=args.length>0?args[0]:"build/imperial-mesh-preview/guanyu-opengl";
    for(boolean textured:new boolean[]{false,true}) {
      if(textured&&!hasTexture)continue;
      GL20.glUniform1f(GL20.glGetUniformLocation(program,"MaterialMode"),textured?1:0);
      for(int yaw:new int[]{0,35,90,180}) {
      double angle=Math.toRadians(yaw);matrix(program,"ModelViewMat",new Matrix4f().lookAt((float)(-.65+23*Math.sin(angle)),5.25f,(float)(23*Math.cos(angle)),-.65f,4.5f,0,0,1,0));
      GL11.glClear(GL11.GL_COLOR_BUFFER_BIT|GL11.GL_DEPTH_BUFFER_BIT);GL11.glDrawArrays(GL11.GL_TRIANGLES,0,mesh.size()*6);GL11.glFinish();
      ByteBuffer pixels=BufferUtils.createByteBuffer(width*height*4);GL11.glReadPixels(0,0,width,height,GL11.GL_RGBA,GL11.GL_UNSIGNED_BYTE,pixels);
      BufferedImage image=new BufferedImage(width,height,BufferedImage.TYPE_INT_ARGB);for(int y=0;y<height;y++)for(int x=0;x<width;x++){int at=((height-1-y)*width+x)*4;int r=pixels.get(at)&255,g=pixels.get(at+1)&255,b=pixels.get(at+2)&255;image.setRGB(x,y,0xff000000|(r<<16)|(g<<8)|b);}
      Path output=Path.of(stem+(textured?"-after":"-before")+"-"+yaw+".png");Files.createDirectories(output.getParent());ImageIO.write(image,"PNG",output.toFile());System.out.println("Actual production OpenGL shader render: "+output);
      }
    }
    long gpuStart=System.nanoTime();
    for(int frame=0;frame<20;frame++){GL11.glClear(GL11.GL_COLOR_BUFFER_BIT|GL11.GL_DEPTH_BUFFER_BIT);GL11.glDrawArrays(GL11.GL_TRIANGLES,0,mesh.size()*6);GL11.glFinish();}
    System.out.printf("One guardian cached GPU draw+finish: %.3f ms/frame at %dx%d, includes shaded/texture fragments and depth%n",(System.nanoTime()-gpuStart)/20e6,width,height);
    int error=GL11.glGetError();if(error!=GL11.GL_NO_ERROR)throw new IllegalStateException("OpenGL error "+error);
    GLFW.glfwDestroyWindow(window);GLFW.glfwTerminate();
  }
}
