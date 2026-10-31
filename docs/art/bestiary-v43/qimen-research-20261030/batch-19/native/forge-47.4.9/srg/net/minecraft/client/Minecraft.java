package net.minecraft.client;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Queues;
import com.mojang.authlib.GameProfile;
import com.mojang.authlib.exceptions.AuthenticationException;
import com.mojang.authlib.minecraft.BanDetails;
import com.mojang.authlib.minecraft.MinecraftSessionService;
import com.mojang.authlib.minecraft.UserApiService;
import com.mojang.authlib.minecraft.UserApiService.UserFlag;
import com.mojang.authlib.properties.PropertyMap;
import com.mojang.authlib.yggdrasil.ServicesKeyType;
import com.mojang.authlib.yggdrasil.YggdrasilAuthenticationService;
import com.mojang.blaze3d.pipeline.MainTarget;
import com.mojang.blaze3d.pipeline.RenderTarget;
import com.mojang.blaze3d.pipeline.TextureTarget;
import com.mojang.blaze3d.platform.DisplayData;
import com.mojang.blaze3d.platform.GlDebug;
import com.mojang.blaze3d.platform.GlUtil;
import com.mojang.blaze3d.platform.IconSet;
import com.mojang.blaze3d.platform.Window;
import com.mojang.blaze3d.platform.WindowEventHandler;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.systems.TimerQuery;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.BufferUploader;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.Tesselator;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.mojang.blaze3d.vertex.VertexSorting;
import com.mojang.datafixers.DataFixer;
import com.mojang.logging.LogUtils;
import com.mojang.realmsclient.client.RealmsClient;
import com.mojang.realmsclient.gui.RealmsDataFetcher;
import java.io.File;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.net.Proxy;
import java.net.SocketAddress;
import java.nio.ByteBuffer;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.DecimalFormat;
import java.text.DecimalFormatSymbols;
import java.time.Duration;
import java.time.Instant;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.MissingResourceException;
import java.util.Optional;
import java.util.Queue;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Supplier;
import java.util.stream.Stream;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.CrashReport;
import net.minecraft.CrashReportCategory;
import net.minecraft.FileUtil;
import net.minecraft.Optionull;
import net.minecraft.ReportedException;
import net.minecraft.SharedConstants;
import net.minecraft.SystemReport;
import net.minecraft.Util;
import net.minecraft.client.color.block.BlockColors;
import net.minecraft.client.color.item.ItemColors;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.Gui;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.toasts.SystemToast;
import net.minecraft.client.gui.components.toasts.ToastComponent;
import net.minecraft.client.gui.components.toasts.TutorialToast;
import net.minecraft.client.gui.font.FontManager;
import net.minecraft.client.gui.screens.AccessibilityOnboardingScreen;
import net.minecraft.client.gui.screens.BanNoticeScreen;
import net.minecraft.client.gui.screens.ChatScreen;
import net.minecraft.client.gui.screens.ConfirmLinkScreen;
import net.minecraft.client.gui.screens.DeathScreen;
import net.minecraft.client.gui.screens.GenericDirtMessageScreen;
import net.minecraft.client.gui.screens.InBedChatScreen;
import net.minecraft.client.gui.screens.LevelLoadingScreen;
import net.minecraft.client.gui.screens.LoadingOverlay;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraft.client.gui.screens.OutOfMemoryScreen;
import net.minecraft.client.gui.screens.Overlay;
import net.minecraft.client.gui.screens.PauseScreen;
import net.minecraft.client.gui.screens.ProgressScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.gui.screens.advancements.AdvancementsScreen;
import net.minecraft.client.gui.screens.inventory.CreativeModeInventoryScreen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.client.gui.screens.social.PlayerSocialManager;
import net.minecraft.client.gui.screens.social.SocialInteractionsScreen;
import net.minecraft.client.gui.screens.worldselection.WorldOpenFlows;
import net.minecraft.client.main.GameConfig;
import net.minecraft.client.model.geom.EntityModelSet;
import net.minecraft.client.multiplayer.ClientHandshakePacketListenerImpl;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.multiplayer.ClientPacketListener;
import net.minecraft.client.multiplayer.MultiPlayerGameMode;
import net.minecraft.client.multiplayer.ProfileKeyPairManager;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.chat.ChatListener;
import net.minecraft.client.multiplayer.chat.report.ReportEnvironment;
import net.minecraft.client.multiplayer.chat.report.ReportingContext;
import net.minecraft.client.particle.ParticleEngine;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.profiling.ClientMetricsSamplersProvider;
import net.minecraft.client.quickplay.QuickPlay;
import net.minecraft.client.quickplay.QuickPlayLog;
import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraft.client.renderer.FogRenderer;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.client.renderer.GpuWarnlistManager;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.RenderBuffers;
import net.minecraft.client.renderer.VirtualScreen;
import net.minecraft.client.renderer.block.BlockModelShaper;
import net.minecraft.client.renderer.block.BlockRenderDispatcher;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderDispatcher;
import net.minecraft.client.renderer.debug.DebugRenderer;
import net.minecraft.client.renderer.entity.EntityRenderDispatcher;
import net.minecraft.client.renderer.entity.EntityRenderers;
import net.minecraft.client.renderer.entity.ItemRenderer;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.renderer.texture.TextureManager;
import net.minecraft.client.resources.ClientPackSource;
import net.minecraft.client.resources.DownloadedPackSource;
import net.minecraft.client.resources.FoliageColorReloadListener;
import net.minecraft.client.resources.GrassColorReloadListener;
import net.minecraft.client.resources.MobEffectTextureManager;
import net.minecraft.client.resources.PaintingTextureManager;
import net.minecraft.client.resources.SkinManager;
import net.minecraft.client.resources.SplashManager;
import net.minecraft.client.resources.language.I18n;
import net.minecraft.client.resources.language.LanguageManager;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.client.resources.model.ModelManager;
import net.minecraft.client.searchtree.FullTextSearchTree;
import net.minecraft.client.searchtree.IdSearchTree;
import net.minecraft.client.searchtree.SearchRegistry;
import net.minecraft.client.searchtree.SearchTree;
import net.minecraft.client.server.IntegratedServer;
import net.minecraft.client.sounds.MusicManager;
import net.minecraft.client.sounds.SoundManager;
import net.minecraft.client.telemetry.ClientTelemetryManager;
import net.minecraft.client.telemetry.TelemetryProperty;
import net.minecraft.client.telemetry.events.GameLoadTimesEvent;
import net.minecraft.client.tutorial.Tutorial;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.network.Connection;
import net.minecraft.network.ConnectionProtocol;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.CommonComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.contents.KeybindResolver;
import net.minecraft.network.protocol.game.ServerboundPlayerActionPacket;
import net.minecraft.network.protocol.handshake.ClientIntentionPacket;
import net.minecraft.network.protocol.login.ServerboundHelloPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.Bootstrap;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.Services;
import net.minecraft.server.WorldStem;
import net.minecraft.server.level.progress.ProcessorChunkProgressListener;
import net.minecraft.server.level.progress.StoringChunkProgressListener;
import net.minecraft.server.packs.PackResources;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.VanillaPackResources;
import net.minecraft.server.packs.repository.FolderRepositorySource;
import net.minecraft.server.packs.repository.PackRepository;
import net.minecraft.server.packs.repository.PackSource;
import net.minecraft.server.packs.repository.RepositorySource;
import net.minecraft.server.packs.resources.ReloadInstance;
import net.minecraft.server.packs.resources.ReloadableResourceManager;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.players.GameProfileCache;
import net.minecraft.sounds.Music;
import net.minecraft.sounds.Musics;
import net.minecraft.tags.BiomeTags;
import net.minecraft.tags.TagKey;
import net.minecraft.util.FileZipper;
import net.minecraft.util.FrameTimer;
import net.minecraft.util.MemoryReserve;
import net.minecraft.util.ModCheck;
import net.minecraft.util.Mth;
import net.minecraft.util.SignatureValidator;
import net.minecraft.util.TimeUtil;
import net.minecraft.util.Unit;
import net.minecraft.util.datafix.DataFixers;
import net.minecraft.util.profiling.ContinuousProfiler;
import net.minecraft.util.profiling.EmptyProfileResults;
import net.minecraft.util.profiling.InactiveProfiler;
import net.minecraft.util.profiling.ProfileResults;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.util.profiling.ResultField;
import net.minecraft.util.profiling.SingleTickProfiler;
import net.minecraft.util.profiling.metrics.profiling.ActiveMetricsRecorder;
import net.minecraft.util.profiling.metrics.profiling.InactiveMetricsRecorder;
import net.minecraft.util.profiling.metrics.profiling.MetricsRecorder;
import net.minecraft.util.profiling.metrics.storage.MetricsPersister;
import net.minecraft.util.thread.ReentrantBlockableEventLoop;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.ChatVisiblity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.PlayerHeadItem;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.SkullBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.LevelStorageSource;
import net.minecraft.world.level.validation.DirectoryValidator;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.apache.commons.io.FileUtils;
import org.joml.Matrix4f;
import org.lwjgl.util.tinyfd.TinyFileDialogs;
import org.slf4j.Logger;

@OnlyIn(Dist.CLIENT)
public class Minecraft extends ReentrantBlockableEventLoop<Runnable> implements WindowEventHandler, net.minecraftforge.client.extensions.IForgeMinecraft {
   static Minecraft f_90981_;
   private static final Logger f_90982_ = LogUtils.getLogger();
   public static final boolean f_91002_ = Util.m_137581_() == Util.OS.OSX;
   private static final int f_167843_ = 10;
   public static final ResourceLocation f_91055_ = new ResourceLocation("default");
   public static final ResourceLocation f_91058_ = new ResourceLocation("uniform");
   public static final ResourceLocation f_91059_ = new ResourceLocation("alt");
   private static final ResourceLocation f_205119_ = new ResourceLocation("regional_compliancies.json");
   private static final CompletableFuture<Unit> f_90983_ = CompletableFuture.completedFuture(Unit.INSTANCE);
   private static final Component f_90984_ = Component.m_237115_("multiplayer.socialInteractions.not_available");
   public static final String f_167848_ = "Please make sure you have up-to-date drivers (see aka.ms/mcdriver for instructions).";
   private final Path f_90985_;
   private final PropertyMap f_90986_;
   public final TextureManager f_90987_;
   private final DataFixer f_90988_;
   private final VirtualScreen f_90989_;
   private final Window f_90990_;
   private final Timer f_90991_ = new Timer(20.0F, 0L);
   private final RenderBuffers f_90993_;
   public final LevelRenderer f_91060_;
   private final EntityRenderDispatcher f_90994_;
   private final ItemRenderer f_90995_;
   public final ParticleEngine f_91061_;
   private final SearchRegistry f_90997_ = new SearchRegistry();
   private final User f_90998_;
   public final Font f_91062_;
   public final Font f_243022_;
   public final GameRenderer f_91063_;
   public final DebugRenderer f_91064_;
   private final AtomicReference<StoringChunkProgressListener> f_90999_ = new AtomicReference<>();
   public final Gui f_91065_;
   public final Options f_91066_;
   private final HotbarManager f_91000_;
   public final MouseHandler f_91067_;
   public final KeyboardHandler f_91068_;
   private InputType f_263699_ = InputType.NONE;
   public final File f_91069_;
   private final String f_91001_;
   private final String f_91029_;
   private final Proxy f_91030_;
   private final LevelStorageSource f_91031_;
   public final FrameTimer f_91070_ = new FrameTimer();
   private final boolean f_91032_;
   private final boolean f_91033_;
   private final boolean f_91034_;
   private final boolean f_91035_;
   private final ReloadableResourceManager f_91036_;
   private final VanillaPackResources f_243783_;
   private final DownloadedPackSource f_243981_;
   private final PackRepository f_91038_;
   private final LanguageManager f_91039_;
   private final BlockColors f_91040_;
   private final ItemColors f_91041_;
   private final RenderTarget f_91042_;
   private final SoundManager f_91043_;
   private final MusicManager f_91044_;
   private final FontManager f_91045_;
   private final SplashManager f_91046_;
   private final GpuWarnlistManager f_91047_;
   private final PeriodicNotificationManager f_205120_ = new PeriodicNotificationManager(f_205119_, Minecraft::m_210782_);
   private final YggdrasilAuthenticationService f_231338_;
   private final MinecraftSessionService f_91048_;
   private final UserApiService f_193584_;
   private final SkinManager f_91050_;
   private final ModelManager f_91051_;
   private final BlockRenderDispatcher f_91052_;
   private final PaintingTextureManager f_91053_;
   private final MobEffectTextureManager f_91054_;
   private final ToastComponent f_91003_;
   private final Tutorial f_91005_;
   private final PlayerSocialManager f_91006_;
   private final EntityModelSet f_167844_;
   private final BlockEntityRenderDispatcher f_167845_;
   private final ClientTelemetryManager f_260676_;
   private final ProfileKeyPairManager f_231337_;
   private final RealmsDataFetcher f_238717_;
   private final QuickPlayLog f_278504_;
   @Nullable
   public MultiPlayerGameMode f_91072_;
   @Nullable
   public ClientLevel f_91073_;
   @Nullable
   public LocalPlayer f_91074_;
   @Nullable
   private IntegratedServer f_91007_;
   @Nullable
   private Connection f_91009_;
   private boolean f_91010_;
   @Nullable
   public Entity f_91075_;
   @Nullable
   public Entity f_91076_;
   @Nullable
   public HitResult f_91077_;
   private int f_91011_;
   protected int f_91078_;
   private volatile boolean f_91012_;
   private float f_91013_;
   private long f_91014_ = Util.m_137569_();
   private long f_91015_;
   private int f_91016_;
   public boolean f_91079_;
   @Nullable
   public Screen f_91080_;
   @Nullable
   private Overlay f_91081_;
   private boolean f_91017_;
   private Thread f_91018_;
   private volatile boolean f_91019_;
   @Nullable
   private Supplier<CrashReport> f_91020_;
   private static int f_91021_;
   public String f_90977_ = "";
   private long f_260560_;
   public boolean f_167842_;
   public boolean f_90978_;
   public boolean f_90979_;
   public boolean f_90980_ = true;
   private boolean f_91022_;
   private final Queue<Runnable> f_91023_ = Queues.newConcurrentLinkedQueue();
   @Nullable
   private CompletableFuture<Void> f_91024_;
   @Nullable
   private TutorialToast f_91025_;
   private ProfilerFiller f_91026_ = InactiveProfiler.f_18554_;
   private int f_91027_;
   private final ContinuousProfiler f_91028_ = new ContinuousProfiler(Util.f_137440_, () -> {
      return this.f_91027_;
   });
   @Nullable
   private ProfileResults f_91056_;
   private MetricsRecorder f_167846_ = InactiveMetricsRecorder.f_146153_;
   private final ResourceLoadStateTracker f_167847_ = new ResourceLoadStateTracker();
   private long f_231340_;
   private double f_231341_;
   @Nullable
   private TimerQuery.FrameProfile f_231342_;
   private final Realms32BitWarningStatus f_231343_;
   private final GameNarrator f_240365_;
   private final ChatListener f_240378_;
   private ReportingContext f_238638_;
   private String f_91057_ = "root";

