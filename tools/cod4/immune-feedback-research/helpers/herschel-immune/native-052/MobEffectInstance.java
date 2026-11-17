package net.minecraft.world.effect;

import com.google.common.collect.ComparisonChain;
import com.mojang.logging.LogUtils;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.mojang.serialization.codecs.RecordCodecBuilder.Instance;
import io.netty.buffer.ByteBuf;
import it.unimi.dsi.fastutil.ints.Int2IntFunction;
import java.util.Optional;
import javax.annotation.Nullable;
import net.minecraft.core.Holder;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtOps;
import net.minecraft.nbt.Tag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.ExtraCodecs;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import org.slf4j.Logger;

public class MobEffectInstance implements Comparable<MobEffectInstance> {
    private static final Logger f_19501_ = LogUtils.getLogger();
    public static final int f_267388_ = -1;
    public static final int f_316862_ = 0;
    public static final int f_316220_ = 255;
    public static final Codec<MobEffectInstance> f_316026_ = RecordCodecBuilder.create(
        p_341259_ -> p_341259_.group(
                    MobEffect.f_337486_.fieldOf("id").forGetter(MobEffectInstance::m_19544_),
                    MobEffectInstance.Details.f_316395_.forGetter(MobEffectInstance::m_324991_)
                )
                .apply(p_341259_, MobEffectInstance::new)
    );
    public static final StreamCodec<RegistryFriendlyByteBuf, MobEffectInstance> f_315755_ = StreamCodec.m_320349_(
        MobEffect.f_336968_, MobEffectInstance::m_19544_, MobEffectInstance.Details.f_315344_, MobEffectInstance::m_324991_, MobEffectInstance::new
    );
    private final Holder<MobEffect> f_19502_;
    private int f_19503_;
    private int f_19504_;
    private boolean f_19506_;
    private boolean f_19508_;
    private boolean f_19509_;
    @Nullable
    private MobEffectInstance f_19510_;
    private final MobEffectInstance.BlendState f_317081_ = new MobEffectInstance.BlendState();

    public MobEffectInstance(Holder<MobEffect> p_333937_) {
        this(p_333937_, 0, 0);
    }

    public MobEffectInstance(Holder<MobEffect> p_332556_, int p_19523_) {
        this(p_332556_, p_19523_, 0);
    }

    public MobEffectInstance(Holder<MobEffect> p_334453_, int p_328066_, int p_330997_) {
        this(p_334453_, p_328066_, p_330997_, false, true);
    }

    public MobEffectInstance(Holder<MobEffect> p_327781_, int p_19529_, int p_19530_, boolean p_19531_, boolean p_19532_) {
        this(p_327781_, p_19529_, p_19530_, p_19531_, p_19532_, p_19532_);
    }

    public MobEffectInstance(Holder<MobEffect> p_333122_, int p_216888_, int p_216889_, boolean p_216890_, boolean p_216891_, boolean p_216892_) {
        this(p_333122_, p_216888_, p_216889_, p_216890_, p_216891_, p_216892_, null);
    }

    public MobEffectInstance(
        Holder<MobEffect> p_334558_, int p_19519_, int p_19520_, boolean p_332448_, boolean p_327855_, boolean p_334281_, @Nullable MobEffectInstance p_332569_
    ) {
        this.f_19502_ = p_334558_;
        this.f_19503_ = p_19519_;
        this.f_19504_ = Mth.m_14045_(p_19520_, 0, 255);
        this.f_19506_ = p_332448_;
        this.f_19508_ = p_327855_;
        this.f_19509_ = p_334281_;
        this.f_19510_ = p_332569_;
    }

    public MobEffectInstance(MobEffectInstance p_19543_) {
        this.f_19502_ = p_19543_.f_19502_;
        this.m_19548_(p_19543_);
    }

    private MobEffectInstance(Holder<MobEffect> p_330051_, MobEffectInstance.Details p_332322_) {
        this(
            p_330051_,
            p_332322_.f_316574_(),
            p_332322_.f_316534_(),
            p_332322_.f_314727_(),
            p_332322_.f_314365_(),
            p_332322_.f_314718_(),
            p_332322_.f_315812_().map(p_326756_ -> new MobEffectInstance(p_330051_, p_326756_)).orElse(null)
        );
    }

