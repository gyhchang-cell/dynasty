package com.Polarice3.Goety.compat.jade;

import com.Polarice3.Goety.Goety;
import com.Polarice3.Goety.api.entities.IOwned;
import com.Polarice3.Goety.utils.EntityFinder;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.OwnableEntity;
import snownee.jade.api.EntityAccessor;
import snownee.jade.api.IServerDataProvider;
import snownee.jade.util.CommonProxy;

import java.util.UUID;

public enum SummonOwnerProvider implements IServerDataProvider<EntityAccessor> {
    INSTANCE;

    @Override
    public void appendServerData(CompoundTag data, EntityAccessor accessor) {
        Entity entity = accessor.getEntity();
        UUID ownerUUID = null;
        int ownerID = -1;
        if (entity instanceof OwnableEntity ownable) {
            ownerUUID = ownable.getOwnerUUID();
            if (ownable.getOwner() != null) {
                ownerID = ownable.getOwner().getId();
            }
        }
        if (ownerUUID == null){
            if (entity instanceof IOwned owned){
                ownerUUID = owned.getOwnerId();
                ownerID = owned.getOwnerClientId();
            }
        }
        if (ownerUUID != null) {
            String name = CommonProxy.getLastKnownUsername(ownerUUID);
            if (name != null) {
                data.putString("OwnerName", name);
            } else {
                Entity entity1 = EntityFinder.getEntityByUuiD(accessor.getLevel(), ownerUUID);
                if (entity1 == null){
                    entity1 = accessor.getLevel().getEntity(ownerID);
                }
                if (entity1 != null){
                    data.putString("OwnerName", entity1.getDisplayName().getString());
                }
            }
        }
    }

    @Override
    public ResourceLocation getUid() {
        return Goety.location("summon_owner");
    }
}
