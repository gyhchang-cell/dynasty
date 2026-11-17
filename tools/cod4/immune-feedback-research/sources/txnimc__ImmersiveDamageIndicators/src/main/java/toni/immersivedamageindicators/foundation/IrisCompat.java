package toni.immersivedamageindicators.foundation;


import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.reflect.Method;

public class IrisCompat {
    private static final MethodHandle SHADERS_ENABLED;
    private static final MethodHandle SHADERS_OPEN_SCREEN;

    static {
        MethodHandle shadersEnabled = null, shaderOpenScreen = null;
        try {
            Class<?> irisApiClass = Class.forName("net.irisshaders.iris.api.v0.IrisApi");
            Method instanceGetter = irisApiClass.getDeclaredMethod("getInstance");
            Object irisApiInstance = instanceGetter.invoke(null);
            shadersEnabled = MethodHandles.lookup().unreflect(irisApiClass.getDeclaredMethod("isShaderPackInUse")).bindTo(irisApiInstance);
            shaderOpenScreen =  MethodHandles.lookup().unreflect(irisApiClass.getDeclaredMethod("openMainIrisScreenObj", Object.class)).bindTo(irisApiInstance);
        } catch (NoSuchMethodException e) {
            e.printStackTrace();
        } catch (Throwable ignored) {
        }
        SHADERS_ENABLED = shadersEnabled;
        SHADERS_OPEN_SCREEN = shaderOpenScreen;
    }


    public static boolean areShadersEnabled() {
        if(SHADERS_ENABLED != null) {
            try {
                return (boolean)SHADERS_ENABLED.invokeExact();
            } catch (Throwable e) {
                return false;
            }
        } else {
            return false;
        }
    }

    public static boolean isShaderModPresent() {
        return SHADERS_ENABLED != null;
    }

}