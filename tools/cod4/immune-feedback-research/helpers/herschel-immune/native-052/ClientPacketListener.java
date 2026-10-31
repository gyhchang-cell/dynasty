package net.minecraft.client.multiplayer;

import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import com.google.common.collect.Sets;
import com.mojang.authlib.GameProfile;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.ParseResults;
import com.mojang.datafixers.util.Pair;
import com.mojang.logging.LogUtils;
import it.unimi.dsi.fastutil.objects.ReferenceOpenHashSet;
import it.unimi.dsi.fastutil.objects.Object2IntMap.Entry;
import java.time.Instant;
import java.util.BitSet;
import java.util.Collection;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import javax.annotation.Nullable;
import net.minecraft.advancements.AdvancementHolder;
import net.minecraft.client.ClientRecipeBook;
import net.minecraft.client.DebugQueryHandler;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Options;
import net.minecraft.client.gui.MapRenderer;
import net.minecraft.client.gui.components.ChatComponent;
import net.minecraft.client.gui.components.toasts.RecipeToast;
import net.minecraft.client.gui.components.toasts.SystemToast;
import net.minecraft.client.gui.screens.DeathScreen;
import net.minecraft.client.gui.screens.DemoIntroScreen;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraft.client.gui.screens.ReceivingLevelScreen;
import net.minecraft.client.gui.screens.WinScreen;
import net.minecraft.client.gui.screens.achievement.StatsScreen;
import net.minecraft.client.gui.screens.inventory.BookViewScreen;
import net.minecraft.client.gui.screens.inventory.CommandBlockEditScreen;
import net.minecraft.client.gui.screens.inventory.CreativeModeInventoryScreen;
import net.minecraft.client.gui.screens.inventory.HorseInventoryScreen;
import net.minecraft.client.gui.screens.multiplayer.ServerReconfigScreen;
import net.minecraft.client.gui.screens.recipebook.RecipeBookComponent;
import net.minecraft.client.gui.screens.recipebook.RecipeCollection;
import net.minecraft.client.gui.screens.recipebook.RecipeUpdateListener;
import net.minecraft.client.particle.ItemPickupParticle;
import net.minecraft.client.player.KeyboardInput;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.player.RemotePlayer;
import net.minecraft.client.renderer.debug.BrainDebugRenderer;
import net.minecraft.client.renderer.debug.NeighborsUpdateRenderer;
import net.minecraft.client.renderer.debug.VillageSectionsDebugRenderer;
import net.minecraft.client.renderer.debug.WorldGenAttemptRenderer;
import net.minecraft.client.resources.sounds.BeeAggressiveSoundInstance;
import net.minecraft.client.resources.sounds.BeeFlyingSoundInstance;
import net.minecraft.client.resources.sounds.BeeSoundInstance;
import net.minecraft.client.resources.sounds.GuardianAttackSoundInstance;
import net.minecraft.client.resources.sounds.MinecartSoundInstance;
import net.minecraft.client.resources.sounds.SnifferSoundInstance;
import net.minecraft.commands.CommandBuildContext;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.commands.arguments.ArgumentSignatures;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.SectionPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.TickablePacketListener;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.LastSeenMessagesTracker;
import net.minecraft.network.chat.LocalChatSession;
import net.minecraft.network.chat.MessageSignature;
import net.minecraft.network.chat.MessageSignatureCache;
import net.minecraft.network.chat.PlayerChatMessage;
import net.minecraft.network.chat.RemoteChatSession;
import net.minecraft.network.chat.SignableCommand;
import net.minecraft.network.chat.SignedMessageBody;
import net.minecraft.network.chat.SignedMessageChain;
import net.minecraft.network.chat.SignedMessageLink;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.PacketUtils;
import net.minecraft.network.protocol.common.ClientboundUpdateTagsPacket;
import net.minecraft.network.protocol.common.custom.BeeDebugPayload;
import net.minecraft.network.protocol.common.custom.BrainDebugPayload;
import net.minecraft.network.protocol.common.custom.BreezeDebugPayload;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.network.protocol.common.custom.GameEventDebugPayload;
import net.minecraft.network.protocol.common.custom.GameEventListenerDebugPayload;
import net.minecraft.network.protocol.common.custom.GameTestAddMarkerDebugPayload;
import net.minecraft.network.protocol.common.custom.GameTestClearMarkersDebugPayload;
import net.minecraft.network.protocol.common.custom.GoalDebugPayload;
import net.minecraft.network.protocol.common.custom.HiveDebugPayload;
import net.minecraft.network.protocol.common.custom.NeighborUpdatesDebugPayload;
import net.minecraft.network.protocol.common.custom.PathfindingDebugPayload;
import net.minecraft.network.protocol.common.custom.PoiAddedDebugPayload;
import net.minecraft.network.protocol.common.custom.PoiRemovedDebugPayload;
import net.minecraft.network.protocol.common.custom.PoiTicketCountDebugPayload;
import net.minecraft.network.protocol.common.custom.RaidsDebugPayload;
import net.minecraft.network.protocol.common.custom.StructuresDebugPayload;
import net.minecraft.network.protocol.common.custom.VillageSectionsDebugPayload;
import net.minecraft.network.protocol.common.custom.WorldGenAttemptDebugPayload;
import net.minecraft.network.protocol.configuration.ConfigurationProtocols;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundAddEntityPacket;
import net.minecraft.network.protocol.game.ClientboundAddExperienceOrbPacket;
import net.minecraft.network.protocol.game.ClientboundAnimatePacket;
import net.minecraft.network.protocol.game.ClientboundAwardStatsPacket;
import net.minecraft.network.protocol.game.ClientboundBlockChangedAckPacket;
import net.minecraft.network.protocol.game.ClientboundBlockDestructionPacket;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.network.protocol.game.ClientboundBlockEventPacket;
import net.minecraft.network.protocol.game.ClientboundBlockUpdatePacket;
import net.minecraft.network.protocol.game.ClientboundBossEventPacket;
import net.minecraft.network.protocol.game.ClientboundBundlePacket;
import net.minecraft.network.protocol.game.ClientboundChangeDifficultyPacket;
import net.minecraft.network.protocol.game.ClientboundChunkBatchFinishedPacket;
import net.minecraft.network.protocol.game.ClientboundChunkBatchStartPacket;
import net.minecraft.network.protocol.game.ClientboundChunksBiomesPacket;
import net.minecraft.network.protocol.game.ClientboundClearTitlesPacket;
import net.minecraft.network.protocol.game.ClientboundCommandSuggestionsPacket;
import net.minecraft.network.protocol.game.ClientboundCommandsPacket;
import net.minecraft.network.protocol.game.ClientboundContainerClosePacket;
import net.minecraft.network.protocol.game.ClientboundContainerSetContentPacket;
import net.minecraft.network.protocol.game.ClientboundContainerSetDataPacket;
import net.minecraft.network.protocol.game.ClientboundContainerSetSlotPacket;
import net.minecraft.network.protocol.game.ClientboundCooldownPacket;
import net.minecraft.network.protocol.game.ClientboundCustomChatCompletionsPacket;
import net.minecraft.network.protocol.game.ClientboundDamageEventPacket;
import net.minecraft.network.protocol.game.ClientboundDebugSamplePacket;
import net.minecraft.network.protocol.game.ClientboundDeleteChatPacket;
import net.minecraft.network.protocol.game.ClientboundDisguisedChatPacket;
import net.minecraft.network.protocol.game.ClientboundEntityEventPacket;
import net.minecraft.network.protocol.game.ClientboundExplodePacket;
import net.minecraft.network.protocol.game.ClientboundForgetLevelChunkPacket;
import net.minecraft.network.protocol.game.ClientboundGameEventPacket;
import net.minecraft.network.protocol.game.ClientboundHorseScreenOpenPacket;
import net.minecraft.network.protocol.game.ClientboundHurtAnimationPacket;
import net.minecraft.network.protocol.game.ClientboundInitializeBorderPacket;
import net.minecraft.network.protocol.game.ClientboundLevelChunkPacketData;
import net.minecraft.network.protocol.game.ClientboundLevelChunkWithLightPacket;
import net.minecraft.network.protocol.game.ClientboundLevelEventPacket;
import net.minecraft.network.protocol.game.ClientboundLevelParticlesPacket;
import net.minecraft.network.protocol.game.ClientboundLightUpdatePacket;
import net.minecraft.network.protocol.game.ClientboundLightUpdatePacketData;
import net.minecraft.network.protocol.game.ClientboundLoginPacket;
import net.minecraft.network.protocol.game.ClientboundMapItemDataPacket;
import net.minecraft.network.protocol.game.ClientboundMerchantOffersPacket;
import net.minecraft.network.protocol.game.ClientboundMoveEntityPacket;
import net.minecraft.network.protocol.game.ClientboundMoveVehiclePacket;
import net.minecraft.network.protocol.game.ClientboundOpenBookPacket;
import net.minecraft.network.protocol.game.ClientboundOpenScreenPacket;
import net.minecraft.network.protocol.game.ClientboundOpenSignEditorPacket;
import net.minecraft.network.protocol.game.ClientboundPlaceGhostRecipePacket;
import net.minecraft.network.protocol.game.ClientboundPlayerAbilitiesPacket;
import net.minecraft.network.protocol.game.ClientboundPlayerChatPacket;
import net.minecraft.network.protocol.game.ClientboundPlayerCombatEndPacket;
import net.minecraft.network.protocol.game.ClientboundPlayerCombatEnterPacket;
import net.minecraft.network.protocol.game.ClientboundPlayerCombatKillPacket;
import net.minecraft.network.protocol.game.ClientboundPlayerInfoRemovePacket;
import net.minecraft.network.protocol.game.ClientboundPlayerInfoUpdatePacket;
import net.minecraft.network.protocol.game.ClientboundPlayerLookAtPacket;
import net.minecraft.network.protocol.game.ClientboundPlayerPositionPacket;
import net.minecraft.network.protocol.game.ClientboundProjectilePowerPacket;
import net.minecraft.network.protocol.game.ClientboundRecipePacket;
import net.minecraft.network.protocol.game.ClientboundRemoveEntitiesPacket;
import net.minecraft.network.protocol.game.ClientboundRemoveMobEffectPacket;
import net.minecraft.network.protocol.game.ClientboundResetScorePacket;
import net.minecraft.network.protocol.game.ClientboundRespawnPacket;
import net.minecraft.network.protocol.game.ClientboundRotateHeadPacket;
import net.minecraft.network.protocol.game.ClientboundSectionBlocksUpdatePacket;
import net.minecraft.network.protocol.game.ClientboundSelectAdvancementsTabPacket;
import net.minecraft.network.protocol.game.ClientboundServerDataPacket;
import net.minecraft.network.protocol.game.ClientboundSetActionBarTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetBorderCenterPacket;
import net.minecraft.network.protocol.game.ClientboundSetBorderLerpSizePacket;
import net.minecraft.network.protocol.game.ClientboundSetBorderSizePacket;
import net.minecraft.network.protocol.game.ClientboundSetBorderWarningDelayPacket;
import net.minecraft.network.protocol.game.ClientboundSetBorderWarningDistancePacket;
import net.minecraft.network.protocol.game.ClientboundSetCameraPacket;
import net.minecraft.network.protocol.game.ClientboundSetCarriedItemPacket;
import net.minecraft.network.protocol.game.ClientboundSetChunkCacheCenterPacket;
import net.minecraft.network.protocol.game.ClientboundSetChunkCacheRadiusPacket;
import net.minecraft.network.protocol.game.ClientboundSetDefaultSpawnPositionPacket;
import net.minecraft.network.protocol.game.ClientboundSetDisplayObjectivePacket;
import net.minecraft.network.protocol.game.ClientboundSetEntityDataPacket;
import net.minecraft.network.protocol.game.ClientboundSetEntityLinkPacket;
import net.minecraft.network.protocol.game.ClientboundSetEntityMotionPacket;
import net.minecraft.network.protocol.game.ClientboundSetEquipmentPacket;
import net.minecraft.network.protocol.game.ClientboundSetExperiencePacket;
import net.minecraft.network.protocol.game.ClientboundSetHealthPacket;
import net.minecraft.network.protocol.game.ClientboundSetObjectivePacket;
import net.minecraft.network.protocol.game.ClientboundSetPassengersPacket;
import net.minecraft.network.protocol.game.ClientboundSetPlayerTeamPacket;
import net.minecraft.network.protocol.game.ClientboundSetScorePacket;
import net.minecraft.network.protocol.game.ClientboundSetSimulationDistancePacket;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTimePacket;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.network.protocol.game.ClientboundSoundEntityPacket;
import net.minecraft.network.protocol.game.ClientboundSoundPacket;
import net.minecraft.network.protocol.game.ClientboundStartConfigurationPacket;
import net.minecraft.network.protocol.game.ClientboundStopSoundPacket;
import net.minecraft.network.protocol.game.ClientboundSystemChatPacket;
import net.minecraft.network.protocol.game.ClientboundTabListPacket;
import net.minecraft.network.protocol.game.ClientboundTagQueryPacket;
import net.minecraft.network.protocol.game.ClientboundTakeItemEntityPacket;
import net.minecraft.network.protocol.game.ClientboundTeleportEntityPacket;
import net.minecraft.network.protocol.game.ClientboundTickingStatePacket;
import net.minecraft.network.protocol.game.ClientboundTickingStepPacket;
import net.minecraft.network.protocol.game.ClientboundUpdateAdvancementsPacket;
import net.minecraft.network.protocol.game.ClientboundUpdateAttributesPacket;
import net.minecraft.network.protocol.game.ClientboundUpdateMobEffectPacket;
import net.minecraft.network.protocol.game.ClientboundUpdateRecipesPacket;
import net.minecraft.network.protocol.game.CommonPlayerSpawnInfo;
import net.minecraft.network.protocol.game.ServerboundAcceptTeleportationPacket;
import net.minecraft.network.protocol.game.ServerboundChatAckPacket;
import net.minecraft.network.protocol.game.ServerboundChatCommandPacket;
import net.minecraft.network.protocol.game.ServerboundChatCommandSignedPacket;
import net.minecraft.network.protocol.game.ServerboundChatPacket;
import net.minecraft.network.protocol.game.ServerboundChatSessionUpdatePacket;
import net.minecraft.network.protocol.game.ServerboundChunkBatchReceivedPacket;
import net.minecraft.network.protocol.game.ServerboundClientCommandPacket;
import net.minecraft.network.protocol.game.ServerboundConfigurationAcknowledgedPacket;
import net.minecraft.network.protocol.game.ServerboundMovePlayerPacket;
import net.minecraft.network.protocol.game.ServerboundMoveVehiclePacket;
import net.minecraft.network.protocol.game.VecDeltaCodec;
import net.minecraft.network.protocol.ping.ClientboundPongResponsePacket;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.ServerLinks;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stat;
import net.minecraft.stats.StatsCounter;
import net.minecraft.util.Crypt;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.util.SignatureValidator;
import net.minecraft.world.Difficulty;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.TickRateManager;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ExperienceOrb;
import net.minecraft.world.entity.Leashable;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.RelativeMovement;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeMap;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.animal.Bee;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraft.world.entity.animal.sniffer.Sniffer;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.Guardian;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.player.ProfileKeyPair;
import net.minecraft.world.entity.player.ProfilePublicKey;
import net.minecraft.world.entity.projectile.AbstractHurtingProjectile;
import net.minecraft.world.entity.vehicle.AbstractMinecart;
import net.minecraft.world.entity.vehicle.Boat;
import net.minecraft.world.flag.FeatureFlagSet;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.HorseInventoryMenu;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.inventory.MerchantMenu;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.alchemy.PotionBrewing;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Explosion;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.CommandBlockEntity;
import net.minecraft.world.level.block.entity.SignBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.border.WorldBorder;
import net.minecraft.world.level.chunk.DataLayer;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.LevelChunkSection;
import net.minecraft.world.level.dimension.DimensionType;
import net.minecraft.world.level.lighting.LevelLightEngine;
import net.minecraft.world.level.saveddata.maps.MapId;
import net.minecraft.world.level.saveddata.maps.MapItemSavedData;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.scores.Objective;
import net.minecraft.world.scores.PlayerTeam;
import net.minecraft.world.scores.ScoreAccess;
import net.minecraft.world.scores.ScoreHolder;
import net.minecraft.world.scores.Scoreboard;
import net.minecraft.world.scores.Team;
import net.minecraft.world.scores.criteria.ObjectiveCriteria;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.slf4j.Logger;

