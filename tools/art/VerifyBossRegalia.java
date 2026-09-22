import com.dynasty.client.BossRegaliaGeometry;

/** Standalone geometry regression: real production faces across both complete animation cycles. */
public final class VerifyBossRegalia {
    public static void main(String[] args) {
        for(int style=1;style<=2;style++)for(int tick=0;tick<1200;tick+=3) {
            int[] count={0};
            new BossRegaliaGeometry((a,b,c,d,color)-> {
                count[0]++;
                for(var p:new BossRegaliaGeometry.P[]{a,b,c,d}) {
                    if(!Double.isFinite(p.x()+p.y()+p.z())||Math.abs(p.x())>2||Math.abs(p.y())>2||Math.abs(p.z())>1)
                        throw new AssertionError("Nonfinite or excessively large boss ornament");
                }
                double ux=b.x()-a.x(),uy=b.y()-a.y(),uz=b.z()-a.z();
                double vx=c.x()-a.x(),vy=c.y()-a.y(),vz=c.z()-a.z();
                double cross=Math.pow(uy*vz-uz*vy,2)+Math.pow(uz*vx-ux*vz,2)+Math.pow(ux*vy-uy*vx,2);
                if(cross<1e-16)throw new AssertionError("Degenerate face");
            }).draw(style,tick);
            if(count[0]<100||count[0]>1000)throw new AssertionError("Unexpected ornament budget: "+count[0]);
        }
        System.out.println("PASS: 800 animated regalia frames, finite vertices, face areas and <1000 faces per boss.");
    }
}
