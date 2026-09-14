package com.dynasty.client;

/**
 * 每个「王朝方块」自己的说明（不要所有方块都写「能盖房子盖宫殿」）。
 *
 * 玩家反馈：一堆方块全是同一句「用来建造房屋、宫殿」，既没信息量又容易和别的模组撞句。
 * 这里按方块的实际用途 / 玩法分别写：矿物说去哪挖、建材说像什么、
 * 功能方块（传送门 / 法阵 / 龙椅）直接写怎么用。
 *
 * Per-block usage text (materials, function blocks, decorations) instead of one generic line.
 */
public final class DynastyBlockInfo {

    private DynastyBlockInfo() {
    }

    /** 返回 {中文, English}；没有专属文案的返回 null / null when the block has no custom line */
    public static String[] use(String path) {
        return switch (path) {
            case "jade_portal" -> new String[]{
                    "§6天朝传送门§r：3×3 玉石块中间放龙晶 → 右键传送到「天朝·龙庭」，再右键返回。",
                    "§6Celestial Portal§r: 3x3 jade blocks with a dragon crystal in the middle; right-click to travel."};
            case "underworld_portal" -> new String[]{
                    "§5地府传送门§r：3×3 玉石块中间放朱砂 → 右键进入「地府」（原版地狱门在王朝里是关着的）。",
                    "§5Underworld Portal§r: 3x3 jade blocks with cinnabar in the middle; right-click to enter the underworld."};
            case "cloud_portal" -> new String[]{
                    "§b九霄传送门§r：玉石块×4 + 龙晶 + 凤凰羽 → 右键往返「九霄天界」。",
                    "§bJiuxiao Portal§r: 4 jade blocks + dragon crystal + phoenix feather; right-click to travel."};
            case "dragon_gate" -> new String[]{
                    "§9龙宫传送门§r：玉石块×4 + 龙晶 + 龙鳞×2 → 右键往返「东海龙宫」。",
                    "§9Dragon Palace Portal§r: 4 jade blocks + dragon crystal + 2 dragon scales; right-click to travel."};
            case "ritual_altar" -> new String[]{
                    "§6法阵·祭坛§r：拿到 Boss 信物（天将令 / 龙宫玉印…）后右键，反复召唤对应 Boss。",
                    "§6Ritual Altar§r: right-click with a boss token to summon that boss again."};
            case "altar" -> new String[]{
                    "§6祭坛§r：低配法阵，用来做节庆与祈福仪式（对应任务会要求放置）。",
                    "§6Altar§r: basic ritual block used by festivals and quest objectives."};
            case "dragon_throne" -> new String[]{
                    "§6龙椅§r：右键坐上去；王朝主线与「登基」相关任务的判定物。",
                    "§6Dragon Throne§r: sit on it - used by the enthronement objectives."};
            case "jade_ore", "deepslate_jade_ore" -> new String[]{
                    "§a玉矿§r：主世界 y≤30 挖到，深层变种在深板岩层；掉玉与玉块。",
                    "§aJade ore§r: found at y<=30 (deepslate variant deeper); drops jade."};
            case "dragon_crystal_ore" -> new String[]{
                    "§d龙晶矿§r：天朝·龙庭地下生成，要用玉镐 / 龙晶镐才挖得动。",
                    "§dDragon crystal ore§r: generates in the celestial realm; needs a jade or crystal pickaxe."};
            case "jade_block" -> new String[]{
                    "§a玉块§r：玉石压缩块，做传送门与玉系装备的中间材料。",
                    "§aJade block§r: compressed jade, used for portals and jade gear."};
            case "marble_block" -> new String[]{
                    "§f汉白玉§r：天朝地表的白色石材，宫室地面与台阶多用它。",
                    "§fMarble§r: the white stone of the celestial realm; floors and stairs."};
            case "palace_bricks" -> new String[]{
                    "§e宫廷砖§r：官方营造用砖，城墙、殿基、龙椅都要它。",
                    "§ePalace bricks§r: official masonry for walls, foundations and thrones."};
            case "crimson_pillar" -> new String[]{
                    "§c朱红柱§r：殿宇立柱，配汉白玉就是标准宫殿配色。",
                    "§cCrimson pillar§r: the red columns of a palace hall."};
            case "imperial_lantern" -> new String[]{
                    "§6宫灯§r：会发光的宫灯，铺在殿前与长廊。",
                    "§6Imperial lantern§r: a glowing palace lantern."};
            case "plaque" -> new String[]{
                    "§6匾额§r：挂在门楣上的题字牌，纯装饰。",
                    "§6Plaque§r: a decorative name board for gateways."};
            case "screen" -> new String[]{"§6屏风§r：室内隔断装饰。", "§6Screen§r: an indoor divider."};
            case "taiko_drum" -> new String[]{
                    "§6太鼓§r：节庆敲击用；放在城中会有节令气氛。",
                    "§6Taiko drum§r: festival percussion."};
            case "chime_bell" -> new String[]{
                    "§6编钟§r：礼乐重器，做节庆任务要摆一座。",
                    "§6Chime bell§r: ritual bronze bells for festivals."};
            case "incense_burner" -> new String[]{
                    "§6香炉§r：点燃后冒烟，祭坛旁的标准配置。",
                    "§6Incense burner§r: smokes when placed; pairs with altars."};
            case "bronze_block" -> new String[]{
                    "§6青铜块§r：青铜锭压缩块，青铜系装备的寄存材料。",
                    "§6Bronze block§r: compressed bronze ingots."};
            default -> null;
        };
    }
}