@OnlyIn(Dist.CLIENT)
public class ClientPacketListener extends ClientCommonPacketListenerImpl implements ClientGamePacketListener, TickablePacketListener {
    private static final Logger f_104883_ = LogUtils.getLogger();
    private static final Component f_242953_ = Component.m_237115_("multiplayer.unsecureserver.toast.title");
    private static final Component f_242949_ = Component.m_237115_("multiplayer.unsecureserver.toast");
    private static final Component f_244321_ = Component.m_237115_("multiplayer.disconnect.invalid_packet");
    private static final Component f_243809_ = Component.m_237115_("multiplayer.disconnect.chat_validation_failed");
    private static final Component f_291494_ = Component.m_237115_("connect.reconfiguring");
    private static final int f_243949_ = 64;
    private final GameProfile f_104886_;
    private ClientLevel f_104889_;
    private ClientLevel.ClientLevelData f_104890_;
    private final Map<UUID, PlayerInfo> f_104892_ = Maps.newHashMap();
    private final Set<PlayerInfo> f_244156_ = new ReferenceOpenHashSet<>();
    private final ClientAdvancements f_104893_;
    private final ClientSuggestionProvider f_104894_;
    private final DebugQueryHandler f_104896_ = new DebugQueryHandler(this);
    private int f_104897_ = 3;
    private int f_194190_ = 3;
    private final RandomSource f_104898_ = RandomSource.m_216337_();
    public CommandDispatcher<SharedSuggestionProvider> f_104899_ = new CommandDispatcher<>();
    private final RecipeManager f_104900_;
    private final UUID f_104901_ = UUID.randomUUID();
    private Set<ResourceKey<Level>> f_104902_;
    private final RegistryAccess.Frozen f_104903_;
    private final FeatureFlagSet f_244039_;
    private final PotionBrewing f_315607_;
    @Nullable
    private LocalChatSession f_252517_;
    private SignedMessageChain.Encoder f_240902_ = SignedMessageChain.Encoder.f_243849_;
    private LastSeenMessagesTracker f_244346_ = new LastSeenMessagesTracker(20);
    private MessageSignatureCache f_244113_ = MessageSignatureCache.m_246587_();
    private final ChunkBatchSizeCalculator f_291253_ = new ChunkBatchSizeCalculator();
    private final PingDebugMonitor f_290671_;
    private final DebugSampleSubscriber f_316489_;
    @Nullable
    private LevelLoadStatusManager f_302509_;
    private boolean f_316183_;
    private boolean f_291332_ = false;
    private volatile boolean f_291533_;
    private final Scoreboard f_315162_ = new Scoreboard();
    private final SessionSearchTrees f_337492_ = new SessionSearchTrees();

    public ClientPacketListener(Minecraft p_253924_, Connection p_253614_, CommonListenerCookie p_298329_) {
        super(p_253924_, p_253614_, p_298329_);
        this.f_104886_ = p_298329_.f_291743_();
        this.f_104903_ = p_298329_.f_291549_();
        this.f_244039_ = p_298329_.f_290859_();
        this.f_104893_ = new ClientAdvancements(p_253924_, this.f_291019_);
        this.f_104894_ = new ClientSuggestionProvider(this, p_253924_);
        this.f_290671_ = new PingDebugMonitor(this, p_253924_.m_293199_().m_294664_());
        this.f_104900_ = new RecipeManager(this.f_104903_);
        this.f_316489_ = new DebugSampleSubscriber(this, p_253924_.m_293199_());
        if (p_298329_.f_315631_() != null) {
            p_253924_.f_91065_.m_93076_().m_324317_(p_298329_.f_315631_());
        }

        this.f_315607_ = PotionBrewing.m_320553_(this.f_244039_);
    }

    public ClientSuggestionProvider m_105137_() {
        return this.f_104894_;
    }

    public void m_261044_() {
        this.f_291533_ = true;
        this.m_306072_();
        this.f_291019_.m_261027_();
    }

    public void m_306072_() {
        this.f_104889_ = null;
        this.f_302509_ = null;
    }

    public RecipeManager m_105141_() {
        return this.f_104900_;
    }

    @Override
    public void m_5998_(ClientboundLoginPacket p_105030_) {
        PacketUtils.m_131363_(p_105030_, this, this.f_291812_);
        this.f_291812_.f_91072_ = new MultiPlayerGameMode(this.f_291812_, this);
        CommonPlayerSpawnInfo commonplayerspawninfo = p_105030_.f_291078_();
        List<ResourceKey<Level>> list = Lists.newArrayList(p_105030_.f_132365_());
        Collections.shuffle(list);
        this.f_104902_ = Sets.newLinkedHashSet(list);
        ResourceKey<Level> resourcekey = commonplayerspawninfo.f_290731_();
        Holder<DimensionType> holder = commonplayerspawninfo.f_291865_();
        this.f_104897_ = p_105030_.f_132370_();
        this.f_194190_ = p_105030_.f_195761_();
        boolean flag = commonplayerspawninfo.f_290330_();
        boolean flag1 = commonplayerspawninfo.f_290486_();
        ClientLevel.ClientLevelData clientlevel$clientleveldata = new ClientLevel.ClientLevelData(Difficulty.NORMAL, p_105030_.f_132362_(), flag1);
        this.f_104890_ = clientlevel$clientleveldata;
        this.f_104889_ = new ClientLevel(
            this,
            clientlevel$clientleveldata,
            resourcekey,
            holder,
            this.f_104897_,
            this.f_194190_,
            this.f_291812_::m_91307_,
            this.f_291812_.f_91060_,
            flag,
            commonplayerspawninfo.f_290589_()
        );
        this.f_291812_.m_91156_(this.f_104889_, ReceivingLevelScreen.Reason.OTHER);
        if (this.f_291812_.f_91074_ == null) {
            this.f_291812_.f_91074_ = this.f_291812_.f_91072_.m_105246_(this.f_104889_, new StatsCounter(), new ClientRecipeBook());
            this.f_291812_.f_91074_.m_146922_(-180.0F);
            if (this.f_291812_.m_91092_() != null) {
                this.f_291812_.m_91092_().m_120046_(this.f_291812_.f_91074_.m_20148_());
            }
        }

        this.f_291812_.f_91064_.m_113434_();
        this.f_291812_.f_91074_.m_172530_();
        net.minecraftforge.client.event.ForgeEventFactoryClient.firePlayerLogin(this.f_291812_.f_91072_, this.f_291812_.f_91074_, this.f_291812_.m_91403_().f_290549_);
        this.f_291812_.f_91074_.m_20234_(p_105030_.f_132360_());
        this.f_104889_.m_104739_(this.f_291812_.f_91074_);
        this.f_291812_.f_91074_.f_108618_ = new KeyboardInput(this.f_291812_.f_91066_);
        this.f_291812_.f_91072_.m_105221_(this.f_291812_.f_91074_);
        this.f_291812_.f_91075_ = this.f_291812_.f_91074_;
        this.m_306243_(this.f_291812_.f_91074_, this.f_104889_, ReceivingLevelScreen.Reason.OTHER);
        this.f_291812_.f_91074_.m_36393_(p_105030_.f_132371_());
        this.f_291812_.f_91074_.m_108711_(p_105030_.f_132372_());
        this.f_291812_.f_91074_.m_294300_(p_105030_.f_291478_());
        this.f_291812_.f_91074_.m_219749_(commonplayerspawninfo.f_290601_());
        this.f_291812_.f_91074_.m_287199_(commonplayerspawninfo.f_291470_());
        this.f_291812_.f_91072_.m_171805_(commonplayerspawninfo.f_291098_(), commonplayerspawninfo.f_290730_());
        this.f_291812_.f_91066_.m_193770_(p_105030_.f_132370_());
        this.f_252517_ = null;
        this.f_244346_ = new LastSeenMessagesTracker(20);
        this.f_244113_ = MessageSignatureCache.m_246587_();
        if (this.f_290549_.m_129535_()) {
            this.f_291812_.m_231465_().m_252904_().thenAcceptAsync(p_253341_ -> p_253341_.ifPresent(this::m_260951_), this.f_291812_);
        }

        this.f_291019_.m_260888_(commonplayerspawninfo.f_291098_(), p_105030_.f_132362_());
        this.f_291812_.m_278644_().m_278768_(this.f_291812_);
        this.f_316183_ = p_105030_.f_316348_();
        if (this.f_291024_ != null && !this.f_291332_ && !this.m_253150_()) {
            SystemToast systemtoast = SystemToast.m_94847_(this.f_291812_, SystemToast.SystemToastId.f_302594_, f_242953_, f_242949_);
            this.f_291812_.m_91300_().m_94922_(systemtoast);
            this.f_291332_ = true;
        }
    }

    @Override
    public void m_6771_(ClientboundAddEntityPacket p_104958_) {
        PacketUtils.m_131363_(p_104958_, this, this.f_291812_);
        Entity entity = this.m_301496_(p_104958_);
        if (entity != null) {
            entity.m_141965_(p_104958_);
            this.f_104889_.m_104739_(entity);
            this.m_233663_(entity);
        } else {
            f_104883_.warn("Skipping Entity with id {}", p_104958_.m_131508_());
        }
    }

    @Nullable
    private Entity m_301496_(ClientboundAddEntityPacket p_301611_) {
        EntityType<?> entitytype = p_301611_.m_131508_();
        if (entitytype == EntityType.f_20532_) {
            PlayerInfo playerinfo = this.m_104949_(p_301611_.m_131499_());
            if (playerinfo == null) {
                f_104883_.warn("Server attempted to add player prior to sending player info (Player id {})", p_301611_.m_131499_());
                return null;
            } else {
                return new RemotePlayer(this.f_104889_, playerinfo.m_105312_());
            }
        } else {
            return entitytype.m_20615_(this.f_104889_);
        }
    }

    private void m_233663_(Entity p_233664_) {
        if (p_233664_ instanceof AbstractMinecart abstractminecart) {
            this.f_291812_.m_91106_().m_120367_(new MinecartSoundInstance(abstractminecart));
        } else if (p_233664_ instanceof Bee bee) {
            boolean flag = bee.m_21660_();
            BeeSoundInstance beesoundinstance;
            if (flag) {
                beesoundinstance = new BeeAggressiveSoundInstance(bee);
            } else {
                beesoundinstance = new BeeFlyingSoundInstance(bee);
            }

            this.f_291812_.m_91106_().m_120372_(beesoundinstance);
        }
    }

    @Override
    public void m_7708_(ClientboundAddExperienceOrbPacket p_104960_) {
        PacketUtils.m_131363_(p_104960_, this, this.f_291812_);
        double d0 = p_104960_.m_131527_();
        double d1 = p_104960_.m_131528_();
        double d2 = p_104960_.m_131529_();
        Entity entity = new ExperienceOrb(this.f_104889_, d0, d1, d2, p_104960_.m_131530_());
        entity.m_217006_(d0, d1, d2);
        entity.m_146922_(0.0F);
        entity.m_146926_(0.0F);
        entity.m_20234_(p_104960_.m_131524_());
        this.f_104889_.m_104739_(entity);
    }

    @Override
    public void m_8048_(ClientboundSetEntityMotionPacket p_105092_) {
        PacketUtils.m_131363_(p_105092_, this, this.f_291812_);
        Entity entity = this.f_104889_.m_6815_(p_105092_.m_133192_());
        if (entity != null) {
            entity.m_6001_(p_105092_.m_133195_(), p_105092_.m_133196_(), p_105092_.m_133197_());
        }
    }

    @Override
    public void m_6455_(ClientboundSetEntityDataPacket p_105088_) {
        PacketUtils.m_131363_(p_105088_, this, this.f_291812_);
        Entity entity = this.f_104889_.m_6815_(p_105088_.f_133143_());
        if (entity != null) {
            entity.m_20088_().m_135356_(p_105088_.f_133144_());
        }
    }

    @Override
    public void m_6435_(ClientboundTeleportEntityPacket p_105124_) {
        PacketUtils.m_131363_(p_105124_, this, this.f_291812_);
        Entity entity = this.f_104889_.m_6815_(p_105124_.m_133545_());
        if (entity != null) {
            double d0 = p_105124_.m_133548_();
            double d1 = p_105124_.m_133549_();
            double d2 = p_105124_.m_133550_();
            entity.m_217006_(d0, d1, d2);
            if (!entity.m_6109_()) {
                float f = (float)(p_105124_.m_133551_() * 360) / 256.0F;
                float f1 = (float)(p_105124_.m_133552_() * 360) / 256.0F;
                entity.m_6453_(d0, d1, d2, f, f1, 3);
                entity.m_6853_(p_105124_.m_133553_());
            }
        }
    }

    @Override
    public void m_307789_(ClientboundTickingStatePacket p_311347_) {
        PacketUtils.m_131363_(p_311347_, this, this.f_291812_);
        if (this.f_291812_.f_91073_ != null) {
            TickRateManager tickratemanager = this.f_291812_.f_91073_.m_304826_();
            tickratemanager.m_307254_(p_311347_.f_303125_());
            tickratemanager.m_306419_(p_311347_.f_302605_());
        }
    }

    @Override
    public void m_305194_(ClientboundTickingStepPacket p_309537_) {
        PacketUtils.m_131363_(p_309537_, this, this.f_291812_);
        if (this.f_291812_.f_91073_ != null) {
            TickRateManager tickratemanager = this.f_291812_.f_91073_.m_304826_();
            tickratemanager.m_307652_(p_309537_.f_302557_());
        }
    }

    @Override
    public void m_5612_(ClientboundSetCarriedItemPacket p_105078_) {
        PacketUtils.m_131363_(p_105078_, this, this.f_291812_);
        if (Inventory.m_36045_(p_105078_.m_133079_())) {
            this.f_291812_.f_91074_.m_150109_().f_35977_ = p_105078_.m_133079_();
        }
    }

