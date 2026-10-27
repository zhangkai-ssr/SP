import React,{useEffect,useMemo} from 'react';
import * as THREE from 'three';
import {progress} from './plan.mjs';

type Vec=[number,number,number];
const Box:React.FC<{p:Vec;s:Vec;color:string;r?:Vec}>=({p,s,color,r=[0,0,0]})=><mesh position={p} rotation={r} castShadow receiveShadow><boxGeometry args={s}/><meshPhysicalMaterial color={color} roughness={.4} clearcoat={.4}/></mesh>;
const Orb:React.FC<{p:Vec;s:Vec;color:string}>=({p,s,color})=><mesh position={p} scale={s} castShadow><sphereGeometry args={[1,24,16]}/><meshPhysicalMaterial color={color} roughness={.35} clearcoat={.5}/></mesh>;
const Pole:React.FC<{p:Vec;h:number;color?:string}>=({p,h,color='#a8b1b3'})=><mesh position={p} castShadow><cylinderGeometry args={[.045,.045,h,12]}/><meshStandardMaterial color={color} metalness={.5} roughness={.3}/></mesh>;
export const Tag:React.FC<{text:string;p:Vec;width?:number;color?:string}>=({text,p,width=1.5,color='#264452'})=>{
  const texture=useMemo(()=>{
    const c=document.createElement('canvas');c.width=768;c.height=192;
    const ctx=c.getContext('2d')!;ctx.fillStyle='#fff8e8';ctx.fillRect(0,0,768,192);
    ctx.fillStyle=color;ctx.textAlign='center';ctx.textBaseline='middle';ctx.font='600 80px "Microsoft YaHei", sans-serif';ctx.fillText(text,384,96,724);
    const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t;
  },[text,color]);
  useEffect(()=>()=>texture.dispose(),[texture]);
  return <mesh position={p}><planeGeometry args={[width,width/4]}/><meshBasicMaterial map={texture} toneMapped={false}/></mesh>;
};
const Coin:React.FC<{p:Vec;s?:number}>=({p,s=1})=><mesh position={p} scale={s} rotation={[Math.PI/2,0,0]} castShadow><cylinderGeometry args={[.23,.23,.065,28]}/><meshPhysicalMaterial color="#e5b955" metalness={.65} roughness={.25}/></mesh>;
const Laptop:React.FC<{p:Vec;code?:boolean;phase:number}>=({p,code=false,phase})=><group position={p} rotation={[0,.12,0]}>
  <Box p={[0,-.45,.25]} s={[2.05,.12,1.05]} color="#adc8d4"/>
  <Box p={[0,.24,-.15]} s={[2.05,1.32,.1]} color="#537785"/>
  <Box p={[0,.24,-.085]} s={[1.85,1.1,.025]} color="#173b4b"/>
  {Array.from({length:5},(_,i)=><Box key={i} p={[-.25,.62-i*.18,-.05]} s={[.3+((i*3)%5)*.2,.055,.02]} color={code?'#9edcca':'#d6e9ef'}/>)}
  <Box p={[0,-.37,.24]} s={[1.7,.035,.55]} color="#577985"/>
  {code&&<group position={[.65,1.1+progress(phase,.4,.75)*.5,.15]} scale={progress(phase,.4,.75)}><Box p={[0,0,0]} s={[.8,.8,.16]} color="#69bfb0"/><Tag text="APP" p={[0,0,.1]} width={.67}/></group>}
</group>;

