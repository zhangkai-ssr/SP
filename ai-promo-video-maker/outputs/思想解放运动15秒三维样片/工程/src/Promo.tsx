import React, {useMemo} from 'react';
import {AbsoluteFill, Html5Audio, staticFile, useCurrentFrame} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import * as THREE from 'three';
import './lib/fonts';
import {BEAT, DROP, progress, cardPose, cameraPose, wordPose, labelVisibility} from './plan.mjs';

export type PromoProps = {withAudio: boolean; webMode?: boolean};
const COLORS = ['#8EE3B0','#FFC08A','#8EC8FF','#C9A8FF'];
const NAMES = ['大睡理论','薄肌理论','大水理论','运动员体魄理论','抗炎饮食理论','冰美式理论','早C晚A理论','低成本养生理论','GPT理论','Vibe Coding理论','多语言理论','个人IP理论','极简消费理论','应急金理论','1%复利理论','数字戒断理论'];
const CATEGORIES = ['身体','养护','心智','生活'];
const TAGS = ['休息 × 节律','力量 × 坚持','补水 · 日常','训练 × 恢复','饮食 · 平衡','咖啡 · 日常','护肤 · 习惯','简单 × 持续','你 × AI','想法 → 作品','语言 × 世界','表达 × 积累','更少 · 更好','储备 → 从容','1.01³⁶⁵ ≈ 37.8','注意力 → 自由'];
const gold = '#ffd689';

const WordTunnel: React.FC<{f:number}> = ({f}) => {
  const words=Array.from({length:64},(_,i)=>{const p=wordPose(i,f),idx=i===2?7:(i*7+1)%16;return {i,idx,...p,width:Math.max(NAMES[idx].length*42,TAGS[idx].length*19)*p.scale,height:96*p.scale};}).sort((a,b)=>b.depth-a.depth);
  return <AbsoluteFill style={{opacity:1-progress(f,224,239),background:'radial-gradient(ellipse at 52% 48%,rgba(10,51,78,.8),rgba(4,14,27,.15) 68%)'}}>
    {words.map(w=>{
      if(w.opacity<.015||w.x< -800||w.x>2720||w.y< -300||w.y>1380)return null;
      const idx=w.idx;
      return <div key={w.i} style={{position:'absolute',left:w.x,top:w.y,transform:`translate(-50%,-50%) rotate(${w.rotation}deg) scale(${w.scale})`,opacity:labelVisibility(w,words),filter:`blur(${w.blur}px)`,textAlign:'center',whiteSpace:'nowrap',transformOrigin:'center'}}>
        <div style={{fontFamily:'Kai, PF',fontWeight:900,fontSize:44,lineHeight:1.15,WebkitTextStroke:1.05,color:'#fff9e9',textShadow:'0 0 14px rgba(242,238,216,.22)'}}>{NAMES[idx]}</div>
        <div style={{height:1,background:'linear-gradient(90deg,transparent,#d7aa50,transparent)',margin:'9px auto 8px',width:'90%'}}/>
        <div style={{fontFamily:'Song, PF',fontSize:21,color:'#e5b558',letterSpacing:1.5}}>{TAGS[idx]}</div>
      </div>;
    })}
    <AbsoluteFill style={{background:'radial-gradient(ellipse at 50% 50%,transparent 35%,rgba(1,7,16,.6) 100%)',pointerEvents:'none'}}/>
  </AbsoluteFill>;
};

const Ball: React.FC<{p: [number,number,number]; s: [number,number,number]; color: string; glow?: boolean}> = ({p,s,color,glow=false}) => <mesh position={p} scale={s} castShadow><sphereGeometry args={[1,24,16]}/><meshPhysicalMaterial color={color} roughness={0.28} metalness={glow?0.55:0.03} clearcoat={0.7} emissive={glow?color:'#000000'} emissiveIntensity={glow?0.15:0}/></mesh>;

