package net.sam.simple_combat_indicators.util;

import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.common.Mod;
import net.sam.simple_combat_indicators.SimpleCombatIndicators;
import net.sam.simple_combat_indicators.config.ClientConfig;


@Mod.EventBusSubscriber(modid = SimpleCombatIndicators.MOD_ID, value = Dist.CLIENT)
public class DamageDealtIndicator {

    public static int lifetime;
    public static int initialTime;

    public static float maxRotation;

    public LivingEntity target;
    public int targetId;
    public Vec3 targetPos;
    public float totalDamage;
    public float damage;
    public boolean isKill; // damage number for an enemy dying

    public float age = 0;
    public float currentPartialTick = 0f;
    public float lastPartialTick = 0f;
    public float rotation; //in degrees
    public float maxHealthProportion = 0f;

    public static float baseScale;
    public static float incrementScale;
    public static float decrementSpeed;

    public static int r_kill;
    public static int g_kill;
    public static int b_kill;

    public float scale;
    public int color;

    public static int r_s;
    public static int g_s;
    public static int b_s;

    public static int r_e;
    public static int g_e;
    public static int b_e;

    public int r;
    public int g;
    public int b;
    public int a = 255;

    public static float gravity = 0.0f;


    public static float sprayVel;
    public static float sprayAngleRange;
    public static float sprayAngleOffset;
    public static float friction;

    public float xOffset = 0;
    public float yOffset = 0;

    public float xVel;
    public float yVel;

    public float sqrtDistToEntity;

    public DamageDealtIndicator(int targetId, LivingEntity target, float damage, float totalDamage, float scale) {
        this.target = target;
        this.targetId = targetId;
        this.targetPos = target.position().add(new Vec3(0,target.getBbHeight() * 0.5f,0));
        this.totalDamage = totalDamage;
        this.damage = damage;
        this.scale = scale;

        LocalPlayer p = Minecraft.getInstance().player;
        if(p != null){
            this.maxHealthProportion = totalDamage / (Minecraft.getInstance().player.getMaxHealth());
            sqrtDistToEntity = (float) Math.sqrt(p.position().distanceTo(target.position()));

            if(maxRotation != 0.0) {
                this.rotation = (target.level().random.nextFloat() * maxRotation * 2) - maxRotation;
            }else{
                this.rotation = 0.0f;
            }

            if(this.damage >= this.target.getHealth()){
                this.isKill = true;
            }else{
                this.isKill = false;
            }

            if(ConfigUtils.getOrDefault(ClientConfig.SPRAY_NUMBERS)){
                float randAngle = (float)(((Minecraft.getInstance().level.random.nextFloat() * (sprayAngleRange * (Math.PI/180.0f)) * 2) - (sprayAngleRange * (Math.PI/180.0f))) + (sprayAngleOffset * (Math.PI/180.0f)));
                double distanceToEntitySqrt = Math.sqrt(Minecraft.getInstance().player.position().distanceTo(this.target.position()));
                xVel = (float)(sprayVel * Math.cos(randAngle) * (1/distanceToEntitySqrt));
                yVel = (float)(sprayVel * Math.sin(randAngle) * (1/distanceToEntitySqrt));
            }else{
                xVel = 0.0f;
                yVel = 0.0f;
            }

            gravity = (float)(double)ConfigUtils.getOrDefault(ClientConfig.NUMBER_GRAVITY);

        }
    }


    public void tick(float partialTick){
        currentPartialTick = partialTick;
        double timeDif;
        if(lastPartialTick > currentPartialTick){
            timeDif = (1 - lastPartialTick + currentPartialTick); //ticks
        }else{
            timeDif = (currentPartialTick - lastPartialTick); //ticks
        }

        float scaleRatio = age/initialTime;
        if (scaleRatio > 1.0f){
            scaleRatio = 1.0f;
        }

        if(!isKill){
            r = (int)(r_e + (scaleRatio * (r_s - r_e)));
            g = (int)(g_e + (scaleRatio * (g_s - g_e)));
            b = (int)(b_e + (scaleRatio * (b_s - b_e)));
        }else{
            r = r_kill;
            g = g_kill;
            b = b_kill;
        }

        this.color = rgba(this.r,this.g,this.b,this.a);

        if (this.scale > baseScale){
            this.scale -= (decrementSpeed / 20) * timeDif;
        }

        this.xOffset += xVel * timeDif;
        this.yOffset += yVel * timeDif;

        yVel += gravity * timeDif;
        xVel *= Math.pow(1-friction, timeDif);
        yVel *= Math.pow(1-friction, timeDif);

        this.age += timeDif;
        lastPartialTick = currentPartialTick;


    }



    public static int rgba(int r, int g, int b, int a) {
        return ((a) << 24) |
                ((r) << 16) |
                ((g) << 8)  |
                ((b));
    }

    //called in ConfigUtils when config is read
    public static void initFromConfig() {

        lifetime = ConfigUtils.getOrDefault(ClientConfig.NUMBER_DURATION);
        initialTime = ConfigUtils.getOrDefault(ClientConfig.INITIAL_HIT_TIME);
        maxRotation = ConfigUtils.getOrDefault(ClientConfig.ROTATE_RANGE);
        baseScale = (float) (ConfigUtils.getOrDefault(ClientConfig.NUMBER_BASE_SCALE)/ Minecraft.getInstance().options.guiScale().get());
        incrementScale = (float) (double) (ConfigUtils.getOrDefault(ClientConfig.NUMBER_INCREMENT_SCALE));
        decrementSpeed = (float) (double) (ConfigUtils.getOrDefault(ClientConfig.NUMBER_DECREMENT_SPEED));
        r_kill = ConfigUtils.getOrDefault(ClientConfig.KILL_COLOR_R);
        g_kill = ConfigUtils.getOrDefault(ClientConfig.KILL_COLOR_G);
        b_kill = ConfigUtils.getOrDefault(ClientConfig.KILL_COLOR_B);
        r_s = ConfigUtils.getOrDefault(ClientConfig.START_NUMBER_COLOR_R);
        g_s = ConfigUtils.getOrDefault(ClientConfig.START_NUMBER_COLOR_G);
        b_s = ConfigUtils.getOrDefault(ClientConfig.START_NUMBER_COLOR_B);
        r_e = ConfigUtils.getOrDefault(ClientConfig.END_NUMBER_COLOR_R);
        g_e = ConfigUtils.getOrDefault(ClientConfig.END_NUMBER_COLOR_G);
        b_e = ConfigUtils.getOrDefault(ClientConfig.END_NUMBER_COLOR_B);
        sprayVel = (float) (double) ConfigUtils.getOrDefault(ClientConfig.SPRAY_VELOCITY);
        friction = (float) (double) ConfigUtils.getOrDefault(ClientConfig.NUMBER_FRICTION);
        sprayAngleRange = (float) (double) ConfigUtils.getOrDefault(ClientConfig.SPRAY_ANGLE_RANGE);
        sprayAngleOffset = (float) (double) ConfigUtils.getOrDefault(ClientConfig.SPRAY_ANGLE_OFFSET);
    }
}
