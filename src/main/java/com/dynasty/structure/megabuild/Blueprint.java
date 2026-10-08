package com.dynasty.structure.megabuild;

import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * 大型建筑的**纯数据画布**：只记录「局部坐标 → 方块种类」，不碰任何 Minecraft 类。
 *
 * 它同时是「离线验证」的唯一入口：
 * <ul>
 *   <li>{@link #solidCount()} / {@link #countByCategory()} 统计最终非空气方块并按类别分开；</li>
 *   <li>{@link #walkable(int[], int[])} 用两格净空 + 楼梯规则检查主路线是否连续；</li>
 *   <li>{@link #topDown(int, int)} / {@link #elevation(int, int)} 输出数据俯视图 / 立面（明确是离线预览）；</li>
 *   <li>{@link #rotate(int)} 支持包围盒与四朝向验证。</li>
 * </ul>
 *
 * Pure painting canvas for the megabuilds; the MC glue maps {@link Kind} to real blocks.
 */
public final class Blueprint {

    public enum Kind {
        AIR, PLATFORM, WALL, FLOOR, WOOD, DARK_WOOD, ROOF, COPPER, LANTERN,
        STAIR_N, STAIR_E, STAIR_S, STAIR_W,
        CHEST, RICH_CHEST, FURNACE, BOOKSHELF, CROP, ORE_IRON, ORE_COPPER, ORE_COAL, BARREL, GATE,
        WATER, LOG, ANVIL, CRAFTING, BREWING, HAY,
        LIGHT, SPAWNER_ZOMBIE, SPAWNER_SKELETON, TINTED_GLASS, CHISELED, RED_WOOD, RAW_IRON, RAW_COPPER, RAW_GOLD, ORE_GOLD, ORE_REDSTONE, ORE_LAPIS, ORE_DIAMOND, MINING_CHEST,
    }

    public final int sizeX;
    public final int sizeY;
    public final int sizeZ;

    private final Map<Long, Kind> cells = new HashMap<>();
    private final java.util.BitSet lights = new java.util.BitSet();
    private int lightIndex(int x,int y,int z){return (y*sizeX+x)*sizeZ+z;}

    public Blueprint(int sizeX, int sizeY, int sizeZ) {
        this.sizeX = sizeX;
        this.sizeY = sizeY;
        this.sizeZ = sizeZ;
    }

    public void set(int x, int y, int z, Kind kind) {
        if (x < 0 || y < 0 || z < 0 || x >= sizeX || y >= sizeY || z >= sizeZ) {
            throw new IndexOutOfBoundsException("越界写入: " + x + "," + y + "," + z
                    + "（画布 " + sizeX + "x" + sizeY + "x" + sizeZ + "）");
        }
        lights.set(lightIndex(x,y,z),kind==Kind.LIGHT);
        if (kind == Kind.AIR || kind == Kind.LIGHT) {
            cells.remove(key(x, y, z));
        } else {
            cells.put(key(x, y, z), kind);
        }
    }

    public Kind at(int x, int y, int z) {
        if(x<0||y<0||z<0||x>=sizeX||y>=sizeY||z>=sizeZ)return Kind.AIR;
        return cells.getOrDefault(key(x, y, z), lights.get(lightIndex(x,y,z))?Kind.LIGHT:Kind.AIR);
    }

    public void box(int x0, int y0, int z0, int x1, int y1, int z1, Kind kind) {
        for (int y = y0; y <= y1; y++) {
            for (int x = x0; x <= x1; x++) {
                for (int z = z0; z <= z1; z++) {
                    set(x, y, z, kind);
                }
            }
        }
    }

    /** 空心盒（只砌六面墙）/ hollow box: six faces only */
    public void hollowBox(int x0, int y0, int z0, int x1, int y1, int z1, Kind kind) {
        for (int y = y0; y <= y1; y++) {
            for (int x = x0; x <= x1; x++) {
                set(x, y, z0, kind);
                set(x, y, z1, kind);
            }
            for (int z = z0 + 1; z < z1; z++) {
                set(x0, y, z, kind);
                set(x1, y, z, kind);
            }
        }
    }

    public void doorway(int x0, int y0, int z0, int x1, int y1, int z1) {
        box(x0, y0, z0, x1, y1, z1, Kind.AIR);
    }

    /** 直向台阶（沿 x 或 z，dir 决定方向与朝向）。*/
    public void stairs(int x0, int y, int z0, int length, int width, Kind dir) {
        boolean alongX = dir == Kind.STAIR_E || dir == Kind.STAIR_W;
        int step = (dir == Kind.STAIR_E || dir == Kind.STAIR_N) ? 1 : -1;
        for (int i = 0; i < length; i++) {
            int x = alongX ? x0 + (dir == Kind.STAIR_E ? i : -i) : x0;
            int z = alongX ? z0 : z0 + (dir == Kind.STAIR_S ? i : -i);
            for (int w = 0; w < width; w++) {
                int wx = alongX ? x : x + w;
                int wz = alongX ? z + w : z;
                set(wx, y + i, wz, dir);
                set(wx, y + i + 1, wz, Kind.AIR);   // 保证每一级头上两格净空
                set(wx, y + i + 2, wz, Kind.AIR);
            }
        }
    }

    public long key(int x, int y, int z) {
        return (((long) x) << 40) | (((long) y) << 20) | (z & 0xFFFFF);
    }

    public int solidCount() {
        return cells.size();
    }
    public int lightCount(){return lights.cardinality();}
    public static boolean empty(Kind k){return k==Kind.AIR||k==Kind.LIGHT;}

    /** 按类别统计：台基填充 / 建筑主体 / 装饰与内容。*/
    public Map<String, Integer> countByCategory() {
        Map<String, Integer> out = new HashMap<>();
        for (Kind kind : cells.values()) {
            out.merge(category(kind), 1, Integer::sum);
        }
        return out;
    }

    private static String category(Kind kind) {
        return switch (kind) {
            case PLATFORM -> "台基填充";
            case WALL, FLOOR, ROOF, WOOD, DARK_WOOD, GATE -> "建筑主体";
            default -> "装饰与内容";
        };
    }

    /** 原地旋转 0..3 次（绕画布中心，内容跟着转，尺寸不变，楼梯朝向同步旋转）。*/
    public Blueprint rotate(int times) {
        Blueprint out = new Blueprint(sizeX, sizeY, sizeZ);
        for(int idx=lights.nextSetBit(0);idx>=0;idx=lights.nextSetBit(idx+1)){
            int z=idx%sizeZ,x=(idx/sizeZ)%sizeX,y=idx/(sizeX*sizeZ);
            for(int i=0;i<Math.floorMod(times,4);i++){int oldX=x;x=sizeX-1-z;z=oldX;}
            out.set(x,y,z,Kind.LIGHT);
        }
        int cx = (sizeX - 1) / 2;
        int cz = (sizeZ - 1) / 2;
        for (Map.Entry<Long, Kind> e : cells.entrySet()) {
            int x = (int) (e.getKey() >> 40);
            int y = (int) ((e.getKey() >> 20) & 0xFFFFF);
            int z = (int) (e.getKey() & 0xFFFFF);
            int nx = x;
            int nz = z;
            for (int i = 0; i < Math.floorMod(times, 4); i++) {
                int oldX = nx;
                nx = sizeX - 1 - nz;
                nz = oldX;
            }
            out.set(nx, y, nz, rotateKind(e.getValue(), times));
        }
        return out;
    }

    private static Kind rotateKind(Kind kind, int times) {
        Kind[] ring = {Kind.STAIR_N, Kind.STAIR_E, Kind.STAIR_S, Kind.STAIR_W};
        for (int i = 0; i < ring.length; i++) {
            if (ring[i] == kind) {
                return ring[Math.floorMod(i + Math.floorMod(times, 4), 4)];
            }
        }
        return kind;
    }

    /** 主路线走线：两格净空 + 楼梯，从 start 能走到 end。/ route reachability with 2-block clearance. */
    public boolean walkable(int[] start, int[] end) {
        if (!standable(start) || !standable(end)) return false;
        Set<Long> seen = new HashSet<>();
        ArrayDeque<int[]> queue = new ArrayDeque<>();
        queue.add(new int[]{start[0], start[1], start[2]});
        seen.add(key(start[0], start[1], start[2]));
        while (!queue.isEmpty()) {
            int[] here = queue.remove();
            if (here[0] == end[0] && here[1] == end[1] && here[2] == end[2]) {
                return true;
            }
            for (int[] d : new int[][]{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}) {
              for(int dy=-1;dy<=1;dy++) {
                int[] next = {here[0] + d[0], here[1] + dy, here[2] + d[1]};
                if (next[1] < 0 || next[1] >= sizeY) {
                    continue;
                }
                if (!standable(next) || (dy>0 && !empty(at(here[0],here[1]+2,here[2])))) {
                    continue;
                }
                long k = key(next[0], next[1], next[2]);
                if (seen.add(k)) {
                    queue.add(next);
                }
              }
            }
        }
        return false;
    }

    private boolean standable(int[] pos) {
        return pos[0]>=0 && pos[0]<sizeX && pos[2]>=0 && pos[2]<sizeZ && pos[1]>0 && pos[1]+1<sizeY
                && empty(at(pos[0], pos[1], pos[2]))
                && empty(at(pos[0], pos[1] + 1, pos[2]))
                && !isAir(pos[0], pos[1] - 1, pos[2]);
    }

    private boolean isStair(int[] pos) {
        Kind k = at(pos[0], pos[1], pos[2]);
        return k == Kind.STAIR_N || k == Kind.STAIR_E || k == Kind.STAIR_S || k == Kind.STAIR_W;
    }

    private boolean isAir(int x, int y, int z) {
        return y < 0 || empty(at(x, y, z));
    }

    /** 数据俯视图（离线预览，不是游戏截图）。*/
    public String topDown(int y, int rot) {
        Blueprint view = rot == 0 ? this : rotate(rot);
        StringBuilder sb = new StringBuilder();
        for (int z = 0; z < view.sizeZ; z += 3) {
            for (int x = 0; x < view.sizeX; x += 2) {
                Kind k = Kind.AIR;
                for (int yy = view.sizeY - 1; yy >= y; yy--) {
                    if (view.at(x, yy, z) != Kind.AIR) {
                        k = view.at(x, yy, z);
                        break;
                    }
                }
                sb.append(glyph(k));
            }
            sb.append('\n');
        }
        return sb.toString();
    }

    /** 数据正立面（固定 x 切片，离线预览）。*/
    public String elevation(int x, int rot) {
        Blueprint view = rot == 0 ? this : rotate(rot);
        StringBuilder sb = new StringBuilder();
        for (int y = view.sizeY - 1; y >= 0; y--) {
            for (int z = 0; z < view.sizeZ; z += 2) {
                Kind k = Kind.AIR;
                for (int xx = x - 2; xx <= x + 2 && xx < view.sizeX; xx++) {
                    if (xx >= 0 && view.at(xx, y, z) != Kind.AIR) {
                        k = view.at(xx, y, z);
                        break;
                    }
                }
                sb.append(glyph(k));
            }
            sb.append('\n');
        }
        return sb.toString();
    }

    private static char glyph(Kind kind) {
        return switch (kind) {
            case AIR -> ' ';
            case PLATFORM -> '.';
            case WALL, GATE -> '#';
            case FLOOR -> '=';
            case WOOD, DARK_WOOD -> 'w';
            case ROOF -> '^';
            case COPPER -> 'c';
            case LANTERN -> '*';
            case STAIR_N, STAIR_E, STAIR_S, STAIR_W -> '>';
            case CHEST, RICH_CHEST, MINING_CHEST -> '@';
            case FURNACE -> 'f';
            case BOOKSHELF -> 'b';
            case CROP -> '~';
            case ORE_IRON, ORE_COPPER, ORE_COAL, RAW_IRON, RAW_COPPER, RAW_GOLD, ORE_GOLD, ORE_REDSTONE, ORE_LAPIS, ORE_DIAMOND -> 'o';
            case BARREL -> 'b';
            case WATER, LOG, ANVIL, CRAFTING, BREWING, HAY, TINTED_GLASS, CHISELED, RED_WOOD -> '+';
            case LIGHT -> ' ';
            case SPAWNER_ZOMBIE, SPAWNER_SKELETON -> 'S';
        };
    }
}
