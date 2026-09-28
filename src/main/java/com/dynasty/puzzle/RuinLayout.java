package com.dynasty.puzzle;

import java.util.ArrayList;
import java.util.List;

/**
 * 遗迹房间的**纯几何与索引核心**（不引用任何 Minecraft 类，可直接单测）。
 *
 * 一处房间 = 控制器 + 外壳 + 入口 + 宝室 + 机关部件。所有坐标都是「相对控制器」的局部坐标，
 * 并且可以被**朝向**旋转：自然生成时按结构起点坐标哈希选一个朝向（南/西/北/东），
 * 于是世界里的房间有四种朝向，而逻辑完全一致。
 *
 * 三条必须成立的不变量（由 {@code RuinLayoutTest} 断言）：
 * <ol>
 *   <li><b>索引一致</b>：运行时 {@code PuzzleService.discoverParts} 按 (y,x,z) 排序给部件编号，
 *       灯阵还用 {@code PuzzleRules.ringOrder} 取世界角度环序；生成时用同一套算法算出世界坐标下的编号，
 *       所以星盘的初始朝向 / 灯阵的初始亮灭总是落在「被认为是第 i 个」的那一件上 —— 任意朝向都成立。</li>
 *   <li><b>开局未完成</b>：每个难度档的初始状态都不等于答案。</li>
 *   <li><b>可达</b>：入口 → 主室每个部件 → 宝室（封印门后）之间有净空 2 格的连通通道。</li>
 * </ol>
 *
 * Pure geometry/index core for the ruin rooms; the caller rotates the room by the
 * deterministic per-instance facing and everything else stays identical.
 */
public final class RuinLayout {

    private RuinLayout() {
    }

    /** 21×6×21 bounding box accommodates the enclosed rear archive in every rotation. */
    public static final int CX = 10;
    public static final int CY = 1;
    public static final int CZ = 10;
    public static final int SIZE = 21;
    public static final int HEIGHT = 6;
    public static final int TREASURY_VERSION = 3;
    public static final int TREASURY_SIZE = 29, TREASURY_CENTER = 14, TREASURY_HEIGHT = 8;

    /** 主室半宽 / half width of the main chamber */
    public static final int HALF_X = 3;
    /** 前门所在的 z（未旋转）/ front wall local z */
    public static final int FRONT_Z = 4;
    /** 封印墙 z / seal wall z */
    public static final int SEAL_Z = -4;
    /** 宝室最里的 z / back of the treasury */
    public static final int BACK_Z = -9;
    /** 地面 / 天花板相对控制器的 y */
    public static final int FLOOR_Y = -1;
    public static final int CEILING_Y = 3;

    /** 朝向：南 = 未旋转（v1 模板就是朝 +Z 开门）。*/
    public static final int FACING_SOUTH = 0;
    public static final int FACING_WEST = 1;
    public static final int FACING_NORTH = 2;
    public static final int FACING_EAST = 3;

    /** 格子用途 / per-cell role of the shell */
    public enum Role {
        FLOOR, WALL, CEILING, AIR, LANTERN, ALTAR, GATE, CLUE, BOOKSHELF, WORKBENCH,
        TREASURE, PILLAR, RELIC, RUG
    }

    /** 局部坐标 + 用途 */
    public record Cell(int x, int y, int z, Role role) {
    }

    /** 把「未旋转（朝南）」的局部坐标旋到目标朝向。*/
    public static int[] rotate(int dx, int dz, int facing) {
        int x = dx;
        int z = dz;
        for (int i = 0; i < Math.floorMod(facing, 4); i++) {
            int nx = z;          // 朝南 → 朝西 → 朝北 → 朝东：绕 Y 轴顺时针（俯视）
            int nz = -x;
            x = nx;
            z = nz;
        }
        return new int[]{x, z};
    }

    /** 部件（星盘 / 编钟 / 四象灯）在未旋转坐标下的偏移；顺序不重要，编号一律按世界坐标重算。*/
    public static int[][] partOffsets(PuzzleRules.Kind kind) {
        return switch (kind) {
            case STAR -> new int[][]{{-2, 0, -2}, {-2, 0, 2}, {2, 0, -2}, {2, 0, 2}};
            case BELL -> new int[][]{{-2, 0, -2}, {-1, 0, -2}, {0, 0, -2}, {1, 0, -2}, {2, 0, -2}};
            case ELEMENTS -> new int[][]{{0, 0, -3}, {3, 0, 0}, {0, 0, 3}, {-3, 0, 0}};
        };
    }

