import java.lang.instrument.*;
import java.security.ProtectionDomain;
import org.objectweb.asm.*;

/** Disposable QA process only. Never packaged in the Dynasty mod. */
public final class QuietWindowAgent {
    public static void premain(String args,Instrumentation instrument){
        instrument.addTransformer(new ClassFileTransformer(){
            public byte[] transform(ClassLoader loader,String name,Class<?> cls,ProtectionDomain domain,byte[] bytes){
                if(!name.equals("org/lwjgl/glfw/GLFW"))return null;
                var writer=new ClassWriter(ClassWriter.COMPUTE_MAXS);
                new ClassReader(bytes).accept(new ClassVisitor(Opcodes.ASM9,writer){
                    public MethodVisitor visitMethod(int access,String method,String desc,String sig,String[] exceptions){
                        var target=super.visitMethod(access,method,desc,sig,exceptions);
                        if((method.equals("glfwShowWindow")||method.equals("glfwFocusWindow"))&&desc.equals("(J)V")){
                            target.visitCode();target.visitInsn(Opcodes.RETURN);target.visitMaxs(0,2);target.visitEnd();return null;
                        }
                        if(!method.equals("glfwCreateWindow"))return target;
                        return new MethodVisitor(Opcodes.ASM9,target){
                            public void visitCode(){super.visitCode();
                                for(int hint:new int[]{0x00020004,0x00020001,0x0002000c}){
                                    visitLdcInsn(hint);visitInsn(Opcodes.ICONST_0);visitMethodInsn(Opcodes.INVOKESTATIC,"org/lwjgl/glfw/GLFW","glfwWindowHint","(II)V",false);
                                }
                                System.err.println("QuietWindowAgent: hidden, unfocused GLFW window creation");
                            }
                        };
                    }
                },0);
                return writer.toByteArray();
            }
        });
    }
}
