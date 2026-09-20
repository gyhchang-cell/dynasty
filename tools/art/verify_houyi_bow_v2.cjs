#!/usr/bin/env node
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');

const root = path.resolve(__dirname, '../..');
const base = path.join(root, 'src/main/resources/assets/dynasty');
const names = ['houyi_bow', 'houyi_bow_pulling_0', 'houyi_bow_pulling_1', 'houyi_bow_pulling_2'];
const fingerprints = new Set();

function rotate([x, y, z], axis, degrees) {
    const radians = degrees * Math.PI / 180;
    const c = Math.cos(radians), s = Math.sin(radians);
    if (axis === 'x') return [x, c * y - s * z, s * y + c * z];
    if (axis === 'y') return [c * x + s * z, y, -s * x + c * z];
    return [c * x - s * y, s * x + c * y, z];
}

function checkDrawnAim(model, name) {
    for (const hand of [1, -1]) {
        const pose = model.display[hand === 1 ? 'firstperson_righthand' : 'firstperson_lefthand'];
        let direction = [-1, 0, 0]; // Sprite arrowhead points toward local -X.
        direction = rotate(direction, 'z', pose.rotation[2] * hand);
        direction = rotate(direction, 'y', pose.rotation[1] * hand);
        direction = rotate(direction, 'x', pose.rotation[0]);
        // Compose the actual vanilla full-draw transform, in reverse application order.
        direction = rotate(direction, 'y', -45 * hand);
        direction[2] *= 1.2;
        direction = rotate(direction, 'z', -9.785 * hand);
        direction = rotate(direction, 'y', 35.3 * hand);
        direction = rotate(direction, 'x', -13.935);
        const length = Math.hypot(...direction);
        direction = direction.map(value => value / length);
        assert.ok(direction[2] < -0.98, `${name}: arrow must point into the scene`);
        assert.ok(direction[1] > 0.04 && direction[1] < 0.12,
            `${name}: drawn arrow must incline toward the sight, not downward`);
        assert.ok(direction[0] * hand < -0.04 && direction[0] * hand > -0.15,
            `${name}: shaft must converge inward for either hand`);
    }
}

for (const name of names) {
    const png = path.join(base, 'textures/item', `${name}.png`);
    const json = path.join(base, 'models/item', `${name}.json`);
    const rgba = execFileSync('magick', [png, '-alpha', 'on', '-depth', '8', 'RGBA:-']);
    assert.equal(rgba.length, 64 * 64 * 4, `${name}: PNG must be 64x64 RGBA`);
    const model = JSON.parse(fs.readFileSync(json, 'utf8'));
    assert.equal(model.render_type, 'minecraft:cutout');
    assert.equal(model.textures.layer0, `dynasty:item/${name}`);
    assert.ok(model.elements.length > 30 && model.elements.length < 200);
    const coverage = new Uint8Array(64 * 64);
    for (const part of model.elements) {
        assert.ok(part.to[2] - part.from[2] <= 0.5, `${name}: bow is too thick`);
        const x0 = Math.round(part.from[0] * 4);
        const x1 = Math.round(part.to[0] * 4);
        const y0 = Math.round(64 - part.to[1] * 4);
        const y1 = Math.round(64 - part.from[1] * 4);
        assert.ok(x0 >= 0 && x1 <= 64 && x0 < x1 && y0 >= 0 && y1 <= 64 && y0 < y1);
        for (let y = y0; y < y1; y++) {
            for (let x = x0; x < x1; x++) {
                assert.equal(coverage[y * 64 + x], 0, `${name}: overlapping voxel face`);
                coverage[y * 64 + x] = 1;
            }
        }
    }
    for (let i = 0; i < 64 * 64; i++) {
        const alpha = rgba[i * 4 + 3];
        assert.ok(alpha === 0 || alpha === 255, `${name}: alpha must be binary`);
        assert.equal(coverage[i], alpha === 255 ? 1 : 0, `${name}: model/sprite mismatch at pixel ${i}`);
    }
    if (name !== 'houyi_bow') {
        checkDrawnAim(model, name);
        const goldHead = [];
        const whiteNock = [];
        for (let y = 28; y <= 35; y++) {
            for (let x = 0; x < 64; x++) {
                const index = (y * 64 + x) * 4;
                const [red, green, blue, alpha] = rgba.subarray(index, index + 4);
                if (alpha === 0) continue;
                if (x < 22 && red > 170 && green > 105 && green > blue + 25) goldHead.push(x);
                if (x > 40 && red > 170 && green > 160 && blue > 130
                    && Math.abs(red - green) < 55) whiteNock.push(x);
            }
        }
        assert.ok(goldHead.length >= 5 && whiteNock.length >= 5,
            `${name}: missing left-facing gold head or right-hand white nock`);
        assert.ok(Math.max(...goldHead) + 18 < Math.min(...whiteNock),
            `${name}: arrow direction is reversed`);
    }
    fingerprints.add(fs.readFileSync(png).toString('base64'));
    if (name === 'houyi_bow') {
        assert.deepEqual(model.overrides.map(entry => entry.model), [
            'dynasty:item/houyi_bow_pulling_0',
            'dynasty:item/houyi_bow_pulling_1',
            'dynasty:item/houyi_bow_pulling_2'
        ]);
    }
    console.log(`${name}: 64x64, ${model.elements.length} matching voxel parts`);
}
assert.equal(fingerprints.size, names.length, 'Each pull state must have distinct pixels');