    @Override
    public void m_7865_(ClientboundMoveEntityPacket p_105036_) {
        PacketUtils.m_131363_(p_105036_, this, this.f_291812_);
        Entity entity = p_105036_.m_132519_(this.f_104889_);
        if (entity != null) {
            if (!entity.m_6109_()) {
                if (p_105036_.m_132534_()) {
                    VecDeltaCodec vecdeltacodec = entity.m_217001_();
                    Vec3 vec3 = vecdeltacodec.m_238021_((long)p_105036_.m_178997_(), (long)p_105036_.m_178998_(), (long)p_105036_.m_178999_());
                    vecdeltacodec.m_238033_(vec3);
                    float f = p_105036_.m_132533_() ? (float)(p_105036_.m_132531_() * 360) / 256.0F : entity.m_293582_();
                    float f1 = p_105036_.m_132533_() ? (float)(p_105036_.m_132532_() * 360) / 256.0F : entity.m_293123_();
                    entity.m_6453_(vec3.m_7096_(), vec3.m_7098_(), vec3.m_7094_(), f, f1, 3);
                } else if (p_105036_.m_132533_()) {
                    float f2 = (float)(p_105036_.m_132531_() * 360) / 256.0F;
                    float f3 = (float)(p_105036_.m_132532_() * 360) / 256.0F;
                    entity.m_6453_(entity.m_293268_(), entity.m_293950_(), entity.m_292720_(), f2, f3, 3);
                }

                entity.m_6853_(p_105036_.m_132535_());
            }
        }
    }

    @Override
    public void m_6176_(ClientboundRotateHeadPacket p_105068_) {
        PacketUtils.m_131363_(p_105068_, this, this.f_291812_);
        Entity entity = p_105068_.m_132969_(this.f_104889_);
        if (entity != null) {
            float f = (float)(p_105068_.m_132977_() * 360) / 256.0F;
            entity.m_6541_(f, 3);
        }
    }

    @Override
    public void m_182047_(ClientboundRemoveEntitiesPacket p_182633_) {
        PacketUtils.m_131363_(p_182633_, this, this.f_291812_);
        p_182633_.m_182730_().forEach((int p_205521_) -> this.f_104889_.m_171642_(p_205521_, Entity.RemovalReason.DISCARDED));
    }

    @Override
    public void m_5682_(ClientboundPlayerPositionPacket p_105056_) {
        PacketUtils.m_131363_(p_105056_, this, this.f_291812_);
        Player player = this.f_291812_.f_91074_;
        Vec3 vec3 = player.m_20184_();
        boolean flag = p_105056_.m_132826_().contains(RelativeMovement.X);
        boolean flag1 = p_105056_.m_132826_().contains(RelativeMovement.Y);
        boolean flag2 = p_105056_.m_132826_().contains(RelativeMovement.Z);
        double d0;
        double d1;
        if (flag) {
            d0 = vec3.m_7096_();
            d1 = player.m_20185_() + p_105056_.m_132818_();
            player.f_19790_ = player.f_19790_ + p_105056_.m_132818_();
            player.f_19854_ = player.f_19854_ + p_105056_.m_132818_();
        } else {
            d0 = 0.0;
            d1 = p_105056_.m_132818_();
            player.f_19790_ = d1;
            player.f_19854_ = d1;
        }

        double d2;
        double d3;
        if (flag1) {
            d2 = vec3.m_7098_();
            d3 = player.m_20186_() + p_105056_.m_132821_();
            player.f_19791_ = player.f_19791_ + p_105056_.m_132821_();
            player.f_19855_ = player.f_19855_ + p_105056_.m_132821_();
        } else {
            d2 = 0.0;
            d3 = p_105056_.m_132821_();
            player.f_19791_ = d3;
            player.f_19855_ = d3;
        }

        double d4;
        double d5;
        if (flag2) {
            d4 = vec3.m_7094_();
            d5 = player.m_20189_() + p_105056_.m_132822_();
            player.f_19792_ = player.f_19792_ + p_105056_.m_132822_();
            player.f_19856_ = player.f_19856_ + p_105056_.m_132822_();
        } else {
            d4 = 0.0;
            d5 = p_105056_.m_132822_();
            player.f_19792_ = d5;
            player.f_19856_ = d5;
        }

        player.m_6034_(d1, d3, d5);
        player.m_20334_(d0, d2, d4);
        float f = p_105056_.m_132823_();
        float f1 = p_105056_.m_132824_();
        if (p_105056_.m_132826_().contains(RelativeMovement.X_ROT)) {
            player.m_146926_(player.m_146909_() + f1);
            player.f_19860_ += f1;
        } else {
            player.m_146926_(f1);
            player.f_19860_ = f1;
        }

        if (p_105056_.m_132826_().contains(RelativeMovement.Y_ROT)) {
            player.m_146922_(player.m_146908_() + f);
            player.f_19859_ += f;
        } else {
            player.m_146922_(f);
            player.f_19859_ = f;
        }

        this.f_290549_.m_129512_(new ServerboundAcceptTeleportationPacket(p_105056_.m_132825_()));
        this.f_290549_
            .m_129512_(
                new ServerboundMovePlayerPacket.PosRot(player.m_20185_(), player.m_20186_(), player.m_20189_(), player.m_146908_(), player.m_146909_(), false)
            );
    }

    @Override
    public void m_5771_(ClientboundSectionBlocksUpdatePacket p_105070_) {
        PacketUtils.m_131363_(p_105070_, this, this.f_291812_);
        p_105070_.m_132992_((p_284633_, p_284634_) -> this.f_104889_.m_233653_(p_284633_, p_284634_, 19));
    }

    @Override
    public void m_183388_(ClientboundLevelChunkWithLightPacket p_194241_) {
        PacketUtils.m_131363_(p_194241_, this, this.f_291812_);
        int i = p_194241_.m_195717_();
        int j = p_194241_.m_195718_();
        this.m_194198_(i, j, p_194241_.m_195719_());
        ClientboundLightUpdatePacketData clientboundlightupdatepacketdata = p_194241_.m_195720_();
        this.f_104889_.m_194171_(() -> {
            this.m_194248_(i, j, clientboundlightupdatepacketdata);
            LevelChunk levelchunk = this.f_104889_.m_7726_().m_62227_(i, j, false);
            if (levelchunk != null) {
                this.m_194212_(levelchunk, i, j);
            }
        });
    }

    @Override
    public void m_274374_(ClientboundChunksBiomesPacket p_275437_) {
        PacketUtils.m_131363_(p_275437_, this, this.f_291812_);

        for (ClientboundChunksBiomesPacket.ChunkBiomeData clientboundchunksbiomespacket$chunkbiomedata : p_275437_.f_273816_()) {
            this.f_104889_
                .m_7726_()
                .m_274444_(
                    clientboundchunksbiomespacket$chunkbiomedata.f_273927_().f_45578_,
                    clientboundchunksbiomespacket$chunkbiomedata.f_273927_().f_45579_,
                    clientboundchunksbiomespacket$chunkbiomedata.m_274543_()
                );
        }

        for (ClientboundChunksBiomesPacket.ChunkBiomeData clientboundchunksbiomespacket$chunkbiomedata1 : p_275437_.f_273816_()) {
            this.f_104889_
                .m_171649_(
                    new ChunkPos(
                        clientboundchunksbiomespacket$chunkbiomedata1.f_273927_().f_45578_, clientboundchunksbiomespacket$chunkbiomedata1.f_273927_().f_45579_
                    )
                );
        }

        for (ClientboundChunksBiomesPacket.ChunkBiomeData clientboundchunksbiomespacket$chunkbiomedata2 : p_275437_.f_273816_()) {
            for (int i = -1; i <= 1; i++) {
                for (int j = -1; j <= 1; j++) {
                    for (int k = this.f_104889_.m_151560_(); k < this.f_104889_.m_151561_(); k++) {
                        this.f_291812_
                            .f_91060_
                            .m_109770_(
                                clientboundchunksbiomespacket$chunkbiomedata2.f_273927_().f_45578_ + i,
                                k,
                                clientboundchunksbiomespacket$chunkbiomedata2.f_273927_().f_45579_ + j
                            );
                    }
                }
            }
        }
    }

    private void m_194198_(int p_194199_, int p_194200_, ClientboundLevelChunkPacketData p_194201_) {
        this.f_104889_.m_7726_().m_194116_(p_194199_, p_194200_, p_194201_.m_195656_(), p_194201_.m_195678_(), p_194201_.m_195657_(p_194199_, p_194200_));
    }

    private void m_194212_(LevelChunk p_194213_, int p_194214_, int p_194215_) {
        LevelLightEngine levellightengine = this.f_104889_.m_7726_().m_7827_();
        LevelChunkSection[] alevelchunksection = p_194213_.m_7103_();
        ChunkPos chunkpos = p_194213_.m_7697_();

        for (int i = 0; i < alevelchunksection.length; i++) {
            LevelChunkSection levelchunksection = alevelchunksection[i];
            int j = this.f_104889_.m_151568_(i);
            levellightengine.m_6191_(SectionPos.m_123196_(chunkpos, j), levelchunksection.m_188008_());
            this.f_104889_.m_104793_(p_194214_, j, p_194215_);
        }
    }

    @Override
    public void m_5729_(ClientboundForgetLevelChunkPacket p_105014_) {
        PacketUtils.m_131363_(p_105014_, this, this.f_291812_);
        this.f_104889_.m_7726_().m_104455_(p_105014_.f_290761_());
        this.m_194252_(p_105014_);
    }

    private void m_194252_(ClientboundForgetLevelChunkPacket p_194253_) {
        ChunkPos chunkpos = p_194253_.f_290761_();
        this.f_104889_.m_194171_(() -> {
            LevelLightEngine levellightengine = this.f_104889_.m_5518_();
            levellightengine.m_9335_(chunkpos, false);

            for (int i = levellightengine.m_164447_(); i < levellightengine.m_164448_(); i++) {
                SectionPos sectionpos = SectionPos.m_123196_(chunkpos, i);
                levellightengine.m_284126_(LightLayer.BLOCK, sectionpos, null);
                levellightengine.m_284126_(LightLayer.SKY, sectionpos, null);
            }

            for (int j = this.f_104889_.m_151560_(); j < this.f_104889_.m_151561_(); j++) {
                levellightengine.m_6191_(SectionPos.m_123196_(chunkpos, j), true);
            }
        });
    }

    @Override
    public void m_6773_(ClientboundBlockUpdatePacket p_104980_) {
        PacketUtils.m_131363_(p_104980_, this, this.f_291812_);
        this.f_104889_.m_233653_(p_104980_.m_131749_(), p_104980_.m_131746_(), 19);
    }

    @Override
    public void m_292634_(ClientboundStartConfigurationPacket p_298839_) {
        PacketUtils.m_131363_(p_298839_, this, this.f_291812_);
        this.f_291812_.m_240442_().m_241954_();
        this.m_247711_();
        ChatComponent.State chatcomponent$state = this.f_291812_.f_91065_.m_93076_().m_322825_();
        this.f_291812_.m_294188_(new ServerReconfigScreen(f_291494_, this.f_290549_));
        this.f_290549_
            .m_324855_(
                ConfigurationProtocols.f_315303_,
                new ClientConfigurationPacketListenerImpl(
                    this.f_291812_,
                    this.f_290549_,
                    new CommonListenerCookie(
                        this.f_104886_,
                        this.f_291019_,
                        this.f_104903_,
                        this.f_244039_,
                        this.f_291180_,
                        this.f_291024_,
                        this.f_291028_,
                        this.f_316471_,
                        chatcomponent$state,
                        this.f_316112_,
                        this.f_337266_,
                        this.f_337041_
                    )
                )
            );
        this.m_295327_(ServerboundConfigurationAcknowledgedPacket.f_317101_);
        this.f_290549_.m_319763_(ConfigurationProtocols.f_315976_);
    }

    @Override
    public void m_8001_(ClientboundTakeItemEntityPacket p_105122_) {
        PacketUtils.m_131363_(p_105122_, this, this.f_291812_);
        Entity entity = this.f_104889_.m_6815_(p_105122_.m_133524_());
        LivingEntity livingentity = (LivingEntity)this.f_104889_.m_6815_(p_105122_.m_133527_());
        if (livingentity == null) {
            livingentity = this.f_291812_.f_91074_;
        }

        if (entity != null) {
            if (entity instanceof ExperienceOrb) {
                this.f_104889_
                    .m_7785_(
                        entity.m_20185_(),
                        entity.m_20186_(),
                        entity.m_20189_(),
                        SoundEvents.f_11871_,
                        SoundSource.PLAYERS,
                        0.1F,
                        (this.f_104898_.m_188501_() - this.f_104898_.m_188501_()) * 0.35F + 0.9F,
                        false
                    );
            } else {
                this.f_104889_
                    .m_7785_(
                        entity.m_20185_(),
                        entity.m_20186_(),
                        entity.m_20189_(),
                        SoundEvents.f_12019_,
                        SoundSource.PLAYERS,
                        0.2F,
                        (this.f_104898_.m_188501_() - this.f_104898_.m_188501_()) * 1.4F + 2.0F,
                        false
                    );
            }

            this.f_291812_
                .f_91061_
                .m_107344_(new ItemPickupParticle(this.f_291812_.m_91290_(), this.f_291812_.m_91269_(), this.f_104889_, entity, livingentity));
            if (entity instanceof ItemEntity itementity) {
                ItemStack itemstack = itementity.m_32055_();
                if (!itemstack.m_41619_()) {
                    itemstack.m_41774_(p_105122_.m_133528_());
                }

                if (itemstack.m_41619_()) {
                    this.f_104889_.m_171642_(p_105122_.m_133524_(), Entity.RemovalReason.DISCARDED);
                }
            } else if (!(entity instanceof ExperienceOrb)) {
                this.f_104889_.m_171642_(p_105122_.m_133524_(), Entity.RemovalReason.DISCARDED);
            }
        }
    }

    @Override
    public void m_213990_(ClientboundSystemChatPacket p_233708_) {
        PacketUtils.m_131363_(p_233708_, this, this.f_291812_);
        this.f_291812_.m_240442_().m_240494_(p_233708_.f_237849_(), p_233708_.f_240374_());
    }

    @Override
    public void m_213629_(ClientboundPlayerChatPacket p_233702_) {
        PacketUtils.m_131363_(p_233702_, this, this.f_291812_);
        Optional<SignedMessageBody> optional = p_233702_.f_244090_().m_252762_(this.f_244113_);
        if (optional.isEmpty()) {
            this.f_290549_.m_129507_(f_244321_);
        } else {
            this.f_244113_.m_247208_(optional.get(), p_233702_.f_243836_());
            UUID uuid = p_233702_.f_243918_();
            PlayerInfo playerinfo = this.m_104949_(uuid);
            if (playerinfo == null) {
                f_104883_.error("Received player chat packet for unknown player with ID: {}", uuid);
                this.f_291812_.m_240442_().m_294071_(uuid, p_233702_.f_240897_());
            } else {
                RemoteChatSession remotechatsession = playerinfo.m_247593_();
                SignedMessageLink signedmessagelink;
                if (remotechatsession != null) {
                    signedmessagelink = new SignedMessageLink(p_233702_.f_244283_(), uuid, remotechatsession.f_244448_());
                } else {
                    signedmessagelink = SignedMessageLink.m_245187_(uuid);
                }

                PlayerChatMessage playerchatmessage = new PlayerChatMessage(
                    signedmessagelink, p_233702_.f_243836_(), optional.get(), p_233702_.f_243686_(), p_233702_.f_243744_()
                );
                playerchatmessage = playerinfo.m_241043_().m_241126_(playerchatmessage);
                if (playerchatmessage != null) {
                    this.f_291812_.m_240442_().m_247425_(playerchatmessage, playerinfo.m_105312_(), p_233702_.f_240897_());
                } else {
                    this.f_291812_.m_240442_().m_294071_(uuid, p_233702_.f_240897_());
                }
            }
        }
    }

