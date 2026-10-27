import React from 'react';
import {AbsoluteFill, Freeze, Html5Audio, Img, staticFile, useCurrentFrame} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import * as THREE from 'three';
import {Hero, Promo} from './Promo';
import {progress} from './plan.mjs';
import {bodyState, timing} from './body-plan.mjs';
import fullTiming from './full-timing.json';
import {TheoryProps} from './TheoryProps';

const chapters = [
  {title:'大睡理论',tag:'休息 × 节律',line:'每天尽量同一时间起床',sub:'先把生活的节奏找回来',color:'#c9dfef',word:'规律作息'},
  {title:'薄肌理论',tag:'力量 × 坚持',line:'循序渐进，量力而行',sub:'从一次稳稳的举起开始',color:'#f3d6b8',word:'慢慢变强'},
  {title:'大水理论',tag:'补水 · 日常',line:'分次喝水，按需补充',sub:'把顺手的选择换一下',color:'#bfe4e2',word:'日常补水'},
  {title:'运动员\n体魄理论',tag:'训练 × 恢复',line:'动起来，慢慢增加',sub:'把身体带回生活里面',color:'#d4cdef',word:'持续行动'},
  {title:'抗炎饮食理论',tag:'均衡 · 多样',line:'多些蔬菜，饮食搭配更均衡',sub:'让餐盘多一点颜色',color:'#f3d6b8',word:'日常饮食，不是治病处方'},
  {title:'冰美式理论',tag:'选择 · 适量',line:'咖啡按需喝，不额外加糖',sub:'把习惯变成自己的选择',color:'#e8d4c1',word:'不靠咖啡硬撑'},
  {title:'早C晚A理论',tag:'肤质 × 耐受',line:'按肤质选择，别盲目叠加',sub:'先做好基础护理和防晒',color:'#f3d8bd',word:'适合自己，比跟风重要'},
  {title:'低成本\n养生理论',tag:'简单 × 持续',line:'散步、休息，从日常做起',sub:'照顾自己，不必很复杂',color:'#d7e3c7',word:'把简单的事做好'},
  {title:'GPT 理论',tag:'你 × AI',line:'交给 AI 一件事，再核对结果',sub:'从整理一份待办开始',color:'#c2deef',word:'让工具帮你动手'},
  {title:'Vibe Coding\n理论',tag:'想法 → 小工具',line:'先做能用的一步，再慢慢改',sub:'把脑海里的想法做出来',color:'#badfdc',word:'描述 → 尝试 → 验证'},
  {title:'多语言理论',tag:'语言 × 世界',line:'每天练几句，试着用出来',sub:'多一种表达，多一个入口',color:'#cbdff0',word:'从一句你好开始'},
  {title:'个人 IP 理论',tag:'表达 × 积累',line:'固定输出，把作品慢慢积累',sub:'先完成，再持续改进',color:'#c9d8ee',word:'用作品介绍自己'},
  {title:'极简消费理论',tag:'暂停 × 选择',line:'先等一等，再决定买不买',sub:'留住真正需要的东西',color:'#ddd2e8',word:'少一点冲动'},
  {title:'应急金理论',tag:'储备 → 从容',line:'量力积累，留一点应急余地',sub:'从负担得起的小额开始',color:'#d5d1e7',word:'给意外留个缓冲'},
  {title:'1% 复利理论',tag:'1.01³⁶⁵ ≈ 37.8',line:'每天做一点，持续复盘',sub:'把一次努力变成长期积累',color:'#d9d0ed',word:'数学示意，不是收益承诺'},
  {title:'数字戒断理论',tag:'注意力 → 自由',line:'留一段时间，放下手机',sub:'让注意力回到眼前',color:'#e4d5c2',word:'读几页书，安静一会儿'},
];
const Pill: React.FC<{children:React.ReactNode}> = ({children})=><div style={{border:'1px solid #29404d30',borderRadius:50,padding:'16px 30px',display:'inline-block',fontSize:30,letterSpacing:3}}>{children}</div>;

