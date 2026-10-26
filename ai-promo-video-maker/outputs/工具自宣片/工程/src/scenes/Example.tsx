import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { BrowserFrame } from "../components/BrowserFrame";
import { ramp, T, type SceneName } from "../lib/anim";
import { C, FONT } from "../lib/theme";
import { WAVE } from "../wave";

const CASES = [
  { src: "cases/case-01.jpg", name: "编程导航", detail: "把学习路线，变成一座城市。" },
  { src: "cases/case-02.jpg", name: "编程导航", detail: "真实页面，也能有镜头语言。" },
  { src: "cases/case-03.jpg", name: "面试鸭", detail: "让产品卖点，走进热血漫画。" },
  { src: "cases/case-04.jpg", name: "面试鸭", detail: "让功能，成为画面的记忆点。" },
  { src: "cases/case-05.jpg", name: "鱼皮 AI 导航", detail: "用轻快的画面，讲清工具价值。" },
  { src: "cases/case-06.jpg", name: "鱼皮 AI 导航", detail: "真实界面，是故事的主角。" },
  { src: "cases/case-07.jpg", name: "Vibe Coding 教程", detail: "让教程，也有预告片的节奏。" },
  { src: "cases/case-08.jpg", name: "Vibe Coding 教程", detail: "每个产品，都有自己的表达。" },
];
const STYLE_SHOTS = ["styles/style-A.jpg", "styles/style-B.jpg", "styles/style-C.jpg", "styles/style-D.jpg"];

const Tag: React.FC<{ children: React.ReactNode; blue?: boolean; style?: React.CSSProperties }> = ({ children, blue, style }) => (
  <div style={{ display: "inline-flex", alignItems: "center", padding: "13px 22px", borderRadius: 80, background: blue ? C.accent : "#E8EEFF", color: blue ? "white" : C.accent, fontSize: 23, fontWeight: 600, whiteSpace: "nowrap", ...style }}>{children}</div>
);

const Title: React.FC<{ a: string; b: string; style?: React.CSSProperties }> = ({ a, b, style }) => (
  <div style={{ fontSize: 96, fontWeight: 600, letterSpacing: -5, lineHeight: 1.24, ...style }}>
    <div>{a}</div><div style={{ color: C.accent }}>{b}</div>
  </div>
);

const Block: React.FC<{ name: SceneName; t: number; children: React.ReactNode }> = ({ name, t, children }) => {
  const [start, end] = T.scenes[name];
  if (t < start - 0.2 || t >= end) return null;
  const enter = start === 0 ? 1 : ramp(t, [start - 0.2, start + 0.35]);
  const leave = name === "cta" ? 0 : ramp(t, [end - 0.22, end]);
  return <AbsoluteFill style={{ opacity: enter * (1 - leave), transform: "translateY(" + (1 - enter) * 24 + "px)" }}>{children}</AbsoluteFill>;
};

const Small: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ color: C.dim, fontSize: 27, lineHeight: 1.8, ...style }}>{children}</div>
);

const Shot: React.FC<{ src: string; url: string; width: number; height?: number; zoom?: number; scroll?: number; style?: React.CSSProperties }> = (props) => (
  <BrowserFrame {...props} ratio={16 / 9} style={{ boxShadow: "0 25px 70px #233D7E20", border: "1px solid #DEE5F5", ...props.style }} />
);