    @Override
    public void m_7039_(ClientboundDisguisedChatPacket p_251920_) {
        PacketUtils.m_131363_(p_251920_, this, this.f_291812_);
        this.f_291812_.m_240442_().m_245141_(p_251920_.f_244491_(), p_251920_.f_244252_());
    }

    @Override
    public void m_241037_(ClientboundDeleteChatPacket p_241325_) {
        PacketUtils.m_131363_(p_241325_, this, this.f_291812_);
        Optional<MessageSignature> optional = p_241325_.f_240904_().m_253223_(this.f_244113_);
        if (optional.isEmpty()) {
            this.f_290549_.m_129507_(f_244321_);
        } else {
            this.f_244346_.m_246067_(optional.get());
            if (!this.f_291812_.m_240442_().m_240956_(optional.get())) {
                this.f_291812_.f_91065_.m_93076_().m_240953_(optional.get());
            }
        }
    }

    @Override
    public void m_7791_(ClientboundAnimatePacket p_104968_) {
        PacketUtils.m_131363_(p_104968_, this, this.f_291812_);
        Entity entity = this.f_104889_.m_6815_(p_104968_.m_131624_());
        if (entity != null) {
            if (p_104968_.m_131627_() == 0) {
                LivingEntity livingentity = (LivingEntity)entity;
                livingentity.m_6674_(InteractionHand.MAIN_HAND);
            } else if (p_104968_.m_131627_() == 3) {
                LivingEntity livingentity1 = (LivingEntity)entity;
                livingentity1.m_6674_(InteractionHand.OFF_HAND);
            } else if (p_104968_.m_131627_() == 2) {
                Player player = (Player)entity;
                player.m_6145_(false, false);
            } else if (p_104968_.m_131627_() == 4) {
                this.f_291812_.f_91061_.m_107329_(entity, ParticleTypes.f_123797_);
            } else if (p_104968_.m_131627_() == 5) {
                this.f_291812_.f_91061_.m_107329_(entity, ParticleTypes.f_123808_);
            }
        }
    }

    @Override
    public void m_264143_(ClientboundHurtAnimationPacket p_265581_) {
        PacketUtils.m_131363_(p_265581_, this, this.f_291812_);
        Entity entity = this.f_104889_.m_6815_(p_265581_.f_263825_());
        if (entity != null) {
            entity.m_6053_(p_265581_.f_263826_());
        }
    }

    @Override
    public void m_7885_(ClientboundSetTimePacket p_105108_) {
        PacketUtils.m_131363_(p_105108_, this, this.f_291812_);
        this.f_291812_.f_91073_.m_104637_(p_105108_.m_133358_());
        this.f_291812_.f_91073_.m_104746_(p_105108_.m_133361_());
        this.f_291019_.m_261206_(p_105108_.m_133358_());
    }

    @Override
    public void m_6571_(ClientboundSetDefaultSpawnPositionPacket p_105084_) {
        PacketUtils.m_131363_(p_105084_, this, this.f_291812_);
        this.f_291812_.f_91073_.m_104752_(p_105084_.m_133123_(), p_105084_.m_133126_());
    }

    @Override
    public void m_6403_(ClientboundSetPassengersPacket p_105102_) {
        PacketUtils.m_131363_(p_105102_, this, this.f_291812_);
        Entity entity = this.f_104889_.m_6815_(p_105102_.m_133286_());
        if (entity == null) {
            f_104883_.warn("Received passengers for unknown entity");
        } else {
            boolean flag = entity.m_20367_(this.f_291812_.f_91074_);
            entity.m_20153_();

            for (int i : p_105102_.m_133283_()) {
                Entity entity1 = this.f_104889_.m_6815_(i);
                if (entity1 != null) {
                    entity1.m_7998_(entity, true);
                    if (entity1 == this.f_291812_.f_91074_ && !flag) {
                        if (entity instanceof Boat) {
                            this.f_291812_.f_91074_.f_19859_ = entity.m_146908_();
                            this.f_291812_.f_91074_.m_146922_(entity.m_146908_());
                            this.f_291812_.f_91074_.m_5616_(entity.m_146908_());
                        }

                        Component component = Component.m_237110_("mount.onboard", this.f_291812_.f_91066_.f_92090_.m_90863_());
                        this.f_291812_.f_91065_.m_93063_(component, false);
                        this.f_291812_.m_240477_().m_168785_(component);
                    }
                }
            }
        }
    }

    @Override
    public void m_5599_(ClientboundSetEntityLinkPacket p_105090_) {
        PacketUtils.m_131363_(p_105090_, this, this.f_291812_);
        if (this.f_104889_.m_6815_(p_105090_.m_133172_()) instanceof Leashable leashable) {
            leashable.m_339199_(p_105090_.m_133175_());
        }
    }

    private static ItemStack m_104927_(Player p_104928_) {
        for (InteractionHand interactionhand : InteractionHand.values()) {
            ItemStack itemstack = p_104928_.m_21120_(interactionhand);
            if (itemstack.m_150930_(Items.f_42747_)) {
                return itemstack;
            }
        }

        return new ItemStack(Items.f_42747_);
    }

    @Override
    public void m_7628_(ClientboundEntityEventPacket p_105010_) {
        PacketUtils.m_131363_(p_105010_, this, this.f_291812_);
        Entity entity = p_105010_.m_132094_(this.f_104889_);
        if (entity != null) {
            switch (p_105010_.m_132102_()) {
                case 21:
                    this.f_291812_.m_91106_().m_120367_(new GuardianAttackSoundInstance((Guardian)entity));
                    break;
                case 35:
                    int i = 40;
                    this.f_291812_.f_91061_.m_107332_(entity, ParticleTypes.f_123767_, 30);
                    this.f_104889_.m_7785_(entity.m_20185_(), entity.m_20186_(), entity.m_20189_(), SoundEvents.f_12513_, entity.m_5720_(), 1.0F, 1.0F, false);
                    if (entity == this.f_291812_.f_91074_) {
                        this.f_291812_.f_91063_.m_109113_(m_104927_(this.f_291812_.f_91074_));
                    }
                    break;
                case 63:
                    this.f_291812_.m_91106_().m_120367_(new SnifferSoundInstance((Sniffer)entity));
                    break;
                default:
                    entity.m_7822_(p_105010_.m_132102_());
            }
        }
    }

    @Override
    public void m_269082_(ClientboundDamageEventPacket p_270800_) {
        PacketUtils.m_131363_(p_270800_, this, this.f_291812_);
        Entity entity = this.f_104889_.m_6815_(p_270800_.f_268504_());
        if (entity != null) {
            entity.m_269138_(p_270800_.m_269591_(this.f_104889_));
        }
    }

    @Override
    public void m_5547_(ClientboundSetHealthPacket p_105098_) {
        PacketUtils.m_131363_(p_105098_, this, this.f_291812_);
        this.f_291812_.f_91074_.m_108760_(p_105098_.m_133247_());
        this.f_291812_.f_91074_.m_36324_().m_38705_(p_105098_.m_133250_());
        this.f_291812_.f_91074_.m_36324_().m_38717_(p_105098_.m_133251_());
    }

    @Override
    public void m_6747_(ClientboundSetExperiencePacket p_105096_) {
        PacketUtils.m_131363_(p_105096_, this, this.f_291812_);
        this.f_291812_.f_91074_.m_108644_(p_105096_.m_133228_(), p_105096_.m_133231_(), p_105096_.m_133232_());
    }

    @Override
    public void m_7992_(ClientboundRespawnPacket p_105066_) {
        PacketUtils.m_131363_(p_105066_, this, this.f_291812_);
        CommonPlayerSpawnInfo commonplayerspawninfo = p_105066_.f_290899_();
        ResourceKey<Level> resourcekey = commonplayerspawninfo.f_290731_();
        Holder<DimensionType> holder = commonplayerspawninfo.f_291865_();
        LocalPlayer localplayer = this.f_291812_.f_91074_;
        ResourceKey<Level> resourcekey1 = localplayer.m_9236_().m_46472_();
        boolean flag = resourcekey != resourcekey1;
        ReceivingLevelScreen.Reason receivinglevelscreen$reason = this.m_324775_(localplayer.m_21224_(), resourcekey, resourcekey1);
        if (flag) {
            Map<MapId, MapItemSavedData> map = this.f_104889_.m_171684_();
            boolean flag1 = commonplayerspawninfo.f_290330_();
            boolean flag2 = commonplayerspawninfo.f_290486_();
            ClientLevel.ClientLevelData clientlevel$clientleveldata = new ClientLevel.ClientLevelData(this.f_104890_.m_5472_(), this.f_104890_.m_5466_(), flag2);
            this.f_104890_ = clientlevel$clientleveldata;
            this.f_104889_ = new ClientLevel(
                this,
                clientlevel$clientleveldata,
                resourcekey,
                holder,
                this.f_104897_,
                this.f_194190_,
                this.f_291812_::m_91307_,
                this.f_291812_.f_91060_,
                flag1,
                commonplayerspawninfo.f_290589_()
            );
            this.f_104889_.m_171672_(map);
            this.f_291812_.m_91156_(this.f_104889_, receivinglevelscreen$reason);
        }

        this.f_291812_.f_91075_ = null;
        if (localplayer.m_242612_()) {
            localplayer.m_6915_();
        }

        LocalPlayer localplayer1;
        if (p_105066_.m_263558_((byte)2)) {
            localplayer1 = this.f_291812_
                .f_91072_
                .m_105250_(this.f_104889_, localplayer.m_108630_(), localplayer.m_108631_(), localplayer.m_6144_(), localplayer.m_20142_());
        } else {
            localplayer1 = this.f_291812_.f_91072_.m_105246_(this.f_104889_, localplayer.m_108630_(), localplayer.m_108631_());
        }

        this.m_306243_(localplayer1, this.f_104889_, receivinglevelscreen$reason);
        localplayer1.m_20234_(localplayer.m_19879_());
        this.f_291812_.f_91074_ = localplayer1;
        if (flag) {
            this.f_291812_.m_91397_().m_120186_();
        }

        this.f_291812_.f_91075_ = localplayer1;
        if (p_105066_.m_263558_((byte)2)) {
            List<SynchedEntityData.DataValue<?>> list = localplayer.m_20088_().m_252804_();
            if (list != null) {
                localplayer1.m_20088_().m_135356_(list);
            }
        }

        if (p_105066_.m_263558_((byte)1)) {
            localplayer1.m_21204_().m_22159_(localplayer.m_21204_());
        } else {
            localplayer1.m_21204_().m_339388_(localplayer.m_21204_());
        }

        localplayer1.updateSyncFields(localplayer); // Forge: fix MC-10657
        localplayer1.m_172530_();
        net.minecraftforge.client.event.ForgeEventFactoryClient.firePlayerRespawn(this.f_291812_.f_91072_, localplayer, localplayer1, localplayer1.f_108617_.f_290549_);
        this.f_104889_.m_104739_(localplayer1);
        localplayer1.m_146922_(-180.0F);
        localplayer1.f_108618_ = new KeyboardInput(this.f_291812_.f_91066_);
        this.f_291812_.f_91072_.m_105221_(localplayer1);
        localplayer1.m_36393_(localplayer.m_36330_());
        localplayer1.m_108711_(localplayer.m_108632_());
        localplayer1.m_219749_(commonplayerspawninfo.f_290601_());
        localplayer1.m_287199_(commonplayerspawninfo.f_291470_());
        localplayer1.f_108589_ = localplayer.f_108589_;
        localplayer1.f_108590_ = localplayer.f_108590_;
        if (this.f_291812_.f_91080_ instanceof DeathScreen || this.f_291812_.f_91080_ instanceof DeathScreen.TitleConfirmScreen) {
            this.f_291812_.m_91152_(null);
        }

        this.f_291812_.f_91072_.m_171805_(commonplayerspawninfo.f_291098_(), commonplayerspawninfo.f_290730_());
    }

    private ReceivingLevelScreen.Reason m_324775_(boolean p_327777_, ResourceKey<Level> p_333661_, ResourceKey<Level> p_327689_) {
        ReceivingLevelScreen.Reason receivinglevelscreen$reason = ReceivingLevelScreen.Reason.OTHER;
        if (!p_327777_) {
            if (p_333661_ == Level.f_46429_ || p_327689_ == Level.f_46429_) {
                receivinglevelscreen$reason = ReceivingLevelScreen.Reason.NETHER_PORTAL;
            } else if (p_333661_ == Level.f_46430_ || p_327689_ == Level.f_46430_) {
                receivinglevelscreen$reason = ReceivingLevelScreen.Reason.END_PORTAL;
            }
        }

        return receivinglevelscreen$reason;
    }

    @Override
    public void m_7345_(ClientboundExplodePacket p_105012_) {
        PacketUtils.m_131363_(p_105012_, this, this.f_291812_);
        Explosion explosion = new Explosion(
            this.f_291812_.f_91073_,
            null,
            p_105012_.m_132132_(),
            p_105012_.m_132133_(),
            p_105012_.m_132134_(),
            p_105012_.m_132135_(),
            p_105012_.m_132136_(),
            p_105012_.m_305992_(),
            p_105012_.m_307612_(),
            p_105012_.m_305172_(),
            p_105012_.m_307893_()
        );
        explosion.m_46075_(true);
        this.f_291812_
            .f_91074_
            .m_20256_(this.f_291812_.f_91074_.m_20184_().m_82520_((double)p_105012_.m_132127_(), (double)p_105012_.m_132130_(), (double)p_105012_.m_132131_()));
    }

    @Override
    public void m_6905_(ClientboundHorseScreenOpenPacket p_105018_) {
        PacketUtils.m_131363_(p_105018_, this, this.f_291812_);
        if (this.f_104889_.m_6815_(p_105018_.m_132208_()) instanceof AbstractHorse abstracthorse) {
            LocalPlayer localplayer = this.f_291812_.f_91074_;
            int i = p_105018_.m_339890_();
            SimpleContainer simplecontainer = new SimpleContainer(AbstractHorse.m_339034_(i));
            HorseInventoryMenu horseinventorymenu = new HorseInventoryMenu(p_105018_.m_132204_(), localplayer.m_150109_(), simplecontainer, abstracthorse, i);
            localplayer.f_36096_ = horseinventorymenu;
            this.f_291812_.m_91152_(new HorseInventoryScreen(horseinventorymenu, localplayer.m_150109_(), abstracthorse, i));
        }
    }

    @Override
    public void m_5980_(ClientboundOpenScreenPacket p_105042_) {
        PacketUtils.m_131363_(p_105042_, this, this.f_291812_);
        MenuScreens.m_96201_(p_105042_.m_132628_(), this.f_291812_, p_105042_.m_132625_(), p_105042_.m_132629_());
    }

