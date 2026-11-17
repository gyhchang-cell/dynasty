package local.mcmacro;

import java.lang.reflect.*;
import java.util.HashMap;
import java.util.Map;

/** Forge 1.8.9 runtime SRG names, with MCP aliases for development. No coremod. */
final class Reflect {
    private static final Map<String, Field> fields = new HashMap<String, Field>();
    private static final Map<String, Method> methods = new HashMap<String, Method>();
    static Class<?> type(String name) throws Exception { return Class.forName(name); }
    static Object get(Object obj, String srg, String mcp) throws Exception {
        return field(obj.getClass(), srg, mcp).get(obj);
    }
    static void set(Object obj, String srg, String mcp, Object value) throws Exception {
        field(obj.getClass(), srg, mcp).set(obj, value);
    }
    private static Field field(Class<?> cls, String srg, String mcp) throws Exception {
        String key = cls.getName() + ":" + srg;
        Field f = fields.get(key);
        if (f != null) return f;
        for (Class<?> c = cls; c != null; c = c.getSuperclass()) {
            for (String name : new String[] {srg, mcp}) {
                try { f = c.getDeclaredField(name); f.setAccessible(true); fields.put(key, f); return f; }
                catch (NoSuchFieldException ignored) { }
            }
        }
        throw new NoSuchFieldException(key);
    }
    static Object call(Object obj, String srg, String mcp, Class<?>[] signature, Object... args) throws Exception {
        Class<?> cls = obj instanceof Class ? (Class<?>)obj : obj.getClass();
        String key = cls.getName() + ":" + srg + java.util.Arrays.toString(signature);
        Method m = methods.get(key);
        if (m == null) {
            outer: for (Class<?> c = cls; c != null; c = c.getSuperclass()) {
                for (String name : new String[] {srg, mcp}) {
                    try { m = c.getDeclaredMethod(name, signature); m.setAccessible(true); methods.put(key, m); break outer; }
                    catch (NoSuchMethodException ignored) { }
                }
            }
        }
        if (m == null) throw new NoSuchMethodException(key);
        return m.invoke(obj instanceof Class ? null : obj, args);
    }
    static Object call(Object obj, String srg, String mcp) throws Exception {
        return call(obj, srg, mcp, new Class<?>[0]);
    }
    static boolean flag(Object obj, String srg, String mcp) throws Exception { return (Boolean)get(obj,srg,mcp); }
    static double num(Object obj, String srg, String mcp) throws Exception { return ((Number)get(obj,srg,mcp)).doubleValue(); }
}