export const Hero: React.FC<{f:number; scale?:number; variant?:number; action?:'idle'|'sleep'|'lift'|'drink'|'run'; phase?:number; gear?:number; beat?:number}> = ({f,scale=1,variant=0,action,phase=0,gear=0,beat}) => {
  const breath = Math.sin(f/19)*0.025;
  const blink = action==='sleep'||f%108>101 ? 0.12 : 1;
  const lift=action==='lift'?(1-Math.cos((beat??phase*6)*Math.PI))*.5:0;
  const run=action==='run'?Math.sin((beat??phase*8)*Math.PI*2):0;
  const drink=action==='drink'?progress(phase,.15,.4)*(1-progress(phase,.75,.95)):0;
  const handY=.08+lift*2.15+drink*.7;
  const handX=action==='lift'?.93:.53-drink*.2;
  const handZ=action==='lift'?.95:.12+drink*.4;
  const line = useMemo(()=>new THREE.Line(new THREE.BufferGeometry().setFromPoints(new THREE.EllipseCurve(0,0,0.13,0.10,Math.PI,Math.PI*2,false,0).getPoints(24).map(p=>new THREE.Vector3(p.x,p.y,0))),new THREE.LineBasicMaterial({color:'#322d40'})),[]);
  return <group scale={scale} position={[0,breath,0]} rotation={[0,Math.sin(f/60)*0.055,0]}>
    <Ball p={[0,0,0]} s={[0.48,0.62,0.36]} color="#fff7ee"/>
    <Ball p={[0,0.99,0]} s={[0.79,0.72,0.64]} color="#fffaf2"/>
    <Ball p={[-0.24,1.06,0.587]} s={[0.105,0.145*blink,0.055]} color="#242337"/>
    <Ball p={[0.24,1.06,0.587]} s={[0.105,0.145*blink,0.055]} color="#242337"/>
    {[-0.24,0.24].map(x=><Ball key={x} p={[x-0.025,1.105,0.63]} s={[0.027,0.035*blink,0.014]} color="white"/>)}
    {[-0.46,0.46].map(x=><Ball key={x} p={[x,0.84,0.51]} s={[0.13,0.07,0.025]} color="#ff9a9c"/>)}
    <primitive object={line} position={[0,0.88,0.648]}/>
    <mesh position={[0,0.42,0]} rotation={[Math.PI/2,0,0]}><torusGeometry args={[0.39,0.065,12,40]}/><meshPhysicalMaterial color={gold} metalness={0.7} roughness={0.2}/></mesh>
    <Ball p={[-0.27,-0.54+Math.max(0,run)*.2,0.12+run*.2]} s={[0.25,0.17,0.36]} color={action==='run'||gear>3?'#63a78d':'#fff7ee'}/>
    <Ball p={[0.27,-0.54+Math.max(0,-run)*.2,0.12-run*.2]} s={[0.25,0.17,0.36]} color={action==='run'||gear>3?'#63a78d':'#fff7ee'}/>
    {gear>4&&<group position={[.2,.12,.36]} rotation={[0,0,-.5]}><Ball p={[0,0,0]} s={[.1,.17,.035]} color="#71a875"/></group>}
    <Ball p={[-handX,handY+run*.23,handZ]} s={[0.19,0.2,0.19]} color="#ff9787"/>
    <Ball p={[handX,action?handY-run*.23:.15+Math.sin(f/22)*.06,handZ+.01]} s={[0.19,0.2,0.19]} color="#ff9787"/>
    {gear>0&&<Ball p={[0,action==='sleep'?1.08:1.47,.57]} s={[.59,.19,.09]} color="#527d96"/>}
    {gear>1&&[-1,1].map(side=><mesh key={side} position={[side*handX,handY+.04-side*run*.23,handZ]} rotation={[Math.PI/2,0,0]}><torusGeometry args={[.17,.035,8,24]}/><meshStandardMaterial color="#70cda3"/></mesh>)}
    {action==='lift'&&<group position={[0,handY,1]}><mesh rotation={[0,0,Math.PI/2]}><cylinderGeometry args={[.045,.045,2.5,16]}/><meshStandardMaterial color="#b3bec6" metalness={.8} roughness={.25}/></mesh>{[-1.2,1.2].map(x=><mesh key={x} position={[x,0,0]} rotation={[0,0,Math.PI/2]}><cylinderGeometry args={[.28,.28,.25,24]}/><meshPhysicalMaterial color="#326d62" roughness={.3} clearcoat={.6}/></mesh>)}</group>}
    {action==='drink'&&<group position={[.12,handY+.1,.65]} rotation={[drink*-.65,0,drink*-.35]}><mesh><cylinderGeometry args={[.22,.25,.65,32]}/><meshPhysicalMaterial color="#91d9ef" transparent opacity={.48} roughness={.15} clearcoat={1}/></mesh><mesh position={[0,-.22+.18*(1-phase),0]} scale={[1,.9-.65*phase,1]}><cylinderGeometry args={[.205,.23,.5,32]}/><meshStandardMaterial color="#42aed6" transparent opacity={.8}/></mesh><mesh position={[0,.37,0]}><cylinderGeometry args={[.12,.12,.1,24]}/><meshStandardMaterial color="#e1f3f3"/></mesh></group>}
    {!action&&(variant%4===0 ? <group position={[0,-0.02,0.44]} rotation={[0,0,-0.1]}><mesh><boxGeometry args={[0.76,0.52,0.11]}/><meshPhysicalMaterial color="#80cfae" roughness={0.4} clearcoat={0.5}/></mesh><mesh position={[0,0,0.06]}><boxGeometry args={[0.018,0.5,0.012]}/><meshBasicMaterial color="#e6f7df"/></mesh></group> : variant%4===1 ? <mesh position={[0,1.72,0]} rotation={[0,0,0.15]}><torusGeometry args={[0.43,0.052,12,40]}/><meshStandardMaterial color={gold} metalness={0.7} roughness={0.2}/></mesh> : variant%4===2 ? <Ball p={[0,0.0,0.52]} s={[0.27,0.27,0.27]} color="#8ec8ff" glow/> : <mesh position={[0,0.0,0.49]} rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[0.28,0.28,0.09,32]}/><meshPhysicalMaterial color={gold} metalness={0.65} roughness={0.23}/></mesh>)}
  </group>;
};

