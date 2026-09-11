"""王朝模组贴图工具库 / Dynasty texture art toolkit (pure PIL)."""
from PIL import Image, ImageDraw
import random


def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))


def lighten(c, t):
    return mix(c, (255, 255, 255, c[3]), t)


def darken(c, t):
    return mix(c, (0, 0, 0, c[3]), t)


def ramp(base, n):
    """返回从亮到暗的 n 级色阶 / returns n shades from light to dark."""
    out = []
    for i in range(n):
        t = i / (n - 1)
        if t <= 0.5:
            out.append(lighten(base, (0.5 - t) * 0.7))
        else:
            out.append(darken(base, (t - 0.5) * 0.85))
    return out


class Cv:
    def __init__(self, w, h, bg=(0, 0, 0, 0)):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w, h), bg)
        self.d = self.im.load()

    # ---------------- 基础绘制 ----------------
    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h and c is not None:
            if len(c) == 3:
                c = (c[0], c[1], c[2], 255)
            if c[3] == 255:
                self.d[x, y] = c
            elif c[3] > 0:
                bg = self.d[x, y]
                a = c[3] / 255
                self.d[x, y] = (int(c[0] * a + bg[0] * (1 - a)), int(c[1] * a + bg[1] * (1 - a)),
                                int(c[2] * a + bg[2] * (1 - a)), max(bg[3], c[3]))

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.d[x, y]
        return (0, 0, 0, 0)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def frame(self, x0, y0, x1, y1, c):
        for x in range(x0, x1 + 1):
            self.px(x, y0, c)
            self.px(x, y1, c)
        for y in range(y0, y1 + 1):
            self.px(x0, y, c)
            self.px(x1, y, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + r * 0.3:
                    self.px(x, y, c)

    def ring(self, cx, cy, r, c, thick=1):
        for y in range(int(cy - r - 2), int(cy + r + 3)):
            for x in range(int(cx - r - 2), int(cx + r + 3)):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if r - thick < d <= r:
                    self.px(x, y, c)

    def poly(self, pts, c):
        if not pts:
            return
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(round(xs[i])), int(round(xs[i + 1])) + 1):
                    self.px(x, y, c)

    # ---------------- 质感 ----------------
    def noise(self, x0, y0, x1, y1, colors, seed=1, density=1.0):
        rnd = random.Random(seed)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if rnd.random() <= density:
                    self.px(x, y, colors[rnd.randrange(len(colors))])

    def bevel(self, x0, y0, x1, y1, base, top=None, bottom=None, left=None, right=None):
        """给矩形加立体边缘（光源左上）/ raises edges, light from top-left."""
        n = len(base) if isinstance(base, list) else None
        self.rect(x0, y0, x1, y1, base)
        t = top or lighten(base, 0.35)
        b = bottom or darken(base, 0.4)
        l = left or lighten(base, 0.2)
        r = right or darken(base, 0.22)
        for x in range(x0, x1 + 1):
            self.px(x, y0, t)
            self.px(x, y1, b)
        for y in range(y0, y1 + 1):
            self.px(x0, y, l)
            self.px(x1, y, r)

    def outline(self, color, alpha_only=True):
        """给非透明像素描边 / outlines the opaque silhouette."""
        add = []
        for y in range(self.h):
            for x in range(self.w):
                if self.get(x, y)[3] > 0:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if self.get(nx, ny)[3] == 0:
                            add.append((nx, ny))
        for x, y in add:
            self.px(x, y, color)

    def save(self, path):
        self.im.save(path)