    @Override
    public void m_5735_(ClientboundContainerSetSlotPacket p_105000_) {
        PacketUtils.m_131363_(p_105000_, this, this.f_291812_);
        Player player = this.f_291812_.f_91074_;
        ItemStack itemstack = p_105000_.m_131995_();
        int i = p_105000_.m_131994_();
        this.f_291812_.m_91301_().m_120568_(itemstack);
        if (p_105000_.m_131991_() == -1) {
            if (!(this.f_291812_.f_91080_ instanceof CreativeModeInventoryScreen)) {
                player.f_36096_.m_142503_(itemstack);
            }
        } else if (p_105000_.m_131991_() == -2) {
            player.m_150109_().m_6836_(i, itemstack);
        } else {
            boolean flag = false;
            if (this.f_291812_.f_91080_ instanceof CreativeModeInventoryScreen creativemodeinventoryscreen) {
                flag = !creativemodeinventoryscreen.m_258017_();
            }

            if (p_105000_.m_131991_() == 0 && InventoryMenu.m_150592_(i)) {
                if (!itemstack.m_41619_()) {
                    ItemStack itemstack1 = player.f_36095_.m_38853_(i).m_7993_();
                    if (itemstack1.m_41619_() || itemstack1.m_41613_() < itemstack.m_41613_()) {
                        itemstack.m_41754_(5);
                    }
                }

                player.f_36095_.m_182406_(i, p_105000_.m_182716_(), itemstack);
            } else if (p_105000_.m_131991_() == player.f_36096_.f_38840_ && (p_105000_.m_131991_() != 0 || !flag)) {
                player.f_36096_.m_182406_(i, p_105000_.m_182716_(), itemstack);
            }
        }
    }

    @Override
    public void m_6837_(ClientboundContainerSetContentPacket p_104996_) {
        PacketUtils.m_131363_(p_104996_, this, this.f_291812_);
        Player player = this.f_291812_.f_91074_;
        if (p_104996_.m_131954_() == 0) {
            player.f_36095_.m_182410_(p_104996_.m_182709_(), p_104996_.m_131957_(), p_104996_.m_182708_());
        } else if (p_104996_.m_131954_() == player.f_36096_.f_38840_) {
            player.f_36096_.m_182410_(p_104996_.m_182709_(), p_104996_.m_131957_(), p_104996_.m_182708_());
        }
    }

    @Override
    public void m_8047_(ClientboundOpenSignEditorPacket p_105044_) {
        PacketUtils.m_131363_(p_105044_, this, this.f_291812_);
        BlockPos blockpos = p_105044_.m_132640_();
        if (this.f_104889_.m_7702_(blockpos) instanceof SignBlockEntity signblockentity) {
            this.f_291812_.f_91074_.m_7739_(signblockentity, p_105044_.m_276774_());
        } else {
            BlockState blockstate = this.f_104889_.m_8055_(blockpos);
            SignBlockEntity signblockentity1 = new SignBlockEntity(blockpos, blockstate);
            signblockentity1.m_142339_(this.f_104889_);
            this.f_291812_.f_91074_.m_7739_(signblockentity1, p_105044_.m_276774_());
        }
    }

    @Override
    public void m_7545_(ClientboundBlockEntityDataPacket p_104976_) {
        PacketUtils.m_131363_(p_104976_, this, this.f_291812_);
        BlockPos blockpos = p_104976_.m_131704_();
        this.f_291812_.f_91073_.m_141902_(blockpos, p_104976_.m_195645_()).ifPresent(p_325478_ -> {
            p_325478_.onDataPacket(f_290549_, p_104976_, this.f_104903_);

            if (p_325478_ instanceof CommandBlockEntity && this.f_291812_.f_91080_ instanceof CommandBlockEditScreen) {
                ((CommandBlockEditScreen)this.f_291812_.f_91080_).m_98398_();
            }
        });
    }

    @Override
    public void m_7257_(ClientboundContainerSetDataPacket p_104998_) {
        PacketUtils.m_131363_(p_104998_, this, this.f_291812_);
        Player player = this.f_291812_.f_91074_;
        if (player.f_36096_ != null && player.f_36096_.f_38840_ == p_104998_.m_131972_()) {
            player.f_36096_.m_7511_(p_104998_.m_131975_(), p_104998_.m_131976_());
        }
    }

    @Override
    public void m_7277_(ClientboundSetEquipmentPacket p_105094_) {
        PacketUtils.m_131363_(p_105094_, this, this.f_291812_);
        if (this.f_104889_.m_6815_(p_105094_.m_133210_()) instanceof LivingEntity livingentity) {
            p_105094_.m_133213_().forEach(p_325480_ -> livingentity.m_21035_(p_325480_.getFirst(), p_325480_.getSecond()));
        }
    }

    @Override
    public void m_7776_(ClientboundContainerClosePacket p_104994_) {
        PacketUtils.m_131363_(p_104994_, this, this.f_291812_);
        this.f_291812_.f_91074_.m_108763_();
    }

    @Override
    public void m_7364_(ClientboundBlockEventPacket p_104978_) {
        PacketUtils.m_131363_(p_104978_, this, this.f_291812_);
        this.f_291812_.f_91073_.m_7696_(p_104978_.m_131725_(), p_104978_.m_131730_(), p_104978_.m_131728_(), p_104978_.m_131729_());
    }

    @Override
    public void m_5943_(ClientboundBlockDestructionPacket p_104974_) {
        PacketUtils.m_131363_(p_104974_, this, this.f_291812_);
        this.f_291812_.f_91073_.m_6801_(p_104974_.m_131685_(), p_104974_.m_131688_(), p_104974_.m_131689_());
    }

    @Override
    public void m_7616_(ClientboundGameEventPacket p_105016_) {
        PacketUtils.m_131363_(p_105016_, this, this.f_291812_);
        Player player = this.f_291812_.f_91074_;
        ClientboundGameEventPacket.Type clientboundgameeventpacket$type = p_105016_.m_132178_();
        float f = p_105016_.m_132181_();
        int i = Mth.m_14143_(f + 0.5F);
        if (clientboundgameeventpacket$type == ClientboundGameEventPacket.f_132153_) {
            player.m_5661_(Component.m_237115_("block.minecraft.spawn.not_valid"), false);
        } else if (clientboundgameeventpacket$type == ClientboundGameEventPacket.f_132154_) {
            this.f_104889_.m_6106_().m_5565_(true);
            this.f_104889_.m_46734_(0.0F);
        } else if (clientboundgameeventpacket$type == ClientboundGameEventPacket.f_132155_) {
            this.f_104889_.m_6106_().m_5565_(false);
            this.f_104889_.m_46734_(1.0F);
        } else if (clientboundgameeventpacket$type == ClientboundGameEventPacket.f_132156_) {
            this.f_291812_.f_91072_.m_105279_(GameType.m_46393_(i));
        } else if (clientboundgameeventpacket$type == ClientboundGameEventPacket.f_132157_) {
            this.f_291812_.m_91152_(new WinScreen(true, () -> {
                this.f_291812_.f_91074_.f_108617_.m_295327_(new ServerboundClientCommandPacket(ServerboundClientCommandPacket.Action.PERFORM_RESPAWN));
                this.f_291812_.m_91152_(null);
            }));
        } else if (clientboundgameeventpacket$type == ClientboundGameEventPacket.f_132158_) {
            Options options = this.f_291812_.f_91066_;
            if (f == 0.0F) {
                this.f_291812_.m_91152_(new DemoIntroScreen());
            } else if (f == 101.0F) {
                this.f_291812_
                    .f_91065_
                    .m_93076_()
                    .m_93785_(
                        Component.m_237110_(
                            "demo.help.movement",
                            options.f_92085_.m_90863_(),
                            options.f_92086_.m_90863_(),
                            options.f_92087_.m_90863_(),
                            options.f_92088_.m_90863_()
                        )
                    );
            } else if (f == 102.0F) {
                this.f_291812_.f_91065_.m_93076_().m_93785_(Component.m_237110_("demo.help.jump", options.f_92089_.m_90863_()));
            } else if (f == 103.0F) {
                this.f_291812_.f_91065_.m_93076_().m_93785_(Component.m_237110_("demo.help.inventory", options.f_92092_.m_90863_()));
            } else if (f == 104.0F) {
                this.f_291812_.f_91065_.m_93076_().m_93785_(Component.m_237110_("demo.day.6", options.f_92102_.m_90863_()));
            }
        } else if (clientboundgameeventpacket$type == ClientboundGameEventPacket.f_132159_) {
            this.f_104889_.m_6263_(player, player.m_20185_(), player.m_20188_(), player.m_20189_(), SoundEvents.f_11686_, SoundSource.PLAYERS, 0.18F, 0.45F);
        } else if (clientboundgameeventpacket$type == ClientboundGameEventPacket.f_132160_) {
            this.f_104889_.m_46734_(f);
        } else if (clientboundgameeventpacket$type == ClientboundGameEventPacket.f_132161_) {
            this.f_104889_.m_46707_(f);
        } else if (clientboundgameeventpacket$type == ClientboundGameEventPacket.f_132162_) {
            this.f_104889_.m_6263_(player, player.m_20185_(), player.m_20186_(), player.m_20189_(), SoundEvents.f_12295_, SoundSource.NEUTRAL, 1.0F, 1.0F);
        } else if (clientboundgameeventpacket$type == ClientboundGameEventPacket.f_132163_) {
            this.f_104889_.m_7106_(ParticleTypes.f_123807_, player.m_20185_(), player.m_20186_(), player.m_20189_(), 0.0, 0.0, 0.0);
            if (i == 1) {
                this.f_104889_.m_6263_(player, player.m_20185_(), player.m_20186_(), player.m_20189_(), SoundEvents.f_11880_, SoundSource.HOSTILE, 1.0F, 1.0F);
            }
        } else if (clientboundgameeventpacket$type == ClientboundGameEventPacket.f_132164_) {
            this.f_291812_.f_91074_.m_108711_(f == 0.0F);
        } else if (clientboundgameeventpacket$type == ClientboundGameEventPacket.f_290437_) {
            this.f_291812_.f_91074_.m_294300_(f == 1.0F);
        } else if (clientboundgameeventpacket$type == ClientboundGameEventPacket.f_302744_ && this.f_302509_ != null) {
            this.f_302509_.m_304720_();
        }
    }

    private void m_306243_(LocalPlayer p_309620_, ClientLevel p_310146_, ReceivingLevelScreen.Reason p_328346_) {
        this.f_302509_ = new LevelLoadStatusManager(p_309620_, p_310146_, this.f_291812_.f_91060_);
        this.f_291812_.m_91152_(new ReceivingLevelScreen(this.f_302509_::m_305903_, p_328346_));
    }

    @Override
    public void m_7633_(ClientboundMapItemDataPacket p_105032_) {
        PacketUtils.m_131363_(p_105032_, this, this.f_291812_);
        MapRenderer maprenderer = this.f_291812_.f_91063_.m_109151_();
        MapId mapid = p_105032_.f_132415_();
        MapItemSavedData mapitemsaveddata = this.f_291812_.f_91073_.m_7489_(mapid);
        if (mapitemsaveddata == null) {
            mapitemsaveddata = MapItemSavedData.m_164776_(p_105032_.f_132416_(), p_105032_.f_132418_(), this.f_291812_.f_91073_.m_46472_());
            this.f_291812_.f_91073_.m_257583_(mapid, mapitemsaveddata);
        }

        p_105032_.m_132437_(mapitemsaveddata);
        maprenderer.m_168765_(mapid, mapitemsaveddata);
    }

    @Override
    public void m_7704_(ClientboundLevelEventPacket p_105024_) {
        PacketUtils.m_131363_(p_105024_, this, this.f_291812_);
        if (p_105024_.m_132274_()) {
            this.f_291812_.f_91073_.m_6798_(p_105024_.m_132277_(), p_105024_.m_132279_(), p_105024_.m_132278_());
        } else {
            this.f_291812_.f_91073_.m_46796_(p_105024_.m_132277_(), p_105024_.m_132279_(), p_105024_.m_132278_());
        }
    }

    @Override
    public void m_5498_(ClientboundUpdateAdvancementsPacket p_105126_) {
        PacketUtils.m_131363_(p_105126_, this, this.f_291812_);
        this.f_104893_.m_104399_(p_105126_);
    }

    @Override
    public void m_7553_(ClientboundSelectAdvancementsTabPacket p_105072_) {
        PacketUtils.m_131363_(p_105072_, this, this.f_291812_);
        ResourceLocation resourcelocation = p_105072_.m_133013_();
        if (resourcelocation == null) {
            this.f_104893_.m_104401_(null, false);
        } else {
            AdvancementHolder advancementholder = this.f_104893_.m_295984_(resourcelocation);
            this.f_104893_.m_104401_(advancementholder, false);
        }
    }

    @Override
    public void m_7443_(ClientboundCommandsPacket p_104990_) {
        PacketUtils.m_131363_(p_104990_, this, this.f_291812_);
        var context = CommandBuildContext.m_255418_(this.f_104903_, this.f_244039_);
        this.f_104899_ = new CommandDispatcher<>(p_104990_.m_237624_(context));
        this.f_104899_ = net.minecraftforge.client.ClientCommandHandler.mergeServerCommands(this.f_104899_, context);
    }

    @Override
    public void m_7183_(ClientboundStopSoundPacket p_105116_) {
        PacketUtils.m_131363_(p_105116_, this, this.f_291812_);
        this.f_291812_.m_91106_().m_120386_(p_105116_.m_133476_(), p_105116_.m_133479_());
    }

    @Override
    public void m_7589_(ClientboundCommandSuggestionsPacket p_104988_) {
        PacketUtils.m_131363_(p_104988_, this, this.f_291812_);
        this.f_104894_.m_105171_(p_104988_.f_131842_(), p_104988_.m_319734_());
    }

    @Override
    public void m_6327_(ClientboundUpdateRecipesPacket p_105132_) {
        PacketUtils.m_131363_(p_105132_, this, this.f_291812_);
        this.f_104900_.m_44024_(p_105132_.m_133644_());
        ClientRecipeBook clientrecipebook = this.f_291812_.f_91074_.m_108631_();
        clientrecipebook.m_266394_(this.f_104900_.m_323867_(), this.f_291812_.f_91073_.m_9598_());
        this.f_337492_.m_338856_(clientrecipebook, this.f_104903_);
        net.minecraftforge.client.ForgeHooksClient.onRecipesUpdated(this.f_104900_);
    }

    @Override
    public void m_7244_(ClientboundPlayerLookAtPacket p_105054_) {
        PacketUtils.m_131363_(p_105054_, this, this.f_291812_);
        Vec3 vec3 = p_105054_.m_132785_(this.f_104889_);
        if (vec3 != null) {
            this.f_291812_.f_91074_.m_7618_(p_105054_.m_132793_(), vec3);
        }
    }

    @Override
    public void m_6148_(ClientboundTagQueryPacket p_105120_) {
        PacketUtils.m_131363_(p_105120_, this, this.f_291812_);
        if (!this.f_104896_.m_90705_(p_105120_.m_133506_(), p_105120_.m_133509_())) {
            f_104883_.debug("Got unhandled response to tag query {}", p_105120_.m_133506_());
        }
    }

