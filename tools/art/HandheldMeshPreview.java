import com.google.gson.*;
import org.lwjgl.glfw.GLFW;
import org.lwjgl.opengl.*;
import org.lwjgl.BufferUtils;
import org.joml.Matrix4f;
import java.nio.*;
import java.nio.file.*;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.util.*;

/** Hidden-context render of shipped JSON geometry, not a Minecraft gameplay screenshot. */
public class HandheldMeshPreview {
    static final int W=480,H=640;
    static int shader(int type,String source){int id=GL20.glCreateShader(type);GL20.glShaderSource(id,source);GL20.glCompileShader(id);if(GL20.glGetShaderi(id,GL20.GL_COMPILE_STATUS)==0)throw new IllegalStateException(GL20.glGetShaderInfoLog(id));return id;}
    static float[] numbers(JsonArray a){float[] out=new float[a.size()];for(int i=0;i<out.length;i++)out[i]=a.get(i).getAsFloat();return out;}
    static FloatBuffer mesh(JsonObject model){
        List<float[]> vertices=new ArrayList<>();
        for(var raw:model.getAsJsonArray("elements")){
            var e=raw.getAsJsonObject();float[] a=numbers(e.getAsJsonArray("from")),b=numbers(e.getAsJsonArray("to"));
            for(var f:e.getAsJsonObject("faces").entrySet()){
                float[][] p=switch(f.getKey()){
                    case "north" -> new float[][]{{b[0],b[1],a[2]},{b[0],a[1],a[2]},{a[0],a[1],a[2]},{a[0],b[1],a[2]}};
                    case "south" -> new float[][]{{a[0],b[1],b[2]},{a[0],a[1],b[2]},{b[0],a[1],b[2]},{b[0],b[1],b[2]}};
                    case "west" -> new float[][]{{a[0],b[1],a[2]},{a[0],a[1],a[2]},{a[0],a[1],b[2]},{a[0],b[1],b[2]}};
                    case "east" -> new float[][]{{b[0],b[1],b[2]},{b[0],a[1],b[2]},{b[0],a[1],a[2]},{b[0],b[1],a[2]}};
                    case "up" -> new float[][]{{a[0],b[1],a[2]},{a[0],b[1],b[2]},{b[0],b[1],b[2]},{b[0],b[1],a[2]}};
                    default -> new float[][]{{a[0],a[1],b[2]},{a[0],a[1],a[2]},{b[0],a[1],a[2]},{b[0],a[1],b[2]}};
                };
                float[] uv=numbers(f.getValue().getAsJsonObject().getAsJsonArray("uv"));
                float[][] tex={{uv[0]/16,uv[1]/16},{uv[0]/16,uv[3]/16},{uv[2]/16,uv[3]/16},{uv[2]/16,uv[1]/16}};
                for(int i:new int[]{0,1,2,0,2,3})vertices.add(new float[]{p[i][0]-8,p[i][1]-8,p[i][2]-8,tex[i][0],tex[i][1]});
            }
        }
        var data=BufferUtils.createFloatBuffer(vertices.size()*5);for(float[] v:vertices)data.put(v);return data.flip();
    }
    public static void main(String[] args)throws Exception{
        // No visible window, no mouse/keyboard callbacks, no Minecraft process interaction.
        GLFW.glfwInitHint(GLFW.GLFW_COCOA_MENUBAR,GLFW.GLFW_FALSE);
        if(!GLFW.glfwInit())throw new IllegalStateException("GLFW init failed");
        GLFW.glfwWindowHint(GLFW.GLFW_VISIBLE,GLFW.GLFW_FALSE);GLFW.glfwWindowHint(GLFW.GLFW_FOCUSED,GLFW.GLFW_FALSE);
        GLFW.glfwWindowHint(GLFW.GLFW_CONTEXT_VERSION_MAJOR,3);GLFW.glfwWindowHint(GLFW.GLFW_CONTEXT_VERSION_MINOR,2);
        GLFW.glfwWindowHint(GLFW.GLFW_OPENGL_PROFILE,GLFW.GLFW_OPENGL_CORE_PROFILE);GLFW.glfwWindowHint(GLFW.GLFW_OPENGL_FORWARD_COMPAT,GLFW.GLFW_TRUE);
        long window=GLFW.glfwCreateWindow(W,H,"Hidden item QA",0,0);if(window==0)throw new IllegalStateException("Hidden context failed");
        GLFW.glfwMakeContextCurrent(window);GL.createCapabilities();
        int program=GL20.glCreateProgram();
        GL20.glAttachShader(program,shader(GL20.GL_VERTEX_SHADER,"#version 150\nin vec3 Position;in vec2 UV;out vec2 tex;uniform mat4 Transform;void main(){tex=UV;gl_Position=Transform*vec4(Position,1);}"));
        GL20.glAttachShader(program,shader(GL20.GL_FRAGMENT_SHADER,"#version 150\nin vec2 tex;out vec4 color;uniform sampler2D Image;void main(){vec4 c=texture(Image,tex);if(c.a<0.1)discard;color=vec4(c.rgb,1);}"));
        GL20.glBindAttribLocation(program,0,"Position");GL20.glBindAttribLocation(program,1,"UV");GL20.glLinkProgram(program);
        if(GL20.glGetProgrami(program,GL20.GL_LINK_STATUS)==0)throw new IllegalStateException(GL20.glGetProgramInfoLog(program));GL20.glUseProgram(program);
        int vao=GL30.glGenVertexArrays();GL30.glBindVertexArray(vao);int vbo=GL15.glGenBuffers();GL15.glBindBuffer(GL15.GL_ARRAY_BUFFER,vbo);
        GL20.glEnableVertexAttribArray(0);GL20.glVertexAttribPointer(0,3,GL11.GL_FLOAT,false,20,0);GL20.glEnableVertexAttribArray(1);GL20.glVertexAttribPointer(1,2,GL11.GL_FLOAT,false,20,12);
        // Dedicated FBO avoids Retina window dimensions affecting the captured result.
        int fbo=GL30.glGenFramebuffers();GL30.glBindFramebuffer(GL30.GL_FRAMEBUFFER,fbo);
        int render=GL11.glGenTextures();GL11.glBindTexture(GL11.GL_TEXTURE_2D,render);GL11.glTexImage2D(GL11.GL_TEXTURE_2D,0,GL11.GL_RGBA8,W,H,0,GL11.GL_RGBA,GL11.GL_UNSIGNED_BYTE,(ByteBuffer)null);
        GL30.glFramebufferTexture2D(GL30.GL_FRAMEBUFFER,GL30.GL_COLOR_ATTACHMENT0,GL11.GL_TEXTURE_2D,render,0);
        int depth=GL30.glGenRenderbuffers();GL30.glBindRenderbuffer(GL30.GL_RENDERBUFFER,depth);GL30.glRenderbufferStorage(GL30.GL_RENDERBUFFER,GL30.GL_DEPTH_COMPONENT24,W,H);GL30.glFramebufferRenderbuffer(GL30.GL_FRAMEBUFFER,GL30.GL_DEPTH_ATTACHMENT,GL30.GL_RENDERBUFFER,depth);
        if(GL30.glCheckFramebufferStatus(GL30.GL_FRAMEBUFFER)!=GL30.GL_FRAMEBUFFER_COMPLETE)throw new IllegalStateException("FBO incomplete");
        GL11.glViewport(0,0,W,H);GL11.glEnable(GL11.GL_DEPTH_TEST);GL11.glEnable(GL11.GL_CULL_FACE);GL11.glDisable(GL11.GL_BLEND);GL11.glClearColor(23/255f,33/255f,39/255f,1);
        Path base=Path.of("src/main/resources/assets/dynasty"),out=Path.of("docs/art/build-feedback-v5/mesh-qa");Files.createDirectories(out);
        for(String id:new String[]{"leifu_staff","taiyi_whisk","hunyuan_staff","qinglong_dao"}){
            var model=JsonParser.parseString(Files.readString(base.resolve("models/item/"+id+".json"))).getAsJsonObject();
            if(!model.has("elements")) {
                // This static tool can preview the preserved icon; articulated runtime poses require the game renderer.
                model=JsonParser.parseString(Files.readString(base.resolve("models/item/"+id+"_icon.json"))).getAsJsonObject();
                System.out.println(id+": inventory artwork only; dynamic held model is not captured by this tool.");
            }
            var geometry=mesh(model);GL15.glBufferData(GL15.GL_ARRAY_BUFFER,geometry,GL15.GL_STATIC_DRAW);
            var bitmap=ImageIO.read(base.resolve("textures/item/"+id+".png").toFile());int tw=bitmap.getWidth(),th=bitmap.getHeight();var texels=BufferUtils.createByteBuffer(tw*th*4);
            for(int y=0;y<th;y++)for(int x=0;x<tw;x++){int c=bitmap.getRGB(x,y);texels.put((byte)(c>>16)).put((byte)(c>>8)).put((byte)c).put((byte)(c>>24));}texels.flip();
            int texture=GL11.glGenTextures();GL11.glBindTexture(GL11.GL_TEXTURE_2D,texture);GL11.glTexImage2D(GL11.GL_TEXTURE_2D,0,GL11.GL_RGBA8,tw,th,0,GL11.GL_RGBA,GL11.GL_UNSIGNED_BYTE,texels);
            GL11.glTexParameteri(GL11.GL_TEXTURE_2D,GL11.GL_TEXTURE_MIN_FILTER,GL11.GL_NEAREST);GL11.glTexParameteri(GL11.GL_TEXTURE_2D,GL11.GL_TEXTURE_MAG_FILTER,GL11.GL_NEAREST);GL11.glTexParameteri(GL11.GL_TEXTURE_2D,GL11.GL_TEXTURE_WRAP_S,GL12.GL_CLAMP_TO_EDGE);GL11.glTexParameteri(GL11.GL_TEXTURE_2D,GL11.GL_TEXTURE_WRAP_T,GL12.GL_CLAMP_TO_EDGE);
            for(int angle:new int[]{0,55,85,180}){
                var transform=new Matrix4f().ortho(-10,10,-13.333f,13.333f,-30,30).rotateY((float)Math.toRadians(angle));var matrix=BufferUtils.createFloatBuffer(16);transform.get(matrix);GL20.glUniformMatrix4fv(GL20.glGetUniformLocation(program,"Transform"),false,matrix);
                GL11.glClear(GL11.GL_COLOR_BUFFER_BIT|GL11.GL_DEPTH_BUFFER_BIT);GL11.glDrawArrays(GL11.GL_TRIANGLES,0,geometry.limit()/5);GL11.glFinish();
                var pixels=BufferUtils.createByteBuffer(W*H*4);GL11.glReadPixels(0,0,W,H,GL11.GL_RGBA,GL11.GL_UNSIGNED_BYTE,pixels);var frame=new BufferedImage(W,H,BufferedImage.TYPE_INT_ARGB);int occupied=0;
                for(int y=0;y<H;y++)for(int x=0;x<W;x++){int at=((H-y-1)*W+x)*4,r=pixels.get(at)&255,g=pixels.get(at+1)&255,b=pixels.get(at+2)&255;frame.setRGB(x,y,0xff000000|r<<16|g<<8|b);if(r!=23||g!=33||b!=39)occupied++;}
                if(occupied<100)throw new IllegalStateException(id+" empty frame");ImageIO.write(frame,"PNG",out.resolve(id+"-"+angle+".png").toFile());System.out.println(id+" yaw="+angle+" occupied="+occupied);
            }GL11.glDeleteTextures(texture);
        }
        if(GL11.glGetError()!=GL11.GL_NO_ERROR)throw new IllegalStateException("OpenGL error");GLFW.glfwDestroyWindow(window);GLFW.glfwTerminate();System.out.println("PASS: 16 hidden-context mesh frames. Not game screenshots.");
    }
}
