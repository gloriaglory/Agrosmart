import { API_URL, authHeaders } from "../config";
import PageHero from "../components/PageHero";
import learnHeroImg from "../assets/images/farm2.jpeg";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Comments from "../components/Comments";
import { useUser } from "../UserContext";

const CONTENTS_API = `${API_URL}/api/education/contents/`;

interface Content {
  id: number;
  title: string;
  type: "article" | "youtube";
  url_or_text: string;
  thumbnail?: string;
  author: { id: number; username: string; name: string } | null;
  status: "approved" | "pending" | "rejected";
  moderation_note: string;
  comments_count: number;
}

const emptyForm = {
  title: "",
  type: "article" as "article" | "youtube",
  url_or_text: "",
};

// Turn a DRF error response into one readable message
const errorMessage = (data: unknown) => {
  if (!data || typeof data !== "object")
    return "Could not publish. Please try again.";
  return Object.values(data as Record<string, unknown>)
    .flat()
    .map(String)
    .join(" ");
};

export default function Education() {
  const { user } = useUser();
  const [contents, setContents] = useState<Content[]>([]);
  const [newContent, setNewContent] = useState(emptyForm);
  const [thumbnailFile, setThumbnailFile] = useState<File | null>(null);
  const [activeContent, setActiveContent] = useState<Content | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  // Only the author or an admin can delete a post
  const canManage = (c: Content) =>
    !!user && (user.is_staff || c.author?.id === user.id);

  const fetchContents = useCallback(async () => {
    const res = await fetch(CONTENTS_API, { headers: authHeaders() });
    if (res.ok) setContents(await res.json());
  }, []);

  useEffect(() => {
    fetchContents();
  }, [fetchContents, user]);

  const closeForm = () => {
    setShowForm(false);
    setFormError(null);
  };

  const addContent = async () => {
    setFormError(null);
    if (!newContent.title.trim() || !newContent.url_or_text.trim()) {
      setFormError("Add a title and the article text or YouTube link.");
      return;
    }

    const formData = new FormData();
    formData.append("title", newContent.title);
    formData.append("type", newContent.type);
    formData.append("url_or_text", newContent.url_or_text);
    if (thumbnailFile && newContent.type === "article") {
      formData.append("thumbnail", thumbnailFile);
    }

    setPublishing(true);
    try {
      const res = await fetch(CONTENTS_API, {
        method: "POST",
        headers: authHeaders(),
        body: formData,
      });
      const data = await res.json().catch(() => null);
      if (!res.ok) {
        setFormError(errorMessage(data));
        return;
      }
      await fetchContents();
      setNewContent(emptyForm);
      setThumbnailFile(null);
      closeForm();
      setNotice(
        data?.status === "approved"
          ? "Your post is published."
          : "Thanks! Your post was submitted and will appear once an admin approves it.",
      );
    } finally {
      setPublishing(false);
    }
  };

  const deleteContent = async (id: number) => {
    if (!window.confirm("Delete this post and its comments?")) return;
    const res = await fetch(`${CONTENTS_API}${id}/`, {
      method: "DELETE",
      headers: authHeaders(),
    });
    if (res.ok) {
      await fetchContents();
      setActiveContent(null);
    }
  };

  // Keep the card's comment count in sync with the open post
  const activeId = activeContent?.id;
  const handleCountChange = useCallback(
    (count: number) =>
      setContents((list) =>
        list.map((c) =>
          c.id === activeId ? { ...c, comments_count: count } : c,
        ),
      ),
    [activeId],
  );

  const embedUrl = (url: string) => url.replace("watch?v=", "embed/");

  return (
    <div>
      <PageHero
        image={learnHeroImg}
        title="Agriculture Education"
        subtitle="Articles and videos on better farming practices."
      >
        {user ? (
          <button
            onClick={() => {
              setNotice(null);
              setShowForm(true);
            }}
            className="btn-primary"
          >
            Add content
          </button>
        ) : (
          <Link
            to="/login"
            state={{ from: "/education" }}
            className="btn-secondary"
          >
            Log in to share content
          </Link>
        )}
      </PageHero>
      <div className="page">
        {notice && (
          <p className="alert-success mb-6 flex items-center justify-between gap-4">
            {notice}
            <button
              onClick={() => setNotice(null)}
              className="text-xs font-semibold"
            >
              Dismiss
            </button>
          </p>
        )}
        {contents.length === 0 && (
          <div className="card p-10 text-center">
            <p className="font-medium text-stone-900">No content yet</p>
            <p className="muted mt-1">Articles and videos will appear here.</p>
          </div>
        )}

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {contents.map((c) => (
            <div
              key={c.id}
              className="card card-hover flex flex-col overflow-hidden"
            >
              {c.type === "article" ? (
                c.thumbnail ? (
                  <img
                    src={c.thumbnail}
                    alt={c.title}
                    className="h-44 w-full object-cover"
                  />
                ) : (
                  <div className="flex h-44 items-center justify-center bg-stone-100 text-sm text-stone-400">
                    Article
                  </div>
                )
              ) : (
                <iframe
                  className="aspect-video w-full"
                  src={embedUrl(c.url_or_text)}
                  allowFullScreen
                  title={c.title}
                />
              )}
              <div
                onClick={() => setActiveContent(c)}
                className="flex flex-1 cursor-pointer flex-col p-4"
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter") setActiveContent(c);
                }}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="stat-label">
                    {c.type === "article" ? "Article" : "Video"}
                  </span>
                  {c.status !== "approved" && (
                    <span
                      className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${
                        c.status === "pending"
                          ? "bg-amber-100 text-amber-800"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {c.status === "pending" ? "Pending review" : "Rejected"}
                    </span>
                  )}
                </div>
                <h3 className="mt-1 font-semibold text-stone-900">{c.title}</h3>
                {c.author && (
                  <p className="mt-0.5 text-xs text-stone-500">
                    by {c.author.username}
                  </p>
                )}
                {c.moderation_note && (
                  <p className="mt-2 rounded-lg bg-stone-50 px-2.5 py-1.5 text-xs text-stone-600">
                    {c.moderation_note}
                  </p>
                )}
                {c.type === "article" && (
                  <p className="mt-1 text-sm text-stone-600 line-clamp-3">
                    {c.url_or_text}
                  </p>
                )}
                <div className="mt-auto flex items-center justify-between pt-4 text-sm">
                  <span className="text-stone-500">
                    {c.comments_count} comment
                    {c.comments_count === 1 ? "" : "s"}
                  </span>
                  {canManage(c) && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteContent(c.id);
                      }}
                      className="text-red-600 hover:underline"
                      aria-label={`Delete ${c.title}`}
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {activeContent && (
          <div
            className="modal-backdrop"
            onClick={() => setActiveContent(null)}
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
          >
            <div
              className="modal flex max-h-[92vh] max-w-6xl flex-col overflow-hidden p-0 md:h-[85vh] md:flex-row"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Post */}
              <div className="max-h-[40vh] shrink-0 overflow-y-auto bg-stone-50 md:max-h-none md:w-3/5 md:shrink">
                {activeContent.type === "youtube" ? (
                  <div className="flex h-full items-center bg-stone-900">
                    <iframe
                      className="aspect-video w-full"
                      src={embedUrl(activeContent.url_or_text)}
                      allowFullScreen
                      title={activeContent.title}
                    />
                  </div>
                ) : (
                  <article>
                    {activeContent.thumbnail && (
                      <img
                        src={activeContent.thumbnail}
                        alt={activeContent.title}
                        className="max-h-80 w-full object-cover"
                      />
                    )}
                    <div className="p-6">
                      <p className="whitespace-pre-line text-sm leading-relaxed text-stone-700">
                        {activeContent.url_or_text}
                      </p>
                    </div>
                  </article>
                )}
              </div>

              {/* Comments */}
              <div className="flex min-h-0 flex-1 flex-col border-t border-stone-200 md:border-l md:border-t-0">
                <div className="flex items-start justify-between gap-4 border-b border-stone-200 px-5 py-4">
                  <div className="min-w-0">
                    <p className="stat-label">
                      {activeContent.type === "article" ? "Article" : "Video"}
                    </p>
                    <h3
                      id="modal-title"
                      className="mt-0.5 font-display text-lg font-semibold leading-snug text-stone-900"
                    >
                      {activeContent.title}
                    </h3>
                  </div>
                  <button
                    onClick={() => setActiveContent(null)}
                    className="btn-ghost -mr-2 shrink-0 px-2 py-1 text-xs"
                  >
                    Close
                  </button>
                </div>
                {activeContent.status === "approved" ? (
                  <Comments
                    key={activeContent.id}
                    contentId={activeContent.id}
                    onCountChange={handleCountChange}
                  />
                ) : (
                  <div className="flex flex-1 items-center justify-center p-8 text-center">
                    <div>
                      <p className="font-semibold text-stone-900">
                        {activeContent.status === "pending"
                          ? "Waiting for review"
                          : "Not published"}
                      </p>
                      <p className="muted mt-1">
                        {activeContent.status === "pending"
                          ? "Comments open once an admin approves this post."
                          : "This post was rejected and is only visible to you."}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {showForm && (
          <div
            className="modal-backdrop"
            role="dialog"
            aria-modal="true"
            aria-labelledby="upload-modal-title"
          >
            <div className="modal max-w-md">
              <h3
                id="upload-modal-title"
                className="text-lg font-semibold text-stone-900"
              >
                Share an article or video
              </h3>
              <div className="mt-5 space-y-4">
                <div>
                  <label htmlFor="title" className="label">
                    Title
                  </label>
                  <input
                    id="title"
                    type="text"
                    value={newContent.title}
                    onChange={(e) =>
                      setNewContent({ ...newContent, title: e.target.value })
                    }
                    className="input"
                  />
                </div>
                <div>
                  <label htmlFor="type" className="label">
                    Type
                  </label>
                  <select
                    id="type"
                    value={newContent.type}
                    onChange={(e) =>
                      setNewContent({
                        ...newContent,
                        type: e.target.value as "article" | "youtube",
                      })
                    }
                    className="input"
                  >
                    <option value="article">Article</option>
                    <option value="youtube">YouTube video</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="body" className="label">
                    {newContent.type === "article"
                      ? "Article content"
                      : "YouTube link"}
                  </label>
                  <textarea
                    id="body"
                    rows={newContent.type === "article" ? 6 : 2}
                    value={newContent.url_or_text}
                    onChange={(e) =>
                      setNewContent({
                        ...newContent,
                        url_or_text: e.target.value,
                      })
                    }
                    className="input"
                  />
                </div>
                {newContent.type === "article" && (
                  <div>
                    <label htmlFor="thumb" className="label">
                      Thumbnail
                    </label>
                    <input
                      id="thumb"
                      type="file"
                      accept="image/*"
                      onChange={(e) =>
                        setThumbnailFile(e.target.files?.[0] || null)
                      }
                      className="input"
                    />
                  </div>
                )}
              </div>
              <p className="mt-4 text-xs text-stone-500">
                Posts are checked automatically. Sexual, violent, hateful or
                offensive content is not allowed. Some posts are reviewed by an
                admin before they appear.
              </p>
              {formError && <p className="alert-error mt-3">{formError}</p>}
              <div className="mt-6 flex justify-end gap-2">
                <button onClick={closeForm} className="btn-secondary">
                  Cancel
                </button>
                <button
                  onClick={addContent}
                  disabled={publishing}
                  className="btn-primary"
                >
                  {publishing ? "Checking…" : "Publish"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
