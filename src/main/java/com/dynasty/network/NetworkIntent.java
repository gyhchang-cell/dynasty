package com.dynasty.network;

import io.netty.handler.codec.DecoderException;
import net.minecraft.network.FriendlyByteBuf;

/** Existing client intents have fixed fields; foreign identity, price and dimension data are never appended. */
public final class NetworkIntent {
    public static <T> T complete(FriendlyByteBuf input,T intent){
        if(input.isReadable())throw new DecoderException("Unexpected fields in Dynasty client intent");
        return intent;
    }
    private NetworkIntent(){}
}
