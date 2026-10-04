// Source/resource regression check. Does not launch Minecraft or open any player save.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const assets = path.join(root, 'src/main/resources/assets/dynasty');
const json = file => JSON.parse(fs.readFileSync(path.join(assets, file), 'utf8'));
const states = json('blockstates/zhenyuan_node.json').variants;
assert.equal(Object.keys(states).length, 10);
let checked = 0;
for (let slot=0;slot<5;slot++) for (const active of [false,true]) {
  const model = states[`active=${active},slot=${slot}`]?.model;
  assert.ok(model, `Missing state for slot ${slot}, active ${active}`);
  const data = json(`models/${model.replace('dynasty:', '')}.json`);
  const limit = slot === 4 ? 12 : 8;
  assert.ok(data.elements.length >= 12, 'Sculpted stand must retain the open rim, feet and inlays');
  for (const element of data.elements) {
    assert.ok(element.to[1] <= limit, `Pedestal geometry exceeds ${limit}/16 collision height`);
    element.from.forEach((v,i) => {
      assert.ok(v >= 0 && v < element.to[i]);
      assert.ok(element.to[i] <= 16);
    });
    for (const face of Object.values(element.faces)) {
      assert.ok(data.textures[face.texture.slice(1)], `Unresolved texture ${face.texture}`);
    }
  }
  for (let i=0;i<data.elements.length;i++) for (let j=i+1;j<data.elements.length;j++) {
    const a=data.elements[i], b=data.elements[j];
    const overlap=a.from.map((_,axis)=>Math.min(a.to[axis],b.to[axis])-Math.max(a.from[axis],b.from[axis]));
    assert.ok(!overlap.every(v=>v>1e-6), `Overlapping elements ${i}/${j} create coplanar z-fighting`);
  }
  for (const texture of Object.values(data.textures)) if (texture.startsWith('dynasty:')) {
    assert.ok(fs.existsSync(path.join(assets, `textures/${texture.replace('dynasty:', '')}.png`)), texture);
  }
  checked++;
}
for(const name of ['ZhenyuanRitualContent','ZhenyuanNodeBlock','ZhenyuanNodeBlockEntity']) {
  const source = fs.readFileSync(path.join(root, `src/main/java/com/dynasty/ritual/${name}.java`), 'utf8');
  assert.doesNotMatch(source, /import net\.minecraft\.client\./, 'Common registrations must load on dedicated server');
}
const renderer = fs.readFileSync(path.join(root,'src/main/java/com/dynasty/client/ZhenyuanNodeRenderer.java'),'utf8');
assert.match(renderer, /value = Dist\.CLIENT/);
assert.match(renderer, /COLOR_WRITE/); // The translucent magic never turns into an invisible depth wall.
assert.match(renderer, /renderAtTime/);
assert.match(renderer, /if \(node\.getStage\(\) >= 2\) return/);
console.log(`PASS: ${checked} state/model combinations, low collision envelopes, texture references, dedicated-server boundary.`);
