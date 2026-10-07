package com.dynasty.cod3;

import java.util.List;

/** Localization keys and named actions; a player's current node never lives on the NPC. */
public record DialogueNode(String textKey,List<Choice> choices) {
    public record Choice(String textKey,Action action){}
    public enum Action {TALK,TRADE,LEAVE}
    public static DialogueNode greeting(String role,boolean first){return new DialogueNode("cod3.dynasty.npc."+role+(first?".first":".ordinary"),List.of(new Choice("cod3.dynasty.dialogue.talk",Action.TALK),new Choice("cod3.dynasty.dialogue.trade",Action.TRADE),new Choice("cod3.dynasty.dialogue.leave",Action.LEAVE)));}
}
