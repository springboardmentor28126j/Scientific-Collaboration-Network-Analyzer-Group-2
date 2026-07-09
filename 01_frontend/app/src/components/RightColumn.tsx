import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLanguage } from "../contexts/LanguageContext";
import { useAuth } from "@/hooks/useAuth";
import { trpc } from "@/providers/trpc";
import ImageUpload from "./ImageUpload";

gsap.registerPlugin(ScrollTrigger);

interface CVItem {
  category: string;
  title: string;
  subtitle?: string;
  year: string;
}

const fallbackCvData: Record<string, CVItem[]> = {
  zh: [
    { category: "Education", title: "中国美术学院", subtitle: "跨媒体艺术学院 / 硕士", year: "2019 - 2022" },
    { category: "Education", title: "中央美术学院", subtitle: "摄影系 / 学士", year: "2015 - 2019" },
    { category: "Employment", title: "独立工作室", subtitle: "视觉艺术创作 / 上海", year: "2022 - 至今" },
    { category: "Employment", title: "空白画廊", subtitle: "驻留艺术家 / 景德镇", year: "2023 (3个月)" },
    { category: "Employment", title: "原美术馆", subtitle: "策展助理 / 重庆", year: "2021 - 2022" },
    { category: "Exhibition", title: "\u201c土与诗\u201d 个人展览", subtitle: "BLANKSPACE 画廊 / 上海", year: "2024" },
    { category: "Exhibition", title: "\u201c时间的纹理\u201d 群展", subtitle: "当代美术馆 / 杭州", year: "2023" },
    { category: "Exhibition", title: "\u201c自然书写\u201d 双个展", subtitle: "藝術門画廊 / 香港", year: "2023" },
    { category: "Exhibition", title: "\u201c新锐视角\u201d 年度展", subtitle: "今日美术馆 / 北京", year: "2022" },
    { category: "Awards", title: "青年艺术家资助计划", subtitle: "获选艺术家 / 提名", year: "2024" },
    { category: "Awards", title: "三影堂摄影奖", subtitle: "入围 / 策展人特别推荐", year: "2023" },
    { category: "Awards", title: "新锐摄影奖", subtitle: "TOP 20", year: "2022" },
    { category: "Press", title: "\u201c在日常中寻找神性\u201d", subtitle: "ArtReview Asia / 专访", year: "2024" },
    { category: "Press", title: "\u201c一位用手思考的艺术家\u201d", subtitle: "艺术界 LEAP / 专题", year: "2023" },
    { category: "Press", title: "\u201c静默的力量\u201d", subtitle: "画刊 / 评论", year: "2023" },
    { category: "Press", title: "\u201c当石头开始说话\u201d", subtitle: "艺术当代 / 评论", year: "2022" },
  ],
  en: [
    { category: "Education", title: "China Academy of Art", subtitle: "School of Intermedia Arts / MFA", year: "2019 - 2022" },
    { category: "Education", title: "Central Academy of Fine Arts", subtitle: "Department of Photography / BFA", year: "2015 - 2019" },
    { category: "Employment", title: "Independent Studio", subtitle: "Visual Art Practice / Shanghai", year: "2022 - Present" },
    { category: "Employment", title: "BLANKSPACE Gallery", subtitle: "Artist-in-Residence / Jingdezhen", year: "2023 (3 months)" },
    { category: "Employment", title: "Yuan Art Museum", subtitle: "Curatorial Assistant / Chongqing", year: "2021 - 2022" },
    { category: "Exhibition", title: "\u201cEarth and Poetry\u201d Solo Exhibition", subtitle: "BLANKSPACE Gallery / Shanghai", year: "2024" },
    { category: "Exhibition", title: "\u201cThe Texture of Time\u201d Group Show", subtitle: "Contemporary Art Museum / Hangzhou", year: "2023" },
    { category: "Exhibition", title: "\u201cNatural Writing\u201d Duo Exhibition", subtitle: "Pearl Lam Galleries / Hong Kong", year: "2023" },
    { category: "Exhibition", title: "\u201cEmerging Perspectives\u201d Annual Show", subtitle: "Today Art Museum / Beijing", year: "2022" },
    { category: "Awards", title: "Young Artist Fellowship Program", subtitle: "Selected Artist / Nominee", year: "2024" },
    { category: "Awards", title: "Three Shadows Photography Award", subtitle: "Shortlisted / Curator's Special Mention", year: "2023" },
    { category: "Awards", title: "New Talent Photography Award", subtitle: "TOP 20", year: "2022" },
    { category: "Press", title: "\u201cFinding the Divine in the Everyday\u201d", subtitle: "ArtReview Asia / Interview", year: "2024" },
    { category: "Press", title: "\u201cAn Artist Who Thinks With Her Hands\u201d", subtitle: "LEAP / Feature", year: "2023" },
    { category: "Press", title: "\u201cThe Power of Silence\u201d", subtitle: "Art Magazine / Review", year: "2023" },
    { category: "Press", title: "\u201cWhen Stones Begin to Speak\u201d", subtitle: "Art China / Review", year: "2022" },
  ],
};

