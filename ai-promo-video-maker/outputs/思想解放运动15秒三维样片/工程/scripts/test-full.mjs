import assert from 'node:assert/strict';
import full from '../src/full-timing.json' with {type:'json'};
import original from '../src/body-timing.json' with {type:'json'};
import {bodyState} from '../src/body-plan.mjs';
assert.equal(full.count,16);
assert.equal(full.starts.length,17);
assert.equal(full.demoEnds.length,16);
assert.deepEqual(full.starts.slice(0,5),original.starts);
assert.deepEqual(full.demoEnds.slice(0,4),original.demoEnds);
assert.ok(full.durationFrames>full.starts[16]+150);
for(let i=0;i<16;i++){
 assert.equal(bodyState(full.starts[i],full).index,i);
 assert.equal(bodyState(full.starts[i+1]-1,full).index,i);
 assert.equal(bodyState(full.demoEnds[i],full).phase,1);
 assert.ok(full.demoEnds[i]-full.starts[i]-18>=105,'At least 3.5s clear viewing');
}
for(let f=0;f<full.durationFrames;f++){
 const s=bodyState(f,full);
 assert.ok(Object.values(s).every(Number.isFinite));
 assert.ok(s.index>=0&&s.index<16&&s.phase>=0&&s.phase<=1);
 assert.ok(s.enter>=0&&s.enter<=1&&s.travel>=0&&s.travel<=1);
}
assert.ok(full.beatFrames.at(-1)>full.durationFrames);
assert.ok(full.beatFrames.every((n,i)=>Number.isInteger(n)&&(i===0||n>full.beatFrames[i-1])));
console.log(`PASS: 16 chapters, ${full.durationFrames} finite frames, original intro/first four timing preserved, beat coverage.`);