const makeCard = () => {
  const s = new THREE.Shape(); const w=5.25,h=2.48,r=0.22;
  s.moveTo(-w/2+r,-h/2); s.lineTo(w/2-r,-h/2); s.quadraticCurveTo(w/2,-h/2,w/2,-h/2+r); s.lineTo(w/2,h/2-r); s.quadraticCurveTo(w/2,h/2,w/2-r,h/2); s.lineTo(-w/2+r,h/2); s.quadraticCurveTo(-w/2,h/2,-w/2,h/2-r); s.lineTo(-w/2,-h/2+r); s.quadraticCurveTo(-w/2,-h/2,-w/2+r,-h/2);
  return new THREE.ExtrudeGeometry(s,{depth:0.16,bevelEnabled:true,bevelSegments:3,steps:1,bevelSize:0.07,bevelThickness:0.07,curveSegments:8});
};

const Space: React.FC<{f:number}> = ({f}) => {
  const g = useMemo(makeCard,[]);
  const stars=useMemo(()=>new Float32Array(Array.from({length:360},(_,i)=>{const k=Math.sin(i*127.1+311.7)*43758.5453;return (k-Math.floor(k)-0.5)*(i%3===2?24:45)})),[]);
  const approach=progress(f, DROP+12*BEAT,DROP+17*BEAT);
  return <>
    <color attach="background" args={['#07121f']}/><fog attach="fog" args={['#07121f',28,65]}/>
    <ambientLight intensity={0.8}/><hemisphereLight args={['#d5edff','#3b304d',1.8]}/>
    <directionalLight position={[-5,9,10]} intensity={4} color="#fff2d8" castShadow shadow-mapSize={[1024,1024]}/>
    <pointLight position={[8,4,5]} intensity={90} color="#80bdff"/><pointLight position={[-8,-3,2]} intensity={55} color="#c4a0ff"/>
    <points><bufferGeometry><bufferAttribute attach="attributes-position" args={[stars,3]}/></bufferGeometry><pointsMaterial color="#adcce5" size={0.036} transparent opacity={0.6} sizeAttenuation/></points>
    {f>=DROP && f<320 && <mesh position={[0,0,-1]} scale={0.1+(f-DROP)*.33}><torusGeometry args={[1,0.017,8,80]}/><meshBasicMaterial color={gold} transparent opacity={1-progress(f,DROP,320)}/></mesh>}
    {f>=288 && NAMES.map((_,i)=>{const pose=cardPose(i,f);return <group key={i} position={pose.position} rotation={[0,pose.rotation,0]} scale={pose.scale}>
      <mesh geometry={g} receiveShadow><meshPhysicalMaterial color={COLORS[Math.floor(i/4)]} roughness={0.32} metalness={0.05} clearcoat={0.6}/></mesh>
      <group position={[1.55,-0.36,0.5]}><Hero f={f+i*7} scale={0.64+((i===0)?approach*.1:0)} variant={i}/></group>
    </group>})}
  </>;
};

