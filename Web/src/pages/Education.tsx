import { useEffect, useState } from "react";

interface Content {
  id: string;
  title: string;
  type: "article" | "youtube";
  url_or_text: string;
  thumbnail?: string;
  comments: Comment[];
}

interface Comment {
  id: string;
  text: string;
  parent?: string | null;
  content: string;
}

export default function Education() {
  const [contents, setContents] = useState<Content[]>([]);
  const [newContent, setNewContent] = useState({
    title: "",
    type: "article",
    url_or_text: "",
    thumbnail: "",
  });
  const [thumbnailFile, setThumbnailFile] = useState<File | null>(null);
  const [newComment, setNewComment] = useState("");
  const [activeContent, setActiveContent] = useState<Content | null>(null);
  const [commentParentId, setCommentParentId] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const token = localStorage.getItem("token");
  const isAuthenticated = !!token;

  const fetchContents = async () => {
    const res = await fetch("http://localhost:8000/api/education/contents/");
    const data = await res.json();
    setContents(data);
  };

  useEffect(() => {
    fetchContents();
  }, []);

  const addContent = async () => {
    if (!newContent.title.trim() || !newContent.url_or_text.trim()) return;

    const formData = new FormData();
    formData.append("title", newContent.title);
    formData.append("type", newContent.type);
    formData.append("url_or_text", newContent.url_or_text);
    if (thumbnailFile) {
      formData.append("thumbnail", thumbnailFile);
    }

    const res = await fetch("http://localhost:8000/api/education/contents/", {
      method: "POST",
      headers: {
        Authorization: `Token ${token}`,
      },
      body: formData,
    });

    if (res.ok) {
      await fetchContents();
      setNewContent({
        title: "",
        type: "article",
        url_or_text: "",
        thumbnail: "",
      });
      setThumbnailFile(null);
      setShowForm(false);
    }
  };

  const deleteContent = async (id: string) => {
    const res = await fetch(
      `http://localhost:8000/api/education/contents/${id}/`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Token ${token}`,
        },
      }
    );
    if (res.ok) {
      await fetchContents();
      setActiveContent(null);
    }
  };

  const addComment = async () => {
    if (!activeContent || !newComment.trim()) return;
    const res = await fetch("http://localhost:8000/api/education/comments/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${token}`,
      },
      body: JSON.stringify({
        text: newComment,
        content: activeContent.id,
        parent: commentParentId,
      }),
    });
    if (res.ok) {
      await fetchContents();
      const updated = contents.find((c) => c.id === activeContent.id);
      if (updated) setActiveContent(updated);
      setNewComment("");
      setCommentParentId(null);
    }
  };

  const deleteComment = async (commentId: string) => {
    const res = await fetch(
      `http://localhost:8000/api/education/comments/${commentId}/`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Token ${token}`,
        },
      }
    );
    if (res.ok && activeContent) {
      await fetchContents();
      const updated = contents.find((c) => c.id === activeContent.id);
      if (updated) setActiveContent(updated);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Agriculture Education</h2>
        {isAuthenticated && (
          <button
            onClick={() => setShowForm(true)}
            className="bg-primary text-white w-14 h-8 rounded text-xl font-bold flex items-center justify-center hover:bg-primary/90"
            aria-label="Add new content"
          >
            New
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {contents.map((c) => (
          <div
            key={c.id}
            className="relative border rounded p-3 bg-white shadow hover:shadow-md"
          >
            {isAuthenticated && (
              <button
                onClick={() => deleteContent(c.id)}
                className="absolute top-2 right-2 text-sm text-red-600 hover:underline z-10"
                aria-label={`Delete ${c.title}`}
              >
                Delete
              </button>
            )}
            <div
              onClick={() => setActiveContent(c)}
              className="cursor-pointer"
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter") setActiveContent(c);
              }}
            >
              <h3 className="text-lg font-semibold mb-2">{c.title}</h3>
              {c.type === "article" ? (
                <>
                  <img
                    src={
                      c.thumbnail ||
                      "https://via.placeholder.com/400x200?text=No+Image"
                    }
                    alt={c.title}
                    className="w-full h-44 object-cover rounded mb-2"
                  />
                  <p className="text-gray-700 text-sm line-clamp-3">
                    {c.url_or_text}
                  </p>
                </>
              ) : (
                <iframe
                  className="w-full aspect-video rounded"
                  src={c.url_or_text.replace("watch?v=", "embed/")}
                  allowFullScreen
                  title={c.title}
                />
              )}
            </div>
          </div>
        ))}
      </div>

      {activeContent && (
        <div
          className="fixed top-0 left-0 w-full h-full bg-black/50 z-50 flex items-center justify-center"
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
        >
          <div className="bg-white w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 rounded shadow-xl relative">
            <button
              onClick={() => setActiveContent(null)}
              className="absolute top-2 right-2 text-gray-500 hover:text-black text-xl"
              aria-label="Close content view"
            >
              &times;
            </button>
            <h3 id="modal-title" className="text-xl font-bold mb-2">
              {activeContent.title}
            </h3>
            {activeContent.type === "article" && (
              <>
                {activeContent.thumbnail && (
                  <img
                    src={activeContent.thumbnail}
                    alt={activeContent.title}
                    className="w-full max-h-60 object-cover rounded mb-4"
                  />
                )}
                <p className="text-gray-800 whitespace-pre-line mb-4">
                  {activeContent.url_or_text}
                </p>
              </>
            )}
            {activeContent.type === "youtube" && (
              <iframe
                className="w-full aspect-video mb-4 rounded"
                src={activeContent.url_or_text.replace("watch?v=", "embed/")}
                allowFullScreen
                title={activeContent.title}
              />
            )}

            <div>
              <h4 className="font-semibold mb-2">Comments</h4>
              {activeContent.comments.length === 0 && (
                <p className="text-sm text-gray-500">
                  Be the first to comment.
                </p>
              )}
              {activeContent.comments
                .filter((cm) => !cm.parent)
                .map((cm) => (
                  <div key={cm.id} className="mb-2 border rounded p-2">
                    <p className="text-sm text-gray-700">{cm.text}</p>
                    {isAuthenticated && (
                      <div className="flex items-center gap-2 mt-1 text-xs">
                        <button
                          onClick={() => setCommentParentId(cm.id)}
                          className="text-blue-600 hover:underline"
                        >
                          Reply
                        </button>
                        <button
                          onClick={() => deleteComment(cm.id)}
                          className="text-red-600 hover:underline"
                        >
                          Delete
                        </button>
                      </div>
                    )}
                    <div className="ml-4 mt-2">
                      {activeContent.comments
                        .filter((r) => r.parent === cm.id)
                        .map((reply) => (
                          <div
                            key={reply.id}
                            className="border-l pl-2 text-sm text-gray-600 mb-1"
                          >
                            {reply.text}
                            {isAuthenticated && (
                              <button
                                onClick={() => deleteComment(reply.id)}
                                className="text-xs text-red-500 ml-2 hover:underline"
                              >
                                Delete
                              </button>
                            )}
                          </div>
                        ))}
                    </div>
                  </div>
                ))}
              {isAuthenticated ? (
                <>
                  <textarea
                    placeholder="Write a comment..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    className="w-full border p-2 rounded mt-2"
                  />
                  <button
                    onClick={addComment}
                    className="mt-1 bg-primary text-white px-3 py-1 rounded hover:bg-primary/90"
                  >
                    Post Comment
                  </button>
                </>
              ) : (
                <p className="text-sm text-gray-600 mt-2">
                  Login to post a comment.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {showForm && (
        <div
          className="fixed top-0 left-0 w-full h-full bg-black/50 z-50 flex items-center justify-center"
          role="dialog"
          aria-modal="true"
          aria-labelledby="upload-modal-title"
        >
          <div className="bg-white p-6 rounded shadow-xl w-full max-w-md">
            <h3 id="upload-modal-title" className="text-xl font-semibold mb-4">
              Upload New Content
            </h3>
            <input
              type="text"
              placeholder="Title"
              value={newContent.title}
              onChange={(e) =>
                setNewContent({ ...newContent, title: e.target.value })
              }
              className="w-full border p-2 rounded mb-2"
            />
            <select
              value={newContent.type}
              onChange={(e) =>
                setNewContent({
                  ...newContent,
                  type: e.target.value as "article" | "youtube",
                })
              }
              className="w-full border p-2 rounded mb-2"
            >
              <option value="article">Article</option>
              <option value="youtube">YouTube Video</option>
            </select>
            <textarea
              placeholder={
                newContent.type === "article"
                  ? "Article content"
                  : "YouTube link"
              }
              value={newContent.url_or_text}
              onChange={(e) =>
                setNewContent({ ...newContent, url_or_text: e.target.value })
              }
              className="w-full border p-2 rounded mb-2"
            />
            {newContent.type === "article" && (
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setThumbnailFile(e.target.files?.[0] || null)}
                className="w-full border p-2 rounded mb-2"
              />
            )}
            <div className="flex justify-between">
              <button
                onClick={addContent}
                className="bg-primary text-white px-4 py-2 rounded hover:bg-primary/90"
              >
                Upload
              </button>
              <button
                onClick={() => setShowForm(false)}
                className="px-4 py-2 rounded border hover:bg-gray-100"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
