package local.mcmacro;

public final class TellyPlanTest {
    static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
    public static void main(String[] args) {
        TellyPlan plan = new TellyPlan();
        for (int cycle=0;cycle<600;cycle++) {
            TellyPlan.Frame start=plan.tick(true);
            check(start.jump && start.forward && !start.place && !start.stalled,"落地后应向前起跳");
            for(int t=1;t<=12;t++) {
                TellyPlan.Frame frame=plan.tick(false);
                check(!frame.jump && !frame.stalled,"空中不应重复跳跃或错误停止");
                check(frame.forward==(t<=3),"起跳初段向前，之后转身后退");
                check(frame.place==(t>3),"仅在转身后进入放置阶段");
            }
        }
        plan=new TellyPlan();
        for(int t=0;t<26;t++) plan.tick(false);
        check(plan.tick(false).stalled,"长时间没有落地必须停止");
        plan=new TellyPlan();
        for(int t=0;t<8;t++) check(!plan.tick(true).stalled,"允许正常起跳延迟");
        check(plan.tick(true).stalled,"原地被阻挡不能无限重复跳跃");
        for(float sensitivity:new float[]{0F,0.1F,0.5F,0.74647886F,1F}) {
            for(int angle=-720;angle<=720;angle++) {
                float actual=TellyPlan.quantize(angle,0,sensitivity);
                check(Math.abs(actual-angle)<=TellyPlan.degreesPerCount(sensitivity)*0.501F+0.0001F,"不同灵敏度角度量化误差过大");
            }
        }
        check(TellyPlan.cardinal(179)==180 && TellyPlan.cardinal(-179)==-180,"正负朝向都应正常处理");
        class Parent { private int field=4; private int add(int x) { return field+x; } }
        class Child extends Parent { }
        try {
            Child obj=new Child();
            check(((Number)Reflect.get(obj,"missing","field")).intValue()==4,"反射应支持父类与开发别名");
            Reflect.set(obj,"missing","field",8);
            check(((Number)Reflect.call(obj,"method","add",new Class<?>[]{int.class},3)).intValue()==11,"反射应匹配准确方法签名");
        } catch(Exception e) { throw new AssertionError(e); }
        System.out.println("通过：600 次起跳/转身/落地周期、超时停止、5 种灵敏度 7205 次角度检查、SRG/MCP 反射适配。");
    }
}
