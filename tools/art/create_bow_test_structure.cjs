// Small empty structure for Forge's isolated gameplay regression tests.
const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const parts = [];
const byte = n => parts.push(Buffer.from([n]));
const int = n => {const b=Buffer.alloc(4); b.writeInt32BE(n); parts.push(b);};
const name = s => {const b=Buffer.from(s); const n=Buffer.alloc(2); n.writeUInt16BE(b.length);parts.push(n,b);};
const tag = (type,s) => {byte(type);name(s);};
tag(10,'');
tag(3,'DataVersion');int(3465);
tag(9,'size');byte(3);int(3);[16,14,16].forEach(int);
tag(9,'palette');byte(10);int(1);tag(8,'Name');name('minecraft:air');byte(0);
tag(9,'blocks');byte(10);int(0);
tag(9,'entities');byte(10);int(0);
byte(0);
const output=path.resolve(__dirname,'../../src/main/resources/data/dynasty/structures/bow_ritual_test.nbt');
fs.mkdirSync(path.dirname(output),{recursive:true});
fs.writeFileSync(output,zlib.gzipSync(Buffer.concat(parts)));