    @Override
    public void m_7271_(ClientboundAwardStatsPacket p_104970_) {
        PacketUtils.m_131363_(p_104970_, this, this.f_291812_);

        for (Entry<Stat<?>> entry : p_104970_.f_131628_().object2IntEntrySet()) {
            Stat<?> stat = entry.getKey();
            int i = entry.getIntValue();
            this.f_291812_.f_91074_.m_108630_().m_6085_(this.f_291812_.f_91074_, stat, i);
        }

        if (this.f_291812_.f_91080_ instanceof StatsScreen statsscreen) {
            statsscreen.m_96980_();
        }
    }

    @Override
    public void m_8076_(ClientboundRecipePacket p_105058_) {
        PacketUtils.m_131363_(p_105058_, this, this.f_291812_);
        ClientRecipeBook clientrecipebook = this.f_291812_.f_91074_.m_108631_();
        clientrecipebook.m_12687_(p_105058_.m_132869_());
        ClientboundRecipePacket.State clientboundrecipepacket$state = p_105058_.m_132870_();
        switch (clientboundrecipepacket$state) {
            case REMOVE:
                for (ResourceLocation resourcelocation3 : p_105058_.m_132865_()) {
                    this.f_104900_.m_44043_(resourcelocation3).ifPresent(clientrecipebook::m_12713_);
                }
                break;
            case INIT:
                for (ResourceLocation resourcelocation1 : p_105058_.m_132865_()) {
                    this.f_104900_.m_44043_(resourcelocation1).ifPresent(clientrecipebook::m_12700_);
                }

                for (ResourceLocation resourcelocation2 : p_105058_.m_132868_()) {
                    this.f_104900_.m_44043_(resourcelocation2).ifPresent(clientrecipebook::m_12723_);
                }
                break;
            case ADD:
                for (ResourceLocation resourcelocation : p_105058_.m_132865_()) {
                    this.f_104900_.m_44043_(resourcelocation).ifPresent(p_296226_ -> {
                        clientrecipebook.m_12700_((RecipeHolder<?>)p_296226_);
                        clientrecipebook.m_12723_((RecipeHolder<?>)p_296226_);
                        if (p_296226_.f_291008_().m_271738_()) {
                            RecipeToast.m_94817_(this.f_291812_.m_91300_(), (RecipeHolder<?>)p_296226_);
                        }
                    });
                }
        }

        clientrecipebook.m_90639_().forEach(p_205540_ -> p_205540_.m_100499_(clientrecipebook));
        if (this.f_291812_.f_91080_ instanceof RecipeUpdateListener) {
            ((RecipeUpdateListener)this.f_291812_.f_91080_).m_6916_();
        }
    }

    @Override
    public void m_7915_(ClientboundUpdateMobEffectPacket p_105130_) {
        PacketUtils.m_131363_(p_105130_, this, this.f_291812_);
        Entity entity = this.f_104889_.m_6815_(p_105130_.m_133622_());
        if (entity instanceof LivingEntity) {
            Holder<MobEffect> holder = p_105130_.m_237878_();
            MobEffectInstance mobeffectinstance = new MobEffectInstance(
                holder, p_105130_.m_133625_(), p_105130_.m_133624_(), p_105130_.m_133627_(), p_105130_.m_133626_(), p_105130_.m_133628_(), null
            );
            if (!p_105130_.m_323944_()) {
                mobeffectinstance.m_320166_();
            }

            ((LivingEntity)entity).m_147215_(mobeffectinstance, null);
        }
    }

    @Override
    public void m_105133_(ClientboundUpdateTagsPacket p_298004_) {
        PacketUtils.m_131363_(p_298004_, this, this.f_291812_);
        TagCollector tagcollector = new TagCollector();
        p_298004_.m_294928_().forEach(tagcollector::m_322781_);
        tagcollector.m_324385_(this.f_104903_, this.f_290549_.m_129531_());
        List<ItemStack> list = List.copyOf(CreativeModeTabs.m_258007_().m_260957_());
        this.f_337492_.m_340407_(list);

        net.minecraftforge.event.ForgeEventFactory.onTagsUpdated(this.f_104903_, true, this.f_290549_.m_129531_());
    }

    @Override
    public void m_142234_(ClientboundPlayerCombatEndPacket p_171771_) {
    }

    @Override
    public void m_142058_(ClientboundPlayerCombatEnterPacket p_171773_) {
    }

    @Override
    public void m_142747_(ClientboundPlayerCombatKillPacket p_171775_) {
        PacketUtils.m_131363_(p_171775_, this, this.f_291812_);
        Entity entity = this.f_104889_.m_6815_(p_171775_.f_179058_());
        if (entity == this.f_291812_.f_91074_) {
            if (this.f_291812_.f_91074_.m_108632_()) {
                this.f_291812_.m_91152_(new DeathScreen(p_171775_.f_179060_(), this.f_104889_.m_6106_().m_5466_()));
            } else {
                this.f_291812_.f_91074_.m_7583_();
            }
        }
    }

    @Override
    public void m_6664_(ClientboundChangeDifficultyPacket p_104984_) {
        PacketUtils.m_131363_(p_104984_, this, this.f_291812_);
        this.f_104890_.m_104851_(p_104984_.m_131820_());
        this.f_104890_.m_104858_(p_104984_.m_131817_());
    }

    @Override
    public void m_6447_(ClientboundSetCameraPacket p_105076_) {
        PacketUtils.m_131363_(p_105076_, this, this.f_291812_);
        Entity entity = p_105076_.m_133059_(this.f_104889_);
        if (entity != null) {
            this.f_291812_.m_91118_(entity);
        }
    }

    @Override
    public void m_142237_(ClientboundInitializeBorderPacket p_171767_) {
        PacketUtils.m_131363_(p_171767_, this, this.f_291812_);
        WorldBorder worldborder = this.f_104889_.m_6857_();
        worldborder.m_61949_(p_171767_.m_178886_(), p_171767_.m_178887_());
        long i = p_171767_.m_178890_();
        if (i > 0L) {
            worldborder.m_61919_(p_171767_.m_178889_(), p_171767_.m_178888_(), i);
        } else {
            worldborder.m_61917_(p_171767_.m_178888_());
        }

        worldborder.m_61923_(p_171767_.m_178891_());
        worldborder.m_61952_(p_171767_.m_178893_());
        worldborder.m_61944_(p_171767_.m_178892_());
    }

    @Override
    public void m_142612_(ClientboundSetBorderCenterPacket p_171781_) {
        PacketUtils.m_131363_(p_171781_, this, this.f_291812_);
        this.f_104889_.m_6857_().m_61949_(p_171781_.m_179224_(), p_171781_.m_179223_());
    }

    @Override
    public void m_142686_(ClientboundSetBorderLerpSizePacket p_171783_) {
        PacketUtils.m_131363_(p_171783_, this, this.f_291812_);
        this.f_104889_.m_6857_().m_61919_(p_171783_.m_179238_(), p_171783_.m_179239_(), p_171783_.m_179240_());
    }

    @Override
    public void m_142238_(ClientboundSetBorderSizePacket p_171785_) {
        PacketUtils.m_131363_(p_171785_, this, this.f_291812_);
        this.f_104889_.m_6857_().m_61917_(p_171785_.m_179252_());
    }

    @Override
    public void m_142696_(ClientboundSetBorderWarningDistancePacket p_171789_) {
        PacketUtils.m_131363_(p_171789_, this, this.f_291812_);
        this.f_104889_.m_6857_().m_61952_(p_171789_.m_179276_());
    }

    @Override
    public void m_142056_(ClientboundSetBorderWarningDelayPacket p_171787_) {
        PacketUtils.m_131363_(p_171787_, this, this.f_291812_);
        this.f_104889_.m_6857_().m_61944_(p_171787_.m_179264_());
    }

    @Override
    public void m_142766_(ClientboundClearTitlesPacket p_171765_) {
        PacketUtils.m_131363_(p_171765_, this, this.f_291812_);
        this.f_291812_.f_91065_.m_168713_();
        if (p_171765_.m_178788_()) {
            this.f_291812_.f_91065_.m_93006_();
        }
    }

    @Override
    public void m_213672_(ClientboundServerDataPacket p_233704_) {
        PacketUtils.m_131363_(p_233704_, this, this.f_291812_);
        if (this.f_291024_ != null) {
            this.f_291024_.f_105365_ = p_233704_.f_237795_();
            p_233704_.f_271248_().map(ServerData::m_301662_).ifPresent(this.f_291024_::m_271813_);
            ServerList.m_105446_(this.f_291024_);
        }
    }

    @Override
    public void m_240695_(ClientboundCustomChatCompletionsPacket p_240832_) {
        PacketUtils.m_131363_(p_240832_, this, this.f_291812_);
        this.f_104894_.m_240713_(p_240832_.f_240661_(), p_240832_.f_240663_());
    }

    @Override
    public void m_142456_(ClientboundSetActionBarTextPacket p_171779_) {
        PacketUtils.m_131363_(p_171779_, this, this.f_291812_);
        this.f_291812_.f_91065_.m_93063_(p_171779_.f_179199_(), false);
    }

    @Override
    public void m_142442_(ClientboundSetTitleTextPacket p_171793_) {
        PacketUtils.m_131363_(p_171793_, this, this.f_291812_);
        this.f_291812_.f_91065_.m_168714_(p_171793_.f_179388_());
    }

    @Override
    public void m_141913_(ClientboundSetSubtitleTextPacket p_171791_) {
        PacketUtils.m_131363_(p_171791_, this, this.f_291812_);
        this.f_291812_.f_91065_.m_168711_(p_171791_.f_179374_());
    }

    @Override
    public void m_142185_(ClientboundSetTitlesAnimationPacket p_171795_) {
        PacketUtils.m_131363_(p_171795_, this, this.f_291812_);
        this.f_291812_.f_91065_.m_168684_(p_171795_.m_179415_(), p_171795_.m_179416_(), p_171795_.m_179417_());
    }

    @Override
    public void m_6235_(ClientboundTabListPacket p_105118_) {
        PacketUtils.m_131363_(p_105118_, this, this.f_291812_);
        this.f_291812_.f_91065_.m_93088_().m_94558_(p_105118_.f_133480_().getString().isEmpty() ? null : p_105118_.f_133480_());
        this.f_291812_.f_91065_.m_93088_().m_94554_(p_105118_.f_133481_().getString().isEmpty() ? null : p_105118_.f_133481_());
    }

    @Override
    public void m_6476_(ClientboundRemoveMobEffectPacket p_105062_) {
        PacketUtils.m_131363_(p_105062_, this, this.f_291812_);
        if (p_105062_.m_132901_(this.f_104889_) instanceof LivingEntity livingentity) {
            livingentity.m_6234_(p_105062_.f_132896_());
        }
    }

    @Override
    public void m_213565_(ClientboundPlayerInfoRemovePacket p_248731_) {
        PacketUtils.m_131363_(p_248731_, this, this.f_291812_);

        for (UUID uuid : p_248731_.f_244383_()) {
            this.f_291812_.m_91266_().m_100690_(uuid);
            PlayerInfo playerinfo = this.f_104892_.remove(uuid);
            if (playerinfo != null) {
                this.f_244156_.remove(playerinfo);
            }
        }
    }

    @Override
    public void m_214045_(ClientboundPlayerInfoUpdatePacket p_250115_) {
        PacketUtils.m_131363_(p_250115_, this, this.f_291812_);

        for (ClientboundPlayerInfoUpdatePacket.Entry clientboundplayerinfoupdatepacket$entry : p_250115_.m_245290_()) {
            PlayerInfo playerinfo = new PlayerInfo(Objects.requireNonNull(clientboundplayerinfoupdatepacket$entry.f_243688_()), this.m_253150_());
            if (this.f_104892_.putIfAbsent(clientboundplayerinfoupdatepacket$entry.f_244142_(), playerinfo) == null) {
                this.f_291812_.m_91266_().m_100676_(playerinfo);
            }
        }

        for (ClientboundPlayerInfoUpdatePacket.Entry clientboundplayerinfoupdatepacket$entry1 : p_250115_.m_246778_()) {
            PlayerInfo playerinfo1 = this.f_104892_.get(clientboundplayerinfoupdatepacket$entry1.f_244142_());
            if (playerinfo1 == null) {
                f_104883_.warn(
                    "Ignoring player info update for unknown player {} ({})", clientboundplayerinfoupdatepacket$entry1.f_244142_(), p_250115_.m_246097_()
                );
            } else {
                for (ClientboundPlayerInfoUpdatePacket.Action clientboundplayerinfoupdatepacket$action : p_250115_.m_246097_()) {
                    this.m_247639_(clientboundplayerinfoupdatepacket$action, clientboundplayerinfoupdatepacket$entry1, playerinfo1);
                }
            }
        }
    }

    private void m_247639_(ClientboundPlayerInfoUpdatePacket.Action p_248954_, ClientboundPlayerInfoUpdatePacket.Entry p_251310_, PlayerInfo p_251146_) {
        switch (p_248954_) {
            case INITIALIZE_CHAT:
                this.m_245842_(p_251310_, p_251146_);
                break;
            case UPDATE_GAME_MODE:
                if (p_251146_.m_105325_() != p_251310_.f_244162_()
                    && this.f_291812_.f_91074_ != null
                    && this.f_291812_.f_91074_.m_20148_().equals(p_251310_.f_244142_())) {
                    this.f_291812_.f_91074_.m_287171_(p_251310_.f_244162_());
                }

                p_251146_.m_105317_(p_251310_.f_244162_());
                break;
            case UPDATE_LISTED:
                if (p_251310_.f_243700_()) {
                    this.f_244156_.add(p_251146_);
                } else {
                    this.f_244156_.remove(p_251146_);
                }
                break;
            case UPDATE_LATENCY:
                p_251146_.m_105313_(p_251310_.f_244322_());
                break;
            case UPDATE_DISPLAY_NAME:
                p_251146_.m_105323_(p_251310_.f_244512_());
        }
    }

    private void m_245842_(ClientboundPlayerInfoUpdatePacket.Entry p_248806_, PlayerInfo p_251136_) {
        GameProfile gameprofile = p_251136_.m_105312_();
        SignatureValidator signaturevalidator = this.f_291812_.m_231417_();
        if (signaturevalidator == null) {
            f_104883_.warn("Ignoring chat session from {} due to missing Services public key", gameprofile.getName());
            p_251136_.m_253204_(this.m_253150_());
        } else {
            RemoteChatSession.Data remotechatsession$data = p_248806_.f_244153_();
            if (remotechatsession$data != null) {
                try {
                    RemoteChatSession remotechatsession = remotechatsession$data.m_247588_(gameprofile, signaturevalidator);
                    p_251136_.m_246479_(remotechatsession);
                } catch (ProfilePublicKey.ValidationException profilepublickey$validationexception) {
                    f_104883_.error("Failed to validate profile key for player: '{}'", gameprofile.getName(), profilepublickey$validationexception);
                    p_251136_.m_253204_(this.m_253150_());
                }
            } else {
                p_251136_.m_253204_(this.m_253150_());
            }
        }
    }

    private boolean m_253150_() {
        return this.f_291812_.m_307493_() && this.f_316183_;
    }

    @Override
    public void m_5767_(ClientboundPlayerAbilitiesPacket p_105048_) {
        PacketUtils.m_131363_(p_105048_, this, this.f_291812_);
        Player player = this.f_291812_.f_91074_;
        player.m_150110_().f_35935_ = p_105048_.m_132677_();
        player.m_150110_().f_35937_ = p_105048_.m_132679_();
        player.m_150110_().f_35934_ = p_105048_.m_132674_();
        player.m_150110_().f_35936_ = p_105048_.m_132678_();
        player.m_150110_().m_35943_(p_105048_.m_132680_());
        player.m_150110_().m_35948_(p_105048_.m_132681_());
    }