export const Promo: React.FC<PromoProps> = ({withAudio}) => {
  const f = useCurrentFrame(); const cam=cameraPose(f);
  const camera=useMemo(()=>new THREE.PerspectiveCamera(38,1920/1080,0.1,100),[]);
  camera.position.set(...cam); camera.lookAt(cam[0],cam[1],0); camera.updateMatrixWorld();
  const project=(v:[number,number,number])=>{const p=new THREE.Vector3(...v).project(camera);return {x:(p.x+1)*960,y:(1-p.y)*540,scale:22/(cam[2]-v[2])};};
  const titleOpacity=progress(f,232,237)*(1-progress(f,286,305));
  const titleScale=1+.4*Math.exp(-Math.max(0,f-232)/7)*Math.cos(Math.max(0,f-232)*.23); const wall=progress(f,302,326);
  return <AbsoluteFill style={{background:'#07121f',color:'#fff7e9',fontFamily:'PF',overflow:'hidden'}}>
    <ThreeCanvas width={1920} height={1080} camera={camera} shadows gl={{antialias:true,alpha:false,toneMapping:THREE.ACESFilmicToneMapping,toneMappingExposure:1.05}}><Space f={f}/></ThreeCanvas>
    <AbsoluteFill style={{background:'radial-gradient(ellipse at 50% 45%,transparent 42%,rgba(2,8,16,.45) 100%)',pointerEvents:'none'}}/>
    {f<239&&<WordTunnel f={f}/>}
    {titleOpacity>0 && <AbsoluteFill style={{alignItems:'center',justifyContent:'center',opacity:titleOpacity,transform:`scale(${titleScale})`,background:'radial-gradient(ellipse,rgba(7,18,31,.8),transparent 75%)'}}>
      <div style={{fontSize:44,letterSpacing:28,color:gold,marginBottom:24}}>2 0 2 6</div>
      <div style={{fontFamily:'Song, PF',fontWeight:900,fontSize:152,WebkitTextStroke:2,letterSpacing:12,textShadow:'0 5px 35px #000'}}>思想解放运动</div>
      <div style={{width:180,height:3,background:gold,margin:'38px 0 28px'}}/>
      <div style={{fontSize:28,letterSpacing:13,color:'#cfdfeb'}}>身体 · 养护 · 心智 · 生活</div>
    </AbsoluteFill>}
    {f>=288 && <>
      <div style={{position:'absolute',top:35,left:100,fontFamily:'Song, PF',fontWeight:900,fontSize:44,letterSpacing:4,opacity:wall}}>思想解放运动<span style={{fontFamily:'PF',fontWeight:400,fontSize:22,color:'#a9c2d8',marginLeft:30,letterSpacing:5}}>16 个改变的入口</span></div>
      <div style={{position:'absolute',right:100,top:51,fontSize:19,letterSpacing:4,color:gold,opacity:wall}}>2026 / CHAPTER 01</div>
      {NAMES.map((name,i)=>{const pose=cardPose(i,f);const p=project([pose.position[0]-2.13*pose.scale,pose.position[1]+.55*pose.scale,pose.position[2]+.24]); const opacity=progress(f,305+i*1.2,323+i*1.2);return <div key={name} style={{position:'absolute',left:p.x,top:p.y,transform:`scale(${p.scale*pose.scale})`,transformOrigin:'left top',color:'#203442',opacity}}>
        <div style={{fontSize:18,letterSpacing:3,opacity:.6,marginBottom:10}}>{String(i+1).padStart(2,'0')} / {CATEGORIES[Math.floor(i/4)]}</div>
        <div style={{fontSize:name.length>8?25:name.length>=6?29:36,fontWeight:600,whiteSpace:'nowrap'}}>{name}</div>
        <div style={{width:38,height:3,background:'#203442',opacity:.25,marginTop:15}}/>
      </div>})}
    </>}
    <AbsoluteFill style={{background:'#e7f4ff',opacity:f>=227&&f<242?Math.sin(progress(f,227,242)*Math.PI)*0.6:0,pointerEvents:'none'}}/>
    {f>DROP+6*BEAT&&f<DROP+6*BEAT+24&&<AbsoluteFill style={{background:'linear-gradient(110deg, transparent 35%,rgba(255,255,255,.16) 49%,transparent 63%)',transform:`translateX(${(progress(f,DROP+6*BEAT,DROP+6*BEAT+24)*2-1)*1600}px)`,pointerEvents:'none'}}/>}
    {withAudio&&<Html5Audio src={staticFile('audio/mix.wav')}/>}
  </AbsoluteFill>;
};
