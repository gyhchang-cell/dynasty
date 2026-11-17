package net.sam.simple_combat_indicators.util;

import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec2;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.common.Mod;
import net.sam.simple_combat_indicators.SimpleCombatIndicators;
import net.sam.simple_combat_indicators.config.ClientConfig;


@Mod.EventBusSubscriber(modid = SimpleCombatIndicators.MOD_ID, value = Dist.CLIENT)
public class DamageTakenIndicator {

    public static int lifetime;
    public static int scaleTime;
    public static float baseSizeScale;
    public static float maxSizeScaleMult;
    public static float maxDistScale = 1.5f;
    public static float minDistScale = 1.0f;
    public static float maxColourScale = 1.0f;
    public static float minColourScale = 0.0f;

    public Entity attacker;
    public int attackerId;
    public Vec3 attackedFromPos;
    public float damage;

    // to be changed every tick()
    public static int centerDistPx;
    public float age = 0;
    public float currentPartialTick = 0f;
    public float lastPartialTick = 0f;
    public float rotation = 0;
    public float maxHealthProportion = 0f;
    public float scale = 0.0f;
    public float distScale = maxDistScale;
    public float scaleRatioSquared = 1.0f;

    public static int baseBigHitColorR;
    public static int baseBigHitColorG;
    public static int baseBigHitColorB;

    public static int baseSmallHitColorR;
    public static int baseSmallHitColorG;
    public static int baseSmallHitColorB;

    public int baseR = 0;
    public int baseG = 0;
    public int baseB = 0;
    public int baseA = 0;

    public int r = 0;
    public int g = 0;
    public int b = 0;
    public int a = 0;

    public DamageTakenIndicator(int attackerId, Entity attacker, float damage) {
        this.attacker = attacker;
        this.attackerId = attackerId;
        this.attackedFromPos = attacker.getEyePosition();
        this.damage = damage;
        LocalPlayer p = Minecraft.getInstance().player;
        if(p != null){
            this.maxHealthProportion = damage / (Minecraft.getInstance().player.getMaxHealth());
            if (this.maxHealthProportion > 1.0f){
                this.maxHealthProportion = 1.0f;
            }
            this.baseR = (int) (((baseBigHitColorR - baseSmallHitColorR) * maxHealthProportion) + baseSmallHitColorR);
            this.baseG = (int) (((baseBigHitColorG - baseSmallHitColorG) * maxHealthProportion) + baseSmallHitColorG);
            this.baseB = (int) (((baseBigHitColorB - baseSmallHitColorB) * maxHealthProportion) + baseSmallHitColorB);

            this.r = this.baseR;
            this.g = this.baseG;
            this.b = this.baseB;
        }
    }

//    @SubscribeEvent
//    public static void onDamaged(LivingDamageEvent event){
//        if(!(event.getEntity().level() instanceof ServerLevel)){return;}
//        Entity attacker = event.getSource().getEntity();
//        LivingEntity receiver = event.getEntity();
//        Player player = Minecraft.getInstance().player;
//        if(receiver instanceof Player p){
//            if(p.isInvulnerableTo(event.getSource())){return;}
//            if(attacker != null){
//                if(player.getUUID() == receiver.getUUID()){
//                    boolean indicator_enabled = ConfigUtils.getOrDefault(ClientConfig.ENABLE_DAMAGE_TAKEN_INDICATOR);
//                    if(!indicator_enabled){return;}
//                    int attackerId = attacker.getId();
//                    DamageIndicatorRenderer.damageTakenIndicators.add(new DamageTakenIndicator(attackerId, attacker, event.getAmount()));
//                }
//            }
//        }
//    }

    public void tick(float partialTick){
        currentPartialTick = partialTick;
        double timeDif;
        if(lastPartialTick > currentPartialTick){
            timeDif = (1 - lastPartialTick + currentPartialTick); //ticks
        }else{
            timeDif = (currentPartialTick - lastPartialTick); //ticks
        }
        this.age += timeDif;
        rotateToAttackerXZ(currentPartialTick);
        //rotateToAttacker(currentPartialTick);
        calcScaleRatioSquared();
        tickScale();
        tickDistScale();
        tickOpacityScale();
        lastPartialTick = currentPartialTick;
    }
        public void rotateToAttackerXZ(float partialTick){
        Player player = Minecraft.getInstance().player;
        Vec3 eyePos = player.getEyePosition(partialTick);
        Vec3 to = (attackedFromPos.subtract(eyePos));
        Vec2 toXZ = new Vec2((float)to.x, (float)to.z).normalized();

        Vec3 up = player.getUpVector(partialTick);
        Vec3 right = player.getLookAngle().cross(up);
        Vec2 rightXZ = new Vec2((float)right.x, (float)right.z).normalized();

        Vec3 look = player.getLookAngle();
        Vec2 lookXZ = new Vec2((float) look.x, (float) look.z).normalized();



        double dotProd = toXZ.dot(lookXZ);
        double angle = Math.acos(dotProd);
        if(toXZ.dot(rightXZ) < 0){
            angle *= -1;
        }
        rotation = (float)( angle * (180/Math.PI));
    }

    public void calcScaleRatioSquared(){
        float scaleRatio = age/scaleTime;
        if(scaleRatio > 1){
            scaleRatio = 1;
        }
        scaleRatioSquared = (1 - scaleRatio) * (1 - scaleRatio);
    }

    public void tickDistScale(){
        this.distScale = (scaleRatioSquared * (maxDistScale - minDistScale)) + minDistScale;
    }

    public void tickScale(){
        this.scale = (baseSizeScale + (scaleRatioSquared)) * (1 + (maxHealthProportion));
    }

    public void tickOpacityScale(){
        float scaleRatio = age/lifetime;
        this.a = (int)((1 - scaleRatio) * 255);
    }

    //called in ConfigUtils when config is read
    public static void initFromConfig() {
        lifetime = ConfigUtils.getOrDefault(ClientConfig.DAMAGE_TAKEN_INDICATOR_DURATION);
        scaleTime = ConfigUtils.getOrDefault(ClientConfig.DAMAGE_TAKEN_INDICATOR_BIG_DURATION);
        baseSizeScale = (float)(double)(ConfigUtils.getOrDefault(ClientConfig.DAMAGE_TAKEN_INDICATOR_BASE_SIZE_SCALE));
        maxSizeScaleMult = (float)(double)(ConfigUtils.getOrDefault(ClientConfig.DAMAGE_TAKEN_INDICATOR_BASE_SIZE_SCALE));

        centerDistPx = ConfigUtils.getOrDefault(ClientConfig.DAMAGE_TAKEN_INDICATOR_DISTANCE);

        baseBigHitColorR = ConfigUtils.getOrDefault(ClientConfig.BIG_HIT_INDICATOR_COLOR_R);
        baseBigHitColorG = ConfigUtils.getOrDefault(ClientConfig.BIG_HIT_INDICATOR_COLOR_G);
        baseBigHitColorB = ConfigUtils.getOrDefault(ClientConfig.BIG_HIT_INDICATOR_COLOR_B);

        baseSmallHitColorR = ConfigUtils.getOrDefault(ClientConfig.SMALL_HIT_INDICATOR_COLOR_R);
        baseSmallHitColorG = ConfigUtils.getOrDefault(ClientConfig.SMALL_HIT_INDICATOR_COLOR_G);
        baseSmallHitColorB = ConfigUtils.getOrDefault(ClientConfig.SMALL_HIT_INDICATOR_COLOR_B);
    }
}
