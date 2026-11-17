package com.dynasty.navigation;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.item.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraftforge.registries.*;
import net.minecraftforge.network.*;
import net.minecraftforge.network.simple.SimpleChannel;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.eventbus.api.IEventBus;

public final class CreatureCompass extends Item {
    public static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,"dynasty");
    public static final RegistryObject<Item> ITEM=ITEMS.register("creature_compass",()->new CreatureCompass());
    private static final SimpleChannel NET=NetworkRegistry.newSimpleChannel(new ResourceLocation("dynasty","creature_compass"),()->"1","1"::equals,"1"::equals);
    public CreatureCompass(){super(new Item.Properties().stacksTo(1));}
    public static void register(IEventBus bus){ITEMS.register(bus);bus.addListener(CreatureCompass::setup);}
    private static void setup(FMLCommonSetupEvent e){
        NET.registerMessage(0,Request.class,(m,b)->b.writeResourceLocation(m.id),b->new Request(b.readResourceLocation()),(m,c)->{
            var ctx=c.get();ctx.enqueueWork(()->search(ctx.getSender(),m.id));ctx.setPacketHandled(true);
        },java.util.Optional.of(NetworkDirection.PLAY_TO_SERVER));
    }
    public record Request(ResourceLocation id){}
    public static void request(ResourceLocation id){NET.sendToServer(new Request(id));}
    @Override public InteractionResultHolder<ItemStack> use(Level l,Player p,InteractionHand h){
        if(l.isClientSide)net.minecraftforge.fml.DistExecutor.unsafeRunWhenOn(net.minecraftforge.api.distmarker.Dist.CLIENT,()->()->CreatureCompassScreen.open());
        return InteractionResultHolder.sidedSuccess(p.getItemInHand(h),l.isClientSide);
    }
    static void search(net.minecraft.server.level.ServerPlayer p,ResourceLocation id){
        if(p==null)return;ItemStack compass=p.getMainHandItem().is(ITEM.get())?p.getMainHandItem():p.getOffhandItem();
        if(!compass.is(ITEM.get())||p.getCooldowns().isOnCooldown(ITEM.get()))return;
        p.getCooldowns().addCooldown(ITEM.get(),40);
        var type=ForgeRegistries.ENTITY_TYPES.getValue(id);if(type==null)return;
        net.minecraft.world.entity.LivingEntity nearest=null;double distance=256*256;
        for(var entity:p.serverLevel().getAllEntities())if(entity.getType()==type&&entity instanceof net.minecraft.world.entity.LivingEntity living&&living.isAlive()&&!living.isRemoved()){
            double d=p.distanceToSqr(entity);if(d<distance){nearest=living;distance=d;}
        }
        var tag=compass.getOrCreateTag();tag.remove("TargetPos");tag.remove("TargetUuid");tag.putString("TargetName",id.toString());
        if(nearest!=null){tag.putUUID("TargetUuid",nearest.getUUID());tag.putLong("TargetPos",nearest.blockPosition().asLong());tag.putString("TargetDimension",p.level().dimension().location().toString());
            p.sendSystemMessage(Component.translatable(type.getDescriptionId()).append("："+nearest.getBlockX()+", "+nearest.getBlockY()+", "+nearest.getBlockZ()+"（"+(int)Math.sqrt(distance)+"格）"));
        }else p.sendSystemMessage(Component.literal("附近256格已加载区域未发现").append(Component.translatable(type.getDescriptionId())).append("；移动到其栖息地后重新搜索。"));
    }
    @Override public void inventoryTick(ItemStack s,Level level,net.minecraft.world.entity.Entity holder,int slot,boolean selected){
        if(level.isClientSide || level.getGameTime()%20!=0 || !s.hasTag() || !s.getTag().hasUUID("TargetUuid"))return;
        var entity=((net.minecraft.server.level.ServerLevel)level).getEntity(s.getTag().getUUID("TargetUuid"));
        if(entity instanceof net.minecraft.world.entity.LivingEntity living && living.isAlive() && holder.distanceToSqr(entity)<=256*256)s.getTag().putLong("TargetPos",entity.blockPosition().asLong());
        else {s.getTag().remove("TargetPos");s.getTag().remove("TargetUuid");}
    }
    @Override public void appendHoverText(ItemStack s,Level l,java.util.List<Component> lines,TooltipFlag flag){lines.add(Component.literal("右键选择生物，追踪附近256格内已加载的活体。"));lines.add(Component.literal("不会生成生物；搜索失败时前往其栖息地再试。"));}
}
