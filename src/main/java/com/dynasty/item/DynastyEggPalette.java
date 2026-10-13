package com.dynasty.item;

/** Shell and spots follow the creature's clothing, fur, shell or element; registry IDs are unchanged. */
public final class DynastyEggPalette {
    public static int[] colors(String id){return switch(id){
        case "lao_chen"->pair(0x704D38,0xC99D72);
        case "han_chong"->pair(0x566372,0xB4BBC0);
        case "qingxuanzi"->pair(0x477552,0xC3CEA6);
        case "baibao_jin"->pair(0xAD753D,0xEDC564);
        case "a_ji"->pair(0x7C705A,0x434A3C);
        case "hei_po"->pair(0x365A88,0xB8C2C7);
        case "xiaoyuanzi"->pair(0x8C9C72,0xE3B899);
        case "mo_jizi"->pair(0x38786D,0xCFB16E);
        case "cao_chengfu"->pair(0x754D89,0xD7C4A0);
        case "hong_ling"->pair(0xC95E6B,0xF0C5BC);
        case "chu_nongyu"->pair(0x343C58,0xE2DED0);
        case "sai_banxian"->pair(0x555362,0xCEB670);
        case "ba_tu"->pair(0x89613F,0xD6C4A0);
        case "yan_chifeng"->pair(0xB94939,0xDFBC79);
        case "huang_laohan"->pair(0x3C7C79,0xC6A36B);
        case "famished_refugee"->pair(0xA79072,0x695843);
        case "bandit_thug"->pair(0x593930,0xAE7660);
        case "night_watchman"->pair(0x334765,0xDBBE6B);
        case "swindler"->pair(0x755A84,0xBD944C);
        case "herb_picker"->pair(0x687E47,0xCAB382);
        case "red_fox"->pair(0xB96335,0xF0DABB);
        case "gray_wolf"->pair(0x7E8589,0xD1D5CB);
        case "wild_boar"->pair(0x5C4237,0xB89A73);
        case "giant_python"->pair(0x3F6341,0xC2B45B);
        case "golden_leopard"->pair(0xD5A347,0x453831);
        case "tree_spirit"->pair(0x655037,0x829C52);
        case "stone_sprite"->pair(0x7D8279,0xAAC1AE);
        case "lantern_ghost"->pair(0x9B3432,0xF1C16A);
        case "paper_cut_child"->pair(0xBA4038,0xE9D7BA);
        case "river_imp"->pair(0x476B55,0xA7C88E);
        case "drowning_ghost"->pair(0x38565F,0x8CC4BC);
        case "carp_spirit"->pair(0xDB7547,0xF4DDAC);
        case "snail_maiden"->pair(0x849A80,0xD4BD90);
        case "crab_soldier"->pair(0xA6503A,0xDAB875);
        case "bat_demon"->pair(0x463444,0xA26C80);
        case "jingwei_bird"->pair(0xA75143,0xE4BD5D);
        case "gray_falcon"->pair(0x566572,0xC6B99D);
        case "locust_swarm"->pair(0x839348,0xD4B65D);
        case "corpse_beetle"->pair(0x342D41,0x8E9A64);
        case "venom_scorpion"->pair(0x7C4C38,0xDCA351);
        case "stone_worm"->pair(0x766B5D,0xBFC1AF);
        case "paper_money_ghost"->pair(0xDFD2AA,0xA77C3E);
        case "wandering_spirit"->pair(0xAFCDC7,0x607D92);
        case "wooden_magpie"->pair(0x90633D,0xC5AF73);
        case "clockwork_rat"->pair(0x8E693F,0x567471);
        default->throw new IllegalArgumentException("Missing Dynasty spawn egg palette: "+id);
    };}
    private static int[] pair(int shell,int spots){return new int[]{shell,spots};}
    private DynastyEggPalette(){}
}