export const TheoryProps:React.FC<{index:number;phase:number;beat:number;f:number}>=({index,phase,beat,f})=>{
  const a=progress(phase,0,1/3),b=progress(phase,1/3,2/3),c=progress(phase,2/3,1);
  if(index===4)return <group position={[-1.65,-.5,1.1]}>
    <mesh rotation={[.18,0,0]}><cylinderGeometry args={[1.05,.9,.13,48]}/><meshPhysicalMaterial color="#fff9e5" roughness={.3}/></mesh>
    {[0,1,2,3,4,5].map(i=>{const enter=progress(phase,i*.07,i*.07+.18);return <group key={i} position={[Math.cos(i*1.1)*.62,.2+(1-enter)*2,Math.sin(i*1.1)*.55]} scale={enter}><Orb p={[0,.12,0]} s={[.27,.25,.22]} color={i%3?'#74ae65':'#ed9267'}/><Orb p={[.1,.25,0]} s={[.16,.13,.13]} color="#99c678"/></group>;})}
    <Box p={[-1.1-a*1.8,.35+a,0]} s={[.5,.7,.5]} color="#cc7d70" r={[0,0,a*1.5]}/>
  </group>;
  if(index===5)return <group position={[-1.55,-.45,1.2]}>
    <mesh><cylinderGeometry args={[.55,.42,1.25,40]}/><meshPhysicalMaterial color="#b6e3e7" transparent opacity={.38} roughness={.15}/></mesh>
    <mesh position={[0,-.4+a*.3,0]} scale={[1,.25+a*.75,1]}><cylinderGeometry args={[.51,.4,1,40]}/><meshStandardMaterial color="#684b3a"/></mesh>
    {[0,1,2].map(i=><Box key={i} p={[(i-1)*.25,.1+(1-progress(phase,i*.09,i*.09+.22))*2,.12]} s={[.3,.28,.28]} color="#c7e5ea" r={[i*.3,i*.7,0]}/>)}
    <Box p={[1.3+(1-b)*.9+b*1.6,1.3+b*.6,0]} s={[.35,.35,.35]} color="#fff9ef" r={[0,0,phase*4]}/>
    <Tag text="不额外加糖" p={[0,-1,.6]} width={2}/>
  </group>;
  if(index===6)return <>
    {[-1,1].map((side,i)=><group key={side} position={[-1.9+i*3.4,-.35,1]} scale={.75+.25*progress(phase,i*.35,i*.35+.2)}>
      <Box p={[0,0,0]} s={[.63,1.05,.5]} color={i?'#8c86bd':'#e8b85f'}/><Box p={[0,.66,0]} s={[.35,.25,.34]} color="#fff5df"/>
      <Tag text={i?'A':'C'} p={[0,0,.26]} width={.5}/>
      <mesh position={[0,1.6,0]}><sphereGeometry args={[.3,32,16]}/><meshStandardMaterial color={i?'#dde7ff':'#ffd681'}/></mesh>
    </group>)}
    <Tag text="先看肤质，再谈搭配" p={[-.05,3.1,.7]} width={3.4}/>
  </>;
  if(index===7)return <>
    {[-2,2].map((x,i)=><group key={x} position={[x,-.25,-.6]}><Pole p={[0,0,0]} h={1.4} color="#b39b72"/><Orb p={[0,1,0]} s={[.65,.85,.6]} color={i?'#94b796':'#abd092'}/></group>)}
    <mesh position={[-1.8,2.8,-1]}><sphereGeometry args={[.4,24,20]}/><meshStandardMaterial color="#f6d184" emissive="#d5aa49" emissiveIntensity={.4}/></mesh>
    <Tag text="散步 · 休息" p={[-.3,3.25,.3]} width={2.7}/>
    {Array.from({length:9},(_,i)=><mesh key={i} position={[Math.cos(i*.65)*2,-1.06,Math.sin(i*.65)*1.7]} rotation={[-Math.PI/2,0,0]}><circleGeometry args={[.12,16]}/><meshBasicMaterial color="#bfaf8a"/></mesh>)}
  </>;
  if(index===8)return <>
    <Laptop p={[-1.7,-.25,1]} phase={phase}/>
    {[0,1,2].map(i=>{const q=progress(phase,i*.15,i*.15+.4);return <group key={i} position={[-3.2+q*3.8,1.4+i*.45+Math.sin(q*Math.PI)*.4,.9]} scale={.75}><Box p={[0,0,0]} s={[.85,.52,.06]} color={q>.6?'#9dd8ba':'#fff1cf'}/><Tag text={q>.6?'✓':'···'} p={[0,0,.045]} width={.65}/></group>;})}
    <Tag text="整理 → 核对" p={[-1.6,-1.0,1.6]} width={2}/>
  </>;
  if(index===9)return <>
    <Laptop p={[-1.6,-.2,1]} phase={phase} code/>
    <Tag text={phase<.35?'一个想法':'做个小工具'} p={[-1.4,2.5,.7]} width={2.6}/>
    {[0,1,2].map(i=><Orb key={i} p={[-1+i*.4,1.7+Math.sin(beat*Math.PI+i)*.08,.8]} s={[.08,.08,.08]} color="#69b9a4"/>)}
  </>;
  if(index===10)return <group position={[-1.7,.3,.5]}>
    <Pole p={[0,-.8,0]} h={.9}/><mesh position={[0,-1.2,0]}><cylinderGeometry args={[.6,.65,.12,32]}/><meshStandardMaterial color="#e4c682"/></mesh>
    <group rotation={[.15,phase*4,0]}><Orb p={[0,0,0]} s={[.95,.95,.95]} color="#77b7d9"/>{Array.from({length:8},(_,i)=><Orb key={i} p={[Math.cos(i*2.4)*.75,Math.sin(i*1.7)*.5,Math.sin(i*2.4)*.75]} s={[.26,.3,.13]} color="#a8ce93"/>)}<mesh rotation={[Math.PI/2,0,0]}><torusGeometry args={[.958,.014,8,64]}/><meshBasicMaterial color="#dce9db"/></mesh></group>
    {['你好','Hello','Hola'].map((text,i)=><group key={text} scale={progress(phase,i*.2,i*.2+.15)}><Tag text={text} p={[Math.cos(i*2.1)*1.1,1.45+Math.sin(i*2.1)*.4,1]} width={1.2}/></group>)}
  </group>;
  if(index===11)return <>
    <group position={[-1.8,-.05,1]} rotation={[0,.25,0]}><Pole p={[0,-.55,0]} h={1.1}/><Box p={[0,.3,0]} s={[1.2,.8,.5]} color="#45616e"/><mesh position={[.12,.3,.42]} rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[.3,.3,.4,32]}/><meshPhysicalMaterial color="#213e4c" metalness={.5} roughness={.2}/></mesh><Orb p={[-.4,.5,.27]} s={[.06,.06,.03]} color={Math.floor(beat)%2?'#ff7d68':'#b34f45'}/></group>
    {['作品 01','作品 02','持续发布'].map((text,i)=><group key={text} scale={progress(phase,i*.2,i*.2+.18)}><Tag text={text} p={[-1.1+i*.7,1.5+i*.55,.6]} width={1.7}/></group>)}
  </>;
  if(index===12)return <>
    <group position={[-1.75,-.4,1]}><Box p={[0,0,0]} s={[1.5,.12,.75]} color="#95a9b2"/>{[-.6,.6].map(x=><mesh key={x} position={[x,-.45,.25]} rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[.18,.18,.13,24]}/><meshStandardMaterial color="#627d86"/></mesh>)}<Pole p={[.7,.4,0]} h={.9}/>
      {[0,1,2].map(i=>{const q=progress(phase,i/6,i/6+1/3);return <Box key={i} p={[(i-1)*.45-q*1.3,.3+q*.8,-.1]} s={[.37,.45,.45]} color={['#d9b491','#8fb8b1','#b7a8cc'][i]}/>;})}
    </group>
    <Box p={[-3.05,.425,.9]} s={[1.8,.1,.65]} color="#bba58d"/>
    <Tag text="暂停一下" p={[-1.7,2.6,.9]} width={2.2}/>
    <Box p={[.2,-.2,1.15]} s={[.95,.65,.22]} color="#b7875f"/>
  </>;
  if(index===13)return <>
    <group position={[-1.8,-.45,1]}><Orb p={[0,0,0]} s={[.78,.58,.55]} color="#e2b7ad"/><Orb p={[.65,.07,.2]} s={[.28,.23,.27]} color="#d6a296"/><Box p={[0,.57,0]} s={[.45,.025,.08]} color="#865f5b"/>{[-.4,.4].map(x=><Box key={x} p={[x,-.5,.2]} s={[.2,.22,.2]} color="#d6a296"/>)}
      {[0,1,2,3].map(i=>{const q=progress(phase,i*.16,i*.16+.15);return q<1&&<Coin key={i} p={[0,2.1-q*1.5,0]} s={.85}/>;})}
    </group>
    <group position={[.35,2.65,.1]} scale={[Math.max(.02,b),Math.max(.02,b),Math.max(.02,b)]}><mesh scale={[1,.42,1]}><sphereGeometry args={[1.7,48,16,0,Math.PI*2,0,Math.PI/2]}/><meshPhysicalMaterial color="#85b8b4" side={THREE.DoubleSide} roughness={.4}/></mesh><Pole p={[0,-.75,0]} h={1.55}/></group>
    {Array.from({length:12},(_,i)=><mesh key={i} position={[-2.8+(i%6)*1.1,3.5-((f*.055+i*.4)%4.6),-1]} scale={[1,b,1]}><capsuleGeometry args={[.018,.16,4,8]}/><meshBasicMaterial color="#88b6d0"/></mesh>)}
    <Tag text="留一点余地" p={[-1.65,1.1,1.1]} width={2}/>
  </>;
  if(index===14)return <>
    {Array.from({length:5},(_,i)=>{const h=.25+i*.32;return <Box key={i} p={[-1.8+i*.85,-1.075+h/2,.3]} s={[.8,h,1]} color={['#b1cbd9','#a0bfcf','#8fb2c3','#7e9fb1','#708fa6'][i]}/>;})}
    <Tag text={`${Math.pow(1.01,Math.round(phase*365)).toFixed(1)} ×`} p={[.25,3.2,.6]} width={2.2}/>
  </>;
  if(index===15)return <>
    <group position={[-1.8,-.7,1]}><Box p={[0,0,0]} s={[1.45,.55,.9]} color="#b19a80"/><group position={[0,.65*(1-b),0]} rotation={[-.2*(1-b),0,0]}><Box p={[0,.15,0]} s={[.55,.95,.09]} color="#274b5c"/><Box p={[0,.15,.055]} s={[.45,.8,.02]} color="#80b8cb"/></group><group position={[0,.3+(1-b)*1.3,-.46]} rotation={[-(1-b)*Math.PI/2,0,0]}><Box p={[0,0,.46]} s={[1.55,.12,.98]} color="#c6b296"/></group></group>
    {[0,1,2].map(i=><group key={i} scale={1-b}><Tag text="···" p={[-2.2+i*.6,1.6+i*.4,.8]} width={.6}/></group>)}
    <group position={[1.7,.2,-.4]}><Pole p={[0,0,0]} h={1.5} color="#b59b6a"/><mesh position={[0,.9,0]}><coneGeometry args={[.65,.7,32,1,true]}/><meshStandardMaterial color="#f1dca8" side={THREE.DoubleSide} emissive="#c9a964" emissiveIntensity={c*.5}/></mesh><pointLight position={[0,.6,.3]} intensity={c*12} color="#ffe7a2"/></group>
  </>;
  return null;
};