   public Minecraft(GameConfig p_91084_) {
      super("Client");
      f_90981_ = this;
      this.f_91069_ = p_91084_.f_101907_.f_101916_;
      File file1 = p_91084_.f_101907_.f_101918_;
      this.f_90985_ = p_91084_.f_101907_.f_101917_.toPath();
      this.f_91001_ = p_91084_.f_101908_.f_101927_;
      this.f_91029_ = p_91084_.f_101908_.f_101928_;
      this.f_90986_ = p_91084_.f_101905_.f_101944_;
      ClientPackSource clientpacksource = new ClientPackSource(p_91084_.f_101907_.m_246261_());
      this.f_243981_ = new DownloadedPackSource(new File(this.f_91069_, "server-resource-packs"));
      RepositorySource repositorysource = new FolderRepositorySource(this.f_90985_, PackType.CLIENT_RESOURCES, PackSource.f_10527_);
      this.f_91038_ = new PackRepository(clientpacksource, this.f_243981_, repositorysource);
      this.f_243783_ = clientpacksource.m_246851_();
      this.f_91030_ = p_91084_.f_101905_.f_101945_;
      this.f_231338_ = new YggdrasilAuthenticationService(this.f_91030_);
      this.f_91048_ = this.f_231338_.createMinecraftSessionService();
      this.f_193584_ = this.m_193585_(this.f_231338_, p_91084_);
      this.f_90998_ = p_91084_.f_101905_.f_101942_;
      f_90982_.info("Setting user: {}", (Object)this.f_90998_.m_92546_());
      this.f_91033_ = p_91084_.f_101908_.f_101926_;
      this.f_91034_ = !p_91084_.f_101908_.f_101929_;
      this.f_91035_ = !p_91084_.f_101908_.f_101930_;
      this.f_91032_ = m_91272_();
      this.f_91007_ = null;
      KeybindResolver.m_237364_(KeyMapping::m_90842_);
      this.f_90988_ = DataFixers.m_14512_();
      this.f_91003_ = new ToastComponent(this);
      this.f_91018_ = Thread.currentThread();
      this.f_91066_ = new Options(this, this.f_91069_);
      RenderSystem.setShaderGlintAlpha(this.f_91066_.m_267782_().m_231551_());
      this.f_91019_ = true;
      this.f_91005_ = new Tutorial(this, this.f_91066_);
      this.f_91000_ = new HotbarManager(this.f_91069_, this.f_90988_);
      f_90982_.info("Backend library: {}", (Object)RenderSystem.getBackendDescription());
      DisplayData displaydata;
      if (this.f_91066_.f_92129_ > 0 && this.f_91066_.f_92128_ > 0) {
         displaydata = new DisplayData(this.f_91066_.f_92128_, this.f_91066_.f_92129_, p_91084_.f_101906_.f_84007_, p_91084_.f_101906_.f_84008_, p_91084_.f_101906_.f_84009_);
      } else {
         displaydata = p_91084_.f_101906_;
      }

      Util.f_137440_ = RenderSystem.initBackendSystem();
      this.f_90989_ = new VirtualScreen(this);
      this.f_90990_ = this.f_90989_.m_110872_(displaydata, this.f_91066_.f_92123_, this.m_91270_());
      this.m_7440_(true);
      GameLoadTimesEvent.f_285635_.m_285901_(TelemetryProperty.f_285649_);

      try {
         this.f_90990_.m_280655_(this.f_243783_, SharedConstants.m_183709_().m_132498_() ? IconSet.RELEASE : IconSet.SNAPSHOT);
      } catch (IOException ioexception) {
         f_90982_.error("Couldn't set icon", (Throwable)ioexception);
      }

      this.f_90990_.m_85380_(this.f_91066_.m_232035_().m_231551_());
      // FORGE: Move mouse and keyboard handler setup further below
      this.f_91067_ = new MouseHandler(this);
      this.f_91068_ = new KeyboardHandler(this);
      RenderSystem.initRenderer(this.f_91066_.f_92035_, false);
      this.f_91042_ = new MainTarget(this.f_90990_.m_85441_(), this.f_90990_.m_85442_());
      this.f_91042_.m_83931_(0.0F, 0.0F, 0.0F, 0.0F);
      this.f_91042_.m_83954_(f_91002_);
      this.f_91036_ = new ReloadableResourceManager(PackType.CLIENT_RESOURCES);
      net.minecraftforge.client.loading.ClientModLoader.begin(this, this.f_91038_, this.f_91036_);
      this.f_91038_.m_10506_();
      this.f_91066_.m_92145_(this.f_91038_);
      this.f_91039_ = new LanguageManager(this.f_91066_.f_92075_);
      this.f_91036_.m_7217_(this.f_91039_);
      this.f_90987_ = new TextureManager(this.f_91036_);
      this.f_91036_.m_7217_(this.f_90987_);
      this.f_91050_ = new SkinManager(this.f_90987_, new File(file1, "skins"), this.f_91048_);
      Path path = this.f_91069_.toPath();
      DirectoryValidator directoryvalidator = LevelStorageSource.m_289881_(path.resolve("allowed_symlinks.txt"));
      this.f_91031_ = new LevelStorageSource(path.resolve("saves"), path.resolve("backups"), directoryvalidator, this.f_90988_);
      this.f_91043_ = new SoundManager(this.f_91066_);
      this.f_91036_.m_7217_(this.f_91043_);
      this.f_91046_ = new SplashManager(this.f_90998_);
      this.f_91036_.m_7217_(this.f_91046_);
      this.f_91044_ = new MusicManager(this);
      this.f_91045_ = new FontManager(this.f_90987_);
      this.f_91062_ = this.f_91045_.m_95006_();
      this.f_243022_ = this.f_91045_.m_243082_();
      this.f_91036_.m_7217_(this.f_91045_);
      this.m_91336_(this.m_91390_());
      this.f_91036_.m_7217_(new GrassColorReloadListener());
      this.f_91036_.m_7217_(new FoliageColorReloadListener());
      this.f_90990_.m_85403_("Startup");
      RenderSystem.setupDefaultState(0, 0, this.f_90990_.m_85441_(), this.f_90990_.m_85442_());
      this.f_90990_.m_85403_("Post startup");
      this.f_91040_ = BlockColors.m_92574_();
      this.f_91041_ = ItemColors.m_92683_(this.f_91040_);
      this.f_91051_ = new ModelManager(this.f_90987_, this.f_91040_, this.f_91066_.m_232119_().m_231551_());
      this.f_91036_.m_7217_(this.f_91051_);
      this.f_167844_ = new EntityModelSet();
      this.f_91036_.m_7217_(this.f_167844_);
      this.f_167845_ = new BlockEntityRenderDispatcher(this.f_91062_, this.f_167844_, this::m_91289_, this::m_91291_, this::m_91290_);
      this.f_91036_.m_7217_(this.f_167845_);
      BlockEntityWithoutLevelRenderer blockentitywithoutlevelrenderer = new BlockEntityWithoutLevelRenderer(this.f_167845_, this.f_167844_);
      this.f_91036_.m_7217_(blockentitywithoutlevelrenderer);
      this.f_90995_ = new ItemRenderer(this, this.f_90987_, this.f_91051_, this.f_91041_, blockentitywithoutlevelrenderer);
      this.f_91036_.m_7217_(this.f_90995_);
      this.f_90993_ = new RenderBuffers();
      this.f_91006_ = new PlayerSocialManager(this, this.f_193584_);
      this.f_91052_ = new BlockRenderDispatcher(this.f_91051_.m_119430_(), blockentitywithoutlevelrenderer, this.f_91040_);
      this.f_91036_.m_7217_(this.f_91052_);
      this.f_90994_ = new EntityRenderDispatcher(this, this.f_90987_, this.f_90995_, this.f_91052_, this.f_91062_, this.f_91066_, this.f_167844_);
      this.f_91036_.m_7217_(this.f_90994_);
      this.f_91063_ = new GameRenderer(this, this.f_90994_.m_234586_(), this.f_91036_, this.f_90993_);
      this.f_91036_.m_7217_(this.f_91063_.m_247116_());
      this.f_91060_ = new LevelRenderer(this, this.f_90994_, this.f_167845_, this.f_90993_);
      net.minecraftforge.fml.ModLoader.get().postEvent(new net.minecraftforge.client.event.RenderLevelStageEvent.RegisterStageEvent());
      this.f_91036_.m_7217_(this.f_91060_);
      // Forge: We delay this to allow registration of modded creative mode tabs
      // this.createSearchTrees();
      this.f_91036_.m_7217_(this.f_90997_);
      this.f_91061_ = new ParticleEngine(this.f_91073_, this.f_90987_);
      net.minecraftforge.client.ForgeHooksClient.onRegisterParticleProviders(this.f_91061_);
      this.f_91036_.m_7217_(this.f_91061_);
      this.f_91053_ = new PaintingTextureManager(this.f_90987_);
      this.f_91036_.m_7217_(this.f_91053_);
      this.f_91054_ = new MobEffectTextureManager(this.f_90987_);
      this.f_91036_.m_7217_(this.f_91054_);
      this.f_91047_ = new GpuWarnlistManager();
      this.f_91036_.m_7217_(this.f_91047_);
      this.f_91036_.m_7217_(this.f_205120_);
      this.f_91065_ = new net.minecraftforge.client.gui.overlay.ForgeGui(this);
      // FORGE: Moved keyboard and mouse handler setup below ingame gui creation to prevent NPEs in them.
      this.f_91067_.m_91524_(this.f_90990_.m_85439_());
      this.f_91068_.m_90887_(this.f_90990_.m_85439_());
      this.f_91064_ = new DebugRenderer(this);
      RealmsClient realmsclient = RealmsClient.m_239151_(this);
      this.f_238717_ = new RealmsDataFetcher(realmsclient);
      RenderSystem.setErrorCallback(this::m_91113_);
      if (this.f_91042_.f_83915_ == this.f_90990_.m_85441_() && this.f_91042_.f_83916_ == this.f_90990_.m_85442_()) {
         if (this.f_91066_.m_231829_().m_231551_() && !this.f_90990_.m_85440_()) {
            this.f_90990_.m_85438_();
            this.f_91066_.m_231829_().m_231514_(this.f_90990_.m_85440_());
         }
      } else {
         StringBuilder stringbuilder = new StringBuilder("Recovering from unsupported resolution (" + this.f_90990_.m_85441_() + "x" + this.f_90990_.m_85442_() + ").\nPlease make sure you have up-to-date drivers (see aka.ms/mcdriver for instructions).");
         if (GlDebug.m_166226_()) {
            stringbuilder.append("\n\nReported GL debug messages:\n").append(String.join("\n", GlDebug.m_166225_()));
         }

         this.f_90990_.m_166447_(this.f_91042_.f_83915_, this.f_91042_.f_83916_);
         TinyFileDialogs.tinyfd_messageBox("Minecraft", stringbuilder.toString(), "ok", "error", false);
      }

      net.minecraftforge.client.ForgeHooksClient.initClientHooks(this, this.f_91036_);
      this.f_90990_.m_85409_(this.f_91066_.m_231817_().m_231551_());
      this.f_90990_.m_85424_(this.f_91066_.m_232123_().m_231551_());
      this.f_90990_.m_85426_();
      this.m_5741_();
      this.f_91063_.m_172722_(this.f_243783_.m_215363_());
      this.f_260676_ = new ClientTelemetryManager(this, this.f_193584_, this.f_90998_);
      this.f_231337_ = ProfileKeyPairManager.m_252915_(this.f_193584_, this.f_90998_, path);
      this.f_231343_ = new Realms32BitWarningStatus(this);
      this.f_240365_ = new GameNarrator(this);
      this.f_240365_.m_288189_(this.f_91066_.m_231930_().m_231551_() != NarratorStatus.OFF);
      this.f_240378_ = new ChatListener(this);
      this.f_240378_.m_240692_(this.f_91066_.m_232118_().m_231551_());
      this.f_238638_ = ReportingContext.m_239685_(ReportEnvironment.m_239898_(), this.f_193584_);
      LoadingOverlay.m_96189_(this);
      List<PackResources> list = this.f_91038_.m_10525_();
      this.f_167847_.m_168557_(ResourceLoadStateTracker.ReloadReason.INITIAL, list);
      ReloadInstance reloadinstance = this.f_91036_.m_142463_(Util.m_183991_(), this, f_90983_, list);
      GameLoadTimesEvent.f_285635_.m_285833_(TelemetryProperty.f_285629_);
      this.m_91150_(net.minecraftforge.fml.loading.ImmediateWindowHandler.<LoadingOverlay>loadingOverlay(()->this, ()->reloadinstance, (p_210745_) -> {
         Util.m_137521_(p_210745_, this::m_91239_, () -> {
            if (SharedConstants.f_136183_) {
               this.m_91273_();
            }

            this.f_167847_.m_168556_();
            this.m_286052_();
            if (net.minecraftforge.client.loading.ClientModLoader.completeModLoading())
               return; // Do not overwrite the error screen if there are errors
            // FORGE: Move opening initial screen to after startup and events are enabled
            if (this.m_239929_()) {
               this.m_91152_(BanNoticeScreen.m_239967_((p_278873_) -> {
                  if (p_278873_) {
                     Util.m_137581_().m_137646_("https://aka.ms/mcjavamoderation");
                  }

                  this.m_278684_(realmsclient, reloadinstance, p_91084_.f_278410_);
               }, this.m_239210_()));
            } else {
               this.m_278684_(realmsclient, reloadinstance, p_91084_.f_278410_);
            }
         });
      }, false).get());
      this.f_278504_ = QuickPlayLog.m_278648_(p_91084_.f_278410_.f_278493_());

   }