const Stage: React.FC<{index:number;phase:number;f:number;config:typeof timing}>=({index,phase,f,config})=>{
  const wake=progress(phase,.42,.68),jump=Math.sin(progress(phase,.65,.85)*Math.PI)*.55;
  const bed=1-progress(phase,.62,.83);
  const orbit=phase*Math.PI*4;
  const beatIndex=Math.max(0,config.beatFrames.findIndex(v=>v>f)-1);
  const beat=beatIndex+(f-config.beatFrames[beatIndex])/(config.beatFrames[beatIndex+1]-config.beatFrames[beatIndex]);
  const propPhase=index>=4?Math.min(1,Math.max(0,(beat-(28+12*index)-1)/6)):phase;
  const step=Math.min(3.9999,propPhase*4),stepIndex=Math.floor(step),stepEase=progress(step-stepIndex,0,1);
  const climb=stepIndex+stepEase;
  const heroX=index===14?-1.8+climb*.85:index===7?Math.sin(phase*Math.PI*2)*.55:index>3&&index!==6?.65:index===0?-.4*(1-wake):0;
  const heroY=index===14?-.257+climb*.32+Math.sin(stepEase*Math.PI)*.25:index===0?.25*(1-wake)+jump:index===3?Math.abs(Math.sin(orbit*2))*.12:0;
  return <>
    <ambientLight intensity={1.2}/><hemisphereLight args={['#fff8ec','#899ca4',2]}/>
    <directionalLight position={[-4,8,9]} intensity={3.5} castShadow shadow-mapSize={[1024,1024]}/>
    <directionalLight position={[5,3,-3]} intensity={2} color="#c5ebff"/>
    <group position={[2.45,-.65,0]}>
      <mesh receiveShadow position={[0,-1.25,0]}><cylinderGeometry args={[2.6,2.8,.35,80]}/><meshPhysicalMaterial color="#fffcf3" roughness={.4} clearcoat={.3}/></mesh>
      <mesh position={[0,-1.47,0]}><cylinderGeometry args={[2.45,2.5,.12,80]}/><meshStandardMaterial color="#b3a781" metalness={.4} roughness={.4}/></mesh>
      {index===0&&bed>.001&&<group position={[.1,-.72,-.35]} scale={[bed,bed,bed]}>
        <mesh castShadow><boxGeometry args={[3.2,.36,1.5]}/><meshPhysicalMaterial color="#7194b0" roughness={.5}/></mesh>
        <mesh position={[0,.23,0]}><boxGeometry args={[3.1,.25,1.45]}/><meshStandardMaterial color="#fffaf0"/></mesh>
        <mesh position={[1.1,.45,0]} rotation={[0,0,-.1]}><boxGeometry args={[.65,.22,1.1]}/><meshStandardMaterial color="#e8f2fa"/></mesh>
      </group>}
      <group position={[heroX,heroY,.4]} rotation={[0,index===3?-.18:0,index===0?-(1-wake)*Math.PI/2:0]}>
        <Hero f={f} scale={index===14?.8:1.42} action={index===0?(wake<.45?'sleep':'idle'):index===1?'lift':index===2?'drink':index===3||index===7?'run':index===15?undefined:'idle'} phase={phase} gear={index+1} beat={beat}/>
      </group>
      {index>=4&&<TheoryProps index={index} phase={propPhase} beat={beat} f={f}/>}
      {index===0&&<group position={[2.2,3.2,-1]} rotation={[0,0,f*.002]}>
        <mesh><sphereGeometry args={[.52,40,24]}/><meshStandardMaterial color={wake<.5?'#e1f4ff':'#ffce73'} emissive={wake<.5?'#6a98ac':'#efb351'} emissiveIntensity={.35}/></mesh>
        {wake>.5&&Array.from({length:8},(_,i)=><mesh key={i} position={[Math.cos(i*Math.PI/4)*.8,Math.sin(i*Math.PI/4)*.8,0]} rotation={[0,0,i*Math.PI/4-Math.PI/2]}><capsuleGeometry args={[.035,.15,4,8]}/><meshBasicMaterial color="#eeb663"/></mesh>)}
      </group>}
      {index===1&&[0,1,2].map(i=><mesh key={i} position={[-2.3+i*.42,-.85+progress(phase,i*.22,i*.22+.18)*.45, -.4]} scale={[1,.15+progress(phase,i*.22,i*.22+.18)*(i+1),1]}><boxGeometry args={[.25,.45,.35]}/><meshStandardMaterial color="#92b9a0"/></mesh>)}
      {index===2&&<group position={[-1.9-progress(phase,0,.3)*3,-.55,0]} scale={1-progress(phase,.2,.4)}><mesh><cylinderGeometry args={[.35,.25,.85,32]}/><meshStandardMaterial color="#ba9e90"/></mesh><mesh position={[0,.46,0]}><cylinderGeometry args={[.37,.37,.08,32]}/><meshStandardMaterial color="#f6eee5"/></mesh><mesh position={[0,.7,0]} rotation={[0,0,-.16]}><cylinderGeometry args={[.035,.035,.6,8]}/><meshStandardMaterial color="#624f52"/></mesh></group>}
      {index===3&&Array.from({length:12},(_,i)=>{const a=i*Math.PI/6-orbit;return <mesh key={i} position={[Math.cos(a)*2.25,-1.03,Math.sin(a)*1.65]} rotation={[-Math.PI/2,0,0]}><circleGeometry args={[.08,12]}/><meshBasicMaterial color={i%3===0?'#b78d45':'#8c82b9'}/></mesh>;})}
    </group>
  </>;
};