    /** 按目标朝向旋转后的部件偏移（相对控制器的世界 dx/dy/dz）。*/
    public static int[][] rotatedPartOffsets(PuzzleRules.Kind kind, int facing) {
        int[][] base = partOffsets(kind);
        int[][] out = new int[base.length][3];
        for (int i = 0; i < base.length; i++) {
            int[] r = rotate(base[i][0], base[i][2], facing);
            out[i] = new int[]{r[0], base[i][1], r[1]};
        }
        return out;
    }

    /**
     * 运行时 {@code discoverParts} 的排序规则：(y, x, z)。
     * 入参是相对控制器的世界偏移，返回「局部下标 → 运行时编号」。
     */
    public static int[] runtimeOrder(int[][] worldOffsets) {
        Integer[] order = new Integer[worldOffsets.length];
        for (int i = 0; i < order.length; i++) {
            order[i] = i;
        }
        java.util.Arrays.sort(order, (a, b) -> {
            int cmp = Integer.compare(worldOffsets[a][1], worldOffsets[b][1]);
            if (cmp != 0) {
                return cmp;
            }
            cmp = Integer.compare(worldOffsets[a][0], worldOffsets[b][0]);
            return cmp != 0 ? cmp : Integer.compare(worldOffsets[a][2], worldOffsets[b][2]);
        });
        int[] rank = new int[order.length];
        for (int position = 0; position < order.length; position++) {
            rank[order[position]] = position;
        }
        return rank;
    }

    /** 外壳：**每格只有一个来源**（避免同一格既算墙又算门，生成和测试都不含糊）。*/
    public static List<Cell> shell() {
        List<Cell> cells = new ArrayList<>();
        for (int z = BACK_Z; z <= FRONT_Z + 1; z++) {
            for (int x = -4; x <= 4; x++) {
                for (int y = FLOOR_Y; y <= CEILING_Y; y++) {
                    Role role = roleAt(x, y, z);
                    if (role != null) {
                        cells.add(new Cell(x, y, z, role));
                    }
                }
            }
        }
        for (int x = -HALF_X; x <= HALF_X; x++) {
            for (int y = 0; y <= CEILING_Y; y++) {          // 必须顶到天花板：否则能从上方绕过封印门
                boolean gate = (x >= -1 && x <= 0) && y <= 1;
                cells.add(new Cell(x, y, SEAL_Z, gate ? Role.GATE : Role.WALL));
            }
        }
        return cells;
    }

    /** Versioned enlarged treasure hall; old starts retain shell() byte-for-byte geometry. */
    public static List<Cell> shell(int version) {
        if(version<TREASURY_VERSION)return shell();
        List<Cell> cells=new ArrayList<>();
        for(Cell cell:shell())if(cell.z()>SEAL_Z)cells.add(cell);
        for(int z=-13;z<=SEAL_Z;z++)for(int x=-7;x<=7;x++)for(int y=-1;y<=5;y++){
            Role role;
            if(y==-1)role=Role.FLOOR;
            else if(y==5)role=Role.CEILING;
            else if(z==SEAL_Z&&x>=-1&&x<=0&&y<=1)role=Role.GATE;
            else if(Math.abs(x)==7||z==-13||z==SEAL_Z)role=Role.WALL;
            else if(Math.abs(x)==4&&z==-10&&y==0)role=Role.TREASURE;
            else if(Math.abs(x)==5&&(z==-6||z==-11)&&y<=3)role=Role.PILLAR;
            else if(Math.abs(x)==5&&(z==-6||z==-11)&&y==4)role=Role.LANTERN;
            else if(Math.abs(x)<=1&&z>=-11&&z<=-9&&y==0)role=Role.PILLAR;
            else if(x==0&&z==-10&&y==1)role=Role.RELIC;
            else if(Math.abs(x)==6&&z>=-11&&z<=-8&&y<=1)role=Role.BOOKSHELF;
            else if(x==3&&z==-7&&y==0)role=Role.WORKBENCH;
            else if(x==-3&&z==-7&&y==0)role=Role.ALTAR;
            else if(x>=-1&&x<=0&&z>=-8&&y==0)role=Role.RUG;
            else role=Role.AIR;
            cells.add(new Cell(x,y,z,role));
        }
        return cells;
    }