export const Example: React.FC<{ t: number }> = ({ t }) => {
  const current = Object.entries(T.scenes).findIndex(([, [a, b]]) => t >= a && t < b);
  const beat = Math.pow(1 - ((t / T.beat) % 1), 4);
  const caseIndex = Math.min(7, Math.max(0, Math.floor(t - T.scenes.cases[0])));
  const item = CASES[caseIndex];
  return (
    <AbsoluteFill style={{ fontFamily: FONT.body, color: C.fg, overflow: "hidden" }}>
      <div style={{ position: "absolute", width: 1280, height: 1280, left: 880 + Math.sin(t * 0.15) * 30, top: -200, borderRadius: "50%", background: "radial-gradient(circle, #C8D7FF 0%, #EAF0FF 43%, #F6F8FF00 70%)", opacity: 0.8 }} />
      <div style={{ position: "absolute", top: 53, left: 84, display: "flex", alignItems: "center", gap: 15, zIndex: 5 }}>
        <Img src={staticFile("img/logo.svg")} style={{ width: 42, height: 42 }} />
        <div style={{ fontSize: 24, fontWeight: 600, letterSpacing: 1 }}>产品宣传视频制作器</div>
      </div>
      <div style={{ position: "absolute", right: 90, top: 66, color: C.dim, fontSize: 17, letterSpacing: 3 }}>OPEN SOURCE / PRODUCT FILMS</div>
      <div style={{ position: "absolute", bottom: 50, left: 90, display: "flex", gap: 15, alignItems: "center", color: C.dim, fontSize: 17 }}>
        <span style={{ color: C.accent, fontWeight: 600 }}>{String(current + 1).padStart(2, "0")}</span><span>/</span><span>一句需求，让产品被看见</span>
      </div>
      <div style={{ position: "absolute", right: 90, bottom: 50, fontSize: 16, color: C.dim }}>本片：字幕 + 曲库配乐 · 无生成类 API</div>
      <div style={{ position: "absolute", bottom: 0, left: 0, height: 5, width: (t / T.duration) * 1920, background: C.accent }} />

      <Block name="hook" t={t}>
        <div style={{ position: "absolute", left: 90, top: 218 }}><Tag>给好产品，一个被看见的机会</Tag></div>
        <div style={{ position: "absolute", left: 90, top: 320, fontSize: 88, fontWeight: 600, lineHeight: 1.27, letterSpacing: -4 }}>
          <div>产品做出来了，</div>
          <div style={{ color: C.accent, opacity: ramp(t, [0.35, 0.95]), transform: "translateY(" + (1 - ramp(t, [0.35, 0.95])) * 20 + "px)" }}>宣传片还没着落？</div>
        </div>
        <Small style={{ position: "absolute", left: 95, top: 590, opacity: ramp(t, [1.1, 1.6]) }}>想讲清卖点，还得找素材、写脚本、做剪辑。</Small>
        <div style={{ position: "absolute", left: 95, top: 744, display: "flex", gap: 15 }}>
          {["调研", "分镜", "素材", "配乐", "剪辑"].map((v, i) => <Tag key={v} style={{ opacity: ramp(t, [1.7 + i * 0.15, 2.1 + i * 0.15]), fontSize: 21 }}>{v}</Tag>)}
        </div>
        <Shot src="shots/repo.jpg" url="github.com/liyupi/ai-promo-video-maker" width={810} height={570} style={{ position: "absolute", left: 1010, top: 232 + Math.sin(t * 0.6) * 6, transform: "rotate(-3deg)" }} />
        <div style={{ position: "absolute", left: 1165, top: 825, color: C.dim, fontSize: 20 }}>真实开源仓库 · 公开页面</div>
      </Block>

      <Block name="brand" t={t}>
        <div style={{ position: "absolute", top: 170, width: "100%", textAlign: "center", color: C.accent, fontSize: 24, letterSpacing: 5 }}>FROM IDEA TO IMPACT</div>
        <div style={{ position: "absolute", top: 234, width: "100%", textAlign: "center", fontSize: 92, fontWeight: 600, letterSpacing: -5 }}>产品宣传视频制作器</div>
        <div style={{ position: "absolute", top: 370, width: "100%", textAlign: "center", fontSize: 34, color: C.dim }}>把一句需求，接成一套视频制作流程。</div>
        {[0, 2, 4].map((idx, i) => {
          const p = ramp(t, [4.35 + i * 0.16, 5.1 + i * 0.16]);
          return <Shot key={idx} src={CASES[idx].src} url={CASES[idx].name + " · 项目公开案例"} width={560} height={350} style={{ position: "absolute", left: 95 + i * 585, top: 505 + (1 - p) * 100 + Math.sin(t * 0.6 + i) * 4, opacity: p, transform: "rotate(" + (i - 1) * 3 + "deg)" }} />;
        })}
        <div style={{ position: "absolute", top: 900, width: "100%", textAlign: "center", fontSize: 23, color: C.dim, opacity: ramp(t, [6, 6.6]) }}>AI 负责推进，你来确认方向。</div>
      </Block>

      <Block name="brief" t={t}>
        <Tag style={{ position: "absolute", top: 223, left: 90 }}>01 / 先定方向</Tag>
        <Title a="先把方向" b="聊清楚。" style={{ position: "absolute", left: 90, top: 326 }} />
        <Small style={{ position: "absolute", left: 95, top: 625 }}>给出差异明确的风格样帧。<br />把受众、画幅与声音，一起确认。</Small>
        <Tag blue style={{ position: "absolute", left: 95, top: 803, opacity: ramp(t, [10, 10.5]) }}>这支片，选 A：明亮产品发布会</Tag>
        {STYLE_SHOTS.map((src, i) => {
          const q = ramp(t, [8.15 + i * 0.12, 8.8 + i * 0.12]);
          return <div key={src} style={{ position: "absolute", left: 950 + (i % 2) * 445, top: 260 + Math.floor(i / 2) * 300 + (1 - q) * 36, width: 420, opacity: q, borderRadius: 15, background: "white", border: i === 0 && t > 9.4 ? "4px solid #295AFF" : "4px solid white", boxShadow: "0 18px 45px #233D7E15", overflow: "hidden", transform: i === 0 ? "scale(" + (1 + ramp(t, [9.4, 10.1]) * 0.035) + ")" : undefined }}>
            <Img src={staticFile(src)} style={{ width: 412, height: 232, display: "block" }} />
            <div style={{ padding: "10px 15px", fontSize: 19, color: i === 0 ? C.accent : C.dim }}>{["A 明亮产品发布会", "B 紫黑电影预告", "C 像素创作车间", "D 暖色创意杂志"][i]}{i === 0 && t > 9.4 ? "  / 已选择" : ""}</div>
          </div>;
        })}
      </Block>

      <Block name="capture" t={t}>
        <Shot src="shots/repo.jpg" url="公开仓库 · 实际页面截图" width={880} height={655} zoom={1.03 + ramp(t, [12, 16]) * 0.06} style={{ position: "absolute", top: 213, left: 90, transform: "rotate(-2deg)" }} />
        <Tag style={{ position: "absolute", left: 1100, top: 244 }}>02 / 找到真实素材</Tag>
        <Title a="让真实产品" b="当主角。" style={{ position: "absolute", left: 1095, top: 350, fontSize: 88 }} />
        <Small style={{ position: "absolute", left: 1100, top: 625 }}>真实页面、真实作品。<br />画面好看，也要有据可查。</Small>
        <Tag blue style={{ position: "absolute", left: 1100, top: 808, opacity: ramp(t, [14, 14.5]) }}>本机网页截图：3840 × 2160</Tag>
      </Block>

      <Block name="edit" t={t}>
        <div style={{ position: "absolute", top: 170, width: "100%", textAlign: "center", fontSize: 65, fontWeight: 600, letterSpacing: -3 }}>把画面、文字和声音，<span style={{ color: C.accent }}>接上节奏。</span></div>
        <Shot src="shots/studio.jpg" url="本地制作台 · 实际界面" width={1320} height={610} style={{ position: "absolute", top: 305, left: 300, transform: "translateY(" + Math.sin(t * 0.5) * 5 + "px)" }} />
        <div style={{ position: "absolute", left: 365, top: 782, width: 1190, padding: "16px 24px", background: "#FFFFFFF2", borderRadius: 16, border: "1px solid #DDE5F5", boxShadow: "0 15px 50px #233D7E20" }}>
          {["镜头", "文字", "音乐"].map((v, i) => <div key={v} style={{ display: "flex", gap: 18, alignItems: "center", margin: "9px 0", fontSize: 18, color: C.dim }}>
            <span style={{ width: 45 }}>{v}</span><div style={{ position: "relative", height: 16, width: 1000, borderRadius: 4, background: "#EAF0FF", overflow: "hidden" }}>
              {[0, 1, 2, 3, 4, 5].map((n) => <div key={n} style={{ position: "absolute", left: n * 174 + i * 13, width: 152, height: 16, borderRadius: 4, background: [C.accent, "#8EA9FF", "#86CFB1"][i], opacity: 0.8 }} />)}
              <div style={{ position: "absolute", width: 3, top: 0, bottom: 0, left: 100 + (t - 16) * 210, background: "#14213E" }} />
            </div>
          </div>)}
        </div>
      </Block>

      <Block name="audio" t={t}>
        <Tag style={{ position: "absolute", top: 218, left: 90 }}>03 / 先把创作跑起来</Tag>
        <Title a="不配 Key，" b="也能先做起来。" style={{ position: "absolute", left: 90, top: 325, fontSize: 88 }} />
        <Small style={{ position: "absolute", left: 95, top: 610 }}>这次选用字幕和曲库配乐。<br />AI 配音与定制作曲，按需再接入。</Small>
        <Tag blue style={{ position: "absolute", top: 812, left: 95, opacity: ramp(t, [22, 22.5]) }}>本次制作：没有调用生成类 API</Tag>
        <Shot src="shots/options.jpg" url="README · ElevenLabs 为可选项" width={815} height={560} style={{ position: "absolute", left: 1000, top: 235, transform: "rotate(2deg)" }} />
        <div style={{ position: "absolute", top: 515, left: 1050, width: 720, height: 270, background: "#FFFFFFF5", borderRadius: 24, border: "1px solid #DAE4FA", boxShadow: "0 18px 65px #233D7E1F", padding: "26px 30px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 20, color: C.dim }}><span>Gimme that Groove!</span><span style={{ color: C.accent }}>Mixkit 曲库配乐</span></div>
          <div style={{ display: "flex", alignItems: "center", gap: 4, height: 150, overflow: "hidden" }}>
            {WAVE.map((value, i) => <div key={i} style={{ width: 5, flexShrink: 0, borderRadius: 3, height: 15 + value * 90 * (0.8 + 0.2 * Math.sin(i * 0.15 + t * 3)), background: i < (t - 20) * 30 ? C.accent : "#B8C9FA" }} />)}
          </div>
          <div style={{ fontSize: 17, color: C.dim }}>真实音轨波形 · 字幕 / 音乐 / 必要音效</div>
        </div>
      </Block>

      <Block name="check" t={t}>
        <div style={{ position: "absolute", top: 180, width: "100%", textAlign: "center", fontSize: 72, fontWeight: 600, letterSpacing: -3 }}>导出前，<span style={{ color: C.accent }}>再检查一遍。</span></div>
        <Shot src="shots/check.jpg" url="本机环境自检 · 实际记录" width={800} height={565} style={{ position: "absolute", left: 150, top: 330, transform: "rotate(-2deg)" }} />
        <div style={{ position: "absolute", left: 1070, top: 360, width: 650 }}>
          {["素材引用与字体", "视频规格与时长", "音轨与响度", "逐场景审图"].map((v, i) => <div key={v} style={{ display: "flex", gap: 22, alignItems: "center", padding: "22px 26px", marginBottom: 18, border: "1px solid #DCE5FA", borderRadius: 18, background: "white", opacity: ramp(t, [24.2 + i * 0.32, 24.8 + i * 0.32]), transform: "translateX(" + (1 - ramp(t, [24.2 + i * 0.32, 24.8 + i * 0.32])) * 35 + "px)" }}>
            <div style={{ width: 40, height: 40, borderRadius: 12, background: "#E8EEFF", color: C.accent, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 21 }}>{String(i + 1).padStart(2, "0")}</div><span style={{ fontSize: 29, fontWeight: 500 }}>{v}</span>
          </div>)}
        </div>
      </Block>

      <Block name="cases" t={t}>
        <div style={{ position: "absolute", left: 110, top: 220, fontSize: 25, color: C.accent, letterSpacing: 4 }}>SAME WORKFLOW. DIFFERENT STORIES.</div>
        <div style={{ position: "absolute", left: 110, top: 325, width: 960, height: 540, borderRadius: 24, overflow: "hidden", boxShadow: "0 28px 70px #233D7E25", transform: "scale(" + (1 + ((t - 28) % 1) * 0.015) + ")" }}>
          <Img key={item.src} src={staticFile(item.src)} style={{ width: 960, height: 540, objectFit: "contain", display: "block" }} />
          <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, padding: "15px 24px", background: "#14213EEB", color: "white", fontSize: 20 }}>项目公开案例 / {item.name}</div>
        </div>
        <div style={{ position: "absolute", left: 1180, top: 303, color: "#B6C7F4", fontSize: 120, fontWeight: 600, lineHeight: 1 }}>{String(caseIndex + 1).padStart(2, "0")}</div>
        <div style={{ position: "absolute", left: 1185, top: 458, fontSize: 67, fontWeight: 600, lineHeight: 1.2 }}>风格，<br /><span style={{ color: C.accent }}>不止一种。</span></div>
        <Small style={{ position: "absolute", left: 1185, top: 665, width: 600 }}>{item.detail}</Small>
        <div style={{ position: "absolute", left: 1185, top: 810, display: "flex", gap: 12 }}>{CASES.map((v, i) => <div key={v.src} style={{ width: i === caseIndex ? 50 : 16, height: 8, borderRadius: 4, background: i === caseIndex ? C.accent : "#CEDAF9" }} />)}</div>
      </Block>

      <Block name="impact" t={t}>
        {CASES.map((v, i) => <div key={v.src} style={{ position: "absolute", width: 390, height: 220, left: 95 + (i % 4) * 445, top: 210 + Math.floor(i / 4) * 410 + Math.sin(t * 0.5 + i) * 7, borderRadius: 16, overflow: "hidden", opacity: 0.85, transform: "rotate(" + (i % 2 ? 4 : -4) + "deg) scale(" + (0.97 + beat * 0.01) + ")", boxShadow: "0 18px 40px #233D7E20" }}>
          <Img src={staticFile(v.src)} style={{ width: 390, height: 220, objectFit: "contain" }} />
        </div>)}
        <div style={{ position: "absolute", left: 235, top: 382, width: 1450, height: 285, borderRadius: 36, background: "#F6F8FFF2", boxShadow: "0 20px 100px #F6F8FF" }} />
        <div style={{ position: "absolute", top: 395, width: "100%", textAlign: "center", fontSize: 105, fontWeight: 600, letterSpacing: -5 }}>一句需求。<span style={{ color: C.accent }}>让产品被看见。</span></div>
        <div style={{ position: "absolute", top: 565, width: "100%", textAlign: "center", fontSize: 33, color: C.accent }}>github.com/liyupi/ai-promo-video-maker</div>
        <div style={{ position: "absolute", top: 920, width: "100%", textAlign: "center", fontSize: 19, color: C.dim }}>背景画面均为项目公开案例</div>
      </Block>

      <Block name="cta" t={t}>
        <div style={{ position: "absolute", top: 195, width: "100%", display: "flex", justifyContent: "center" }}><Tag>由它，介绍它。</Tag></div>
        <div style={{ position: "absolute", top: 310, width: "100%", textAlign: "center", fontSize: 106, fontWeight: 600, letterSpacing: -5, transform: "translateY(" + Math.sin(t * 0.4) * 3 + "px)" }}>从<span style={{ color: C.accent }}>一句需求</span>开始。</div>
        <div style={{ position: "absolute", top: 482, width: "100%", textAlign: "center", fontSize: 39, color: C.dim }}>产品宣传视频制作器</div>
        <div style={{ position: "absolute", top: 603, left: 390, width: 1140, padding: "27px 28px", textAlign: "center", fontSize: 36, fontWeight: 500, color: "white", background: C.accent, borderRadius: 90, boxShadow: "0 20px 50px #295AFF28" }}>github.com/liyupi/ai-promo-video-maker</div>
        <div style={{ position: "absolute", top: 776, width: "100%", display: "flex", justifyContent: "center", gap: 32 }}>{["MIT 开源", "完整工程", "本地预览"].map((v, i) => <Tag key={v} style={{ opacity: ramp(t, [41.3 + i * 0.3, 41.9 + i * 0.3]) }}>{v}</Tag>)}</div>
      </Block>
    </AbsoluteFill>
  );
};
