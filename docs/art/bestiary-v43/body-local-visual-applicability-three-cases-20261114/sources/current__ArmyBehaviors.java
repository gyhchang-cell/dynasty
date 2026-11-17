// READ RANGE 200..285

    private static final class RedToad extends Base {
        Vec3 tongueDirection=new Vec3(0,0,1),landing=Vec3.ZERO;
        UUID pulled;long pullUntil,burstUntil;boolean leaping,landed;
        RedToad(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.TOAD_TONGUE||id==ArmySkills.TOAD_LEAP||id==ArmySkills.TOAD_BURST;}
        public boolean canStart(int id,LivingEntity target){
            if(id==ArmySkills.TOAD_BURST)return level().getGameTime()<burstUntil;
            return (mob.onGround()||mob.isInWater())&&(id!=ArmySkills.TOAD_LEAP||mob.distanceToSqr(target)>12.25);
        }
        public int choose(LivingEntity target,long now){
            if(now<burstUntil&&mob.attack().ready(ArmySkills.TOAD_BURST,now))return ArmySkills.TOAD_BURST;
            return mob.distanceToSqr(target)<=25?ArmySkills.TOAD_TONGUE:ArmySkills.TOAD_LEAP;
        }
        public void move(LivingEntity target,long now){mob.getNavigation().stop();mob.setSprinting(false);}
        public void started(int id,LivingEntity target){
            if(id==ArmySkills.TOAD_TONGUE){
                tongueDirection=target.position().add(0,Math.min(.55,target.getBbHeight()*.5),0).subtract(mob.position().add(0,.55,0)).normalize();
                mob.setTongueReach(5);
            }
            if(id==ArmySkills.TOAD_LEAP){
                Vec3 delta=target.position().subtract(mob.position()).multiply(1,0,1);
                landing=mob.position().add(delta.normalize().scale(Math.min(6,delta.length())));leaping=false;landed=false;
            }
        }
        public void tick(long now){
            if(leaping&&!landed&&mob.actionAge(0)>12&&(mob.onGround()||mob.isInWater())){
                landed=true;leaping=false;
                for(var enemy:CombatGeometry.query(level(),mob.position(),Vec3.ZERO,CombatGeometry.Shape.CIRCLE,1.8,0,360,1.4,
                    e->mob.validEnemy(e)&&mob.hasLineOfSight(e)))enemy.hurt(mob.damageSources().mobAttack(mob),4);
                level().sendParticles(net.minecraft.core.particles.ParticleTypes.POOF,mob.getX(),mob.getY()+.1,mob.getZ(),8,.6,.05,.6,.02);
            }
            if(mob.skillId()!=ArmySkills.TOAD_LEAP)leaping=false;
            if(pulled==null)return;
            var target=mob.resolve(pulled);
            if(now>=pullUntil||!mob.validEnemy(target)||mob.skillId()!=ArmySkills.TOAD_TONGUE||mob.distanceToSqr(target)>36||!mob.hasLineOfSight(target)){
                if(target!=null&&now>=pullUntil){target.setDeltaMovement(target.getDeltaMovement().multiply(0,1,0));target.hurtMarked=true;}
                pulled=null;return;
            }
            double resistance=Math.max(0,Math.min(1,target.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE)));
            Vec3 delta=mob.position().subtract(target.position()).multiply(1,0,1);
            if(delta.lengthSqr()<2.25){pulled=null;return;}
            Vec3 step=delta.normalize().scale(.22*(1-resistance));
            if(!level().hasChunkAt(net.minecraft.core.BlockPos.containing(target.position().add(step)))||!level().noCollision(target,target.getBoundingBox().move(step))){pulled=null;return;}
            target.setDeltaMovement(step.x,target.getDeltaMovement().y,step.z);target.hurtMarked=true;
        }
        public void impact(SkillDefinition skill,int frame){
            if(skill.id()==ArmySkills.TOAD_LEAP){
                Vec3 delta=landing.subtract(mob.position()).multiply(1,0,1);
                if(!level().hasChunkAt(net.minecraft.core.BlockPos.containing(landing)))return;
                // Vanilla gravity and air drag integrate this impulse; no teleport or noclip.
                mob.setOnGround(false);mob.setDeltaMovement(delta.scale(1/8.68).add(0,.65,0));mob.hasImpulse=true;leaping=true;return;
            }
            if(skill.id()==ArmySkills.TOAD_BURST){
                burstUntil=0;
                int existing=level().getEntitiesOfClass(TemplateProjectile.class,mob.getBoundingBox().inflate(16),p->p.armyMode()==3).size();
                int shots=Math.min(6,Math.max(0,12-existing));
                for(int i=0;i<shots;i++)TemplateProjectile.shootVenom(mob,i*Math.PI/3);
                return;
            }
            Vec3 from=mob.position().add(0,.55,0),end=from.add(tongueDirection.scale(5));
            var wall=level().clip(new net.minecraft.world.level.ClipContext(from,end,net.minecraft.world.level.ClipContext.Block.COLLIDER,
                net.minecraft.world.level.ClipContext.Fluid.NONE,mob));
            if(wall.getType()!=net.minecraft.world.phys.HitResult.Type.MISS)end=wall.getLocation();
            LivingEntity hit=null;double nearest=from.distanceToSqr(end);
            for(var candidate:level().getEntitiesOfClass(LivingEntity.class,new net.minecraft.world.phys.AABB(from,end).inflate(.25),e->e!=mob&&e.isAlive()&&!e.isSpectator())){
                var point=candidate.getBoundingBox().inflate(.15).clip(from,end);
                if(point.isPresent()&&from.distanceToSqr(point.get())<nearest){nearest=from.distanceToSqr(point.get());hit=candidate;}
            }
            mob.setTongueReach((float)Math.sqrt(nearest));
            if(mob.validEnemy(hit)&&hit.hurt(mob.damageSources().mobAttack(mob),(float)mob.getAttributeValue(Attributes.ATTACK_DAMAGE))
                    &&!(hit instanceof com.dynasty.DynastyBossCombat.BarHolder)){
                pulled=hit.getUUID();pullUntil=level().getGameTime()+6;
            }
        }
        public void hurtAccepted(DamageSource source,boolean frontal,float healthLost){
            if(healthLost>=6&&mob.attack().ready(ArmySkills.TOAD_BURST,level().getGameTime()))burstUntil=level().getGameTime()+80;
        }
        public CompoundTag save(){var t=new CompoundTag();t.putDouble("TongueX",tongueDirection.x);t.putDouble("TongueY",tongueDirection.y);t.putDouble("TongueZ",tongueDirection.z);
            t.putDouble("LandX",landing.x);t.putDouble("LandY",landing.y);t.putDouble("LandZ",landing.z);t.putBoolean("Leaping",leaping);t.putBoolean("Landed",landed);
            t.putLong("BurstUntil",burstUntil);t.putLong("PullUntil",pullUntil);if(pulled!=null)t.putUUID("Pulled",pulled);return t;}
        public void load(CompoundTag t){tongueDirection=new Vec3(t.getDouble("TongueX"),t.getDouble("TongueY"),t.getDouble("TongueZ")).normalize();
            landing=new Vec3(t.getDouble("LandX"),t.getDouble("LandY"),t.getDouble("LandZ"));leaping=t.getBoolean("Leaping");landed=t.getBoolean("Landed");
            burstUntil=t.getLong("BurstUntil");pullUntil=t.getLong("PullUntil");pulled=t.hasUUID("Pulled")&&pullUntil>level().getGameTime()?t.getUUID("Pulled"):null;}
    }

