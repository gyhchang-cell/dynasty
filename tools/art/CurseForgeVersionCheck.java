import java.io.BufferedReader;
import java.io.InputStreamReader;
import org.apache.maven.artifact.versioning.DefaultArtifactVersion;
import org.apache.maven.artifact.versioning.VersionRange;

/** Check dependency ranges with the same Maven implementation used by Forge. */
class CurseForgeVersionCheck {
    public static void main(String[] args) throws Exception {
        var input = new BufferedReader(new InputStreamReader(System.in));
        String line;
        while ((line = input.readLine()) != null) {
            var fields = line.split("\t", -1);
            var range = fields[1];
            boolean ok = range.equals("*") || VersionRange.createFromVersionSpec(range)
                .containsVersion(new DefaultArtifactVersion(fields[0]));
            System.out.println(ok);
        }
    }
}