    private MobEffectInstance.Details m_324991_() {
        return new MobEffectInstance.Details(
            this.m_19564_(),
            this.m_19557_(),
            this.m_19571_(),
            this.m_19572_(),
            this.m_19575_(),
            Optional.ofNullable(this.f_19510_).map(MobEffectInstance::m_324991_)
        );
    }

    public float m_318631_(LivingEntity p_333473_, float p_327866_) {
        return this.f_317081_.m_322860_(p_333473_, p_327866_);
    }

    public ParticleOptions m_319016_() {
        return this.f_19502_.m_203334_().m_321363_(this);
    }

    void m_19548_(MobEffectInstance p_19549_) {
        this.f_19503_ = p_19549_.f_19503_;
        this.f_19504_ = p_19549_.f_19504_;
        this.f_19506_ = p_19549_.f_19506_;
        this.f_19508_ = p_19549_.f_19508_;
        this.f_19509_ = p_19549_.f_19509_;
    }

    public boolean m_19558_(MobEffectInstance p_19559_) {
        if (!this.f_19502_.equals(p_19559_.f_19502_)) {
            f_19501_.warn("This method should only be called for matching effects!");
        }

        boolean flag = false;
        if (p_19559_.f_19504_ > this.f_19504_) {
            if (p_19559_.m_267670_(this)) {
                MobEffectInstance mobeffectinstance = this.f_19510_;
                this.f_19510_ = new MobEffectInstance(this);
                this.f_19510_.f_19510_ = mobeffectinstance;
            }

            this.f_19504_ = p_19559_.f_19504_;
            this.f_19503_ = p_19559_.f_19503_;
            flag = true;
        } else if (this.m_267670_(p_19559_)) {
            if (p_19559_.f_19504_ == this.f_19504_) {
                this.f_19503_ = p_19559_.f_19503_;
                flag = true;
            } else if (this.f_19510_ == null) {
                this.f_19510_ = new MobEffectInstance(p_19559_);
            } else {
                this.f_19510_.m_19558_(p_19559_);
            }
        }

        if (!p_19559_.f_19506_ && this.f_19506_ || flag) {
            this.f_19506_ = p_19559_.f_19506_;
            flag = true;
        }

        if (p_19559_.f_19508_ != this.f_19508_) {
            this.f_19508_ = p_19559_.f_19508_;
            flag = true;
        }

        if (p_19559_.f_19509_ != this.f_19509_) {
            this.f_19509_ = p_19559_.f_19509_;
            flag = true;
        }

        return flag;
    }

    private boolean m_267670_(MobEffectInstance p_268133_) {
        return !this.m_267577_() && (this.f_19503_ < p_268133_.f_19503_ || p_268133_.m_267577_());
    }

    public boolean m_267577_() {
        return this.f_19503_ == -1;
    }

    public boolean m_267633_(int p_268088_) {
        return !this.m_267577_() && this.f_19503_ <= p_268088_;
    }

    public int m_267696_(Int2IntFunction p_268089_) {
        return !this.m_267577_() && this.f_19503_ != 0 ? p_268089_.applyAsInt(this.f_19503_) : this.f_19503_;
    }

    public Holder<MobEffect> m_19544_() {
        return this.f_19502_;
    }

    public int m_19557_() {
        return this.f_19503_;
    }

    public int m_19564_() {
        return this.f_19504_;
    }

    public boolean m_19571_() {
        return this.f_19506_;
    }

    public boolean m_19572_() {
        return this.f_19508_;
    }

    public boolean m_19575_() {
        return this.f_19509_;
    }

    public boolean m_19552_(LivingEntity p_19553_, Runnable p_19554_) {
        if (this.m_267725_()) {
            int i = this.m_267577_() ? p_19553_.f_19797_ : this.f_19503_;
            if (this.f_19502_.m_203334_().m_19443_(i, this.f_19504_) && !this.f_19502_.m_203334_().m_294194_(p_19553_, this.f_19504_)) {
                p_19553_.m_21195_(this.f_19502_);
            }

            this.m_19579_();
            if (this.f_19503_ == 0 && this.f_19510_ != null) {
                this.m_19548_(this.f_19510_);
                this.f_19510_ = this.f_19510_.f_19510_;
                p_19554_.run();
            }
        }

        this.f_317081_.m_319519_(this);
        return this.m_267725_();
    }