    @Override
    public void m_8068_(ClientboundSoundPacket p_105114_) {
        PacketUtils.m_131363_(p_105114_, this, this.f_291812_);
        this.f_291812_
            .f_91073_
            .m_262808_(
                this.f_291812_.f_91074_,
                p_105114_.m_133459_(),
                p_105114_.m_133460_(),
                p_105114_.m_133461_(),
                p_105114_.m_263229_(),
                p_105114_.m_133458_(),
                p_105114_.m_133462_(),
                p_105114_.m_133463_(),
                p_105114_.m_237848_()
            );
    }

    @Override
    public void m_5863_(ClientboundSoundEntityPacket p_105112_) {
        PacketUtils.m_131363_(p_105112_, this, this.f_291812_);
        Entity entity = this.f_104889_.m_6815_(p_105112_.m_133430_());
        if (entity != null) {
            this.f_291812_
                .f_91073_
                .m_213890_(
                    this.f_291812_.f_91074_,
                    entity,
                    p_105112_.m_263456_(),
                    p_105112_.m_133429_(),
                    p_105112_.m_133431_(),
                    p_105112_.m_133432_(),
                    p_105112_.m_237837_()
                );
        }
    }

    @Override
    public void m_7685_(ClientboundBossEventPacket p_104982_) {
        PacketUtils.m_131363_(p_104982_, this, this.f_291812_);
        this.f_291812_.f_91065_.m_93090_().m_93711_(p_104982_);
    }

    @Override
    public void m_7701_(ClientboundCooldownPacket p_105002_) {
        PacketUtils.m_131363_(p_105002_, this, this.f_291812_);
        if (p_105002_.f_131997_() == 0) {
            this.f_291812_.f_91074_.m_36335_().m_41527_(p_105002_.f_131996_());
        } else {
            this.f_291812_.f_91074_.m_36335_().m_41524_(p_105002_.f_131996_(), p_105002_.f_131997_());
        }
    }

    @Override
    public void m_7410_(ClientboundMoveVehiclePacket p_105038_) {
        PacketUtils.m_131363_(p_105038_, this, this.f_291812_);
        Entity entity = this.f_291812_.f_91074_.m_20201_();
        if (entity != this.f_291812_.f_91074_ && entity.m_6109_()) {
            entity.m_19890_(p_105038_.m_132591_(), p_105038_.m_132594_(), p_105038_.m_132595_(), p_105038_.m_132596_(), p_105038_.m_132597_());
            this.f_290549_.m_129512_(new ServerboundMoveVehiclePacket(entity));
        }
    }

    @Override
    public void m_6503_(ClientboundOpenBookPacket p_105040_) {
        PacketUtils.m_131363_(p_105040_, this, this.f_291812_);
        ItemStack itemstack = this.f_291812_.f_91074_.m_21120_(p_105040_.m_132608_());
        BookViewScreen.BookAccess bookviewscreen$bookaccess = BookViewScreen.BookAccess.m_98308_(itemstack);
        if (bookviewscreen$bookaccess != null) {
            this.f_291812_.m_91152_(new BookViewScreen(bookviewscreen$bookaccess));
        }
    }

    @Override
    public void m_105003_(CustomPacketPayload p_300286_) {
        if (p_300286_ instanceof PathfindingDebugPayload pathfindingdebugpayload) {
            this.f_291812_
                .f_91064_
                .f_113413_
                .m_113611_(pathfindingdebugpayload.f_290536_(), pathfindingdebugpayload.f_291873_(), pathfindingdebugpayload.f_291217_());
        } else if (p_300286_ instanceof NeighborUpdatesDebugPayload neighborupdatesdebugpayload) {
            ((NeighborsUpdateRenderer)this.f_291812_.f_91064_.f_113418_)
                .m_113596_(neighborupdatesdebugpayload.f_291308_(), neighborupdatesdebugpayload.f_290702_());
        } else if (p_300286_ instanceof StructuresDebugPayload structuresdebugpayload) {
            this.f_291812_
                .f_91064_
                .f_113420_
                .m_113682_(structuresdebugpayload.f_291102_(), structuresdebugpayload.f_291713_(), structuresdebugpayload.f_291455_());
        } else if (p_300286_ instanceof WorldGenAttemptDebugPayload worldgenattemptdebugpayload) {
            ((WorldGenAttemptRenderer)this.f_291812_.f_91064_.f_113422_)
                .m_113737_(
                    worldgenattemptdebugpayload.f_291689_(),
                    worldgenattemptdebugpayload.f_290326_(),
                    worldgenattemptdebugpayload.f_291188_(),
                    worldgenattemptdebugpayload.f_290800_(),
                    worldgenattemptdebugpayload.f_291344_(),
                    worldgenattemptdebugpayload.f_291261_()
                );
        } else if (p_300286_ instanceof PoiTicketCountDebugPayload poiticketcountdebugpayload) {
            this.f_291812_.f_91064_.f_113425_.m_113230_(poiticketcountdebugpayload.f_291600_(), poiticketcountdebugpayload.f_291747_());
        } else if (p_300286_ instanceof PoiAddedDebugPayload poiaddeddebugpayload) {
            BrainDebugRenderer.PoiInfo braindebugrenderer$poiinfo = new BrainDebugRenderer.PoiInfo(
                poiaddeddebugpayload.f_290840_(), poiaddeddebugpayload.f_315076_(), poiaddeddebugpayload.f_290692_()
            );
            this.f_291812_.f_91064_.f_113425_.m_113226_(braindebugrenderer$poiinfo);
        } else if (p_300286_ instanceof PoiRemovedDebugPayload poiremoveddebugpayload) {
            this.f_291812_.f_91064_.f_113425_.m_113228_(poiremoveddebugpayload.f_290491_());
        } else if (p_300286_ instanceof VillageSectionsDebugPayload villagesectionsdebugpayload) {
            VillageSectionsDebugRenderer villagesectionsdebugrenderer = this.f_291812_.f_91064_.f_113426_;
            villagesectionsdebugpayload.f_290824_().forEach(villagesectionsdebugrenderer::m_113709_);
            villagesectionsdebugpayload.f_291861_().forEach(villagesectionsdebugrenderer::m_113711_);
        } else if (p_300286_ instanceof GoalDebugPayload goaldebugpayload) {
            this.f_291812_.f_91064_.f_113429_.m_113548_(goaldebugpayload.f_290936_(), goaldebugpayload.f_290389_(), goaldebugpayload.f_290879_());
        } else if (p_300286_ instanceof BrainDebugPayload braindebugpayload) {
            this.f_291812_.f_91064_.f_113425_.m_113219_(braindebugpayload.f_291293_());
        } else if (p_300286_ instanceof BeeDebugPayload beedebugpayload) {
            this.f_291812_.f_91064_.f_113427_.m_113066_(beedebugpayload.f_291784_());
        } else if (p_300286_ instanceof HiveDebugPayload hivedebugpayload) {
            this.f_291812_.f_91064_.f_113427_.m_113071_(hivedebugpayload.f_291746_(), this.f_104889_.m_46467_());
        } else if (p_300286_ instanceof GameTestAddMarkerDebugPayload gametestaddmarkerdebugpayload) {
            this.f_291812_
                .f_91064_
                .f_113430_
                .m_113524_(
                    gametestaddmarkerdebugpayload.f_291551_(),
                    gametestaddmarkerdebugpayload.f_290458_(),
                    gametestaddmarkerdebugpayload.f_291302_(),
                    gametestaddmarkerdebugpayload.f_290945_()
                );
        } else if (p_300286_ instanceof GameTestClearMarkersDebugPayload) {
            this.f_291812_.f_91064_.f_113430_.m_5630_();
        } else if (p_300286_ instanceof RaidsDebugPayload raidsdebugpayload) {
            this.f_291812_.f_91064_.f_113428_.m_113663_(raidsdebugpayload.f_291474_());
        } else if (p_300286_ instanceof GameEventDebugPayload gameeventdebugpayload) {
            this.f_291812_.f_91064_.f_173815_.m_234513_(gameeventdebugpayload.f_314514_(), gameeventdebugpayload.f_291471_());
        } else if (p_300286_ instanceof GameEventListenerDebugPayload gameeventlistenerdebugpayload) {
            this.f_291812_.f_91064_.f_173815_.m_173830_(gameeventlistenerdebugpayload.f_290887_(), gameeventlistenerdebugpayload.f_291067_());
        } else if (p_300286_ instanceof BreezeDebugPayload breezedebugpayload) {
            this.f_291812_.f_91064_.f_302493_.m_306647_(breezedebugpayload.f_303745_());
        } else {
            this.m_292823_(p_300286_);
        }
    }

    private void m_292823_(CustomPacketPayload p_301051_) {
        f_104883_.warn("Unknown custom packet payload: {}", p_301051_.m_293297_().f_314054_());
    }

    @Override
    public void m_7957_(ClientboundSetObjectivePacket p_105100_) {
        PacketUtils.m_131363_(p_105100_, this, this.f_291812_);
        String s = p_105100_.m_133266_();
        if (p_105100_.m_133270_() == 0) {
            this.f_315162_.m_83436_(s, ObjectiveCriteria.f_83588_, p_105100_.m_133269_(), p_105100_.m_133271_(), false, p_105100_.m_307940_().orElse(null));
        } else {
            Objective objective = this.f_315162_.m_83477_(s);
            if (objective != null) {
                if (p_105100_.m_133270_() == 1) {
                    this.f_315162_.m_83502_(objective);
                } else if (p_105100_.m_133270_() == 2) {
                    objective.m_83314_(p_105100_.m_133271_());
                    objective.m_83316_(p_105100_.m_133269_());
                    objective.m_305060_(p_105100_.m_307940_().orElse(null));
                }
            }
        }
    }

    @Override
    public void m_7519_(ClientboundSetScorePacket p_105106_) {
        PacketUtils.m_131363_(p_105106_, this, this.f_291812_);
        String s = p_105106_.f_133324_();
        ScoreHolder scoreholder = ScoreHolder.m_306660_(p_105106_.f_133323_());
        Objective objective = this.f_315162_.m_83477_(s);
        if (objective != null) {
            ScoreAccess scoreaccess = this.f_315162_.m_307672_(scoreholder, objective, true);
            scoreaccess.m_305183_(p_105106_.f_133325_());
            scoreaccess.m_306789_(p_105106_.f_302966_().orElse(null));
            scoreaccess.m_304839_(p_105106_.f_302463_().orElse(null));
        } else {
            f_104883_.warn("Received packet for unknown scoreboard objective: {}", s);
        }
    }

    @Override
    public void m_305143_(ClientboundResetScorePacket p_312811_) {
        PacketUtils.m_131363_(p_312811_, this, this.f_291812_);
        String s = p_312811_.f_302815_();
        ScoreHolder scoreholder = ScoreHolder.m_306660_(p_312811_.f_303137_());
        if (s == null) {
            this.f_315162_.m_307153_(scoreholder);
        } else {
            Objective objective = this.f_315162_.m_83477_(s);
            if (objective != null) {
                this.f_315162_.m_305788_(scoreholder, objective);
            } else {
                f_104883_.warn("Received packet for unknown scoreboard objective: {}", s);
            }
        }
    }

    @Override
    public void m_5556_(ClientboundSetDisplayObjectivePacket p_105086_) {
        PacketUtils.m_131363_(p_105086_, this, this.f_291812_);
        String s = p_105086_.m_133142_();
        Objective objective = s == null ? null : this.f_315162_.m_83477_(s);
        this.f_315162_.m_7136_(p_105086_.m_133139_(), objective);
    }

    @Override
    public void m_5582_(ClientboundSetPlayerTeamPacket p_105104_) {
        PacketUtils.m_131363_(p_105104_, this, this.f_291812_);
        ClientboundSetPlayerTeamPacket.Action clientboundsetplayerteampacket$action = p_105104_.m_179338_();
        PlayerTeam playerteam;
        if (clientboundsetplayerteampacket$action == ClientboundSetPlayerTeamPacket.Action.ADD) {
            playerteam = this.f_315162_.m_83492_(p_105104_.m_133311_());
        } else {
            playerteam = this.f_315162_.m_83489_(p_105104_.m_133311_());
            if (playerteam == null) {
                f_104883_.warn(
                    "Received packet for unknown team {}: team action: {}, player action: {}",
                    p_105104_.m_133311_(),
                    p_105104_.m_179338_(),
                    p_105104_.m_179335_()
                );
                return;
            }
        }

        Optional<ClientboundSetPlayerTeamPacket.Parameters> optional = p_105104_.m_179339_();
        optional.ifPresent(p_233670_ -> {
            playerteam.m_83353_(p_233670_.m_179363_());
            playerteam.m_83351_(p_233670_.m_179367_());
            playerteam.m_83342_(p_233670_.m_179366_());
            Team.Visibility team$visibility = Team.Visibility.m_83579_(p_233670_.m_179368_());
            if (team$visibility != null) {
                playerteam.m_83346_(team$visibility);
            }

            Team.CollisionRule team$collisionrule = Team.CollisionRule.m_83555_(p_233670_.m_179369_());
            if (team$collisionrule != null) {
                playerteam.m_83344_(team$collisionrule);
            }

            playerteam.m_83360_(p_233670_.m_179370_());
            playerteam.m_83365_(p_233670_.m_179371_());
        });
        ClientboundSetPlayerTeamPacket.Action clientboundsetplayerteampacket$action1 = p_105104_.m_179335_();
        if (clientboundsetplayerteampacket$action1 == ClientboundSetPlayerTeamPacket.Action.ADD) {
            for (String s : p_105104_.m_133315_()) {
                this.f_315162_.m_6546_(s, playerteam);
            }
        } else if (clientboundsetplayerteampacket$action1 == ClientboundSetPlayerTeamPacket.Action.REMOVE) {
            for (String s1 : p_105104_.m_133315_()) {
                this.f_315162_.m_6519_(s1, playerteam);
            }
        }

        if (clientboundsetplayerteampacket$action == ClientboundSetPlayerTeamPacket.Action.REMOVE) {
            this.f_315162_.m_83475_(playerteam);
        }
    }