    /** 某一格的用途（null = 这一格不写，交给世界生成）。*/
    public static Role roleAt(int x, int y, int z) {
        boolean chamber = Math.abs(x) <= HALF_X && z >= -3 && z <= 3;
        boolean treasury = Math.abs(x) <= HALF_X && z > BACK_Z && z <= -5;
        boolean inside = chamber || treasury;
        boolean doorColumn = (x == -1 || x == 0);
        boolean frontWall = z == FRONT_Z;
        boolean walls = Math.abs(x) == 4 || z == BACK_Z || frontWall;
        // 主室/宝室两盏灯与祭坛
        if (x == -3 && y == 2 && z == 3) {
            return Role.LANTERN;
        }
        if (x == 3 && y == 2 && z == 3) {
            return Role.LANTERN;
        }
        if (x == 0 && y == 0 && z == -7) {
            return Role.ALTAR;
        }
        if (Math.abs(x)==2 && y>=0 && y<=1 && z>=-8 && z<=-6) return Role.BOOKSHELF;
        if (x==1 && y==0 && z==-8) return Role.WORKBENCH;
        if ((x == -2 || x == 2) && y == 0 && z == -5) {
            return Role.LANTERN;
        }
        if (y == FLOOR_Y) {
            // 室内地面 + 门槛与门外一级台阶（门口与封印门下方都必须有地板，否则门开了也走不过去）
            boolean threshold = doorColumn && (frontWall || z == FRONT_Z + 1 || z == SEAL_Z);
            return inside || threshold ? Role.FLOOR : null;
        }
        if (doorColumn && frontWall && y >= 0 && y <= 1) {
            return Role.AIR;                                  // 门口挖空
        }
        if (x == 0 && frontWall && y == 2) {
            return Role.CLUE;                                 // 门楣线索石板
        }
        if (inside) {
            return y == CEILING_Y ? Role.CEILING : Role.AIR;
        }
        if (walls && y >= 0 && y <= CEILING_Y) {
            return Role.WALL;
        }
        return null;
    }

    /** 每座遗迹的难度档：由结构起点坐标决定（稳定、可复现、重载不变）。*/
    public static int variantFor(int originX, int originZ) {
        return Math.floorMod(originX * 31 + originZ * 17, PuzzleRules.LAYOUTS);
    }

    /** 每座遗迹的朝向：同样由坐标决定，四向均匀分布。*/
    public static int facingFor(int originX, int originZ) {
        return Math.floorMod(originX * 13 + originZ * 29, 4);
    }

    /** 朝向编号（PuzzleRules.FACING_KEYS：north/east/south/west）→ 单位偏移。*/
    public static int[] facingVector(int orientation) {
        return switch (Math.floorMod(orientation, 4)) {
            case 0 -> new int[]{0, -1};   // north
            case 1 -> new int[]{1, 0};    // east
            case 2 -> new int[]{0, 1};    // south
            default -> new int[]{-1, 0};  // west
        };
    }

    /** 把朝向编号按房间朝向一起旋转（星盘 FACING 必须跟着房间转，否则线索对不上）。*/
    public static int rotateFacing(int orientation, int facing) {
        int[] v = facingVector(orientation);
        int[] r = rotate(v[0], v[1], facing);
        for (int i = 0; i < 4; i++) {
            int[] candidate = facingVector(i);
            if (candidate[0] == r[0] && candidate[1] == r[1]) {
                return i;
            }
        }
        return orientation;
    }

    /** 外壳 + 部件 + 控制器的全部偏移（旋转后），用于越界与可达性检查。*/
    public static List<int[]> allOffsets(PuzzleRules.Kind kind, int facing) {
        List<int[]> out = new ArrayList<>();
        for (Cell cell : shell()) {
            int[] r = rotate(cell.x(), cell.z(), facing);
            out.add(new int[]{r[0], cell.y(), r[1]});
        }
        for (int[] part : rotatedPartOffsets(kind, facing)) {
            out.add(part);
        }
        out.add(new int[]{0, 0, 0});
        return out;
    }

    /** 旋转后的内容是否仍落在包围盒内（越界 = 生成半间房的常见原因）。*/
    public static boolean fits(PuzzleRules.Kind kind, int facing) {
        for (int[] cell : allOffsets(kind, facing)) {
            if (CX + cell[0] < 0 || CX + cell[0] >= SIZE
                    || CZ + cell[2] < 0 || CZ + cell[2] >= SIZE
                    || CY + cell[1] < 0 || CY + cell[1] >= HEIGHT) {
                return false;
            }
        }
        return true;
    }
}
