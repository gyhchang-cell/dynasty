import java.io.InputStream;
import java.lang.annotation.ElementType;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipInputStream;
import net.minecraftforge.fml.loading.moddiscovery.ModClassVisitor;
import net.minecraftforge.forgespi.language.ModFileScanData;
import net.minecraftforge.forgespi.language.ModFileScanData.AnnotationData;
import org.objectweb.asm.ClassReader;

/** Read Forge metadata from the distribution without loading or initializing any game class. */
public final class LegacyForgeSubscriberScan {
    private static final String TYPE = "net.minecraftforge.fml.common.Mod$EventBusSubscriber";
    private static final String METHOD = "net.minecraftforge.eventbus.api.SubscribeEvent";
    private static final Map<String, String> HANDLERS = Map.of(
        "com.dynasty.LegacyItemMappings", "missingItems(Lnet/minecraftforge/registries/MissingMappingsEvent;)V",
        "com.dynasty.LegacyPlayerProgression", "clonePlayer(Lnet/minecraftforge/event/entity/player/PlayerEvent$Clone;)V"
    );

    private static int scan(InputStream input, ModFileScanData data) throws Exception {
        int count = 0;
        try (var jar = new ZipInputStream(input)) {
            for (ZipEntry entry; (entry = jar.getNextEntry()) != null;) {
                if (!entry.getName().startsWith("com/dynasty/") || !entry.getName().endsWith(".class")) continue;
                var reader = new ClassReader(jar.readAllBytes());
                if (!entry.getName().equals(reader.getClassName() + ".class")) {
                    throw new IllegalStateException("Class path differs from declared name: " + entry.getName());
                }
                var visitor = new ModClassVisitor();
                reader.accept(visitor, ClassReader.SKIP_CODE | ClassReader.SKIP_DEBUG | ClassReader.SKIP_FRAMES);
                visitor.buildData(data.getClasses(), data.getAnnotations());
                count++;
            }
        }
        return count;
    }

    public static void main(String[] args) throws Exception {
        var data = new ModFileScanData();
        try (var release = new ZipFile(args[0])) {
            int classes = scan(release.getInputStream(release.getEntry("overrides/mods/dynasty-1.4.0.jar")), data);
            System.out.println("Distributed Dynasty classes scanned: " + classes);
        }
        for (var cls : data.getClasses()) {
            if (HANDLERS.containsKey(cls.clazz().getClassName())) throw new AssertionError("Release already has " + cls.clazz());
        }
        var existing = new TreeSet<String>();
        for (var a : data.getAnnotations()) {
            if (a.annotationType().getClassName().equals(METHOD) && HANDLERS.values().stream()
                    .map(s -> s.substring(s.indexOf('('))).anyMatch(a.memberName()::endsWith)) {
                existing.add(a.clazz().getClassName() + "." + a.memberName());
            }
        }
        existing.forEach(s -> System.out.println("Existing listener: " + s));
        try (var additions = java.nio.file.Files.newInputStream(Path.of(args[1]))) {
            if (scan(additions, data) != HANDLERS.size()) throw new AssertionError("Unexpected overlay classes");
        }
        for (var handler : HANDLERS.entrySet()) {
            List<AnnotationData> annotations = data.getAnnotations().stream()
                .filter(a -> a.clazz().getClassName().equals(handler.getKey())).toList();
            var types = annotations.stream().filter(a -> a.targetType() == ElementType.TYPE
                && a.annotationType().getClassName().equals(TYPE)).toList();
            if (types.size() != 1 || !types.get(0).annotationData().equals(Map.of("modid", "dynasty"))) {
                throw new AssertionError("Expected Dynasty subscriber with default sides and Forge bus: " + types);
            }
            var methods = annotations.stream().filter(a -> a.targetType() == ElementType.METHOD
                && a.annotationType().getClassName().equals(METHOD)).toList();
            if (methods.size() != 1 || !handler.getValue().equals(methods.get(0).memberName())) {
                throw new AssertionError("Expected one exact Forge event handler: " + methods);
            }
            System.out.println("Discovered: " + handler.getKey() + "." + handler.getValue());
        }
    }
}
