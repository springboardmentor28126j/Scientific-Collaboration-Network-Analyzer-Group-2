import { useState } from "react";
import ShaderCanvas from "./ShaderCanvas";
import { useLanguage } from "../contexts/LanguageContext";
import { useAuth } from "@/hooks/useAuth";
import { trpc } from "@/providers/trpc";

interface LeftColumnProps {
  onContactClick: () => void;
}

const fallbackText = {
  zh: "陈林 / Chen Lin，视觉艺术家与写作者，现居上海。创作围绕自然材料、摄影工艺与手工技艺展开，试图在最朴素的物质中发现被日常所遮蔽的诗意。从托斯卡纳的石灰岩到景德镇的赤陶，从阿尔卑斯山的冰川溪流到欧洲花园里风化百年的雕塑——我相信记录本身就是创作，而凝视是一种需要反复练习的能力。曾在空白画廊担任驻留艺术家，作品被国内外多个美术馆与私人收藏。闲暇时经营一本植物手账，用不同季节的墨水记录那些容易被遗忘的微小瞬间。",
  en: "Chen Lin, visual artist and writer, based in Shanghai. My practice revolves around natural materials, photographic processes, and handmade crafts \u2014 seeking the poetry concealed by the everyday within the most humble substances. From the limestone of Tuscany to the terracotta of Jingdezhen, from glacial streams in the Alps to century-weathered sculptures in European gardens \u2014 I believe that recording is itself a form of creation, and that the act of looking is a skill that requires repeated practice. Former artist-in-residence at BLANKSPACE Gallery, with works collected by museums and private collectors at home and abroad. In my spare time, I keep a botanical journal, using inks of different seasons to record those tiny moments easily forgotten.",
};

