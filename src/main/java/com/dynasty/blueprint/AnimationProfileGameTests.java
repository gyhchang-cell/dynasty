package com.dynasty.blueprint;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class AnimationProfileGameTests {
    @GameTest(template="bow_ritual_test",batch="cod2_animation")
    public static void locomotionProfilesNeverScaleServerContactOrDeathClocks(GameTestHelper h){
        h.assertTrue(AnimationProfile.values().length==11,"All eleven source families are available");
        for(var kind:TemplateMob.Kind.values())h.assertTrue(AnimationProfile.forKind(kind)!=null,"Every real cod1 template has a family: "+kind);
        for(var profile:AnimationProfile.values()){
            h.assertTrue(profile.playbackRate("attack",.8,.2,true)==1&&profile.playbackRate("death",.8,.2,true)==1,"Movement matching never changes attack/death phase: "+profile);
            h.assertTrue(profile.loops("walk")&&!profile.loops("attack")&&!profile.loops("death"),"Only locomotion/idle loops");
        }
        h.assertTrue(AnimationProfile.FLOATING.floating()&&!AnimationProfile.ARCHER.floating(),"Floating and footstep families remain distinct");
        h.assertTrue(AnimationProfile.BLADE.playbackRate("walk",.08,.25,false)<AnimationProfile.BLADE.playbackRate("walk",.16,.25,false),"Moving faster increases authored gait rate within clamp");h.succeed();
    }
    private AnimationProfileGameTests(){}
}