   private void m_286052_() {
      GameLoadTimesEvent.f_285635_.m_285901_(TelemetryProperty.f_285629_);
      GameLoadTimesEvent.f_285635_.m_285901_(TelemetryProperty.f_285605_);
      GameLoadTimesEvent.f_285635_.m_286019_(this.f_260676_.m_285963_());
   }

   private void m_278684_(RealmsClient p_279285_, ReloadInstance p_279164_, GameConfig.QuickPlayData p_279146_) {
      if (p_279146_.m_278736_()) {
         QuickPlay.m_278613_(this, p_279146_, p_279164_, p_279285_);
      } else if (this.f_91066_.f_263744_) {
         this.m_91152_(new AccessibilityOnboardingScreen(this.f_91066_));
      } else {
         this.m_91152_(new TitleScreen(true));
      }

   }

   private static boolean m_210782_(Object p_210783_) {
      try {
         return Locale.getDefault().getISO3Country().equals(p_210783_);
      } catch (MissingResourceException missingresourceexception) {
         return false;
      }
   }

   public void m_91341_() {
      this.f_90990_.m_85422_(this.m_91270_());
   }

   private String m_91270_() {
      StringBuilder stringbuilder = new StringBuilder("Minecraft");
      if (m_193589_().m_184597_()) {
         stringbuilder.append("* ").append(net.minecraftforge.forge.snapshots.ForgeSnapshotsMod.BRANDING_NAME);
      }

      stringbuilder.append(" ");
      stringbuilder.append(SharedConstants.m_183709_().m_132493_());
      ClientPacketListener clientpacketlistener = this.m_91403_();
      if (clientpacketlistener != null && clientpacketlistener.m_104910_().m_129536_()) {
         stringbuilder.append(" - ");
         if (this.f_91007_ != null && !this.f_91007_.m_6992_()) {
            stringbuilder.append(I18n.m_118938_("title.singleplayer"));
         } else if (this.m_91294_()) {
            stringbuilder.append(I18n.m_118938_("title.multiplayer.realms"));
         } else if (this.f_91007_ == null && (this.m_91089_() == null || !this.m_91089_().m_105389_())) {
            stringbuilder.append(I18n.m_118938_("title.multiplayer.other"));
         } else {
            stringbuilder.append(I18n.m_118938_("title.multiplayer.lan"));
         }
      }

      return stringbuilder.toString();
   }

   private UserApiService m_193585_(YggdrasilAuthenticationService p_193586_, GameConfig p_193587_) {
      try {
         if ("0".equals(p_193587_.f_101905_.f_101942_.m_92547_())) // Forge: We use "0" in dev. Short circuit to stop exception spam.
            return UserApiService.OFFLINE;
         return p_193586_.createUserApiService(p_193587_.f_101905_.f_101942_.m_92547_());
      } catch (AuthenticationException authenticationexception) {
         f_90982_.error("Failed to verify authentication", (Throwable)authenticationexception);
         return UserApiService.OFFLINE;
      }
   }

   public static ModCheck m_193589_() {
      return ModCheck.m_184600_("vanilla", ClientBrandRetriever::getClientModName, "Client", Minecraft.class);
   }

   private void m_91239_(Throwable p_91240_) {
      if (this.f_91038_.m_10524_().stream().anyMatch(e -> !e.m_10449_())) { //Forge: This caused infinite loop if any resource packs are forced. Such as mod resources. So check if we can disable any.
         this.m_91241_(p_91240_, (Component)null);
      } else {
         Util.m_137559_(p_91240_);
      }

   }

   public void m_91241_(Throwable p_91242_, @Nullable Component p_91243_) {
      f_90982_.info("Caught error loading resourcepacks, removing all selected resourcepacks", p_91242_);
      this.f_167847_.m_168560_(p_91242_);
      this.f_91038_.m_10509_(Collections.emptyList());
      this.f_91066_.f_92117_.clear();
      this.f_91066_.f_92118_.clear();
      this.f_91066_.m_92169_();
      this.m_168019_(true).thenRun(() -> {
         this.m_271937_(p_91243_);
      });
   }

   private void m_272186_() {
      this.m_91150_((Overlay)null);
      if (this.f_91073_ != null) {
         this.f_91073_.m_7462_();
         this.m_91399_();
      }

      this.m_91152_(new TitleScreen());
      this.m_271937_((Component)null);
   }

   private void m_271937_(@Nullable Component p_273566_) {
      ToastComponent toastcomponent = this.m_91300_();
      SystemToast.m_94869_(toastcomponent, SystemToast.SystemToastIds.PACK_LOAD_FAILURE, Component.m_237115_("resourcePack.load_fail"), p_273566_);
   }

   public void m_91374_() {
      this.f_91018_ = Thread.currentThread();
      if (Runtime.getRuntime().availableProcessors() > 4) {
         this.f_91018_.setPriority(10);
      }

      try {
         boolean flag = false;

         while(this.f_91019_) {
            if (this.f_91020_ != null) {
               m_91332_(this.f_91020_.get());
               return;
            }

            try {
               SingleTickProfiler singletickprofiler = SingleTickProfiler.m_18632_("Renderer");
               boolean flag1 = this.m_91274_();
               this.f_91026_ = this.m_167970_(flag1, singletickprofiler);
               this.f_91026_.m_7242_();
               this.f_167846_.m_142759_();
               this.m_91383_(!flag);
               this.f_167846_.m_142758_();
               this.f_91026_.m_7241_();
               this.m_91338_(flag1, singletickprofiler);
            } catch (OutOfMemoryError outofmemoryerror) {
               if (flag) {
                  throw outofmemoryerror;
               }

               this.m_91394_();
               this.m_91152_(new OutOfMemoryScreen());
               System.gc();
               f_90982_.error(LogUtils.FATAL_MARKER, "Out of memory", (Throwable)outofmemoryerror);
               flag = true;
            }
         }
      } catch (ReportedException reportedexception) {
         this.m_91354_(reportedexception.m_134761_());
         this.m_91394_();
         f_90982_.error(LogUtils.FATAL_MARKER, "Reported exception thrown!", (Throwable)reportedexception);
         m_91332_(reportedexception.m_134761_());
      } catch (Throwable throwable) {
         CrashReport crashreport = this.m_91354_(new CrashReport("Unexpected error", throwable));
         f_90982_.error(LogUtils.FATAL_MARKER, "Unreported exception thrown!", throwable);
         this.m_91394_();
         m_91332_(crashreport);
      }

   }

   void m_91336_(boolean p_91337_) {
      this.f_91045_.m_95011_(p_91337_ ? ImmutableMap.of(f_91055_, f_91058_) : ImmutableMap.of());
   }

   public void m_91271_() {
      var nameSearchKeys = net.minecraftforge.client.CreativeModeTabSearchRegistry.getNameSearchKeys();
      var tagSearchKeys = net.minecraftforge.client.CreativeModeTabSearchRegistry.getTagSearchKeys();
      for (var nameSearchKey : nameSearchKeys.values())
      this.f_90997_.m_235232_(nameSearchKey, (p_231389_) -> {
         return new FullTextSearchTree<>((p_210797_) -> {
            return p_210797_.m_41651_((Player)null, TooltipFlag.Default.f_256752_.m_257777_()).stream().map((p_210807_) -> {
               return ChatFormatting.m_126649_(p_210807_.getString()).trim();
            }).filter((p_210809_) -> {
               return !p_210809_.isEmpty();
            });
         }, (p_91317_) -> {
            return Stream.of(BuiltInRegistries.f_257033_.m_7981_(p_91317_.m_41720_()));
         }, p_231389_);
      });
      for (var tagSearchKey : tagSearchKeys.values())
      this.f_90997_.m_235232_(tagSearchKey, (p_231430_) -> {
         return new IdSearchTree<>((p_231353_) -> {
            return p_231353_.m_204131_().map(TagKey::f_203868_);
         }, p_231430_);
      });
      this.f_90997_.m_235232_(SearchRegistry.f_119943_, (p_231451_) -> {
         return new FullTextSearchTree<>((p_266611_) -> {
            return p_266611_.m_100516_().stream().flatMap((p_266607_) -> {
               return p_266607_.m_8043_(p_266611_.m_266543_()).m_41651_((Player)null, TooltipFlag.Default.f_256752_).stream();
            }).map((p_231455_) -> {
               return ChatFormatting.m_126649_(p_231455_.getString()).trim();
            }).filter((p_231449_) -> {
               return !p_231449_.isEmpty();
            });
         }, (p_266608_) -> {
            return p_266608_.m_100516_().stream().map((p_266610_) -> {
               return BuiltInRegistries.f_257033_.m_7981_(p_266610_.m_8043_(p_266608_.m_266543_()).m_41720_());
            });
         }, p_231451_);
      });
      nameSearchKeys.forEach((tab, nameSearchKey) -> {
         var tagSearchKey = tagSearchKeys.get(tab);
         tab.m_257882_(contents -> {
            this.m_231374_(nameSearchKey, contents);
            this.m_231374_(tagSearchKey, contents);
         });
      });
   }

   private void m_91113_(int p_91114_, long p_91115_) {
      this.f_91066_.m_231817_().m_231514_(false);
      this.f_91066_.m_92169_();
   }

   private static boolean m_91272_() {
      String[] astring = new String[]{"sun.arch.data.model", "com.ibm.vm.bitmode", "os.arch"};

      for(String s : astring) {
         String s1 = System.getProperty(s);
         if (s1 != null && s1.contains("64")) {
            return true;
         }
      }

      return false;
   }

   public RenderTarget m_91385_() {
      return this.f_91042_;
   }

   public String m_91388_() {
      return this.f_91001_;
   }

   public String m_91389_() {
      return this.f_91029_;
   }

   public void m_231412_(CrashReport p_231413_) {
      this.f_91020_ = () -> {
         return this.m_91354_(p_231413_);
      };
   }

   public void m_231439_(CrashReport p_231440_) {
      this.f_91020_ = () -> {
         return p_231440_;
      };
   }

   public static void m_91332_(CrashReport p_91333_) {
      File file1 = new File(m_91087_().f_91069_, "crash-reports");
      File file2 = new File(file1, "crash-" + Util.m_241986_() + "-client.txt");
      Bootstrap.m_135875_(p_91333_.m_127526_());
      if (p_91333_.m_127527_() != null) {
         Bootstrap.m_135875_("#@!@# Game crashed! Crash report saved to: #@!@# " + p_91333_.m_127527_());
         net.minecraftforge.server.ServerLifecycleHooks.handleExit(-1);
      } else if (p_91333_.m_127512_(file2)) {
         Bootstrap.m_135875_("#@!@# Game crashed! Crash report saved to: #@!@# " + file2.getAbsolutePath());
         net.minecraftforge.server.ServerLifecycleHooks.handleExit(-1);
      } else {
         Bootstrap.m_135875_("#@?@# Game crashed! Crash report could not be saved. #@?@#");
         net.minecraftforge.server.ServerLifecycleHooks.handleExit(-2);
      }

   }

   public boolean m_91390_() {
      return this.f_91066_.m_231819_().m_231551_();
   }

   public CompletableFuture<Void> m_91391_() {
      return this.m_168019_(false);
   }

   private CompletableFuture<Void> m_168019_(boolean p_168020_) {
      if (this.f_91024_ != null) {
         return this.f_91024_;
      } else {
         CompletableFuture<Void> completablefuture = new CompletableFuture<>();
         if (!p_168020_ && this.f_91081_ instanceof LoadingOverlay) {
            this.f_91024_ = completablefuture;
            return completablefuture;
         } else {
            this.f_91038_.m_10506_();
            List<PackResources> list = this.f_91038_.m_10525_();
            if (!p_168020_) {
               this.f_167847_.m_168557_(ResourceLoadStateTracker.ReloadReason.MANUAL, list);
            }

            this.m_91150_(new LoadingOverlay(this, this.f_91036_.m_142463_(Util.m_183991_(), this, f_90983_, list), (p_272299_) -> {
               Util.m_137521_(p_272299_, (p_272301_) -> {
                  if (p_168020_) {
                     this.m_272186_();
                  } else {
                     this.m_91239_(p_272301_);
                  }

               }, () -> {
                  this.f_91060_.m_109818_();
                  this.f_167847_.m_168556_();
                  completablefuture.complete((Void)null);
               });
            }, true));
            return completablefuture;
         }
      }
   }

   private void m_91273_() {
      boolean flag = false;
      BlockModelShaper blockmodelshaper = this.m_91289_().m_110907_();
      BakedModel bakedmodel = blockmodelshaper.m_110881_().m_119409_();

      for(Block block : BuiltInRegistries.f_256975_) {
         for(BlockState blockstate : block.m_49965_().m_61056_()) {
            if (blockstate.m_60799_() == RenderShape.MODEL) {
               BakedModel bakedmodel1 = blockmodelshaper.m_110893_(blockstate);
               if (bakedmodel1 == bakedmodel) {
                  f_90982_.debug("Missing model for: {}", (Object)blockstate);
                  flag = true;
               }
            }
         }
      }

      TextureAtlasSprite textureatlassprite1 = bakedmodel.m_6160_();

      for(Block block1 : BuiltInRegistries.f_256975_) {
         for(BlockState blockstate1 : block1.m_49965_().m_61056_()) {
            TextureAtlasSprite textureatlassprite = blockmodelshaper.m_110882_(blockstate1);
            if (!blockstate1.m_60795_() && textureatlassprite == textureatlassprite1) {
               f_90982_.debug("Missing particle icon for: {}", (Object)blockstate1);
            }
         }
      }

      for(Item item : BuiltInRegistries.f_257033_) {
         ItemStack itemstack = item.m_7968_();
         String s = itemstack.m_41778_();
         String s1 = Component.m_237115_(s).getString();
         if (s1.toLowerCase(Locale.ROOT).equals(item.m_5524_())) {
            f_90982_.debug("Missing translation for: {} {} {}", itemstack, s, item);
         }
      }

      flag |= MenuScreens.m_96198_();
      flag |= EntityRenderers.m_174035_();
      if (flag) {
         throw new IllegalStateException("Your game data is foobar, fix the errors above!");
      }
   }

   public LevelStorageSource m_91392_() {
      return this.f_91031_;
   }

