import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.List;
import java.util.Set;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtIo;

/** Exercises a packaged SRG migration method with read-only archived player data. */
class LegacyArchivedProgressReadback {
    private static final Set<String> ORIGINAL_KEYS = Set.of(
            "dq_p_18", "dynasty_merit", "dynasty_rank", "dynasty_loyalty");

    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static CompoundTag roundTrip(CompoundTag tag) throws Exception {
        var stream = new ByteArrayOutputStream();
        NbtIo.m_128947_(tag, stream);
        return NbtIo.m_128939_(new ByteArrayInputStream(stream.toByteArray()));
    }

    public static void main(String[] args) throws Exception {
        var migration = Class.forName("com.dynasty.LegacyPlayerProgression");
        try (var bytes = migration.getResourceAsStream("LegacyPlayerProgression.class")) {
            var digest = MessageDigest.getInstance("SHA-256").digest(bytes.readAllBytes());
            require(HexFormat.of().formatHex(digest).equals(args[0]), "Unexpected migration class");
        }
        var copy = migration.getDeclaredMethod("copyAuditedRoot", CompoundTag.class, CompoundTag.class);
        copy.setAccessible(true);
        CompoundTag archive;
        try (var bytes = Files.newInputStream(Path.of(args[1]))) {
            archive = NbtIo.m_128939_(bytes);
        }
        var original = archive.m_128469_("ForgeData");
        require(original.m_128431_().equals(ORIGINAL_KEYS), "Unexpected archived progression keys");
        require(original.m_128451_("dynasty_merit") == 280 && original.m_128451_("dynasty_rank") == 2
                && original.m_128451_("dynasty_loyalty") == 10 && original.m_128451_("dq_p_18") == 1,
                "Archived values differ from the original receipt");
        var before = roundTrip(original);
        var destination = new CompoundTag();
        require(List.of().equals(copy.invoke(null, original, destination)), "Malformed original fields");
        var reloaded = roundTrip(destination);
        require(reloaded.equals(before), "First copy lost or added fields");
        require(List.of().equals(copy.invoke(null, reloaded, destination)), "Malformed reloaded fields");
        require(roundTrip(destination).equals(before), "Repeated copy changed progress");
        destination.m_128473_("dq_p_18");
        require(original.equals(before) && reloaded.equals(before), "Input compound modified");
        System.out.println("PASS: four typed original fields, compressed NBT round trip, replay and source isolation");
    }
}