    @Override
    public void m_7406_(ClientboundLevelParticlesPacket p_105026_) {
        PacketUtils.m_131363_(p_105026_, this, this.f_291812_);
        if (p_105026_.m_132321_() == 0) {
            double d0 = (double)(p_105026_.m_132320_() * p_105026_.m_132317_());
            double d2 = (double)(p_105026_.m_132320_() * p_105026_.m_132318_());
            double d4 = (double)(p_105026_.m_132320_() * p_105026_.m_132319_());

            try {
                this.f_104889_
                    .m_6493_(p_105026_.m_132322_(), p_105026_.m_132311_(), p_105026_.m_132314_(), p_105026_.m_132315_(), p_105026_.m_132316_(), d0, d2, d4);
            } catch (Throwable throwable1) {
                f_104883_.warn("Could not spawn particle effect {}", p_105026_.m_132322_());
            }
        } else {
            for (int i = 0; i < p_105026_.m_132321_(); i++) {
                double d1 = this.f_104898_.m_188583_() * (double)p_105026_.m_132317_();
                double d3 = this.f_104898_.m_188583_() * (double)p_105026_.m_132318_();
                double d5 = this.f_104898_.m_188583_() * (double)p_105026_.m_132319_();
                double d6 = this.f_104898_.m_188583_() * (double)p_105026_.m_132320_();
                double d7 = this.f_104898_.m_188583_() * (double)p_105026_.m_132320_();
                double d8 = this.f_104898_.m_188583_() * (double)p_105026_.m_132320_();

                try {
                    this.f_104889_
                        .m_6493_(
                            p_105026_.m_132322_(),
                            p_105026_.m_132311_(),
                            p_105026_.m_132314_() + d1,
                            p_105026_.m_132315_() + d3,
                            p_105026_.m_132316_() + d5,
                            d6,
                            d7,
                            d8
                        );
                } catch (Throwable throwable) {
                    f_104883_.warn("Could not spawn particle effect {}", p_105026_.m_132322_());
                    return;
                }
            }
        }
    }

    @Override
    public void m_7710_(ClientboundUpdateAttributesPacket p_105128_) {
        PacketUtils.m_131363_(p_105128_, this, this.f_291812_);
        Entity entity = this.f_104889_.m_6815_(p_105128_.m_133588_());
        if (entity != null) {
            if (!(entity instanceof LivingEntity)) {
                throw new IllegalStateException("Server tried to update attributes of a non-living entity (actually: " + entity + ")");
            } else {
                AttributeMap attributemap = ((LivingEntity)entity).m_21204_();

                for (ClientboundUpdateAttributesPacket.AttributeSnapshot clientboundupdateattributespacket$attributesnapshot : p_105128_.m_133591_()) {
                    AttributeInstance attributeinstance = attributemap.m_246600_(clientboundupdateattributespacket$attributesnapshot.f_133593_());
                    if (attributeinstance == null) {
                        f_104883_.warn(
                            "Entity {} does not have attribute {}", entity, clientboundupdateattributespacket$attributesnapshot.f_133593_().m_323990_()
                        );
                    } else {
                        attributeinstance.m_22100_(clientboundupdateattributespacket$attributesnapshot.f_133594_());
                        attributeinstance.m_22132_();

                        for (AttributeModifier attributemodifier : clientboundupdateattributespacket$attributesnapshot.f_133595_()) {
                            attributeinstance.m_22118_(attributemodifier);
                        }
                    }
                }
            }
        }
    }

    @Override
    public void m_7339_(ClientboundPlaceGhostRecipePacket p_105046_) {
        PacketUtils.m_131363_(p_105046_, this, this.f_291812_);
        AbstractContainerMenu abstractcontainermenu = this.f_291812_.f_91074_.f_36096_;
        if (abstractcontainermenu.f_38840_ == p_105046_.m_132658_()) {
            this.f_104900_.m_44043_(p_105046_.m_132655_()).ifPresent(p_296228_ -> {
                if (this.f_291812_.f_91080_ instanceof RecipeUpdateListener) {
                    RecipeBookComponent recipebookcomponent = ((RecipeUpdateListener)this.f_291812_.f_91080_).m_5564_();
                    recipebookcomponent.m_7173_((RecipeHolder<?>)p_296228_, abstractcontainermenu.f_38839_);
                }
            });
        }
    }

    @Override
    public void m_183514_(ClientboundLightUpdatePacket p_194243_) {
        PacketUtils.m_131363_(p_194243_, this, this.f_291812_);
        int i = p_194243_.m_132349_();
        int j = p_194243_.m_132352_();
        ClientboundLightUpdatePacketData clientboundlightupdatepacketdata = p_194243_.m_195722_();
        this.f_104889_.m_194171_(() -> this.m_194248_(i, j, clientboundlightupdatepacketdata));
    }

    private void m_194248_(int p_194249_, int p_194250_, ClientboundLightUpdatePacketData p_194251_) {
        LevelLightEngine levellightengine = this.f_104889_.m_7726_().m_7827_();
        BitSet bitset = p_194251_.m_195740_();
        BitSet bitset1 = p_194251_.m_195751_();
        Iterator<byte[]> iterator = p_194251_.m_195754_().iterator();
        this.m_171734_(p_194249_, p_194250_, levellightengine, LightLayer.SKY, bitset, bitset1, iterator);
        BitSet bitset2 = p_194251_.m_195757_();
        BitSet bitset3 = p_194251_.m_195758_();
        Iterator<byte[]> iterator1 = p_194251_.m_195759_().iterator();
        this.m_171734_(p_194249_, p_194250_, levellightengine, LightLayer.BLOCK, bitset2, bitset3, iterator1);
        levellightengine.m_9335_(new ChunkPos(p_194249_, p_194250_), true);
    }

    @Override
    public void m_7330_(ClientboundMerchantOffersPacket p_105034_) {
        PacketUtils.m_131363_(p_105034_, this, this.f_291812_);
        AbstractContainerMenu abstractcontainermenu = this.f_291812_.f_91074_.f_36096_;
        if (p_105034_.m_132468_() == abstractcontainermenu.f_38840_ && abstractcontainermenu instanceof MerchantMenu merchantmenu) {
            merchantmenu.m_40046_(p_105034_.m_132471_());
            merchantmenu.m_40066_(p_105034_.m_132473_());
            merchantmenu.m_40069_(p_105034_.m_132472_());
            merchantmenu.m_40048_(p_105034_.m_132474_());
            merchantmenu.m_40058_(p_105034_.m_132475_());
        }
    }

    @Override
    public void m_7299_(ClientboundSetChunkCacheRadiusPacket p_105082_) {
        PacketUtils.m_131363_(p_105082_, this, this.f_291812_);
        this.f_104897_ = p_105082_.m_133108_();
        this.f_291812_.f_91066_.m_193770_(this.f_104897_);
        this.f_104889_.m_7726_().m_104416_(p_105082_.m_133108_());
    }

    @Override
    public void m_183623_(ClientboundSetSimulationDistancePacket p_194245_) {
        PacketUtils.m_131363_(p_194245_, this, this.f_291812_);
        this.f_194190_ = p_194245_.f_195796_();
        this.f_104889_.m_194174_(this.f_194190_);
    }

    @Override
    public void m_8065_(ClientboundSetChunkCacheCenterPacket p_105080_) {
        PacketUtils.m_131363_(p_105080_, this, this.f_291812_);
        this.f_104889_.m_7726_().m_104459_(p_105080_.m_133094_(), p_105080_.m_133097_());
    }

    @Override
    public void m_214108_(ClientboundBlockChangedAckPacket p_233698_) {
        PacketUtils.m_131363_(p_233698_, this, this.f_291812_);
        this.f_104889_.m_233651_(p_233698_.f_237578_());
    }

    @Override
    public void m_264308_(ClientboundBundlePacket p_265195_) {
        PacketUtils.m_131363_(p_265195_, this, this.f_291812_);

        for (Packet<? super ClientGamePacketListener> packet : p_265195_.m_264216_()) {
            packet.m_5797_(this);
        }
    }

    @Override
    public void m_319269_(ClientboundProjectilePowerPacket p_330827_) {
        PacketUtils.m_131363_(p_330827_, this, this.f_291812_);
        if (this.f_104889_.m_6815_(p_330827_.m_321243_()) instanceof AbstractHurtingProjectile abstracthurtingprojectile) {
            abstracthurtingprojectile.f_337582_ = p_330827_.m_338421_();
        }
    }

    @Override
    public void m_292715_(ClientboundChunkBatchStartPacket p_297740_) {
        this.f_291253_.m_293630_();
    }

    @Override
    public void m_293721_(ClientboundChunkBatchFinishedPacket p_300262_) {
        this.f_291253_.m_293201_(p_300262_.f_291136_());
        this.m_295327_(new ServerboundChunkBatchReceivedPacket(this.f_291253_.m_293338_()));
    }

    @Override
    public void m_319072_(ClientboundDebugSamplePacket p_333240_) {
        this.f_291812_.m_293199_().m_323707_(p_333240_.f_315508_(), p_333240_.f_316193_());
    }

    @Override
    public void m_105486_(ClientboundPongResponsePacket p_329147_) {
        this.f_290671_.m_295898_(p_329147_);
    }

    private void m_171734_(
        int p_171735_, int p_171736_, LevelLightEngine p_171737_, LightLayer p_171738_, BitSet p_171739_, BitSet p_171740_, Iterator<byte[]> p_171741_
    ) {
        for (int i = 0; i < p_171737_.m_164446_(); i++) {
            int j = p_171737_.m_164447_() + i;
            boolean flag = p_171739_.get(i);
            boolean flag1 = p_171740_.get(i);
            if (flag || flag1) {
                p_171737_.m_284126_(
                    p_171738_, SectionPos.m_123173_(p_171735_, j, p_171736_), flag ? new DataLayer((byte[])p_171741_.next().clone()) : new DataLayer()
                );
                this.f_104889_.m_104793_(p_171735_, j, p_171736_);
            }
        }
    }

    public Connection m_104910_() {
        return this.f_290549_;
    }

    @Override
    public boolean m_6198_() {
        return this.f_290549_.m_129536_() && !this.f_291533_;
    }

    public Collection<PlayerInfo> m_246170_() {
        return this.f_244156_;
    }

    public Collection<PlayerInfo> m_105142_() {
        return this.f_104892_.values();
    }

    public Collection<UUID> m_105143_() {
        return this.f_104892_.keySet();
    }

    @Nullable
    public PlayerInfo m_104949_(UUID p_104950_) {
        return this.f_104892_.get(p_104950_);
    }

    @Nullable
    public PlayerInfo m_104938_(String p_104939_) {
        for (PlayerInfo playerinfo : this.f_104892_.values()) {
            if (playerinfo.m_105312_().getName().equals(p_104939_)) {
                return playerinfo;
            }
        }

        return null;
    }

    public GameProfile m_105144_() {
        return this.f_104886_;
    }

    public ClientAdvancements m_105145_() {
        return this.f_104893_;
    }

    public CommandDispatcher<SharedSuggestionProvider> m_105146_() {
        return this.f_104899_;
    }

    public ClientLevel m_105147_() {
        return this.f_104889_;
    }

    public DebugQueryHandler m_105149_() {
        return this.f_104896_;
    }

    public UUID m_105150_() {
        return this.f_104901_;
    }

    public Set<ResourceKey<Level>> m_105151_() {
        return this.f_104902_;
    }

    public RegistryAccess.Frozen m_105152_() {
        return this.f_104903_;
    }

    public void m_242011_(PlayerChatMessage p_242356_, boolean p_242455_) {
        MessageSignature messagesignature = p_242356_.f_244279_();
        if (messagesignature != null && this.f_244346_.m_245220_(messagesignature, p_242455_) && this.f_244346_.m_245480_() > 64) {
            this.m_247711_();
        }
    }

    private void m_247711_() {
        int i = this.f_244346_.m_245313_();
        if (i > 0) {
            this.m_295327_(new ServerboundChatAckPacket(i));
        }
    }

    public void m_246175_(String p_249888_) {
        p_249888_ = net.minecraftforge.client.ForgeHooksClient.onClientSendMessage(p_249888_);
        if (p_249888_.isEmpty()) return;
        Instant instant = Instant.now();
        long i = Crypt.SaltSupplier.m_216113_();
        LastSeenMessagesTracker.Update lastseenmessagestracker$update = this.f_244346_.m_246442_();
        MessageSignature messagesignature = this.f_240902_.m_240988_(new SignedMessageBody(p_249888_, instant, i, lastseenmessagestracker$update.f_243872_()));
        this.m_295327_(new ServerboundChatPacket(p_249888_, instant, i, messagesignature, lastseenmessagestracker$update.f_244473_()));
    }

    public void m_246623_(String p_250092_) {
        if (net.minecraftforge.client.ClientCommandHandler.runCommand(p_250092_)) return;
        SignableCommand<SharedSuggestionProvider> signablecommand = SignableCommand.m_246497_(this.m_245186_(p_250092_));
        if (signablecommand.f_244150_().isEmpty()) {
            this.m_295327_(new ServerboundChatCommandPacket(p_250092_));
        } else {
            Instant instant = Instant.now();
            long i = Crypt.SaltSupplier.m_216113_();
            LastSeenMessagesTracker.Update lastseenmessagestracker$update = this.f_244346_.m_246442_();
            ArgumentSignatures argumentsignatures = ArgumentSignatures.m_245158_(signablecommand, p_247875_ -> {
                SignedMessageBody signedmessagebody = new SignedMessageBody(p_247875_, instant, i, lastseenmessagestracker$update.f_243872_());
                return this.f_240902_.m_240988_(signedmessagebody);
            });
            this.m_295327_(new ServerboundChatCommandSignedPacket(p_250092_, instant, i, argumentsignatures, lastseenmessagestracker$update.f_244473_()));
        }
    }

    public boolean m_246979_(String p_251509_) {
        if (!SignableCommand.m_319898_(this.m_245186_(p_251509_))) {
            this.m_295327_(new ServerboundChatCommandPacket(p_251509_));
            return true;
        } else {
            return false;
        }
    }

    private ParseResults<SharedSuggestionProvider> m_245186_(String p_249982_) {
        return this.f_104899_.parse(p_249982_, this.f_104894_);
    }

    @Override
    public void m_9933_() {
        if (this.f_290549_.m_129535_()) {
            ProfileKeyPairManager profilekeypairmanager = this.f_291812_.m_231465_();
            if (profilekeypairmanager.m_253130_()) {
                profilekeypairmanager.m_252904_().thenAcceptAsync(p_253339_ -> p_253339_.ifPresent(this::m_260951_), this.f_291812_);
            }
        }

        this.m_295826_();
        if (this.f_291812_.m_293199_().m_295643_()) {
            this.f_290671_.m_295617_();
        }

        this.f_316489_.m_322605_();
        this.f_291019_.m_261056_();
        if (this.f_302509_ != null) {
            this.f_302509_.m_304812_();
        }
    }

    public void m_260951_(ProfileKeyPair p_261475_) {
        if (this.f_291812_.m_292661_(this.f_104886_.getId())) {
            if (this.f_252517_ == null || !this.f_252517_.f_243926_().equals(p_261475_)) {
                this.f_252517_ = LocalChatSession.m_245157_(p_261475_);
                this.f_240902_ = this.f_252517_.m_247507_(this.f_104886_.getId());
                this.m_295327_(new ServerboundChatSessionUpdatePacket(this.f_252517_.m_245584_().m_245986_()));
            }
        }
    }

    @Nullable
    public ServerData m_245416_() {
        return this.f_291024_;
    }

    public FeatureFlagSet m_247016_() {
        return this.f_244039_;
    }

    public boolean m_246351_(FeatureFlagSet p_250605_) {
        return p_250605_.m_247715_(this.m_247016_());
    }

    public Scoreboard m_323009_() {
        return this.f_315162_;
    }

    public PotionBrewing m_320887_() {
        return this.f_315607_;
    }

    public void m_340234_() {
        this.f_337492_.m_340292_();
    }

    public SessionSearchTrees m_338605_() {
        return this.f_337492_;
    }

    public ServerLinks m_340176_() {
        return this.f_337041_;
    }
}