   private void m_91326_(String p_91327_) {
      Minecraft.ChatStatus minecraft$chatstatus = this.m_168022_();
      if (!minecraft$chatstatus.m_142594_(this.m_91090_())) {
         if (this.f_91065_.m_238351_()) {
            this.f_91065_.m_238397_(false);
            this.m_91152_(new ConfirmLinkScreen((p_243338_) -> {
               if (p_243338_) {
                  Util.m_137581_().m_137646_("https://aka.ms/JavaAccountSettings");
               }

               this.m_91152_((Screen)null);
            }, Minecraft.ChatStatus.f_238170_, "https://aka.ms/JavaAccountSettings", true));
         } else {
            Component component = minecraft$chatstatus.m_168034_();
            this.f_91065_.m_93063_(component, false);
            this.f_240365_.m_168785_(component);
            this.f_91065_.m_238397_(minecraft$chatstatus == Minecraft.ChatStatus.DISABLED_BY_PROFILE);
         }
      } else {
         this.m_91152_(new ChatScreen(p_91327_));
      }

   }

   public void m_91152_(@Nullable Screen p_91153_) {
      if (SharedConstants.f_136183_ && Thread.currentThread() != this.f_91018_) {
         f_90982_.error("setScreen called from non-game thread");
      }

      if (p_91153_ == null && this.f_91073_ == null) {
         p_91153_ = new TitleScreen();
      } else if (p_91153_ == null && this.f_91074_.m_21224_()) {
         if (this.f_91074_.m_108632_()) {
            p_91153_ = new DeathScreen((Component)null, this.f_91073_.m_6106_().m_5466_());
         } else {
            this.f_91074_.m_7583_();
         }
      }

      net.minecraftforge.client.ForgeHooksClient.clearGuiLayers(this);
      Screen old = this.f_91080_;
      if (p_91153_ != null) {
         var event = new net.minecraftforge.client.event.ScreenEvent.Opening(old, p_91153_);
         if (net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(event)) return;
         p_91153_ = event.getNewScreen();
      }

      if (old != null && p_91153_ != old) {
         net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.client.event.ScreenEvent.Closing(old));
         old.m_7861_();
      }

      this.f_91080_ = p_91153_;
      if (this.f_91080_ != null) {
         this.f_91080_.m_274333_();
      }

      BufferUploader.m_166835_();
      if (p_91153_ != null) {
         this.f_91067_.m_91602_();
         KeyMapping.m_90847_();
         p_91153_.m_6575_(this, this.f_90990_.m_85445_(), this.f_90990_.m_85446_());
         this.f_91079_ = false;
      } else {
         this.f_91043_.m_120407_();
         this.f_91067_.m_91601_();
      }

