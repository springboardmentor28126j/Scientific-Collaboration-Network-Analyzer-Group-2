import { useParams, useNavigate, useSearchParams } from "react-router";
import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { useLanguage } from "../contexts/LanguageContext";
import { useAuth } from "@/hooks/useAuth";
import { trpc } from "@/providers/trpc";
import type { BlogPost } from "../data/blogPosts";
import ImageUpload from "./ImageUpload";

interface PostDetailProps {
  posts: BlogPost[];
}

export default function PostDetail({ posts }: PostDetailProps) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const contentRef = useRef<HTMLDivElement>(null);
  const { language } = useLanguage();
  const { isAdmin } = useAuth();
  const utils = trpc.useUtils();

  const isEditMode = searchParams.get("mode") === "edit" && isAdmin;

  const post = posts.find((p) => p.id === Number(id));

  const updatePost = trpc.blog.update.useMutation({
    onSuccess: () => {
      utils.blog.list.invalidate();
      navigate(`/post/${id}`);
    },
  });

  const [editForm, setEditForm] = useState({
    year: "", image: "", zhTitle: "", zhSubtitle: "", zhCollection: "",
    zhContent: "", zhDetailContent: "", enTitle: "", enSubtitle: "",
    enCollection: "", enContent: "", enDetailContent: "",
  });

  useEffect(() => {
    if (post && isEditMode) {
      setEditForm({
        year: post.year, image: post.image, zhTitle: post.zh.title,
        zhSubtitle: post.zh.subtitle, zhCollection: post.zh.collection,
        zhContent: post.zh.content, zhDetailContent: post.zh.detailContent,
        enTitle: post.en.title, enSubtitle: post.en.subtitle,
        enCollection: post.en.collection, enContent: post.en.content,
        enDetailContent: post.en.detailContent,
      });
    }
  }, [post, isEditMode]);

  useEffect(() => {
    if (contentRef.current && !isEditMode) {
      gsap.fromTo(
        contentRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" },
      );
    }
  }, [id, isEditMode]);

  const backText = language === "zh" ? "返回首页" : "Back to home";
  const notFoundText = language === "zh" ? "文章不存在" : "Article not found";
  const editThisText = language === "zh" ? "编辑此文章" : "Edit this post";
  const viewText = language === "zh" ? "查看文章" : "View article";

  const inputBase = {
    width: "100%",
    background: "#2A2A2A",
    border: "1px solid #444",
    borderRadius: "2px",
    padding: "10px 12px",
    fontSize: "13px",
    color: "#FFFFFF",
    fontFamily: "'Space Mono', monospace",
    outline: "none",
  };

  const labelStyle = {
    fontSize: "11px",
    color: "rgba(255,255,255,0.6)",
    display: "block" as const,
    marginBottom: "6px",
    fontFamily: "'Space Mono', monospace",
    letterSpacing: "0.05em",
  };

  if (!post) {
    return (
      <div className="flex items-center justify-center" style={{ height: "100vh", backgroundColor: "var(--bg-warm-white)" }}>
        <div className="text-center">
          <p style={{ fontSize: "14px", color: "var(--text-grey)" }}>{notFoundText}</p>
          <button onClick={() => navigate("/")} style={{ marginTop: "16px", fontSize: "12px", color: "var(--text-charcoal)", background: "none", border: "none", cursor: "pointer", textDecoration: "underline", textUnderlineOffset: "3px" }}>
            {backText}
          </button>
        </div>
      </div>
    );
  }

  // EDIT MODE
  if (isEditMode) {
    return (
      <div className="min-h-screen" style={{ backgroundColor: "#1A1A1A" }}>
        <header className="fixed top-0 left-0 right-0 flex items-center justify-between px-6" style={{ height: "40px", zIndex: 50, backgroundColor: "#1A1A1A", borderBottom: "1px solid #333" }}>
          <button onClick={() => navigate("/")} style={{ fontSize: "12px", fontWeight: 400, letterSpacing: "0.05em", textTransform: "uppercase", color: "#FFFFFF", background: "none", border: "none", cursor: "pointer" }}>
            NEURAL ATELIER (BLOG)
          </button>
          <div className="flex items-center gap-4">
            <button onClick={() => navigate(`/post/${post.id}`)} style={{ fontSize: "11px", fontFamily: "'Space Mono', monospace", color: "rgba(255,255,255,0.6)", background: "none", border: "none", cursor: "pointer" }}>
              {viewText}
            </button>
            <button onClick={() => navigate("/")} style={{ fontSize: "11px", fontFamily: "'Space Mono', monospace", color: "#FFFFFF", background: "none", border: "none", cursor: "pointer" }}>
              {language === "zh" ? "关闭" : "Close"}
            </button>
          </div>
        </header>

        <div className="mx-auto" style={{ maxWidth: "720px", padding: "80px 24px 80px" }}>
          <div className="flex items-center justify-between mb-8">
            <h1 style={{ fontSize: "16px", fontWeight: 400, color: "#FFFFFF", letterSpacing: "0.05em" }}>{editThisText}</h1>
          </div>

          <div className="space-y-5">
            <div>
              <label style={labelStyle}>Year</label>
              <input type="text" value={editForm.year} onChange={(e) => setEditForm({ ...editForm, year: e.target.value })} style={inputBase} />
            </div>

            <div>
              <ImageUpload
                value={editForm.image}
                onChange={(url) => setEditForm({ ...editForm, image: url })}
                label="Image"
              />
            </div>

            <div style={{ borderTop: "1px solid #333", paddingTop: "20px" }}>
              <h3 style={{ fontSize: "12px", color: "rgba(255,255,255,0.5)", marginBottom: "16px", letterSpacing: "0.05em", fontFamily: "'Space Mono', monospace" }}>中文内容</h3>
              <div className="space-y-4">
                <div><label style={labelStyle}>标题</label><input type="text" value={editForm.zhTitle} onChange={(e) => setEditForm({ ...editForm, zhTitle: e.target.value })} style={inputBase} /></div>
                <div><label style={labelStyle}>副标题</label><input type="text" value={editForm.zhSubtitle} onChange={(e) => setEditForm({ ...editForm, zhSubtitle: e.target.value })} style={inputBase} /></div>
                <div><label style={labelStyle}>分类</label><input type="text" value={editForm.zhCollection} onChange={(e) => setEditForm({ ...editForm, zhCollection: e.target.value })} style={inputBase} /></div>
                <div><label style={labelStyle}>摘要</label><textarea value={editForm.zhContent} onChange={(e) => setEditForm({ ...editForm, zhContent: e.target.value })} rows={3} style={{ ...inputBase, resize: "vertical" }} /></div>
                <div><label style={labelStyle}>详细内容</label><textarea value={editForm.zhDetailContent} onChange={(e) => setEditForm({ ...editForm, zhDetailContent: e.target.value })} rows={8} style={{ ...inputBase, resize: "vertical" }} /></div>
              </div>
            </div>

            <div style={{ borderTop: "1px solid #333", paddingTop: "20px" }}>
              <h3 style={{ fontSize: "12px", color: "rgba(255,255,255,0.5)", marginBottom: "16px", letterSpacing: "0.05em", fontFamily: "'Space Mono', monospace" }}>English Content</h3>
              <div className="space-y-4">
                <div><label style={labelStyle}>Title</label><input type="text" value={editForm.enTitle} onChange={(e) => setEditForm({ ...editForm, enTitle: e.target.value })} style={inputBase} /></div>
                <div><label style={labelStyle}>Subtitle</label><input type="text" value={editForm.enSubtitle} onChange={(e) => setEditForm({ ...editForm, enSubtitle: e.target.value })} style={inputBase} /></div>
                <div><label style={labelStyle}>Collection</label><input type="text" value={editForm.enCollection} onChange={(e) => setEditForm({ ...editForm, enCollection: e.target.value })} style={inputBase} /></div>
                <div><label style={labelStyle}>Summary</label><textarea value={editForm.enContent} onChange={(e) => setEditForm({ ...editForm, enContent: e.target.value })} rows={3} style={{ ...inputBase, resize: "vertical" }} /></div>
                <div><label style={labelStyle}>Detail Content</label><textarea value={editForm.enDetailContent} onChange={(e) => setEditForm({ ...editForm, enDetailContent: e.target.value })} rows={8} style={{ ...inputBase, resize: "vertical" }} /></div>
              </div>
            </div>

            <div className="flex gap-3 pt-4" style={{ borderTop: "1px solid #333" }}>
              <button
                onClick={() => updatePost.mutate({ id: post.id, ...editForm, sortOrder: post.id })}
                disabled={updatePost.isPending}
                style={{ flex: 1, padding: "12px", fontSize: "12px", fontFamily: "'Space Mono', monospace", color: "#1A1A1A", background: "#FFFFFF", border: "none", borderRadius: "2px", cursor: updatePost.isPending ? "wait" : "pointer", opacity: updatePost.isPending ? 0.7 : 1, letterSpacing: "0.05em" }}
              >
                {updatePost.isPending ? (language === "zh" ? "保存中..." : "Saving...") : (language === "zh" ? "保存" : "SAVE")}
              </button>
              <button
                onClick={() => navigate(`/post/${post.id}`)}
                style={{ flex: 1, padding: "12px", fontSize: "12px", fontFamily: "'Space Mono', monospace", color: "#FFFFFF", background: "rgba(255,255,255,0.1)", border: "none", borderRadius: "2px", cursor: "pointer", letterSpacing: "0.05em" }}
              >
                {language === "zh" ? "取消" : "CANCEL"}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // VIEW MODE
  const content = post[language];
  const paragraphs = content.detailContent.split("\n\n");

  return (
    <div className="min-h-screen" style={{ backgroundColor: "var(--bg-warm-white)" }}>
      <header className="fixed top-0 left-0 right-0 flex items-center justify-between px-6" style={{ height: "40px", zIndex: 50, backgroundColor: "var(--bg-warm-white)", borderBottom: "1px solid var(--border-light)" }}>
        <button onClick={() => navigate("/")} style={{ fontSize: "12px", fontWeight: 400, letterSpacing: "0.05em", textTransform: "uppercase", color: "var(--text-charcoal)", background: "none", border: "none", cursor: "pointer" }}>
          NEURAL ATELIER (BLOG)
        </button>
        <div className="flex items-center gap-4">
          {isAdmin && (
            <button onClick={() => navigate(`/post/${post.id}?mode=edit`)} style={{ fontSize: "11px", fontFamily: "'Space Mono', monospace", color: "var(--text-grey)", background: "none", border: "none", cursor: "pointer" }}>
              EDIT
            </button>
          )}
          <button onClick={() => navigate("/")} style={{ fontSize: "12px", fontFamily: "'Space Mono', monospace", color: "var(--text-charcoal)", background: "none", border: "none", cursor: "pointer" }}>
            {language === "zh" ? "关闭" : "Close"}
          </button>
        </div>
      </header>

      <div ref={contentRef} className="mx-auto" style={{ maxWidth: "680px", padding: "80px 24px 80px" }}>
        <div className="mb-8" style={{ border: "1px solid var(--border-light)" }}>
          <img src={post.image} alt={content.title} className="w-full h-auto block" loading="eager" />
        </div>

        <div className="flex items-center gap-2 mb-4">
          <span style={{ fontSize: "11px", color: "var(--text-grey)" }}>{post.year}</span>
          <span style={{ fontSize: "11px", color: "var(--border-light)" }}> / </span>
          <span style={{ fontSize: "11px", color: "var(--text-grey)" }}>{content.collection}</span>
        </div>

        <h1 style={{ fontSize: "22px", fontWeight: 400, lineHeight: 1.3, color: "var(--text-charcoal)", marginBottom: "6px" }}>{content.title}</h1>
        <p style={{ fontSize: "13px", color: "var(--text-grey)", lineHeight: 1.5, marginBottom: "32px" }}>{content.subtitle}</p>

        <div style={{ borderTop: "1px solid var(--border-light)", marginBottom: "32px" }} />

        <div className="space-y-5">
          {paragraphs.map((para, idx) => (
            <p key={idx} style={{ fontSize: "13px", lineHeight: 1.8, color: "var(--text-charcoal)", whiteSpace: "pre-line" }}>{para}</p>
          ))}
        </div>

        <div style={{ borderTop: "1px solid var(--border-light)", marginTop: "48px", paddingTop: "24px" }}>
          <button onClick={() => navigate("/")} style={{ fontSize: "12px", color: "var(--text-charcoal)", background: "none", border: "none", cursor: "pointer", textDecoration: "underline", textUnderlineOffset: "3px" }}>
            {language === "zh" ? "返回全部文章" : "Back to all articles"}
          </button>
        </div>
      </div>
    </div>
  );
}
