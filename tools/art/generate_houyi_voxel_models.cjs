#!/usr/bin/env node
// Extrude the four approved 64x64 bow sprites into thin voxel item models.
// Each opaque horizontal run becomes a cuboid; front/back retain exact sprite UVs.
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const root = path.resolve(__dirname, '../..');
const textures = path.join(root, 'src/main/resources/assets/dynasty/textures/item');
const models = path.join(root, 'src/main/resources/assets/dynasty/models/item');
const frames = ['houyi_bow', 'houyi_bow_pulling_0', 'houyi_bow_pulling_1', 'houyi_bow_pulling_2'];
const size = 64;

function opaqueRectangles(pngPath) {
    const rgba = execFileSync('magick', [pngPath, '-alpha', 'on', '-depth', '8', 'RGBA:-'],
        { maxBuffer: size * size * 4 + 1024 });
    if (rgba.length !== size * size * 4) {
        throw new Error(`Expected 64x64 RGBA: ${pngPath} (${rgba.length} bytes)`);
    }
    const rectangles = [];
    let active = new Map();
    for (let y = 0; y < size; y++) {
        const next = new Map();
        for (let x = 0; x < size;) {
            if (rgba[(y * size + x) * 4 + 3] < 128) {
                x++;
                continue;
            }
            const start = x;
            while (x < size && rgba[(y * size + x) * 4 + 3] >= 128) x++;
            const key = `${start}:${x}`;
            const previous = active.get(key);
            next.set(key, previous
                ? { ...previous, y1: y + 1 }
                : { x0: start, x1: x, y0: y, y1: y + 1 });
        }
        for (const [key, rectangle] of active) {
            if (!next.has(key)) rectangles.push(rectangle);
        }
        active = next;
    }
    rectangles.push(...active.values());
    return rectangles;
}

function element(rectangle) {
    const { x0, x1, y0, y1 } = rectangle;
    const uv = [x0 / 4, y0 / 4, x1 / 4, y1 / 4];
    // An interior opaque pixel supplies a matching side color, including the string.
    const sx = Math.floor((x0 + x1 - 1) / 2);
    const sy = Math.floor((y0 + y1 - 1) / 2);
    const edgeUv = [sx / 4, sy / 4, (sx + 1) / 4, (sy + 1) / 4];
    const face = (coordinates) => ({ uv: coordinates, texture: '#layer0' });
    return {
        from: [x0 / 4, (size - y1) / 4, 7.8],
        to: [x1 / 4, (size - y0) / 4, 8.2],
        faces: {
            north: face(uv),
            south: face(uv),
            east: face(edgeUv),
            west: face(edgeUv),
            up: face(edgeUv),
            down: face(edgeUv)
        }
    };
}

const display = {
    gui: { rotation: [10, 24, 0], translation: [0, 0, 0], scale: [0.88, 0.88, 0.88] },
    ground: { rotation: [0, 0, 0], translation: [0, 3, 0], scale: [0.5, 0.5, 0.5] },
    fixed: { rotation: [0, 0, 0], translation: [0, 0, 0], scale: [0.8, 0.8, 0.8] },
    thirdperson_righthand: { rotation: [-80, 260, -40], translation: [-1, -2, 2.5], scale: [0.9, 0.9, 0.9] },
    thirdperson_lefthand: { rotation: [-80, -280, 40], translation: [-1, -2, 2.5], scale: [0.9, 0.9, 0.9] },
    firstperson_righthand: { rotation: [0, -90, 25], translation: [1.13, 3.2, 1.13], scale: [0.68, 0.68, 0.68] },
    firstperson_lefthand: { rotation: [0, 90, -25], translation: [1.13, 3.2, 1.13], scale: [0.68, 0.68, 0.68] }
};

for (const frame of frames) {
    const rectangles = opaqueRectangles(path.join(textures, `${frame}.png`));
    const model = {
        parent: 'minecraft:block/block',
        ambientocclusion: false,
        gui_light: 'front',
        render_type: 'minecraft:cutout',
        textures: { layer0: `dynasty:item/${frame}`, particle: `dynasty:item/${frame}` },
        display: frame === 'houyi_bow' ? display : {
            ...display,
            // Compensate the vanilla BOW pose (X -13.935, Y ±35.3,
            // Z ∓9.785, Z stretch, Y ∓45). Shaft converges slightly upward
            // and inward from the hand toward the sight, including left-hand mirroring.
            firstperson_righthand: { rotation: [26.78, -76.87, 0], translation: [0.8, 3.2, 0.8], scale: [0.62, 0.62, 0.62] },
            firstperson_lefthand: { rotation: [26.78, 103.13, 0], translation: [0.8, 3.2, 0.8], scale: [0.62, 0.62, 0.62] }
        },
        elements: rectangles.map(element)
    };
    if (frame === 'houyi_bow') {
        model.overrides = [
            { predicate: { 'dynasty:pulling': 1 }, model: 'dynasty:item/houyi_bow_pulling_0' },
            { predicate: { 'dynasty:pulling': 1, 'dynasty:pull': 0.65 }, model: 'dynasty:item/houyi_bow_pulling_1' },
            { predicate: { 'dynasty:pulling': 1, 'dynasty:pull': 0.90 }, model: 'dynasty:item/houyi_bow_pulling_2' }
        ];
    }
    fs.writeFileSync(path.join(models, `${frame}.json`), JSON.stringify(model, null, 2) + '\n');
    console.log(`${frame}: ${rectangles.length} voxel elements`);
}