export default function LeftColumn({ onContactClick }: LeftColumnProps) {
  const { language } = useLanguage();
  const { isAdmin } = useAuth();
  const utils = trpc.useUtils();

  const { data: bio } = trpc.profile.get.useQuery();
  const updateBio = trpc.profile.update.useMutation({
    onSuccess: () => utils.profile.get.invalidate(),
  });

  const [isEditing, setIsEditing] = useState(false);
  const [editZh, setEditZh] = useState("");
  const [editEn, setEditEn] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [editInstagram, setEditInstagram] = useState("");

  const profileText = {
    zh: bio?.zhText || fallbackText.zh,
    en: bio?.enText || fallbackText.en,
  };
  const email = bio?.email || "lin.chen@studio.com";
  const instagram = bio?.instagram || "https://instagram.com";

  const startEdit = () => {
    setEditZh(profileText.zh);
    setEditEn(profileText.en);
    setEditEmail(email);
    setEditInstagram(instagram);
    setIsEditing(true);
  };

  const saveEdit = () => {
    updateBio.mutate({ zhText: editZh, enText: editEn, email: editEmail, instagram: editInstagram });
    setIsEditing(false);
  };

  const inputStyle = {
    width: "100%",
    background: "transparent",
    border: "1px solid rgba(255,255,255,0.3)",
    padding: "6px 8px",
    fontSize: "11px",
    color: "#FFFFFF",
    outline: "none" as const,
    resize: "vertical" as const,
    fontFamily: "'Space Mono', monospace",
  };

  const labelStyle = {
    fontSize: "10px",
    color: "rgba(255,255,255,0.6)",
    display: "block" as const,
    marginBottom: "4px",
  };

  return (
    <aside
      className="sticky top-0 h-screen flex flex-col"
      style={{
        width: "21%",
        minWidth: "240px",
        borderRight: "1px solid var(--border-light)",
        position: "relative",
      }}
    >
      <ShaderCanvas />

      <div
        className="relative z-10 flex flex-col h-full p-6"
        style={{ mixBlendMode: "difference" }}
      >
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <h2
              style={{
                fontSize: "12px",
                fontWeight: 400,
                letterSpacing: "0.05em",
                textTransform: "uppercase",
                color: "#FFFFFF",
                marginBottom: "16px",
                lineHeight: 1.4,
              }}
            >
              PROFILE (CONTACT)
            </h2>
            {isAdmin && !isEditing && (
              <button
                onClick={startEdit}
                style={{
                  fontSize: "10px",
                  color: "rgba(255,255,255,0.6)",
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  fontFamily: "'Space Mono', monospace",
                  marginBottom: "16px",
                }}
              >
                EDIT
              </button>
            )}
          </div>

          {isEditing ? (
            <div className="space-y-2">
              <div>
                <label style={labelStyle}>EMAIL</label>
                <input
                  type="text"
                  value={editEmail}
                  onChange={(e) => setEditEmail(e.target.value)}
                  style={{ ...inputStyle, resize: "none" }}
                />
              </div>
              <div>
                <label style={labelStyle}>INSTAGRAM URL</label>
                <input
                  type="text"
                  value={editInstagram}
                  onChange={(e) => setEditInstagram(e.target.value)}
                  style={{ ...inputStyle, resize: "none" }}
                />
              </div>
            </div>
          ) : (
            <div className="space-y-1">
              <a
                href={`mailto:${email}`}
                style={{
                  fontSize: "12px",
                  color: "#FFFFFF",
                  textDecoration: "underline",
                  textUnderlineOffset: "3px",
                  display: "block",
                  lineHeight: 1.6,
                }}
              >
                {email}
              </a>
              <a
                href={instagram}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  fontSize: "12px",
                  color: "#FFFFFF",
                  textDecoration: "underline",
                  textUnderlineOffset: "3px",
                  display: "block",
                  lineHeight: 1.6,
                }}
              >
                Instagram
              </a>
            </div>
          )}
        </div>

        <div style={{ flex: 1, minHeight: 0, overflowY: "auto" }}>
          {isEditing ? (
            <div className="space-y-3">
              <div>
                <label style={labelStyle}>ZH</label>
                <textarea
                  value={editZh}
                  onChange={(e) => setEditZh(e.target.value)}
                  rows={8}
                  style={inputStyle}
                />
              </div>
              <div>
                <label style={labelStyle}>EN</label>
                <textarea
                  value={editEn}
                  onChange={(e) => setEditEn(e.target.value)}
                  rows={8}
                  style={inputStyle}
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={saveEdit}
                  style={{
                    fontSize: "10px",
                    color: "#1A1A1A",
                    background: "#FFFFFF",
                    border: "none",
                    padding: "4px 12px",
                    cursor: "pointer",
                    fontFamily: "'Space Mono', monospace",
                  }}
                >
                  SAVE
                </button>
                <button
                  onClick={() => setIsEditing(false)}
                  style={{
                    fontSize: "10px",
                    color: "#FFFFFF",
                    background: "rgba(255,255,255,0.2)",
                    border: "none",
                    padding: "4px 12px",
                    cursor: "pointer",
                    fontFamily: "'Space Mono', monospace",
                  }}
                >
                  CANCEL
                </button>
              </div>
            </div>
          ) : (
            <p
              style={{
                fontSize: "12px",
                lineHeight: 1.8,
                color: "#FFFFFF",
                maxWidth: "240px",
                textAlign: "justify",
              }}
            >
              {profileText[language]}
            </p>
          )}
        </div>

        <div className="mt-auto" style={{ flexShrink: 0, paddingBottom: "24px" }}>
          <button
            onClick={onContactClick}
            style={{
              fontSize: "12px",
              fontWeight: 400,
              letterSpacing: "0.05em",
              textTransform: "uppercase",
              color: "#FFFFFF",
              background: "none",
              border: "none",
              cursor: "pointer",
              padding: 0,
              textDecoration: "none",
              transition: "opacity 0.2s ease",
            }}
            onMouseEnter={(e) => {
              (e.target as HTMLElement).style.opacity = "0.6";
            }}
            onMouseLeave={(e) => {
              (e.target as HTMLElement).style.opacity = "1";
            }}
          >
            CONTACT
          </button>
        </div>
      </div>
    </aside>
  );
}