export const BodyPreview: React.FC<{withAudio:boolean;full?:boolean}>=({withAudio,full=false})=>{
  const f=useCurrentFrame();
  const cfg=full?fullTiming:timing;
  const {index,local,phase,travel,enter}=bodyState(f,cfg);
  const ending=f>=cfg.starts[cfg.count];
  const c=chapters[index];
  const zoom=enter*(1-travel);
  const cellX=358+(index%4)*401,cellY=286+Math.floor(index/4)*202;
  const panelScale=.205+.795*zoom;
  const x=(cellX-960)*(1-zoom),y=(cellY-540)*(1-zoom);
  const mapped=Math.round(f<cfg.titleFrame?f/cfg.titleFrame*232:f<cfg.wallFrame?232+(f-cfg.titleFrame)/(cfg.wallFrame-cfg.titleFrame)*56:288+(f-cfg.wallFrame)/(cfg.introFrames-cfg.wallFrame)*82);
  const endFrame=f-cfg.starts[cfg.count];
  return <AbsoluteFill style={{background:'#07121f',fontFamily:'PF',overflow:'hidden'}}>
    {f<cfg.introFrames?<Freeze frame={mapped}><Promo withAudio={false}/></Freeze>:<>
      <Img src={staticFile('wall.png')} style={{width:1920,height:1080}}/>
      {Array.from({length:cfg.count},(_,i)=>(i<index||ending||(i===index&&travel>.15))&&<div key={i} style={{position:'absolute',left:489+(i%4)*401,top:205+Math.floor(i/4)*202,width:42,height:42,borderRadius:'50%',background:'#fbf5d9',color:'#286c57',fontSize:31,textAlign:'center',boxShadow:'0 0 26px #b9ffd488'}}>✓</div>)}
      {ending?(full?<AbsoluteFill style={{background:`rgba(4,13,24,${progress(endFrame,12,38)*.8})`,alignItems:'center',justifyContent:'center',color:'#fff5dc',fontFamily:'Song, PF',textAlign:'center'}}>
        {['思想解放，','不是想通了什么，','而是开始做了什么。'].map((text,i)=><div key={text} style={{fontSize:i===0?108:96,fontWeight:900,letterSpacing:6,lineHeight:1.55,color:i===2?'#ffe299':'#fff5dc',opacity:progress(endFrame,24+i*30,38+i*30),transform:`translateY(${(1-progress(endFrame,24+i*30,38+i*30))*22}px)`}}>{text}</div>)}
        <div style={{fontFamily:'PF',fontSize:30,letterSpacing:5,marginTop:40,opacity:progress(endFrame,118,134),color:'#d0dce7'}}>16 个入口 · 从一个行动开始</div>
      </AbsoluteFill>:<div style={{position:'absolute',bottom:35,width:'100%',textAlign:'center',color:'#ffe2a2',fontSize:29,letterSpacing:6}}>身体 · 从一个小习惯开始</div>):<AbsoluteFill style={{transform:`translate(${x}px,${y}px) scale(${panelScale})`,transformOrigin:'center',padding:42,opacity:progress(enter,0,.12)}}>
        <AbsoluteFill style={{left:42,top:42,right:'auto',bottom:'auto',width:1836,height:996,borderRadius:38,overflow:'hidden',background:`radial-gradient(ellipse at 70% 24%,#ffffffb8,transparent 65%),${c.color}`,boxShadow:'0 22px 80px #0005',border:'2px solid #ffffff90'}}>
          <div style={{position:'absolute',fontSize:330,fontWeight:600,color:'#ffffff35',right:80,bottom:80,lineHeight:1}}>{String(index+1).padStart(2,'0')}</div>
          <ThreeCanvas width={1836} height={996} camera={{position:[0,1.4,16],fov:37}} shadows gl={{antialias:true,alpha:true,toneMapping:THREE.ACESFilmicToneMapping,toneMappingExposure:1.05}}><Stage index={index} phase={phase} f={f} config={cfg}/></ThreeCanvas>
          <div style={{position:'absolute',left:98,top:72,color:'#263c47'}}>
            <div style={{fontSize:25,letterSpacing:7,opacity:.6,marginBottom:45}}>{['身体','养护','心智','生活'][Math.floor(index/4)]} / {String(index+1).padStart(2,'0')}</div>
            <div style={{fontFamily:'Song, PF',fontWeight:900,WebkitTextStroke:1.4,fontSize:index<4?(index===3?90:104):c.title.includes('Vibe')?75:88,whiteSpace:'pre-line',lineHeight:1.18,letterSpacing:3}}>{c.title}</div>
            <div style={{height:3,width:75,background:'#a68042',margin:'30px 0'}}/>
            <div style={{fontSize:36,color:'#8f6e38',letterSpacing:3}}>{c.tag}</div>
            <div style={{fontSize:29,marginTop:44,opacity:.72}}>{c.sub}</div>
            <div style={{marginTop:40,opacity:progress(local,35,52),transform:`translateY(${(1-progress(local,35,52))*16}px)`}}><Pill>{c.word}</Pill></div>
          </div>
          <div style={{position:'absolute',left:98,right:98,bottom:55,borderRadius:60,background:'#203a46',height:100,display:'flex',alignItems:'center',justifyContent:'center',boxShadow:'0 12px 30px #18344420',color:'#fff7dc',fontSize:44,letterSpacing:3}}>{c.line}</div>
          <div style={{position:'absolute',left:0,bottom:0,height:7,background:'#9d7b45',width:`${phase*100}%`}}/>
        </AbsoluteFill>
      </AbsoluteFill>}
    </>}
    {withAudio&&<Html5Audio src={staticFile(full?'audio/full.wav':'audio/continuation.wav')}/>}
  </AbsoluteFill>;
};