export default function RightColumn() {
  const { language } = useLanguage();
  const { isAdmin } = useAuth();
  const artFrameRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  const utils = trpc.useUtils();

  const { data: cvDataDb } = trpc.cv.list.useQuery();
  const createCv = trpc.cv.create.useMutation({ onSuccess: () => utils.cv.list.invalidate() });
  const updateCv = trpc.cv.update.useMutation({ onSuccess: () => utils.cv.list.invalidate() });
  const deleteCv = trpc.cv.delete.useMutation({ onSuccess: () => utils.cv.list.invalidate() });

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState({ category: "", zhTitle: "", zhSubtitle: "", enTitle: "", enSubtitle: "", year: "" });
  const [isAdding, setIsAdding] = useState(false);

  useEffect(() => {
    if (!artFrameRef.current || !imageRef.current) return;
    const tween = gsap.to(imageRef.current, {
      y: -40,
      ease: "none",
      scrollTrigger: {
        trigger: artFrameRef.current,
        start: "top bottom",
        end: "bottom top",
        scrub: true,
      },
    });
    return () => {
      if (tween.scrollTrigger) tween.scrollTrigger.kill();
      tween.kill();
    };
  }, []);

  // Transform DB entries to grouped format
  const dbItems = cvDataDb ?? [];
  const useDb = dbItems.length > 0;

  const items = useDb
    ? dbItems.map((e) => ({
        category: e.category,
        title: language === "zh" ? e.zhTitle : e.enTitle,
        subtitle: language === "zh" ? (e.zhSubtitle || undefined) : (e.enSubtitle || undefined),
        year: e.year,
        id: e.id,
      }))
    : fallbackCvData[language].map((e, i) => ({ ...e, id: i }));

  const sections = items.reduce<Record<string, typeof items>>((acc, item) => {
    if (!acc[item.category]) acc[item.category] = [];
    acc[item.category].push(item);
    return acc;
  }, {});

  const sectionOrder = ["Education", "Employment", "Exhibition", "Awards", "Press"];

  const startEdit = (item: (typeof items)[0]) => {
    const dbItem = dbItems.find((d) => d.id === item.id);
    if (dbItem) {
      setEditForm({
        category: dbItem.category,
        zhTitle: dbItem.zhTitle,
        zhSubtitle: dbItem.zhSubtitle || "",
        enTitle: dbItem.enTitle,
        enSubtitle: dbItem.enSubtitle || "",
        year: dbItem.year,
      });
      setEditingId(item.id);
      setIsAdding(false);
    }
  };

  const startAdd = () => {
    setEditForm({ category: "Education", zhTitle: "", zhSubtitle: "", enTitle: "", enSubtitle: "", year: "" });
    setIsAdding(true);
    setEditingId(null);
  };

  const saveEdit = () => {
    if (isAdding) {
      createCv.mutate({ ...editForm, sortOrder: dbItems.length + 1 });
    } else if (editingId !== null) {
      updateCv.mutate({ id: editingId, ...editForm });
    }
    setIsAdding(false);
    setEditingId(null);
  };

  return (
    <aside
      className="sticky top-0 h-screen overflow-y-auto"
      style={{ width: "25%", minWidth: "280px" }}
    >
      <div className="p-6 pb-24">
        <div className="flex items-center justify-between">
          <h2 style={{ fontSize: "12px", fontWeight: 400, letterSpacing: "0.05em", textTransform: "uppercase", color: "var(--text-grey)", marginBottom: "48px", lineHeight: 1.4 }}>
            CV (ARCHIVE)
          </h2>
          {isAdmin && (
            <button onClick={startAdd} style={{ fontSize: "10px", color: "var(--text-grey)", background: "none", border: "none", cursor: "pointer", fontFamily: "'Space Mono', monospace", marginBottom: "48px" }}>
              + ADD
            </button>
          )}
        </div>

        <AvatarSection />

        {(isAdding || editingId !== null) && (
          <div className="mb-6 p-3" style={{ border: "1px solid var(--border-light)" }}>
            <div className="space-y-2">
              {[
                { key: "category", ph: "Category" },
                { key: "zhTitle", ph: "ZH Title" },
                { key: "zhSubtitle", ph: "ZH Subtitle" },
                { key: "enTitle", ph: "EN Title" },
                { key: "enSubtitle", ph: "EN Subtitle" },
                { key: "year", ph: "Year" },
              ].map((f) => (
                <input
                  key={f.key}
                  placeholder={f.ph}
                  value={editForm[f.key as keyof typeof editForm]}
                  onChange={(e) => setEditForm({ ...editForm, [f.key]: e.target.value })}
                  style={{
                    width: "100%",
                    fontSize: "11px",
                    padding: "6px 8px",
                    border: "1px solid var(--border-light)",
                    outline: "none",
                    background: "transparent",
                    color: "var(--text-charcoal)",
                    fontFamily: "'Space Mono', monospace",
                  }}
                />
              ))}
            </div>
            <div className="flex gap-2 mt-2">
              <button onClick={saveEdit} style={{ fontSize: "10px", padding: "3px 10px", background: "#FFFFFF", color: "#1A1A1A", border: "none", cursor: "pointer", fontFamily: "'Space Mono', monospace" }}>SAVE</button>
              <button onClick={() => { setIsAdding(false); setEditingId(null); }} style={{ fontSize: "10px", padding: "3px 10px", background: "none", border: "1px solid var(--border-light)", cursor: "pointer", fontFamily: "'Space Mono', monospace", color: "var(--text-charcoal)" }}>CANCEL</button>
            </div>
          </div>
        )}

        {sectionOrder.map((category) => {
          const sectionItems = sections[category];
          if (!sectionItems || sectionItems.length === 0) return null;
          return (
            <div key={category} style={{ borderBottom: "1px solid var(--border-light)", paddingBottom: "16px", marginBottom: "16px" }}>
              {sectionItems.map((item, idx) => (
                <div key={item.id} className="flex gap-4" style={{ marginBottom: idx < sectionItems.length - 1 ? "16px" : "0" }}>
                  {idx === 0 && <span style={{ fontSize: "12px", fontWeight: 400, color: "var(--text-charcoal)", lineHeight: 1.6, flexShrink: 0, width: "80px" }}>{category}</span>}
                  {idx > 0 && <span style={{ width: "80px", flexShrink: 0 }} />}
                  <div className="flex-1 relative group">
                    <p style={{ fontSize: "12px", lineHeight: 1.6, color: "var(--text-charcoal)", whiteSpace: "pre-line" }}>{item.title}</p>
                    {item.subtitle && <p style={{ fontSize: "12px", lineHeight: 1.6, color: "var(--text-grey)", whiteSpace: "pre-line" }}>{item.subtitle}</p>}
                    <p style={{ fontSize: "12px", lineHeight: 1.6, color: "var(--text-charcoal)" }}>{item.year}</p>
                    {isAdmin && useDb && (
                      <div className="flex gap-2 mt-1">
                        <button onClick={() => startEdit(item)} style={{ fontSize: "9px", color: "var(--text-grey)", background: "none", border: "none", cursor: "pointer", fontFamily: "'Space Mono', monospace" }}>EDIT</button>
                        <button onClick={() => { if (confirm("Delete?")) deleteCv.mutate({ id: item.id }); }} style={{ fontSize: "9px", color: "#E74C3C", background: "none", border: "none", cursor: "pointer", fontFamily: "'Space Mono', monospace" }}>DEL</button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          );
        })}

        <p style={{ fontSize: "11px", color: "var(--text-grey)", marginTop: "32px" }}>Last Updated 2024.12</p>
      </div>
    </aside>
  );
}

function AvatarSection() {
  const { isAdmin } = useAuth();
  const utils = trpc.useUtils();
  const artFrameRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  const [editingAvatar, setEditingAvatar] = useState(false);

  const { data: settings } = trpc.settings.get.useQuery();
  const updateSettings = trpc.settings.update.useMutation({
    onSuccess: () => utils.settings.get.invalidate(),
  });

  const avatarUrl = settings?.avatarImage || "/images/portrait.jpg";

  useEffect(() => {
    if (!artFrameRef.current || !imageRef.current) return;
    const tween = gsap.to(imageRef.current, {
      y: -40,
      ease: "none",
      scrollTrigger: {
        trigger: artFrameRef.current,
        start: "top bottom",
        end: "bottom top",
        scrub: true,
      },
    });
    return () => {
      if (tween.scrollTrigger) tween.scrollTrigger.kill();
      tween.kill();
    };
  }, [avatarUrl]);

  return (
    <div className="mb-10">
      <div ref={artFrameRef} style={{ border: "1px solid var(--border-light)", boxShadow: "0px 4px 15px rgba(0,0,0,0.08)", overflow: "hidden", aspectRatio: "1 / 1", width: "100%" }}>
        <img ref={imageRef} src={avatarUrl} alt="Portrait" className="block" style={{ width: "100%", height: "100%", objectFit: "cover" }} loading="lazy" />
      </div>
      {isAdmin && (
        <div className="mt-2">
          {editingAvatar ? (
            <div className="p-2" style={{ border: "1px solid var(--border-light)" }}>
              <ImageUpload
                value={avatarUrl}
                onChange={(url) => updateSettings.mutate({ avatarImage: url })}
                label="Avatar"
                variant="light"
              />
              <button
                onClick={() => setEditingAvatar(false)}
                style={{ fontSize: "10px", marginTop: "8px", padding: "3px 10px", background: "none", border: "1px solid var(--border-light)", cursor: "pointer", fontFamily: "'Space Mono', monospace", color: "var(--text-charcoal)" }}
              >
                CLOSE
              </button>
            </div>
          ) : (
            <button
              onClick={() => setEditingAvatar(true)}
              style={{ fontSize: "10px", color: "var(--text-grey)", background: "none", border: "none", cursor: "pointer", fontFamily: "'Space Mono', monospace" }}
            >
              EDIT AVATAR
            </button>
          )}
        </div>
      )}
    </div>
  );
}
