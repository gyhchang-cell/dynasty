import com.dynasty.BowTrajectoryMath;
import net.minecraft.world.phys.Vec3;

/** Runs against production math, without a Minecraft client/server or Gradle task. */
public final class VerifyBowTrajectory {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
    public static void main(String[] args) {
        Vec3 forward = new Vec3(0,0,3);
        int cases = 0;
        for (int yaw = -85; yaw <= 85; yaw += 5) for (int pitch = -80; pitch <= 80; pitch += 5) {
            Vec3 aim = BowTrajectoryMath.renderedDirection(yaw,yaw,pitch,pitch,0);
            Vec3 moved = BowTrajectoryMath.steer(forward,aim.scale(4));
            require(Math.abs(moved.length()-3) < 1.0E-10,"Speed changed");
            double turn = Math.acos(Math.min(1,moved.normalize().dot(forward.normalize())));
            require(turn <= BowTrajectoryMath.TURN_RADIANS_PER_TICK + 1.0E-10,"Turn limit exceeded");
            require(Double.isFinite(moved.x + moved.y + moved.z),"Non-finite flight vector");
            cases++;
        }
        require(!BowTrajectoryMath.insideAssistCorridor(new Vec3(4,0,4),forward,forward),"Wide side target acquired");
        require(!BowTrajectoryMath.insideAssistCorridor(new Vec3(0,0,-2),forward,forward),"Rear target acquired");
        require(!BowTrajectoryMath.insideAssistCorridor(new Vec3(0,0,7),forward,forward),"Out-of-range target acquired");
        require(BowTrajectoryMath.insideAssistCorridor(new Vec3(1,0.4,4),forward,forward),"Close aimed target rejected");
        require(BowTrajectoryMath.steer(forward,Vec3.ZERO).equals(forward),"Zero delta disturbed flight");
        require(BowTrajectoryMath.steer(forward,new Vec3(0,0,-1)).equals(forward),"Arrow reversed");
        for (int pitch = -90; pitch <= 90; pitch++) {
            Vec3 rendered = BowTrajectoryMath.renderedDirection(170,190,pitch,pitch,0.5F);
            require(Math.abs(rendered.length()-1) < 1.0E-10,"Render axis length");
            require(Math.abs(rendered.y-Math.sin(Math.toRadians(pitch))) < 1.0E-10,"Arrow pitch sign reversed");
            cases++;
        }
        // Reproduce the actual Mth lookup table used by vanilla launch and camera code.
        // getLookAngle's result is only approximately unit length; angular tests need both normalized.
        float launchPitch = -60 * ((float)Math.PI / 180F), launchYaw = 33 * ((float)Math.PI / 180F);
        Vec3 vanillaLaunch = new Vec3(-net.minecraft.util.Mth.sin(launchYaw) * net.minecraft.util.Mth.cos(launchPitch),
                -net.minecraft.util.Mth.sin(launchPitch), net.minecraft.util.Mth.cos(launchYaw) * net.minecraft.util.Mth.cos(launchPitch));
        Vec3 vanillaLook = new Vec3(net.minecraft.util.Mth.sin(-launchYaw) * net.minecraft.util.Mth.cos(launchPitch),
                -net.minecraft.util.Mth.sin(launchPitch), net.minecraft.util.Mth.cos(-launchYaw) * net.minecraft.util.Mth.cos(launchPitch));
        require(vanillaLaunch.normalize().dot(vanillaLook.normalize()) > 0.99999,"Vanilla upward launch disagrees with camera");
        System.out.println("PASS bow trajectory: " + cases + " finite/turn/speed/render-angle cases + corridor safeguards");
    }
}