    private boolean m_267725_() {
        return this.m_267577_() || this.f_19503_ > 0;
    }

    private int m_19579_() {
        if (this.f_19510_ != null) {
            this.f_19510_.m_19579_();
        }

        return this.f_19503_ = this.m_267696_(p_267916_ -> p_267916_ - 1);
    }

    public void m_292680_(LivingEntity p_297679_) {
        this.f_19502_.m_203334_().m_292868_(p_297679_, this.f_19504_);
    }

    public void m_325044_(LivingEntity p_329318_, Entity.RemovalReason p_333232_) {
        this.f_19502_.m_203334_().m_319157_(p_329318_, this.f_19504_, p_333232_);
    }

    public void m_321810_(LivingEntity p_327684_, DamageSource p_328403_, float p_331463_) {
        this.f_19502_.m_203334_().m_6742_(p_327684_, this.f_19504_, p_328403_, p_331463_);
    }

    public String m_19576_() {
        return this.f_19502_.m_203334_().m_19481_();
    }

    @Override
    public String toString() {
        String s;
        if (this.f_19504_ > 0) {
            s = this.m_19576_() + " x " + (this.f_19504_ + 1) + ", Duration: " + this.m_267740_();
        } else {
            s = this.m_19576_() + ", Duration: " + this.m_267740_();
        }

        if (!this.f_19508_) {
            s = s + ", Particles: false";
        }

        if (!this.f_19509_) {
            s = s + ", Show Icon: false";
        }

        return s;
    }

    private String m_267740_() {
        return this.m_267577_() ? "infinite" : Integer.toString(this.f_19503_);
    }

    @Override
    public boolean equals(Object p_19574_) {
        if (this == p_19574_) {
            return true;
        } else {
            return !(p_19574_ instanceof MobEffectInstance mobeffectinstance)
                ? false
                : this.f_19503_ == mobeffectinstance.f_19503_
                    && this.f_19504_ == mobeffectinstance.f_19504_
                    && this.f_19506_ == mobeffectinstance.f_19506_
                    && this.f_19508_ == mobeffectinstance.f_19508_
                    && this.f_19509_ == mobeffectinstance.f_19509_
                    && this.f_19502_.equals(mobeffectinstance.f_19502_);
        }
    }

    @Override
    public int hashCode() {
        int i = this.f_19502_.hashCode();
        i = 31 * i + this.f_19503_;
        i = 31 * i + this.f_19504_;
        i = 31 * i + (this.f_19506_ ? 1 : 0);
        i = 31 * i + (this.f_19508_ ? 1 : 0);
        return 31 * i + (this.f_19509_ ? 1 : 0);
    }

    public Tag m_19555_() {
        return f_316026_.encodeStart(NbtOps.f_128958_, this).getOrThrow();
    }

    @Nullable
    public static MobEffectInstance m_19560_(CompoundTag p_19561_) {
        return f_316026_.parse(NbtOps.f_128958_, p_19561_).resultOrPartial(f_19501_::error).orElse(null);
    }

    public int compareTo(MobEffectInstance p_19566_) {
        int i = 32147;
        return (this.m_19557_() <= 32147 || p_19566_.m_19557_() <= 32147) && (!this.m_19571_() || !p_19566_.m_19571_())
            ? ComparisonChain.start()
                .compareFalseFirst(this.m_19571_(), p_19566_.m_19571_())
                .compareFalseFirst(this.m_267577_(), p_19566_.m_267577_())
                .compare(this.m_19557_(), p_19566_.m_19557_())
                .compare(this.m_19544_().m_203334_().m_19484_(), p_19566_.m_19544_().m_203334_().m_19484_())
                .result()
            : ComparisonChain.start()
                .compare(this.m_19571_(), p_19566_.m_19571_())
                .compare(this.m_19544_().m_203334_().m_19484_(), p_19566_.m_19544_().m_203334_().m_19484_())
                .result();
    }

    public void m_322321_(LivingEntity p_334348_) {
        this.f_19502_.m_203334_().m_325074_(p_334348_, this.f_19504_);
    }

    public boolean m_323663_(Holder<MobEffect> p_329529_) {
        return this.f_19502_.equals(p_329529_);
    }

    public void m_324193_(MobEffectInstance p_335404_) {
        this.f_317081_.m_324074_(p_335404_.f_317081_);
    }