      this.m_91341_();
   }

   public void m_91150_(@Nullable Overlay p_91151_) {
      this.f_91081_ = p_91151_;
   }

   public void m_91393_() {
      try {
         f_90982_.info("Stopping!");

         try {
            this.f_240365_.m_93329_();
         } catch (Throwable throwable1) {
         }

         try {
            if (this.f_91073_ != null) {
               this.f_91073_.m_7462_();
            }

            this.m_91399_();
         } catch (Throwable throwable) {
         }

         if (this.f_91080_ != null) {
            this.f_91080_.m_7861_();
         }

         this.close();
      } finally {
         Util.f_137440_ = System::nanoTime;
         if (this.f_91020_ == null) {
            System.exit(0);
         }

      }

   }

   public void close() {
      if (this.f_231342_ != null) {
         this.f_231342_.m_231149_();
      }

      try {
         this.f_260676_.close();
         this.f_205120_.close();
         this.f_91051_.close();
         this.f_91045_.close();
         this.f_91063_.close();
         this.f_91060_.close();
         this.f_91043_.m_120406_();
         this.f_91061_.m_107301_();
         this.f_91054_.close();
         this.f_91053_.close();
         this.f_90987_.close();
         this.f_91036_.close();
         Util.m_137580_();
      } catch (Throwable throwable) {
         f_90982_.error("Shutdown failure!", throwable);
         throw throwable;
      } finally {
         this.f_90989_.close();
         this.f_90990_.close();
      }

   }

   private void m_91383_(boolean p_91384_) {
      this.f_90990_.m_85403_("Pre render");
      long i = Util.m_137569_();
      if (this.f_90990_.m_85411_()) {
         this.m_91395_();
      }

      if (this.f_91024_ != null && !(this.f_91081_ instanceof LoadingOverlay)) {
         CompletableFuture<Void> completablefuture = this.f_91024_;
         this.f_91024_ = null;
         this.m_91391_().thenRun(() -> {
            completablefuture.complete((Void)null);
         });
      }

      Runnable runnable;
      while((runnable = this.f_91023_.poll()) != null) {
         runnable.run();
      }

      if (p_91384_) {
         int j = this.f_90991_.m_92525_(Util.m_137550_());
         this.f_91026_.m_6180_("scheduledExecutables");
         this.m_18699_();
         this.f_91026_.m_7238_();
         this.f_91026_.m_6180_("tick");

         for(int k = 0; k < Math.min(10, j); ++k) {
            this.f_91026_.m_6174_("clientTick");
            this.m_91398_();
         }

         this.f_91026_.m_7238_();
      }

      this.f_91067_.m_91523_();
      this.f_90990_.m_85403_("Render");
      this.f_91026_.m_6180_("sound");
      this.f_91043_.m_120361_(this.f_91063_.m_109153_());
      this.f_91026_.m_7238_();
      this.f_91026_.m_6180_("render");
      long j1 = Util.m_137569_();
      boolean flag;
      if (!this.f_91066_.f_92063_ && !this.f_167846_.m_142763_()) {
         flag = false;
         this.f_231341_ = 0.0D;
      } else {
         flag = this.f_231342_ == null || this.f_231342_.m_231150_();
         if (flag) {
            TimerQuery.m_231140_().ifPresent(TimerQuery::m_231141_);
         }
      }

      RenderSystem.clear(16640, f_91002_);
      this.f_91042_.m_83947_(true);
      FogRenderer.m_109017_();
      this.f_91026_.m_6180_("display");
      RenderSystem.enableCull();
      this.f_91026_.m_7238_();
      if (!this.f_91079_) {
         this.realPartialTick = this.f_91012_ ? this.f_91013_ : this.f_90991_.f_92518_; // Cache this since pause is volatile
         net.minecraftforge.event.ForgeEventFactory.onRenderTickStart(this.realPartialTick);
         this.f_91026_.m_6182_("gameRenderer");
         this.f_91063_.m_109093_(this.f_91012_ ? this.f_91013_ : this.f_90991_.f_92518_, i, p_91384_);
         this.f_91026_.m_7238_();
         net.minecraftforge.event.ForgeEventFactory.onRenderTickEnd(this.realPartialTick);
      }

      if (this.f_91056_ != null) {
         this.f_91026_.m_6180_("fpsPie");
         GuiGraphics guigraphics = new GuiGraphics(this, this.f_90993_.m_110104_());
         this.m_280564_(guigraphics, this.f_91056_);
         guigraphics.m_280262_();
         this.f_91026_.m_7238_();
      }

      this.f_91026_.m_6180_("blit");
      this.f_91042_.m_83970_();
      this.f_91042_.m_83938_(this.f_90990_.m_85441_(), this.f_90990_.m_85442_());
      this.f_260560_ = Util.m_137569_() - j1;
      if (flag) {
         TimerQuery.m_231140_().ifPresent((p_231363_) -> {
            this.f_231342_ = p_231363_.m_231142_();
         });
      }

      this.f_91026_.m_6182_("updateDisplay");
      this.f_90990_.m_85435_();
      int k1 = this.m_91275_();
      if (k1 < 260) {
         RenderSystem.limitDisplayFPS(k1);
      }

      this.f_91026_.m_6182_("yield");
      Thread.yield();
      this.f_91026_.m_7238_();
      this.f_90990_.m_85403_("Post render");
      ++this.f_91016_;
      boolean flag1 = this.m_91091_() && (this.f_91080_ != null && this.f_91080_.m_7043_() || this.f_91081_ != null && this.f_91081_.m_7859_()) && !this.f_91007_.m_6992_();
      if (this.f_91012_ != flag1) {
         if (this.f_91012_) {
            this.f_91013_ = this.f_90991_.f_92518_;
         } else {
            this.f_90991_.f_92518_ = this.f_91013_;
         }

         this.f_91012_ = flag1;
      }

      long l = Util.m_137569_();
      long i1 = l - this.f_91014_;
      if (flag) {
         this.f_231340_ = i1;
      }

      this.f_91070_.m_13755_(i1);
      this.f_91014_ = l;
      this.f_91026_.m_6180_("fpsUpdate");
      if (this.f_231342_ != null && this.f_231342_.m_231150_()) {
         this.f_231341_ = (double)this.f_231342_.m_231151_() * 100.0D / (double)this.f_231340_;
      }

      while(Util.m_137550_() >= this.f_91015_ + 1000L) {
         String s;
         if (this.f_231341_ > 0.0D) {
            s = " GPU: " + (this.f_231341_ > 100.0D ? ChatFormatting.RED + "100%" : Math.round(this.f_231341_) + "%");
         } else {
            s = "";
         }

         f_91021_ = this.f_91016_;
         this.f_90977_ = String.format(Locale.ROOT, "%d fps T: %s%s%s%s B: %d%s", f_91021_, k1 == 260 ? "inf" : k1, this.f_91066_.m_231817_().m_231551_() ? " vsync" : "", this.f_91066_.m_232060_().m_231551_(), this.f_91066_.m_232050_().m_231551_() == CloudStatus.OFF ? "" : (this.f_91066_.m_232050_().m_231551_() == CloudStatus.FAST ? " fast-clouds" : " fancy-clouds"), this.f_91066_.m_232121_().m_231551_(), s);
         this.f_91015_ += 1000L;
         this.f_91016_ = 0;
      }

      this.f_91026_.m_7238_();
   }

   private boolean m_91274_() {
      return this.f_91066_.f_92063_ && this.f_91066_.f_92064_ && !this.f_91066_.f_92062_;
   }

   private ProfilerFiller m_167970_(boolean p_167971_, @Nullable SingleTickProfiler p_167972_) {
      if (!p_167971_) {
         this.f_91028_.m_18437_();
         if (!this.f_167846_.m_142763_() && p_167972_ == null) {
            return InactiveProfiler.f_18554_;
         }
      }

      ProfilerFiller profilerfiller;
      if (p_167971_) {
         if (!this.f_91028_.m_18436_()) {
            this.f_91027_ = 0;
            this.f_91028_.m_18438_();
         }

         ++this.f_91027_;
         profilerfiller = this.f_91028_.m_18439_();
      } else {
         profilerfiller = InactiveProfiler.f_18554_;
      }

      if (this.f_167846_.m_142763_()) {
         profilerfiller = ProfilerFiller.m_18578_(profilerfiller, this.f_167846_.m_142610_());
      }

      return SingleTickProfiler.m_18629_(profilerfiller, p_167972_);
   }

   private void m_91338_(boolean p_91339_, @Nullable SingleTickProfiler p_91340_) {
      if (p_91340_ != null) {
         p_91340_.m_18634_();
      }

      if (p_91339_) {
         this.f_91056_ = this.f_91028_.m_18440_();
      } else {
         this.f_91056_ = null;
      }

      this.f_91026_ = this.f_91028_.m_18439_();
   }

   public void m_5741_() {
      int i = this.f_90990_.m_85385_(this.f_91066_.m_231928_().m_231551_(), this.m_91390_());
      this.f_90990_.m_85378_((double)i);
      if (this.f_91080_ != null) {
         this.f_91080_.m_6574_(this, this.f_90990_.m_85445_(), this.f_90990_.m_85446_());
         net.minecraftforge.client.ForgeHooksClient.resizeGuiLayers(this, this.f_90990_.m_85445_(), this.f_90990_.m_85446_());
      }

      RenderTarget rendertarget = this.m_91385_();
      rendertarget.m_83941_(this.f_90990_.m_85441_(), this.f_90990_.m_85442_(), f_91002_);
      if (this.f_91063_ != null)
      this.f_91063_.m_109097_(this.f_90990_.m_85441_(), this.f_90990_.m_85442_());
      this.f_91067_.m_91599_();
   }

   public void m_5740_() {
      this.f_91067_.m_91603_();
   }

   public int m_260875_() {
      return f_91021_;
   }

   public long m_261169_() {
      return this.f_260560_;
   }

   private int m_91275_() {
      return this.f_91073_ != null || this.f_91080_ == null && this.f_91081_ == null ? this.f_90990_.m_85434_() : 60;
   }

   public void m_91394_() {
      try {
         MemoryReserve.m_182328_();
         this.f_91060_.m_109824_();
      } catch (Throwable throwable1) {
      }

      try {
         System.gc();
         if (this.f_91010_ && this.f_91007_ != null) {
            this.f_91007_.m_7570_(true);
         }

         this.m_91320_(new GenericDirtMessageScreen(Component.m_237115_("menu.savingLevel")));
      } catch (Throwable throwable) {
      }

      System.gc();
   }

   public boolean m_167946_(Consumer<Component> p_167947_) {
      if (this.f_167846_.m_142763_()) {
         this.m_167975_();
         return false;
      } else {
         Consumer<ProfileResults> consumer = (p_231435_) -> {
            if (p_231435_ != EmptyProfileResults.f_18441_) {
               int i = p_231435_.m_7315_();
               double d0 = (double)p_231435_.m_18577_() / (double)TimeUtil.f_145016_;
               this.execute(() -> {
                  p_167947_.accept(Component.m_237110_("commands.debug.stopped", String.format(Locale.ROOT, "%.2f", d0), i, String.format(Locale.ROOT, "%.2f", (double)i / d0)));
               });
            }
         };
         Consumer<Path> consumer1 = (p_231438_) -> {
            Component component = Component.m_237113_(p_231438_.toString()).m_130940_(ChatFormatting.UNDERLINE).m_130938_((p_231387_) -> {
               return p_231387_.m_131142_(new ClickEvent(ClickEvent.Action.OPEN_FILE, p_231438_.toFile().getParent()));
            });
            this.execute(() -> {
               p_167947_.accept(Component.m_237110_("debug.profiling.stop", component));
            });
         };
         SystemReport systemreport = m_167850_(new SystemReport(), this, this.f_91039_, this.f_91001_, this.f_91066_);
         Consumer<List<Path>> consumer2 = (p_231349_) -> {
            Path path = this.m_167856_(systemreport, p_231349_);
            consumer1.accept(path);
         };
         Consumer<Path> consumer3;
         if (this.f_91007_ == null) {
            consumer3 = (p_231404_) -> {
               consumer2.accept(ImmutableList.of(p_231404_));
            };
         } else {
            this.f_91007_.m_177935_(systemreport);
            CompletableFuture<Path> completablefuture = new CompletableFuture<>();
            CompletableFuture<Path> completablefuture1 = new CompletableFuture<>();
            CompletableFuture.allOf(completablefuture, completablefuture1).thenRunAsync(() -> {
               consumer2.accept(ImmutableList.of(completablefuture.join(), completablefuture1.join()));
            }, Util.m_183992_());
            this.f_91007_.m_177923_((p_231351_) -> {
            }, completablefuture1::complete);
            consumer3 = completablefuture::complete;
         }

         this.f_167846_ = ActiveMetricsRecorder.m_146132_(new ClientMetricsSamplersProvider(Util.f_137440_, this.f_91060_), Util.f_137440_, Util.m_183992_(), new MetricsPersister("client"), (p_231401_) -> {
            this.f_167846_ = InactiveMetricsRecorder.f_146153_;
            consumer.accept(p_231401_);
         }, consumer3);
         return true;
      }
   }

   private void m_167975_() {
      this.f_167846_.m_142760_();
      if (this.f_91007_ != null) {
         this.f_91007_.m_177929_();
      }

   }

   private void m_231418_() {
      this.f_167846_.m_213832_();
      if (this.f_91007_ != null) {
         this.f_91007_.m_236737_();
      }

   }

   private Path m_167856_(SystemReport p_167857_, List<Path> p_167858_) {
      String s;
      if (this.m_91090_()) {
         s = this.m_91092_().m_129910_().m_5462_();
      } else {
         ServerData serverdata = this.m_91089_();
         s = serverdata != null ? serverdata.f_105362_ : "unknown";
      }

      Path path;
      try {
         String s2 = String.format(Locale.ROOT, "%s-%s-%s", Util.m_241986_(), s, SharedConstants.m_183709_().m_132492_());
         String s1 = FileUtil.m_133730_(MetricsPersister.f_146209_, s2, ".zip");
         path = MetricsPersister.f_146209_.resolve(s1);
      } catch (IOException ioexception1) {
         throw new UncheckedIOException(ioexception1);
      }

      try (FileZipper filezipper = new FileZipper(path)) {
         filezipper.m_144703_(Paths.get("system.txt"), p_167857_.m_143515_());
         filezipper.m_144703_(Paths.get("client").resolve(this.f_91066_.m_168450_().getName()), this.f_91066_.m_168451_());
         p_167858_.forEach(filezipper::m_144698_);
      } finally {
         for(Path path1 : p_167858_) {
            try {
               FileUtils.forceDelete(path1.toFile());
            } catch (IOException ioexception) {
               f_90982_.warn("Failed to delete temporary profiling result {}", path1, ioexception);
            }
         }

      }

      return path;
   }

   public void m_91111_(int p_91112_) {
      if (this.f_91056_ != null) {
         List<ResultField> list = this.f_91056_.m_6412_(this.f_91057_);
         if (!list.isEmpty()) {
            ResultField resultfield = list.remove(0);
            if (p_91112_ == 0) {
               if (!resultfield.f_18610_.isEmpty()) {
                  int i = this.f_91057_.lastIndexOf(30);
                  if (i >= 0) {
                     this.f_91057_ = this.f_91057_.substring(0, i);
                  }
               }
            } else {
               --p_91112_;
               if (p_91112_ < list.size() && !"unspecified".equals((list.get(p_91112_)).f_18610_)) {
                  if (!this.f_91057_.isEmpty()) {
                     this.f_91057_ = this.f_91057_ + "\u001e";
                  }

                  this.f_91057_ = this.f_91057_ + (list.get(p_91112_)).f_18610_;
               }
            }

         }
      }
   }

   private void m_280564_(GuiGraphics p_281277_, ProfileResults p_281574_) {
      List<ResultField> list = p_281574_.m_6412_(this.f_91057_);
      ResultField resultfield = list.remove(0);
      RenderSystem.clear(256, f_91002_);
      RenderSystem.setShader(GameRenderer::m_172811_);
      Matrix4f matrix4f = (new Matrix4f()).setOrtho(0.0F, (float)this.f_90990_.m_85441_(), (float)this.f_90990_.m_85442_(), 0.0F, 1000.0F, 3000.0F);
      RenderSystem.setProjectionMatrix(matrix4f, VertexSorting.f_276633_);
      PoseStack posestack = RenderSystem.getModelViewStack();
      posestack.m_85836_();
      posestack.m_166856_();
      posestack.m_252880_(0.0F, 0.0F, -2000.0F);
      RenderSystem.applyModelViewMatrix();
      RenderSystem.lineWidth(1.0F);
      Tesselator tesselator = Tesselator.m_85913_();
      BufferBuilder bufferbuilder = tesselator.m_85915_();
      int i = 160;
      int j = this.f_90990_.m_85441_() - 160 - 10;
      int k = this.f_90990_.m_85442_() - 320;
      RenderSystem.enableBlend();
      bufferbuilder.m_166779_(VertexFormat.Mode.QUADS, DefaultVertexFormat.f_85815_);
      bufferbuilder.m_5483_((double)((float)j - 176.0F), (double)((float)k - 96.0F - 16.0F), 0.0D).m_6122_(200, 0, 0, 0).m_5752_();
      bufferbuilder.m_5483_((double)((float)j - 176.0F), (double)(k + 320), 0.0D).m_6122_(200, 0, 0, 0).m_5752_();
      bufferbuilder.m_5483_((double)((float)j + 176.0F), (double)(k + 320), 0.0D).m_6122_(200, 0, 0, 0).m_5752_();
      bufferbuilder.m_5483_((double)((float)j + 176.0F), (double)((float)k - 96.0F - 16.0F), 0.0D).m_6122_(200, 0, 0, 0).m_5752_();
      tesselator.m_85914_();
      RenderSystem.disableBlend();
      double d0 = 0.0D;

      for(ResultField resultfield1 : list) {
         int l = Mth.m_14107_(resultfield1.f_18607_ / 4.0D) + 1;
         bufferbuilder.m_166779_(VertexFormat.Mode.TRIANGLE_FAN, DefaultVertexFormat.f_85815_);
         int i1 = resultfield1.m_18616_();
         int j1 = i1 >> 16 & 255;
         int k1 = i1 >> 8 & 255;
         int l1 = i1 & 255;
         bufferbuilder.m_5483_((double)j, (double)k, 0.0D).m_6122_(j1, k1, l1, 255).m_5752_();

         for(int i2 = l; i2 >= 0; --i2) {
            float f = (float)((d0 + resultfield1.f_18607_ * (double)i2 / (double)l) * (double)((float)Math.PI * 2F) / 100.0D);
            float f1 = Mth.m_14031_(f) * 160.0F;
            float f2 = Mth.m_14089_(f) * 160.0F * 0.5F;
            bufferbuilder.m_5483_((double)((float)j + f1), (double)((float)k - f2), 0.0D).m_6122_(j1, k1, l1, 255).m_5752_();
         }

         tesselator.m_85914_();
         bufferbuilder.m_166779_(VertexFormat.Mode.TRIANGLE_STRIP, DefaultVertexFormat.f_85815_);

         for(int l2 = l; l2 >= 0; --l2) {
            float f3 = (float)((d0 + resultfield1.f_18607_ * (double)l2 / (double)l) * (double)((float)Math.PI * 2F) / 100.0D);
            float f4 = Mth.m_14031_(f3) * 160.0F;
            float f5 = Mth.m_14089_(f3) * 160.0F * 0.5F;
            if (!(f5 > 0.0F)) {
               bufferbuilder.m_5483_((double)((float)j + f4), (double)((float)k - f5), 0.0D).m_6122_(j1 >> 1, k1 >> 1, l1 >> 1, 255).m_5752_();
               bufferbuilder.m_5483_((double)((float)j + f4), (double)((float)k - f5 + 10.0F), 0.0D).m_6122_(j1 >> 1, k1 >> 1, l1 >> 1, 255).m_5752_();
            }
         }

         tesselator.m_85914_();
         d0 += resultfield1.f_18607_;
      }

      DecimalFormat decimalformat = new DecimalFormat("##0.00");
      decimalformat.setDecimalFormatSymbols(DecimalFormatSymbols.getInstance(Locale.ROOT));
      String s = ProfileResults.m_18575_(resultfield.f_18610_);
      String s1 = "";
      if (!"unspecified".equals(s)) {
         s1 = s1 + "[0] ";
      }

      if (s.isEmpty()) {
         s1 = s1 + "ROOT ";
      } else {
         s1 = s1 + s + " ";
      }

      int k2 = 16777215;
      p_281277_.m_280488_(this.f_91062_, s1, j - 160, k - 80 - 16, 16777215);
      s1 = decimalformat.format(resultfield.f_18608_) + "%";
      p_281277_.m_280488_(this.f_91062_, s1, j + 160 - this.f_91062_.m_92895_(s1), k - 80 - 16, 16777215);

      for(int j2 = 0; j2 < list.size(); ++j2) {
         ResultField resultfield2 = list.get(j2);
         StringBuilder stringbuilder = new StringBuilder();
         if ("unspecified".equals(resultfield2.f_18610_)) {
            stringbuilder.append("[?] ");
         } else {
            stringbuilder.append("[").append(j2 + 1).append("] ");
         }

         String s2 = stringbuilder.append(resultfield2.f_18610_).toString();
         p_281277_.m_280488_(this.f_91062_, s2, j - 160, k + 80 + j2 * 8 + 20, resultfield2.m_18616_());
         s2 = decimalformat.format(resultfield2.f_18607_) + "%";
         p_281277_.m_280488_(this.f_91062_, s2, j + 160 - 50 - this.f_91062_.m_92895_(s2), k + 80 + j2 * 8 + 20, resultfield2.m_18616_());
         s2 = decimalformat.format(resultfield2.f_18608_) + "%";
         p_281277_.m_280488_(this.f_91062_, s2, j + 160 - this.f_91062_.m_92895_(s2), k + 80 + j2 * 8 + 20, resultfield2.m_18616_());
      }

      posestack.m_85849_();
      RenderSystem.applyModelViewMatrix();
   }

   public void m_91395_() {
      if (this.m_91396_()) net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.GameShuttingDownEvent());
      this.f_91019_ = false;
   }

   public boolean m_91396_() {
      return this.f_91019_;
   }

   public void m_91358_(boolean p_91359_) {
      if (this.f_91080_ == null) {
         boolean flag = this.m_91091_() && !this.f_91007_.m_6992_();
         if (flag) {
            this.m_91152_(new PauseScreen(!p_91359_));
            this.f_91043_.m_120391_();
         } else {
            this.m_91152_(new PauseScreen(true));
         }

      }
   }

   private void m_91386_(boolean p_91387_) {
      if (!p_91387_) {
         this.f_91078_ = 0;
      }

      if (this.f_91078_ <= 0 && !this.f_91074_.m_6117_()) {
         if (p_91387_ && this.f_91077_ != null && this.f_91077_.m_6662_() == HitResult.Type.BLOCK) {
            BlockHitResult blockhitresult = (BlockHitResult)this.f_91077_;
            BlockPos blockpos = blockhitresult.m_82425_();
            if (!this.f_91073_.m_46859_(blockpos)) {
               var inputEvent = net.minecraftforge.client.ForgeHooksClient.onClickInput(0, this.f_91066_.f_92096_, InteractionHand.MAIN_HAND);
               if (inputEvent.isCanceled()) {
                  if (inputEvent.shouldSwingHand()) {
                     this.f_91061_.addBlockHitEffects(blockpos, blockhitresult);
                     this.f_91074_.m_6674_(InteractionHand.MAIN_HAND);
                  }
                  return;
               }
               Direction direction = blockhitresult.m_82434_();
               if (this.f_91072_.m_105283_(blockpos, direction) && inputEvent.shouldSwingHand()) {
                  this.f_91061_.addBlockHitEffects(blockpos, blockhitresult);
                  this.f_91074_.m_6674_(InteractionHand.MAIN_HAND);
               }
            }

         } else {
            this.f_91072_.m_105276_();
         }
      }
   }

   private boolean m_202354_() {
      if (this.f_91078_ > 0) {
         return false;
      } else if (this.f_91077_ == null) {
         f_90982_.error("Null returned as 'hitResult', this shouldn't happen!");
         if (this.f_91072_.m_105289_()) {
            this.f_91078_ = 10;
         }

         return false;
      } else if (this.f_91074_.m_108637_()) {
         return false;
      } else {
         ItemStack itemstack = this.f_91074_.m_21120_(InteractionHand.MAIN_HAND);
         if (!itemstack.m_246617_(this.f_91073_.m_246046_())) {
            return false;
         } else {
            boolean flag = false;
            var inputEvent = net.minecraftforge.client.ForgeHooksClient.onClickInput(0, this.f_91066_.f_92096_, InteractionHand.MAIN_HAND);
            if (!inputEvent.isCanceled())
            switch (this.f_91077_.m_6662_()) {
               case ENTITY:
                  this.f_91072_.m_105223_(this.f_91074_, ((EntityHitResult)this.f_91077_).m_82443_());
                  break;
               case BLOCK:
                  BlockHitResult blockhitresult = (BlockHitResult)this.f_91077_;
                  BlockPos blockpos = blockhitresult.m_82425_();
                  if (!this.f_91073_.m_46859_(blockpos)) {
                     this.f_91072_.m_105269_(blockpos, blockhitresult.m_82434_());
                     if (this.f_91073_.m_8055_(blockpos).m_60795_()) {
                        flag = true;
                     }
                     break;
                  }
               case MISS:
                  if (this.f_91072_.m_105289_()) {
                     this.f_91078_ = 10;
                  }

                  this.f_91074_.m_36334_();
                  net.minecraftforge.common.ForgeHooks.onEmptyLeftClick(this.f_91074_);
            }

            if (inputEvent.shouldSwingHand())
            this.f_91074_.m_6674_(InteractionHand.MAIN_HAND);
            return flag;
         }
      }
   }

   private void m_91277_() {
      if (!this.f_91072_.m_105296_()) {
         this.f_91011_ = 4;
         if (!this.f_91074_.m_108637_()) {
            if (this.f_91077_ == null) {
               f_90982_.warn("Null returned as 'hitResult', this shouldn't happen!");
            }

            for(InteractionHand interactionhand : InteractionHand.values()) {
               var inputEvent = net.minecraftforge.client.ForgeHooksClient.onClickInput(1, this.f_91066_.f_92095_, interactionhand);
               if (inputEvent.isCanceled()) {
                  if (inputEvent.shouldSwingHand()) this.f_91074_.m_6674_(interactionhand);
                  return;
               }
               ItemStack itemstack = this.f_91074_.m_21120_(interactionhand);
               if (!itemstack.m_246617_(this.f_91073_.m_246046_())) {
                  return;
               }

               if (this.f_91077_ != null) {
                  switch (this.f_91077_.m_6662_()) {
                     case ENTITY:
                        EntityHitResult entityhitresult = (EntityHitResult)this.f_91077_;
                        Entity entity = entityhitresult.m_82443_();
                        if (!this.f_91073_.m_6857_().m_61937_(entity.m_20183_())) {
                           return;
                        }

                        InteractionResult interactionresult = this.f_91072_.m_105230_(this.f_91074_, entity, entityhitresult, interactionhand);
                        if (!interactionresult.m_19077_()) {
                           interactionresult = this.f_91072_.m_105226_(this.f_91074_, entity, interactionhand);
                        }

                        if (interactionresult.m_19077_()) {
                           if (interactionresult.m_19080_() && inputEvent.shouldSwingHand()) {
                              this.f_91074_.m_6674_(interactionhand);
                           }

                           return;
                        }
                        break;
                     case BLOCK:
                        BlockHitResult blockhitresult = (BlockHitResult)this.f_91077_;
                        int i = itemstack.m_41613_();
                        InteractionResult interactionresult1 = this.f_91072_.m_233732_(this.f_91074_, interactionhand, blockhitresult);
                        if (interactionresult1.m_19077_()) {
                           if (interactionresult1.m_19080_() && inputEvent.shouldSwingHand()) {
                              this.f_91074_.m_6674_(interactionhand);
                              if (!itemstack.m_41619_() && (itemstack.m_41613_() != i || this.f_91072_.m_105290_())) {
                                 this.f_91063_.f_109055_.m_109320_(interactionhand);
                              }
                           }

                           return;
                        }

                        if (interactionresult1 == InteractionResult.FAIL) {
                           return;
                        }
                  }
               }

               if (itemstack.m_41619_() && (this.f_91077_ == null || this.f_91077_.m_6662_() == HitResult.Type.MISS))
                  net.minecraftforge.common.ForgeHooks.onEmptyClick(this.f_91074_, interactionhand);

               if (!itemstack.m_41619_()) {
                  InteractionResult interactionresult2 = this.f_91072_.m_233721_(this.f_91074_, interactionhand);
                  if (interactionresult2.m_19077_()) {
                     if (interactionresult2.m_19080_()) {
                        this.f_91074_.m_6674_(interactionhand);
                     }

                     this.f_91063_.f_109055_.m_109320_(interactionhand);
                     return;
                  }
               }
            }

         }
      }
   }

   public MusicManager m_91397_() {
      return this.f_91044_;
   }

   public void m_91398_() {
      if (this.f_91011_ > 0) {
         --this.f_91011_;
      }

      net.minecraftforge.event.ForgeEventFactory.onPreClientTick();

      this.f_91026_.m_6180_("gui");
      this.f_240378_.m_240688_();
      this.f_91065_.m_193832_(this.f_91012_);
      this.f_91026_.m_7238_();
      this.f_91063_.m_109087_(1.0F);
      this.f_91005_.m_120578_(this.f_91073_, this.f_91077_);
      this.f_91026_.m_6180_("gameMode");
      if (!this.f_91012_ && this.f_91073_ != null) {
         this.f_91072_.m_105287_();
      }

      this.f_91026_.m_6182_("textures");
      if (this.f_91073_ != null) {
         this.f_90987_.m_7673_();
      }

      if (this.f_91080_ == null && this.f_91074_ != null) {
         if (this.f_91074_.m_21224_() && !(this.f_91080_ instanceof DeathScreen)) {
            this.m_91152_((Screen)null);
         } else if (this.f_91074_.m_5803_() && this.f_91073_ != null) {
            this.m_91152_(new InBedChatScreen());
         }
      } else {
         Screen $$4 = this.f_91080_;
         if ($$4 instanceof InBedChatScreen) {
            InBedChatScreen inbedchatscreen = (InBedChatScreen)$$4;
            if (!this.f_91074_.m_5803_()) {
               inbedchatscreen.m_193839_();
            }
         }
      }

      if (this.f_91080_ != null) {
         this.f_91078_ = 10000;
      }

      if (this.f_91080_ != null) {
         Screen.m_96579_(() -> {
            this.f_91080_.m_86600_();
         }, "Ticking screen", this.f_91080_.getClass().getCanonicalName());
      }

      if (!this.f_91066_.f_92063_) {
         this.f_91065_.m_93091_();
      }

      if (this.f_91081_ == null && this.f_91080_ == null) {
         this.f_91026_.m_6182_("Keybindings");
         this.m_91279_();
         if (this.f_91078_ > 0) {
            --this.f_91078_;
         }
      }

      if (this.f_91073_ != null) {
         this.f_91026_.m_6182_("gameRenderer");
         if (!this.f_91012_) {
            this.f_91063_.m_109148_();
         }

         this.f_91026_.m_6182_("levelRenderer");
         if (!this.f_91012_) {
            this.f_91060_.m_109823_();
         }

         this.f_91026_.m_6182_("level");
         if (!this.f_91012_) {
            this.f_91073_.m_104804_();
         }
      } else if (this.f_91063_.m_109149_() != null) {
         this.f_91063_.m_109086_();
      }

      if (!this.f_91012_) {
         this.f_91044_.m_120183_();
      }

      this.f_91043_.m_120389_(this.f_91012_);
      if (this.f_91073_ != null) {
         if (!this.f_91012_) {
            if (!this.f_91066_.f_92031_ && this.m_91278_()) {
               Component component = Component.m_237115_("tutorial.socialInteractions.title");
               Component component1 = Component.m_237110_("tutorial.socialInteractions.description", Tutorial.m_120592_("socialInteractions"));
               this.f_91025_ = new TutorialToast(TutorialToast.Icons.SOCIAL_INTERACTIONS, component, component1, true);
               this.f_91005_.m_120572_(this.f_91025_, 160);
               this.f_91066_.f_92031_ = true;
               this.f_91066_.m_92169_();
            }

            this.f_91005_.m_120596_();

            net.minecraftforge.event.ForgeEventFactory.onPreLevelTick(this.f_91073_, () -> true);
            try {
               this.f_91073_.m_104726_(() -> {
                  return true;
               });
            } catch (Throwable throwable) {
               CrashReport crashreport = CrashReport.m_127521_(throwable, "Exception in world tick");
               if (this.f_91073_ == null) {
                  CrashReportCategory crashreportcategory = crashreport.m_127514_("Affected level");
                  crashreportcategory.m_128159_("Problem", "Level is null!");
               } else {
                  this.f_91073_.m_6026_(crashreport);
               }

               throw new ReportedException(crashreport);
            }
            net.minecraftforge.event.ForgeEventFactory.onPostLevelTick(this.f_91073_, () -> true);
         }

         this.f_91026_.m_6182_("animateTick");
         if (!this.f_91012_ && this.f_91073_ != null) {
            this.f_91073_.m_104784_(this.f_91074_.m_146903_(), this.f_91074_.m_146904_(), this.f_91074_.m_146907_());
         }

         this.f_91026_.m_6182_("particles");
         if (!this.f_91012_) {
            this.f_91061_.m_107388_();
         }
      } else if (this.f_91009_ != null) {
         this.f_91026_.m_6182_("pendingConnection");
         this.f_91009_.m_129483_();
      }

      this.f_91026_.m_6182_("keyboard");
      this.f_91068_.m_90931_();
      this.f_91026_.m_7238_();

      net.minecraftforge.event.ForgeEventFactory.onPostClientTick();
   }

   private boolean m_91278_() {
      return !this.f_91010_ || this.f_91007_ != null && this.f_91007_.m_6992_();
   }

   private void m_91279_() {
      for(; this.f_91066_.f_92103_.m_90859_(); this.f_91060_.m_109826_()) {
         CameraType cameratype = this.f_91066_.m_92176_();
         this.f_91066_.m_92157_(this.f_91066_.m_92176_().m_90614_());
         if (cameratype.m_90612_() != this.f_91066_.m_92176_().m_90612_()) {
            this.f_91063_.m_109106_(this.f_91066_.m_92176_().m_90612_() ? this.m_91288_() : null);
         }
      }

      while(this.f_91066_.f_92104_.m_90859_()) {
         this.f_91066_.f_92067_ = !this.f_91066_.f_92067_;
      }

      for(int i = 0; i < 9; ++i) {
         boolean flag = this.f_91066_.f_92057_.m_90857_();
         boolean flag1 = this.f_91066_.f_92058_.m_90857_();
         if (this.f_91066_.f_92056_[i].m_90859_()) {
            if (this.f_91074_.m_5833_()) {
               this.f_91065_.m_93085_().m_94771_(i);
            } else if (!this.f_91074_.m_7500_() || this.f_91080_ != null || !flag1 && !flag) {
               this.f_91074_.m_150109_().f_35977_ = i;
            } else {
               CreativeModeInventoryScreen.m_98598_(this, i, flag1, flag);
            }
         }
      }

      while(this.f_91066_.f_92101_.m_90859_()) {
         if (!this.m_91278_()) {
            this.f_91074_.m_5661_(f_90984_, true);
            this.f_240365_.m_168785_(f_90984_);
         } else {
            if (this.f_91025_ != null) {
               this.f_91005_.m_120570_(this.f_91025_);
               this.f_91025_ = null;
            }

            this.m_91152_(new SocialInteractionsScreen());
         }
      }

      while(this.f_91066_.f_92092_.m_90859_()) {
         if (this.f_91072_.m_105292_()) {
            this.f_91074_.m_108628_();
         } else {
            this.f_91005_.m_120564_();
            this.m_91152_(new InventoryScreen(this.f_91074_));
         }
      }

      while(this.f_91066_.f_92055_.m_90859_()) {
         this.m_91152_(new AdvancementsScreen(this.f_91074_.f_108617_.m_105145_()));
      }

      while(this.f_91066_.f_92093_.m_90859_()) {
         if (!this.f_91074_.m_5833_()) {
            this.m_91403_().m_104955_(new ServerboundPlayerActionPacket(ServerboundPlayerActionPacket.Action.SWAP_ITEM_WITH_OFFHAND, BlockPos.f_121853_, Direction.DOWN));
         }
      }

      while(this.f_91066_.f_92094_.m_90859_()) {
         if (!this.f_91074_.m_5833_() && this.f_91074_.m_108700_(Screen.m_96637_())) {
            this.f_91074_.m_6674_(InteractionHand.MAIN_HAND);
         }
      }

      while(this.f_91066_.f_92098_.m_90859_()) {
         this.m_91326_("");
      }

      if (this.f_91080_ == null && this.f_91081_ == null && this.f_91066_.f_92100_.m_90859_()) {
         this.m_91326_("/");
      }

      boolean flag2 = false;
      if (this.f_91074_.m_6117_()) {
         if (!this.f_91066_.f_92095_.m_90857_()) {
            this.f_91072_.m_105277_(this.f_91074_);
         }

         while(this.f_91066_.f_92096_.m_90859_()) {
         }

         while(this.f_91066_.f_92095_.m_90859_()) {
         }

         while(this.f_91066_.f_92097_.m_90859_()) {
         }
      } else {
         while(this.f_91066_.f_92096_.m_90859_()) {
            flag2 |= this.m_202354_();
         }

         while(this.f_91066_.f_92095_.m_90859_()) {
            this.m_91277_();
         }

         while(this.f_91066_.f_92097_.m_90859_()) {
            this.m_91280_();
         }
      }

      if (this.f_91066_.f_92095_.m_90857_() && this.f_91011_ == 0 && !this.f_91074_.m_6117_()) {
         this.m_91277_();
      }

      this.m_91386_(this.f_91080_ == null && !flag2 && this.f_91066_.f_92096_.m_90857_() && this.f_91067_.m_91600_());
   }

   public ClientTelemetryManager m_261007_() {
      return this.f_260676_;
   }

   public double m_231464_() {
      return this.f_231341_;
   }

   public ProfileKeyPairManager m_231465_() {
      return this.f_231337_;
   }

   public WorldOpenFlows m_231466_() {
      return new WorldOpenFlows(this, this.f_91031_);
   }

   public void m_261031_(String p_261891_, LevelStorageSource.LevelStorageAccess p_261564_, PackRepository p_261826_, WorldStem p_261470_, boolean p_261465_) {
      this.m_91399_();
      this.f_90999_.set((StoringChunkProgressListener)null);
      Instant instant = Instant.now();

      try {
         p_261564_.m_78287_(p_261470_.f_244542_().m_247579_(), p_261470_.f_206895_());
         Services services = Services.m_214344_(this.f_231338_, this.f_91069_);
         services.f_214336_().m_143974_(this);
         SkullBlockEntity.m_222885_(services, this);
         GameProfileCache.m_11004_(false);
         this.f_91007_ = MinecraftServer.m_129872_((p_231361_) -> {
            return new IntegratedServer(p_231361_, this, p_261564_, p_261826_, p_261470_, services, (p_231447_) -> {
               StoringChunkProgressListener storingchunkprogresslistener = new StoringChunkProgressListener(p_231447_ + 0);
               this.f_90999_.set(storingchunkprogresslistener);
               return ProcessorChunkProgressListener.m_143583_(storingchunkprogresslistener, this.f_91023_::add);
            });
         });
         this.f_91010_ = true;
         this.m_239476_(ReportEnvironment.m_239898_());
         this.f_278504_.m_278642_(QuickPlayLog.Type.SINGLEPLAYER, p_261891_, p_261470_.f_206895_().m_5462_());
      } catch (Throwable throwable) {
         CrashReport crashreport = CrashReport.m_127521_(throwable, "Starting integrated server");
         CrashReportCategory crashreportcategory = crashreport.m_127514_("Starting integrated server");
         crashreportcategory.m_128159_("Level ID", p_261891_);
         crashreportcategory.m_128165_("Level Name", () -> {
            return p_261470_.f_206895_().m_5462_();
         });
         throw new ReportedException(crashreport);
      }

      while(this.f_90999_.get() == null) {
         Thread.yield();
      }

      LevelLoadingScreen levelloadingscreen = new LevelLoadingScreen(this.f_90999_.get());
      this.m_91152_(levelloadingscreen);
      this.f_91026_.m_6180_("waitForServer");

      while(!this.f_91007_.m_129920_()) {
         levelloadingscreen.m_86600_();
         this.m_91383_(false);

         try {
            Thread.sleep(16L);
         } catch (InterruptedException interruptedexception) {
         }

         if (this.f_91020_ != null) {
            m_91332_(this.f_91020_.get());
            return;
         }
      }

      this.f_91026_.m_7238_();
      Duration duration = Duration.between(instant, Instant.now());
      SocketAddress socketaddress = this.f_91007_.m_129919_().m_9708_();
      Connection connection = Connection.m_129493_(socketaddress);
      connection.m_129505_(new ClientHandshakePacketListenerImpl(connection, this, (ServerData)null, (Screen)null, p_261465_, duration, (p_231442_) -> {
      }));
      connection.m_129512_(new ClientIntentionPacket(socketaddress.toString(), 0, ConnectionProtocol.LOGIN));
      connection.m_129512_(new ServerboundHelloPacket(this.m_91094_().m_92546_(), Optional.ofNullable(this.m_91094_().m_240411_())));
      this.f_91009_ = connection;
   }

   public void m_91156_(ClientLevel p_91157_) {
      if (this.f_91073_ != null) net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.level.LevelEvent.Unload(this.f_91073_));
      ProgressScreen progressscreen = new ProgressScreen(true);
      progressscreen.m_6309_(Component.m_237115_("connect.joining"));
      this.m_91362_(progressscreen);
      this.f_91073_ = p_91157_;
      this.m_91324_(p_91157_);
      if (!this.f_91010_) {
         Services services = Services.m_214344_(this.f_231338_, this.f_91069_);
         services.f_214336_().m_143974_(this);
         SkullBlockEntity.m_222885_(services, this);
         GameProfileCache.m_11004_(false);
      }

   }

   public void m_91399_() {
      this.m_91320_(new ProgressScreen(true));
   }

   public void m_91320_(Screen p_91321_) {
      ClientPacketListener clientpacketlistener = this.m_91403_();
      if (clientpacketlistener != null) {
         this.m_18698_();
         clientpacketlistener.m_261044_();
      }

      this.f_91006_.m_194060_();
      if (this.f_167846_.m_142763_()) {
         this.m_231418_();
      }

      IntegratedServer integratedserver = this.f_91007_;
      this.f_91007_ = null;
      this.f_91063_.m_109150_();
      net.minecraftforge.client.ForgeHooksClient.firePlayerLogout(this.f_91072_, this.f_91074_);
      this.f_91072_ = null;
      this.f_240365_.m_93328_();
      this.m_91362_(p_91321_);
      if (this.f_91073_ != null) {
         net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.level.LevelEvent.Unload(this.f_91073_));
         if (integratedserver != null) {
            this.f_91026_.m_6180_("waitForServer");

            while(!integratedserver.m_129782_()) {
               this.m_91383_(false);
            }

            this.f_91026_.m_7238_();
         }

         this.f_243981_.m_246151_();
         this.f_91065_.m_93089_();
         this.f_91010_ = false;
         net.minecraftforge.client.ForgeHooksClient.handleClientLevelClosing(this.f_91073_);
      }

      this.f_91073_ = null;
      this.m_91324_((ClientLevel)null);
      this.f_91074_ = null;
      SkullBlockEntity.m_196704_();
   }

   private void m_91362_(Screen p_91363_) {
      this.f_91026_.m_6180_("forcedTick");
      this.f_91043_.m_120405_();
      this.f_91075_ = null;
      this.f_91009_ = null;
      this.m_91152_(p_91363_);
      this.m_91383_(false);
      this.f_91026_.m_7238_();
   }

   public void m_91346_(Screen p_91347_) {
      this.f_91026_.m_6180_("forcedTick");
      this.m_91152_(p_91347_);
      this.m_91383_(false);
      this.f_91026_.m_7238_();
   }

   private void m_91324_(@Nullable ClientLevel p_91325_) {
      this.f_91060_.m_109701_(p_91325_);
      this.f_91061_.m_107342_(p_91325_);
      this.f_167845_.m_112257_(p_91325_);
      this.m_91341_();
   }

   public boolean m_260979_() {
      return this.m_261227_() && this.f_91066_.m_261324_().m_231551_();
   }

   public boolean m_261227_() {
      return this.m_261210_() && this.f_193584_.properties().flag(UserFlag.OPTIONAL_TELEMETRY_AVAILABLE);
   }

   public boolean m_261210_() {
      return this.f_193584_.properties().flag(UserFlag.TELEMETRY_ENABLED);
   }

   public boolean m_91400_() {
      return this.f_91034_ && this.f_193584_.properties().flag(UserFlag.SERVERS_ALLOWED) && this.m_239210_() == null;
   }

   public boolean m_168021_() {
      return this.f_193584_.properties().flag(UserFlag.REALMS_ALLOWED) && this.m_239210_() == null;
   }

   public boolean m_239929_() {
      return this.m_239210_() != null;
   }

   @Nullable
   public BanDetails m_239210_() {
      return this.f_193584_.properties().bannedScopes().get("MULTIPLAYER");
   }

   public boolean m_91246_(UUID p_91247_) {
      if (this.m_168022_().m_142594_(false)) {
         return this.f_91006_.m_100684_(p_91247_);
      } else {
         return (this.f_91074_ == null || !p_91247_.equals(this.f_91074_.m_20148_())) && !p_91247_.equals(Util.f_137441_);
      }
   }

   public Minecraft.ChatStatus m_168022_() {
      if (this.f_91066_.m_232090_().m_231551_() == ChatVisiblity.HIDDEN) {
         return Minecraft.ChatStatus.DISABLED_BY_OPTIONS;
      } else if (!this.f_91035_) {
         return Minecraft.ChatStatus.DISABLED_BY_LAUNCHER;
      } else {
         return !this.f_193584_.properties().flag(UserFlag.CHAT_ALLOWED) ? Minecraft.ChatStatus.DISABLED_BY_PROFILE : Minecraft.ChatStatus.ENABLED;
      }
   }

   public final boolean m_91402_() {
      return this.f_91033_;
   }

   @Nullable
   public ClientPacketListener m_91403_() {
      return this.f_91074_ == null ? null : this.f_91074_.f_108617_;
   }

   public static boolean m_91404_() {
      return !f_90981_.f_91066_.f_92062_;
   }

   public static boolean m_91405_() {
      return f_90981_.f_91066_.m_232060_().m_231551_().m_35965_() >= GraphicsStatus.FANCY.m_35965_();
   }

   public static boolean m_91085_() {
      return !f_90981_.f_91063_.m_172715_() && f_90981_.f_91066_.m_232060_().m_231551_().m_35965_() >= GraphicsStatus.FABULOUS.m_35965_();
   }

   public static boolean m_91086_() {
      return f_90981_.f_91066_.m_232070_().m_231551_();
   }

   private void m_91280_() {
      if (this.f_91077_ != null && this.f_91077_.m_6662_() != HitResult.Type.MISS) {
         if (net.minecraftforge.client.ForgeHooksClient.onClickInput(2, this.f_91066_.f_92097_, InteractionHand.MAIN_HAND).isCanceled()) return;
         boolean flag = this.f_91074_.m_150110_().f_35937_;
         BlockEntity blockentity = null;
         HitResult.Type hitresult$type = this.f_91077_.m_6662_();
         ItemStack itemstack;
         if (hitresult$type == HitResult.Type.BLOCK) {
            BlockPos blockpos = ((BlockHitResult)this.f_91077_).m_82425_();
            BlockState blockstate = this.f_91073_.m_8055_(blockpos);
            if (blockstate.m_60795_()) {
               return;
            }

            Block block = blockstate.m_60734_();
            itemstack = blockstate.getCloneItemStack(this.f_91077_, this.f_91073_, blockpos, this.f_91074_);

            if (flag && Screen.m_96637_() && blockstate.m_155947_()) {
               blockentity = this.f_91073_.m_7702_(blockpos);
            }
         } else {
            if (hitresult$type != HitResult.Type.ENTITY || !flag) {
               return;
            }

            Entity entity = ((EntityHitResult)this.f_91077_).m_82443_();
            itemstack = entity.getPickedResult(this.f_91077_);
            if (itemstack == null) {
               return;
            }
         }

         if (itemstack.m_41619_()) {
            String s = "";
            if (hitresult$type == HitResult.Type.BLOCK) {
               s = BuiltInRegistries.f_256975_.m_7981_(this.f_91073_.m_8055_(((BlockHitResult)this.f_91077_).m_82425_()).m_60734_()).toString();
            } else if (hitresult$type == HitResult.Type.ENTITY) {
               s = BuiltInRegistries.f_256780_.m_7981_(((EntityHitResult)this.f_91077_).m_82443_().m_6095_()).toString();
            }

            f_90982_.warn("Picking on: [{}] {} gave null item", hitresult$type, s);
         } else {
            Inventory inventory = this.f_91074_.m_150109_();
            if (blockentity != null) {
               this.m_263196_(itemstack, blockentity);
            }

            int i = inventory.m_36030_(itemstack);
            if (flag) {
               inventory.m_36012_(itemstack);
               this.f_91072_.m_105241_(this.f_91074_.m_21120_(InteractionHand.MAIN_HAND), 36 + inventory.f_35977_);
            } else if (i != -1) {
               if (Inventory.m_36045_(i)) {
                  inventory.f_35977_ = i;
               } else {
                  this.f_91072_.m_105206_(i);
               }
            }

         }
      }
   }

   private void m_263196_(ItemStack p_263370_, BlockEntity p_263368_) {
      CompoundTag compoundtag = p_263368_.m_187480_();
      BlockItem.m_186338_(p_263370_, p_263368_.m_58903_(), compoundtag);
      if (p_263370_.m_41720_() instanceof PlayerHeadItem && compoundtag.m_128441_("SkullOwner")) {
         CompoundTag compoundtag3 = compoundtag.m_128469_("SkullOwner");
         CompoundTag compoundtag4 = p_263370_.m_41784_();
         compoundtag4.m_128365_("SkullOwner", compoundtag3);
         CompoundTag compoundtag2 = compoundtag4.m_128469_("BlockEntityTag");
         compoundtag2.m_128473_("SkullOwner");
         compoundtag2.m_128473_("x");
         compoundtag2.m_128473_("y");
         compoundtag2.m_128473_("z");
      } else {
         CompoundTag compoundtag1 = new CompoundTag();
         ListTag listtag = new ListTag();
         listtag.add(StringTag.m_129297_("\"(+NBT)\""));
         compoundtag1.m_128365_("Lore", listtag);
         p_263370_.m_41700_("display", compoundtag1);
      }
   }

   public CrashReport m_91354_(CrashReport p_91355_) {
      SystemReport systemreport = p_91355_.m_178626_();
      m_167850_(systemreport, this, this.f_91039_, this.f_91001_, this.f_91066_);
      if (this.f_91073_ != null) {
         this.f_91073_.m_6026_(p_91355_);
      }

      if (this.f_91007_ != null) {
         this.f_91007_.m_177935_(systemreport);
      }

      this.f_167847_.m_168562_(p_91355_);
      return p_91355_;
   }

   public static void m_167872_(@Nullable Minecraft p_167873_, @Nullable LanguageManager p_167874_, String p_167875_, @Nullable Options p_167876_, CrashReport p_167877_) {
      SystemReport systemreport = p_167877_.m_178626_();
      m_167850_(systemreport, p_167873_, p_167874_, p_167875_, p_167876_);
   }

   private static SystemReport m_167850_(SystemReport p_167851_, @Nullable Minecraft p_167852_, @Nullable LanguageManager p_167853_, String p_167854_, Options p_167855_) {
      p_167851_.m_143522_("Launched Version", () -> {
         return p_167854_;
      });
      p_167851_.m_143522_("Backend library", RenderSystem::getBackendDescription);
      p_167851_.m_143522_("Backend API", RenderSystem::getApiDescription);
      p_167851_.m_143522_("Window size", () -> {
         return p_167852_ != null ? p_167852_.f_90990_.m_85441_() + "x" + p_167852_.f_90990_.m_85442_() : "<not initialized>";
      });
      p_167851_.m_143522_("GL Caps", RenderSystem::getCapsString);
      p_167851_.m_143522_("GL debug messages", () -> {
         return GlDebug.m_166226_() ? String.join("\n", GlDebug.m_166225_()) : "<disabled>";
      });
      p_167851_.m_143522_("Using VBOs", () -> {
         return "Yes";
      });
      p_167851_.m_143522_("Is Modded", () -> {
         return m_193589_().m_184605_();
      });
      p_167851_.m_143519_("Type", "Client (map_client.txt)");
      if (p_167855_ != null) {
         if (f_90981_ != null) {
            String s = f_90981_.m_91105_().m_109256_();
            if (s != null) {
               p_167851_.m_143519_("GPU Warnings", s);
            }
         }

         p_167851_.m_143519_("Graphics mode", p_167855_.m_232060_().m_231551_().toString());
         p_167851_.m_143522_("Resource Packs", () -> {
            StringBuilder stringbuilder = new StringBuilder();

            for(String s1 : p_167855_.f_92117_) {
               if (stringbuilder.length() > 0) {
                  stringbuilder.append(", ");
               }

               stringbuilder.append(s1);
               if (p_167855_.f_92118_.contains(s1)) {
                  stringbuilder.append(" (incompatible)");
               }
            }

            return stringbuilder.toString();
         });
      }

      if (p_167853_ != null) {
         p_167851_.m_143522_("Current Language", () -> {
            return p_167853_.m_264236_();
         });
      }

      p_167851_.m_143522_("CPU", GlUtil::m_84819_);
      return p_167851_;
   }

   public static Minecraft m_91087_() {
      return f_90981_;
   }

   public CompletableFuture<Void> m_91088_() {
      return this.m_18691_(() -> this.m_91391_()).thenCompose((p_231391_) -> {
         return p_231391_;
      });
   }

   public void m_239476_(ReportEnvironment p_239477_) {
      if (!this.f_238638_.m_239733_(p_239477_)) {
         this.f_238638_ = ReportingContext.m_239685_(p_239477_, this.f_193584_);
      }

   }

   @Nullable
   public ServerData m_91089_() {
      return Optionull.m_269382_(this.m_91403_(), ClientPacketListener::m_245416_);
   }

   public boolean m_91090_() {
      return this.f_91010_;
   }

   public boolean m_91091_() {
      return this.f_91010_ && this.f_91007_ != null;
   }

   @Nullable
   public IntegratedServer m_91092_() {
      return this.f_91007_;
   }

   public boolean m_257720_() {
      IntegratedServer integratedserver = this.m_91092_();
      return integratedserver != null && !integratedserver.m_6992_();
   }

   public User m_91094_() {
      return this.f_90998_;
   }

   public PropertyMap m_91095_() {
      if (this.f_90986_.isEmpty()) {
         GameProfile gameprofile = this.m_91108_().fillProfileProperties(this.f_90998_.m_92548_(), false);
         this.f_90986_.putAll(gameprofile.getProperties());
      }

      return this.f_90986_;
   }

   public Proxy m_91096_() {
      return this.f_91030_;
   }

   public TextureManager m_91097_() {
      return this.f_90987_;
   }

   public ResourceManager m_91098_() {
      return this.f_91036_;
   }

   public PackRepository m_91099_() {
      return this.f_91038_;
   }

   public VanillaPackResources m_246804_() {
      return this.f_243783_;
   }

   public DownloadedPackSource m_247489_() {
      return this.f_243981_;
   }

   public Path m_245161_() {
      return this.f_90985_;
   }

   public LanguageManager m_91102_() {
      return this.f_91039_;
   }

   public Function<ResourceLocation, TextureAtlasSprite> m_91258_(ResourceLocation p_91259_) {
      return this.f_91051_.m_119428_(p_91259_)::m_118316_;
   }

   public boolean m_91103_() {
      return this.f_91032_;
   }

   public boolean m_91104_() {
      return this.f_91012_;
   }

   public GpuWarnlistManager m_91105_() {
      return this.f_91047_;
   }

   public SoundManager m_91106_() {
      return this.f_91043_;
   }

   public Music m_91107_() {
      Music music = Optionull.m_269382_(this.f_91080_, Screen::m_278176_);
      if (music != null) {
         return music;
      } else if (this.f_91074_ != null) {
         if (this.f_91074_.m_9236_().m_46472_() == Level.f_46430_) {
            return this.f_91065_.m_93090_().m_93713_() ? Musics.f_11648_ : Musics.f_11649_;
         } else {
            Holder<Biome> holder = this.f_91074_.m_9236_().m_204166_(this.f_91074_.m_20183_());
            if (!this.f_91044_.m_120187_(Musics.f_11650_) && (!this.f_91074_.m_5842_() || !holder.m_203656_(BiomeTags.f_215801_))) {
               return this.f_91074_.m_9236_().m_46472_() != Level.f_46429_ && this.f_91074_.m_150110_().f_35937_ && this.f_91074_.m_150110_().f_35936_ ? Musics.f_11646_ : holder.m_203334_().m_47566_().orElse(Musics.f_11651_);
            } else {
               return Musics.f_11650_;
            }
         }
      } else {
         return Musics.f_11645_;
      }
   }

   public MinecraftSessionService m_91108_() {
      return this.f_91048_;
   }

   public SkinManager m_91109_() {
      return this.f_91050_;
   }

   @Nullable
   public Entity m_91288_() {
      return this.f_91075_;
   }

   public void m_91118_(Entity p_91119_) {
      this.f_91075_ = p_91119_;
      this.f_91063_.m_109106_(p_91119_);
   }

   public boolean m_91314_(Entity p_91315_) {
      return p_91315_.m_142038_() || this.f_91074_ != null && this.f_91074_.m_5833_() && this.f_91066_.f_92054_.m_90857_() && p_91315_.m_6095_() == EntityType.f_20532_;
   }

   protected Thread m_6304_() {
      return this.f_91018_;
   }

   protected Runnable m_6681_(Runnable p_91376_) {
      return p_91376_;
   }

   protected boolean m_6362_(Runnable p_91365_) {
      return true;
   }

   public BlockRenderDispatcher m_91289_() {
      return this.f_91052_;
   }

   public EntityRenderDispatcher m_91290_() {
      return this.f_90994_;
   }

   public BlockEntityRenderDispatcher m_167982_() {
      return this.f_167845_;
   }

   public ItemRenderer m_91291_() {
      return this.f_90995_;
   }

   public <T> SearchTree<T> m_231372_(SearchRegistry.Key<T> p_231373_) {
      return this.f_90997_.m_235230_(p_231373_);
   }

   public <T> void m_231374_(SearchRegistry.Key<T> p_231375_, List<T> p_231376_) {
      this.f_90997_.m_235235_(p_231375_, p_231376_);
   }

   public FrameTimer m_91293_() {
      return this.f_91070_;
   }

   public boolean m_91294_() {
      return this.f_91017_;
   }

   public void m_91372_(boolean p_91373_) {
      this.f_91017_ = p_91373_;
   }

   public DataFixer m_91295_() {
      return this.f_90988_;
   }

   public float m_91296_() {
      return this.f_90991_.f_92518_;
   }

   public float m_91297_() {
      return this.f_90991_.f_92519_;
   }

   public BlockColors m_91298_() {
      return this.f_91040_;
   }

   public boolean m_91299_() {
      return this.f_91074_ != null && this.f_91074_.m_36330_() || this.f_91066_.m_231824_().m_231551_();
   }

   public ToastComponent m_91300_() {
      return this.f_91003_;
   }

   public Tutorial m_91301_() {
      return this.f_91005_;
   }

   public boolean m_91302_() {
      return this.f_91022_;
   }

   public HotbarManager m_91303_() {
      return this.f_91000_;
   }

   public ModelManager m_91304_() {
      return this.f_91051_;
   }

   public PaintingTextureManager m_91305_() {
      return this.f_91053_;
   }

   public MobEffectTextureManager m_91306_() {
      return this.f_91054_;
   }

   public void m_7440_(boolean p_91261_) {
      this.f_91022_ = p_91261_;
   }

   public Component m_167899_(File p_167900_, int p_167901_, int p_167902_) {
      int i = this.f_90990_.m_85441_();
      int j = this.f_90990_.m_85442_();
      RenderTarget rendertarget = new TextureTarget(p_167901_, p_167902_, true, f_91002_);
      float f = this.f_91074_.m_146909_();
      float f1 = this.f_91074_.m_146908_();
      float f2 = this.f_91074_.f_19860_;
      float f3 = this.f_91074_.f_19859_;
      this.f_91063_.m_172775_(false);

      MutableComponent mutablecomponent;
      try {
         this.f_91063_.m_172779_(true);
         this.f_91060_.m_173014_();
         this.f_90990_.m_166450_(p_167901_);
         this.f_90990_.m_166452_(p_167902_);

         for(int k = 0; k < 6; ++k) {
            switch (k) {
               case 0:
                  this.f_91074_.m_146922_(f1);
                  this.f_91074_.m_146926_(0.0F);
                  break;
               case 1:
                  this.f_91074_.m_146922_((f1 + 90.0F) % 360.0F);
                  this.f_91074_.m_146926_(0.0F);
                  break;
               case 2:
                  this.f_91074_.m_146922_((f1 + 180.0F) % 360.0F);
                  this.f_91074_.m_146926_(0.0F);
                  break;
               case 3:
                  this.f_91074_.m_146922_((f1 - 90.0F) % 360.0F);
                  this.f_91074_.m_146926_(0.0F);
                  break;
               case 4:
                  this.f_91074_.m_146922_(f1);
                  this.f_91074_.m_146926_(-90.0F);
                  break;
               case 5:
               default:
                  this.f_91074_.m_146922_(f1);
                  this.f_91074_.m_146926_(90.0F);
            }

            this.f_91074_.f_19859_ = this.f_91074_.m_146908_();
            this.f_91074_.f_19860_ = this.f_91074_.m_146909_();
            rendertarget.m_83947_(true);
            this.f_91063_.m_109089_(1.0F, 0L, new PoseStack());

            try {
               Thread.sleep(10L);
            } catch (InterruptedException interruptedexception) {
            }

            Screenshot.m_92295_(p_167900_, "panorama_" + k + ".png", rendertarget, (p_231415_) -> {
            });
         }

         Component component = Component.m_237113_(p_167900_.getName()).m_130940_(ChatFormatting.UNDERLINE).m_130938_((p_231426_) -> {
            return p_231426_.m_131142_(new ClickEvent(ClickEvent.Action.OPEN_FILE, p_167900_.getAbsolutePath()));
         });
         return Component.m_237110_("screenshot.success", component);
      } catch (Exception exception) {
         f_90982_.error("Couldn't save image", (Throwable)exception);
         mutablecomponent = Component.m_237110_("screenshot.failure", exception.getMessage());
      } finally {
         this.f_91074_.m_146926_(f);
         this.f_91074_.m_146922_(f1);
         this.f_91074_.f_19860_ = f2;
         this.f_91074_.f_19859_ = f3;
         this.f_91063_.m_172775_(true);
         this.f_90990_.m_166450_(i);
         this.f_90990_.m_166452_(j);
         rendertarget.m_83930_();
         this.f_91063_.m_172779_(false);
         this.f_91060_.m_173014_();
         this.m_91385_().m_83947_(true);
      }

      return mutablecomponent;
   }

   private Component m_167903_(File p_167904_, int p_167905_, int p_167906_, int p_167907_, int p_167908_) {
      try {
         ByteBuffer bytebuffer = GlUtil.m_166247_(p_167905_ * p_167906_ * 3);
         Screenshot screenshot = new Screenshot(p_167904_, p_167907_, p_167908_, p_167906_);
         float f = (float)p_167907_ / (float)p_167905_;
         float f1 = (float)p_167908_ / (float)p_167906_;
         float f2 = f > f1 ? f : f1;

         for(int i = (p_167908_ - 1) / p_167906_ * p_167906_; i >= 0; i -= p_167906_) {
            for(int j = 0; j < p_167907_; j += p_167905_) {
               RenderSystem.setShaderTexture(0, TextureAtlas.f_118259_);
               float f3 = (float)(p_167907_ - p_167905_) / 2.0F * 2.0F - (float)(j * 2);
               float f4 = (float)(p_167908_ - p_167906_) / 2.0F * 2.0F - (float)(i * 2);
               f3 /= (float)p_167905_;
               f4 /= (float)p_167906_;
               this.f_91063_.m_172718_(f2, f3, f4);
               bytebuffer.clear();
               RenderSystem.pixelStore(3333, 1);
               RenderSystem.pixelStore(3317, 1);
               RenderSystem.readPixels(0, 0, p_167905_, p_167906_, 32992, 5121, bytebuffer);
               screenshot.m_168609_(bytebuffer, j, i, p_167905_, p_167906_);
            }

            screenshot.m_168605_();
         }

         File file1 = screenshot.m_168615_();
         GlUtil.m_166251_(bytebuffer);
         Component component = Component.m_237113_(file1.getName()).m_130940_(ChatFormatting.UNDERLINE).m_130938_((p_231379_) -> {
            return p_231379_.m_131142_(new ClickEvent(ClickEvent.Action.OPEN_FILE, file1.getAbsolutePath()));
         });
         return Component.m_237110_("screenshot.success", component);
      } catch (Exception exception) {
         f_90982_.warn("Couldn't save screenshot", (Throwable)exception);
         return Component.m_237110_("screenshot.failure", exception.getMessage());
      }
   }

   public ProfilerFiller m_91307_() {
      return this.f_91026_;
   }

   @Nullable
   public StoringChunkProgressListener m_167983_() {
      return this.f_90999_.get();
   }

   public SplashManager m_91310_() {
      return this.f_91046_;
   }

   @Nullable
   public Overlay m_91265_() {
      return this.f_91081_;
   }

   public PlayerSocialManager m_91266_() {
      return this.f_91006_;
   }

   public boolean m_91267_() {
      return false;
   }

   public Window m_91268_() {
      return this.f_90990_;
   }

   public RenderBuffers m_91269_() {
      return this.f_90993_;
   }

   public void m_91312_(int p_91313_) {
      this.f_91051_.m_119410_(p_91313_);
   }

   public ItemColors getItemColors() {
      return this.f_91041_;
   }

   public SearchRegistry getSearchTreeManager() {
      return this.f_90997_;
   }

   private float realPartialTick;
   public float getPartialTick() {
      return this.realPartialTick;
   }

   public EntityModelSet m_167973_() {
      return this.f_167844_;
   }

   public boolean m_167974_() {
      return this.f_193584_.properties().flag(UserFlag.PROFANITY_FILTER_ENABLED);
   }

   public void m_193588_() {
      this.f_91006_.m_194059_();
      this.m_231465_().m_252904_();
   }

   public Realms32BitWarningStatus m_231416_() {
      return this.f_231343_;
   }

   @Nullable
   public SignatureValidator m_231417_() {
      return SignatureValidator.m_284488_(this.f_231338_.getServicesKeySet(), ServicesKeyType.PROFILE_KEY);
   }

   public InputType m_264529_() {
      return this.f_263699_;
   }

   public void m_264033_(InputType p_265509_) {
      this.f_263699_ = p_265509_;
   }

   public GameNarrator m_240477_() {
      return this.f_240365_;
   }

   public ChatListener m_240442_() {
      return this.f_240378_;
   }

   public ReportingContext m_239211_() {
      return this.f_238638_;
   }

   public RealmsDataFetcher m_239420_() {
      return this.f_238717_;
   }

   public QuickPlayLog m_278644_() {
      return this.f_278504_;
   }

   @OnlyIn(Dist.CLIENT)
   public static enum ChatStatus {
      ENABLED(CommonComponents.f_237098_) {
         public boolean m_142594_(boolean p_168045_) {
            return true;
         }
      },
      DISABLED_BY_OPTIONS(Component.m_237115_("chat.disabled.options").m_130940_(ChatFormatting.RED)) {
         public boolean m_142594_(boolean p_168051_) {
            return false;
         }
      },
      DISABLED_BY_LAUNCHER(Component.m_237115_("chat.disabled.launcher").m_130940_(ChatFormatting.RED)) {
         public boolean m_142594_(boolean p_168057_) {
            return p_168057_;
         }
      },
      DISABLED_BY_PROFILE(Component.m_237110_("chat.disabled.profile", Component.m_237117_(Minecraft.f_90981_.f_91066_.f_92098_.m_90860_())).m_130940_(ChatFormatting.RED)) {
         public boolean m_142594_(boolean p_168063_) {
            return p_168063_;
         }
      };

      static final Component f_238170_ = Component.m_237115_("chat.disabled.profile.moreInfo");
      private final Component f_168027_;

      ChatStatus(Component p_168033_) {
         this.f_168027_ = p_168033_;
      }

      public Component m_168034_() {
         return this.f_168027_;
      }

      public abstract boolean m_142594_(boolean p_168035_);
   }
}
