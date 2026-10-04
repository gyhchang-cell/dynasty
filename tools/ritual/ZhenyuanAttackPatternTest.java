import com.dynasty.ritual.ZhenyuanAttackPattern;
public class ZhenyuanAttackPatternTest {
    private static void check(boolean value,String note) { if(!value)throw new AssertionError(note); }
    public static void main(String[] args) {
        check(ZhenyuanAttackPattern.phase(1)==0,"first phase");
        check(ZhenyuanAttackPattern.phase(.65)==1,"second boundary");
        check(ZhenyuanAttackPattern.phase(.30)==2,"third boundary");
        for(int p=0;p<3;p++) {
            double r=ZhenyuanAttackPattern.ringRadius(p);
            check(ZhenyuanAttackPattern.hit(0,p,r,0),"ring active");
            check(!ZhenyuanAttackPattern.hit(0,p,0,0),"ring center safe");
            check(!ZhenyuanAttackPattern.hit(0,p,r+2,0),"ring outside safe");
            check(ZhenyuanAttackPattern.hit(1,p,0,0),"circle active");
            check(!ZhenyuanAttackPattern.hit(1,p,5,0),"circle escape");
            check(ZhenyuanAttackPattern.hit(2,p,0,19),"cross active");
            check(!ZhenyuanAttackPattern.hit(2,p,7,7),"cross quadrant safe");
            check(!ZhenyuanAttackPattern.hit(2,p,0,23),"cross finite extent");
        }
        check(!ZhenyuanAttackPattern.hit(0,0,Double.NaN,0),"invalid coords");
        check(!ZhenyuanAttackPattern.hit(1,0,Double.POSITIVE_INFINITY,0),"infinity");
        check(!ZhenyuanAttackPattern.hit(99,0,0,0),"invalid pattern");
        check(ZhenyuanAttackPattern.WARNING_TICKS>=30,"readable warning");
        System.out.println("PASS: 31 phase/hit-boundary/escape checks");
    }
}
