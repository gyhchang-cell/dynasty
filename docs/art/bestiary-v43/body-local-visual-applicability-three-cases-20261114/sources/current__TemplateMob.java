// READ RANGE 648..674
    @Override public boolean canBreatheUnderwater(){return kind==Kind.TOAD||kind==Kind.SERPENT||kind==Kind.DROWNER||super.canBreatheUnderwater();}
    @Override public boolean checkSpawnObstruction(net.minecraft.world.level.LevelReader reader){
        return (kind==Kind.TOAD||kind==Kind.SERPENT||kind==Kind.DROWNER)?reader.isUnobstructed(this):super.checkSpawnObstruction(reader);
    }
    @Override public void travel(Vec3 input) {
        if(kind==Kind.TREE&&!treeAwake()&&isAlive()){
            setDeltaMovement(0,getDeltaMovement().y,0);super.travel(Vec3.ZERO);return;
        }
        if((kind==Kind.TOAD||kind==Kind.SERPENT||kind==Kind.DROWNER)&&isAlive()&&isInWater()&&isControlledByLocalInstance()){
            moveRelative(.1F,input);move(net.minecraft.world.entity.MoverType.SELF,getDeltaMovement());
            setDeltaMovement(getDeltaMovement().scale(.8));calculateEntityAnimation(false);return;
        }
        if ((kind != Kind.SKULL && kind != Kind.LANTERN_BAT && kind != Kind.BLIND_FISH && kind != Kind.YECHA) || !isAlive() || isInWater() || isInLava()) {
            super.travel(input); return;
        }
        // FlyingMoveControl supplies vertical input; ground travel uses ground friction
        // and cannot provide a controlled ascent after the bite. Keep normal collision.
        if (isControlledByLocalInstance()) {
            moveRelative(.1F, input);
            move(net.minecraft.world.entity.MoverType.SELF, getDeltaMovement());
            setDeltaMovement(getDeltaMovement().scale(.85));
        }
        calculateEntityAnimation(true);
    }

    @Override public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return kind == Kind.BEAST || kind == Kind.TOAD ? super.causeFallDamage(Math.max(0, distance - 5), multiplier, source) : super.causeFallDamage(distance, multiplier, source);
