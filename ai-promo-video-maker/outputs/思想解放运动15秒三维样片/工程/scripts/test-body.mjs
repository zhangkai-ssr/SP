import assert from 'node:assert/strict';
import {bodyState,timing} from '../src/body-plan.mjs';
for(let i=0;i<4;i++){
 assert.equal(bodyState(timing.starts[i]).index,i);
 assert.equal(bodyState(timing.starts[i+1]-1).index,i);
 assert.equal(bodyState(timing.demoEnds[i]).phase,1);
 assert.equal(bodyState(timing.starts[i]).enter,0);
}
for(let f=0;f<timing.durationFrames;f++){
 const s=bodyState(f);
 assert.ok(Object.values(s).every(Number.isFinite));
 assert.ok(s.index>=0&&s.index<4&&s.enter>=0&&s.enter<=1&&s.travel>=0&&s.travel<=1);
}
assert.equal(timing.musicStatus,'user_reference_separated');
assert.ok(timing.durationFrames>timing.starts[4]);
assert.ok(timing.beatFrames.at(-1)>timing.durationFrames);
assert.ok(timing.beatFrames.every((v,i)=>Number.isInteger(v)&&(i===0||v>timing.beatFrames[i-1])));
console.log('PASS: four measured scene boundaries, finite animation frames and exact music source.');
