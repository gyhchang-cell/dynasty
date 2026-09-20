import com.dynasty.client.BowSigilGeometry;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;

/** Exports the actual in-game stroke geometry, not an artist's approximation. */
public final class BowSigilPreview {
    public static void main(String[] args) throws Exception {
        StringBuilder svg = new StringBuilder("<svg xmlns='http://www.w3.org/2000/svg' width='1440' height='620' viewBox='0 0 1440 620'>");
        svg.append("<rect width='1440' height='620' fill='#0a101d'/>");
        svg.append("<text x='48' y='52' font-family='sans-serif' font-size='25' fill='#f3dfc8'>DYNASTY / BOW SIGIL</text>");
        svg.append("<text x='48' y='84' font-family='sans-serif' font-size='16' fill='#8493a8'>Continuous luminous geometry · progressive formation · open aiming center</text>");
        double[] phases = {0.25, 0.60, 1.0};
        for (int index = 0; index < phases.length; index++) {
            double center = 240 + index * 480;
            double progress = phases[index];
            svg.append(String.format(Locale.ROOT, "<rect x='%d' y='118' width='448' height='390' rx='18' fill='#111c2d'/>", 16 + index * 480));
            StringBuilder lines = new StringBuilder();
            new BowSigilGeometry(progress, (x1,y1,x2,y2,width) -> lines.append(String.format(Locale.ROOT,
                    "<line x1='%.3f' y1='%.3f' x2='%.3f' y2='%.3f' stroke-width='%.3f'/>",
                    center+x1*162, 310-y1*162, center+x2*162, 310-y2*162, width*324))).draw(4, 80);
            svg.append("<g stroke='#ff9555' stroke-opacity='0.8' stroke-linecap='round'>").append(lines).append("</g>");
            svg.append(String.format(Locale.ROOT, "<text x='%.0f' y='553' text-anchor='middle' font-family='sans-serif' font-size='20' fill='#e8cfb0'>%.0f%% CHARGE</text>", center, progress*100));
        }
        svg.append("<text x='720' y='597' text-anchor='middle' font-family='sans-serif' font-size='14' fill='#8794a8'>Geometry preview from the game renderer — not an in-game screenshot</text></svg>");
        Files.writeString(Path.of(args[0]), svg);
    }
}
