import assert from 'node:assert/strict';
import { progress, cardPose, cameraPose, wordPose, labelVisibility, DROP, BEAT } from '../src/plan.mjs';
assert.equal(progress(-1, 0, 10), 0);
assert.equal(progress(11, 0, 10), 1);
assert.equal(DROP, 232);
assert.ok(Math.abs(BEAT - 30 * 60 / 112)<1e-12);
const settled = Array.from({length:16}, (_, i) => cardPose(i, 415));
assert.equal(new Set(settled.map(p => p.position.join(','))).size,16);
for (let f=0; f<450; f++) {
  assert.ok(cameraPose(f).every(Number.isFinite));
  for (let i=0;i<16;i++) assert.ok(cardPose(i,f).position.every(Number.isFinite));
}
assert.deepEqual(cardPose(0, 415), cardPose(0, 415));
console.log('PASS: 450 frames, 16 unique card destinations, deterministic finite camera and layout.');
for (let f=0; f<232; f++) {
  const words=Array.from({length:64},(_,i)=>wordPose(i,f));
  assert.ok(words.every(w=>[w.x,w.y,w.scale,w.opacity,w.blur].every(Number.isFinite)));
  assert.ok(words.filter(w=>w.opacity>.3&&w.x>0&&w.x<1920&&w.y>0&&w.y<1080).length>=4);
}
assert.ok(wordPose(20,100).scale>wordPose(20,0).scale);
assert.deepEqual(wordPose(9,90),wordPose(9,90));
console.log('PASS: deterministic fly-through, projected depth, no empty text-space frames.');
const back={x:100,y:100,width:100,height:50,depth:50,opacity:1};
assert.equal(labelVisibility(back,[{...back,depth:20}]),0);
assert.equal(labelVisibility(back,[{...back,x:400,depth:20}]),1);
assert.equal(labelVisibility(back,[{...back,depth:80}]),1);
console.log('PASS: nearer type obscures distant type without hiding disjoint labels.');
