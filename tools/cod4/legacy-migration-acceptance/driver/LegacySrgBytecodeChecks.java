package com.dynasty.qa;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.jar.JarFile;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.util.CheckClassAdapter;

/** ASM data-flow verification only. No Minecraft entry point or class initialization. */
public final class LegacySrgBytecodeChecks {
    public static void main(String[] args) throws Exception {
        URL[] urls = Files.readAllLines(Path.of(args[1])).stream()
                .map(line -> {
                    try { return Path.of(line).toUri().toURL(); }
                    catch (Exception exception) { throw new IllegalArgumentException(exception); }
                }).toArray(URL[]::new);
        int checked = 0;
        try (URLClassLoader loader = new URLClassLoader(urls, ClassLoader.getPlatformClassLoader());
             JarFile patch = new JarFile(args[0])) {
            for (String name : new String[] {"com/dynasty/LegacyItemMappings.class",
                    "com/dynasty/LegacyPlayerProgression.class"}) {
                StringWriter diagnostics = new StringWriter();
                try (var stream = patch.getInputStream(patch.getJarEntry(name))) {
                    CheckClassAdapter.verify(new ClassReader(stream), loader, false,
                            new PrintWriter(diagnostics));
                }
                if (!diagnostics.toString().isBlank()) {
                    throw new AssertionError(name + "\n" + diagnostics);
                }
                checked++;
            }
        }
        if (checked != 2) throw new AssertionError("Two production classes required");
        System.out.println("PASS: 2 SRG classes; ASM data-flow verification; no game or event dispatch");
    }
}