    public void m_320166_() {
        this.f_317081_.m_318781_(this);
    }

    static class BlendState {
        private float f_315287_;
        private float f_315595_;

        public void m_318781_(MobEffectInstance p_333918_) {
            this.f_315287_ = m_323207_(p_333918_);
            this.f_315595_ = this.f_315287_;
        }

        public void m_324074_(MobEffectInstance.BlendState p_327821_) {
            this.f_315287_ = p_327821_.f_315287_;
            this.f_315595_ = p_327821_.f_315595_;
        }

        public void m_319519_(MobEffectInstance p_330345_) {
            this.f_315595_ = this.f_315287_;
            int i = m_324372_(p_330345_);
            if (i == 0) {
                this.f_315287_ = 1.0F;
            } else {
                float f = m_323207_(p_330345_);
                if (this.f_315287_ != f) {
                    float f1 = 1.0F / (float)i;
                    this.f_315287_ = this.f_315287_ + Mth.m_14036_(f - this.f_315287_, -f1, f1);
                }
            }
        }

        private static float m_323207_(MobEffectInstance p_334116_) {
            boolean flag = !p_334116_.m_267633_(m_324372_(p_334116_));
            return flag ? 1.0F : 0.0F;
        }

        private static int m_324372_(MobEffectInstance p_335826_) {
            return p_335826_.m_19544_().m_203334_().m_323916_();
        }

        public float m_322860_(LivingEntity p_333208_, float p_330792_) {
            if (p_333208_.m_213877_()) {
                this.f_315595_ = this.f_315287_;
            }

            return Mth.m_14179_(p_330792_, this.f_315595_, this.f_315287_);
        }
    }

    static record Details(int f_316534_, int f_316574_, boolean f_314727_, boolean f_314365_, boolean f_314718_, Optional<MobEffectInstance.Details> f_315812_) {
        public static final MapCodec<MobEffectInstance.Details> f_316395_ = MapCodec.recursive(
            "MobEffectInstance.Details",
            p_332855_ -> RecordCodecBuilder.mapCodec(
                    p_327980_ -> p_327980_.group(
                                ExtraCodecs.f_316863_.optionalFieldOf("amplifier", 0).forGetter(MobEffectInstance.Details::f_316534_),
                                Codec.INT.optionalFieldOf("duration", Integer.valueOf(0)).forGetter(MobEffectInstance.Details::f_316574_),
                                Codec.BOOL.optionalFieldOf("ambient", Boolean.valueOf(false)).forGetter(MobEffectInstance.Details::f_314727_),
                                Codec.BOOL.optionalFieldOf("show_particles", Boolean.valueOf(true)).forGetter(MobEffectInstance.Details::f_314365_),
                                Codec.BOOL.optionalFieldOf("show_icon").forGetter(p_330483_ -> Optional.of(p_330483_.f_314718_())),
                                p_332855_.optionalFieldOf("hidden_effect").forGetter(MobEffectInstance.Details::f_315812_)
                            )
                            .apply(p_327980_, MobEffectInstance.Details::m_323128_)
                )
        );
        public static final StreamCodec<ByteBuf, MobEffectInstance.Details> f_315344_ = StreamCodec.m_320869_(
            p_333279_ -> StreamCodec.m_322230_(
                    ByteBufCodecs.f_316730_,
                    MobEffectInstance.Details::f_316534_,
                    ByteBufCodecs.f_316730_,
                    MobEffectInstance.Details::f_316574_,
                    ByteBufCodecs.f_315514_,
                    MobEffectInstance.Details::f_314727_,
                    ByteBufCodecs.f_315514_,
                    MobEffectInstance.Details::f_314365_,
                    ByteBufCodecs.f_315514_,
                    MobEffectInstance.Details::f_314718_,
                    p_333279_.m_321801_(ByteBufCodecs::m_319027_),
                    MobEffectInstance.Details::f_315812_,
                    MobEffectInstance.Details::new
                )
        );

        private static MobEffectInstance.Details m_323128_(
            int p_334251_, int p_332882_, boolean p_330487_, boolean p_334607_, Optional<Boolean> p_329280_, Optional<MobEffectInstance.Details> p_330477_
        ) {
            return new MobEffectInstance.Details(p_334251_, p_332882_, p_330487_, p_334607_, p_329280_.orElse(p_334607_), p_330477_);
        }
    }
}
