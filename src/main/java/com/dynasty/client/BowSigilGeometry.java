package com.dynasty.client;

/** Pure geometry shared by the in-game renderer and the visual preview exporter. */
public final class BowSigilGeometry {
    private static final double TAU = Math.PI * 2.0D;
    private final double charge;
    private final Stroke sink;

    @FunctionalInterface
    public interface Stroke {
        void draw(double x1, double y1, double x2, double y2, double width);
    }

    public BowSigilGeometry(double charge, Stroke sink) {
        this.charge = charge;
        this.sink = sink;
    }

    public void draw(int tier, double time) {
        double spin = time * 0.007D;
        double reveal = ease(charge);
        arc(0, 0, 1.0D, spin, TAU * reveal);
        arc(0, 0, 0.955D, spin, TAU * reveal);
        arc(0, 0, 0.78D, -spin, TAU * ease((charge - 0.15D) / 0.85D));
        arc(0, 0, 0.74D, -spin, TAU * ease((charge - 0.15D) / 0.85D));
        // Keep the central sight clear; small ring never fills in the target.
        arc(0, 0, 0.16D, spin, TAU * reveal);
        int runes = 12 + tier * 6;
        for (int i = 0; i < runes * reveal; i++) {
            double a = TAU * i / runes + spin;
            rune(Math.cos(a) * 0.866D, Math.sin(a) * 0.866D, a, i);
        }
        if (charge > 0.3D) {
            int vertices = tier >= 2 ? 6 : 3;
            double progress = ease((charge - 0.3D) / 0.7D);
            for (int i = 0; i < vertices * progress; i++) {
                double a = TAU * i / vertices - spin;
                double b = a + TAU * (tier >= 2 ? 2 : 1) / vertices;
                stroke(Math.cos(a) * 0.72D, Math.sin(a) * 0.72D,
                Math.cos(b) * 0.72D, Math.sin(b) * 0.72D, 0.003D);
            }
        }
        if (tier >= 2 && charge > 0.55D) {
            double progress = ease((charge - 0.55D) / 0.45D);
            int seals = tier >= 3 ? 6 : 3;
            for (int i = 0; i < seals; i++) {
                double a = TAU * i / seals - spin;
                double x = Math.cos(a) * 0.49D, y = Math.sin(a) * 0.49D;
                arc(x, y, 0.145D, spin, TAU * progress);
                arc(x, y, 0.115D, -spin, TAU * progress);
                if (progress > 0.5D) {
                    for (int j = 0; j < 3; j++) {
                        double b = TAU * j / 3 + spin, c = b + TAU / 3;
                        stroke(x + Math.cos(b) * 0.09D, y + Math.sin(b) * 0.09D,
                        x + Math.cos(c) * 0.09D, y + Math.sin(c) * 0.09D, 0.0025D);
                    }
                }
            }
        }
        if (tier == 4 && charge > 0.8D) {
            for (int i = 0; i < 8; i++) {
                double a = TAU * i / 8 + spin;
                stroke(Math.cos(a), Math.sin(a), Math.cos(a) * 1.065D,
                Math.sin(a) * 1.065D, 0.006D);
            }
        }
    }

    public void drawBagua(double time) {
        double spin = time * 0.005;
        arc(0,0,1,spin,TAU * ease(charge));
        arc(0,0,0.92,spin,TAU * ease(charge));
        arc(0,0,0.4,0,TAU);
        arc(0,0.2,0.2,-Math.PI/2,Math.PI);
        arc(0,-0.2,0.2,Math.PI/2,Math.PI);
        arc(0,0.2,0.035,0,TAU); arc(0,-0.2,0.035,0,TAU);
        for (int i = 0; i < 8 * ease(charge); i++) {
            double a = TAU * i / 8 + spin, c = Math.cos(a), s = Math.sin(a);
            for (int j = 0; j < 3; j++) {
                double r = 0.57 + j * 0.105;
                if ((i & (1 << j)) == 0) {
                    stroke(c*r+s*0.14,s*r-c*0.14,c*r-s*0.14,s*r+c*0.14,0.012);
                } else {
                    stroke(c*r+s*0.14,s*r-c*0.14,c*r+s*0.04,s*r-c*0.04,0.012);
                    stroke(c*r-s*0.04,s*r+c*0.04,c*r-s*0.14,s*r+c*0.14,0.012);
                }
            }
        }
    }

    private void rune(double x, double y, double a, int seed) {
        double c = Math.cos(a), s = Math.sin(a);
        double[][] points = {{-0.025D,-0.04D}, {-0.025D,0.04D}, {0.025D,0.02D},
            {-0.025D,0}, {0.025D,-0.025D}, {0.025D,0.045D}};
        int count = 3 + seed % 3;
        for (int j = 0; j < count; j++) {
            double[] p = points[j], q = points[j + 1];
            stroke(x + p[0]*c - p[1]*s, y + p[0]*s + p[1]*c,
            x + q[0]*c - q[1]*s, y + q[0]*s + q[1]*c, 0.003D);
        }
    }

    private void arc(double x, double y, double radius, double start, double sweep) {
        int segments = Math.max(1, (int) Math.ceil(Math.max(24, 128 * radius) * sweep / TAU));
        for (int i = 0; i < segments; i++) {
            double a = start + sweep * i / segments, b = start + sweep * (i + 1) / segments;
            stroke(x + Math.cos(a)*radius, y + Math.sin(a)*radius,
            x + Math.cos(b)*radius, y + Math.sin(b)*radius, 0.003D);
        }
    }


    private void stroke(double x1, double y1, double x2, double y2, double width) {
        sink.draw(x1, y1, x2, y2, width);
    }

    private static double ease(double value) {
        double t = Math.max(0, Math.min(1, value));
        return t * t * (3 - 2 * t);
    }
}
