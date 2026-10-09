import { Fragment, useCallback, useEffect, useRef, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { API_URL, authHeaders } from "../config";
import { useUser } from "../UserContext";
import MentionInput, { type MentionInputHandle } from "./MentionInput";

const COMMENTS_API = `${API_URL}/api/education/comments/`;

type Author = {
  id: number;
  username: string;
  name: string;
  is_seller: boolean;
  nida_verified: boolean;
};

export type Comment = {
  id: number;
  text: string;
  parent: number | null;
  author: Author | null;
  mentions: string[];
  likes_count: number;
  liked: boolean;
  replies: Comment[];
  created_at: string;
};

// "now", "5m", "3h", "2d", "4w", then a date — like Instagram
const timeAgo = (iso: string) => {
  const seconds = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (seconds < 60) return "now";
  const minutes = seconds / 60;
  if (minutes < 60) return `${Math.floor(minutes)}m`;
  const hours = minutes / 60;
  if (hours < 24) return `${Math.floor(hours)}h`;
  const days = hours / 24;
  if (days < 7) return `${Math.floor(days)}d`;
  if (days < 56) return `${Math.floor(days / 7)}w`;
  return new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
};

const initials = (name: string) =>
  name
    .split(/\s+/)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase() ?? "")
    .join("") || "?";

// Shows comment text with tagged accounts highlighted
const CommentText = ({ text, mentions }: { text: string; mentions: string[] }) => {
  const tagged = new Set(mentions.map((m) => m.toLowerCase()));
  const parts = text.split(/((?<![\w@])@[\w.+-]+)/g);
  return (
    <>
      {parts.map((part, i) => {
        const name = part.startsWith("@") ? part.slice(1).replace(/\.$/, "") : null;
        return name && tagged.has(name.toLowerCase()) ? (
          <span key={i} className="font-semibold text-primary">
            {part}
          </span>
        ) : (
          <Fragment key={i}>{part}</Fragment>
        );
      })}
    </>
  );
};

type ItemProps = {
  comment: Comment;
  isReply?: boolean;
  repliesOpen?: boolean;
  onToggleReplies?: (comment: Comment) => void;
  onReply: (comment: Comment) => void;
  onLike: (comment: Comment) => void;
  onDelete: (comment: Comment) => void;
};

const CommentItem = ({
  comment,
  isReply,
  repliesOpen,
  onToggleReplies,
  onReply,
  onLike,
  onDelete,
}: ItemProps) => {
  const { user } = useUser();
  const author = comment.author;
  const mine = !!user && author?.id === user.id;

  return (
    <li className={isReply ? "mt-4" : "py-3"}>
      <div className="flex gap-3">
        <span
          className={`flex shrink-0 items-center justify-center rounded-full bg-primary-soft font-semibold text-primary ${
            isReply ? "h-7 w-7 text-[10px]" : "h-9 w-9 text-xs"
          }`}
          aria-hidden
        >
          {author ? initials(author.name) : "?"}
        </span>
        <div className="min-w-0 flex-1">
          <p className="whitespace-pre-line break-words text-sm text-stone-800">
            <span className="mr-1.5 font-semibold text-stone-900">{author?.username ?? "Anonymous"}</span>
            <CommentText text={comment.text} mentions={comment.mentions} />
          </p>
          <div className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-stone-500">
            <span>{timeAgo(comment.created_at)}</span>
            {author?.is_seller && (
              <span className={author.nida_verified ? "text-primary" : ""}>
                {author.nida_verified ? "Verified seller" : "Seller"}
              </span>
            )}
            {comment.likes_count > 0 && (
              <span className="font-semibold">
                {comment.likes_count} {comment.likes_count === 1 ? "like" : "likes"}
              </span>
            )}
            {user && (
              <button onClick={() => onReply(comment)} className="font-semibold hover:text-stone-800">
                Reply
              </button>
            )}
            {mine && (
              <button onClick={() => onDelete(comment)} className="font-semibold hover:text-red-600">
                Delete
              </button>
            )}
          </div>
        </div>
        {user && (
          <button
            onClick={() => onLike(comment)}
            aria-pressed={comment.liked}
            className={`self-start pt-0.5 text-xs font-semibold transition ${
              comment.liked ? "text-primary" : "text-stone-400 hover:text-stone-700"
            }`}
          >
            {comment.liked ? "Liked" : "Like"}
          </button>
        )}
      </div>

      {comment.replies.length > 0 && (
        <div className={isReply ? "" : "ml-12 mt-2"}>
          <button
            onClick={() => onToggleReplies?.(comment)}
            className="flex items-center gap-3 text-xs font-semibold text-stone-500 hover:text-stone-800"
          >
            <span className="h-px w-6 bg-stone-300" />
            {repliesOpen
              ? "Hide replies"
              : `View ${comment.replies.length === 1 ? "1 reply" : `replies (${comment.replies.length})`}`}
          </button>
          {repliesOpen && (
            <ul>
              {comment.replies.map((r) => (
                <CommentItem
                  key={r.id}
                  comment={r}
                  isReply
                  onReply={onReply}
                  onLike={onLike}
                  onDelete={onDelete}
                />
              ))}
            </ul>
          )}
        </div>
      )}
    </li>
  );
};

type Props = {
  contentId: number | string;
  // Lets the page update its comment counts after posting or deleting
  onCountChange?: (count: number) => void;
};

// Instagram-style comments: likes, one level of replies, and @tagging
export default function Comments({ contentId, onCountChange }: Props) {
  const { user } = useUser();
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [text, setText] = useState("");
  const [replyTo, setReplyTo] = useState<Comment | null>(null);
  const [posting, setPosting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Top-level comments whose replies are showing
  const [openThreads, setOpenThreads] = useState<Set<number>>(new Set());
  const inputRef = useRef<MentionInputHandle>(null);
  const listEndRef = useRef<HTMLDivElement>(null);

  const load = useCallback(async () => {
    try {
      const res = await axios.get<Comment[]>(COMMENTS_API, {
        params: { content: contentId },
        headers: authHeaders(),
      });
      setComments(res.data);
      onCountChange?.(res.data.reduce((n, c) => n + 1 + c.replies.length, 0));
    } catch {
      setError("Could not load comments.");
    } finally {
      setLoading(false);
    }
  }, [contentId, onCountChange]);

  useEffect(() => {
    load();
  }, [load]);

  // Apply a change to one comment wherever it sits (top level or reply)
  const updateComment = (id: number, change: (c: Comment) => Comment) =>
    setComments((list) =>
      list.map((c) =>
        c.id === id ? change(c) : { ...c, replies: c.replies.map((r) => (r.id === id ? change(r) : r)) }
      )
    );

  const toggleThread = (comment: Comment) =>
    setOpenThreads((open) => {
      const next = new Set(open);
      if (next.has(comment.id)) next.delete(comment.id);
      else next.add(comment.id);
      return next;
    });

  const handleReply = (comment: Comment) => {
    setReplyTo(comment);
    const name = comment.author?.username;
    if (name && !text.includes(`@${name}`)) setText(`@${name} ${text}`);
    inputRef.current?.focus();
  };

  const handleLike = async (comment: Comment) => {
    // Update immediately, then confirm with the server
    const optimistic = (c: Comment) => ({
      ...c,
      liked: !c.liked,
      likes_count: c.likes_count + (c.liked ? -1 : 1),
    });
    updateComment(comment.id, optimistic);
    try {
      const res = await axios.post(`${COMMENTS_API}${comment.id}/like/`, {}, { headers: authHeaders() });
      updateComment(comment.id, (c) => ({ ...c, liked: res.data.liked, likes_count: res.data.likes_count }));
    } catch {
      updateComment(comment.id, optimistic); // undo
    }
  };

  const handleDelete = async (comment: Comment) => {
    if (!window.confirm("Delete this comment?")) return;
    try {
      await axios.delete(`${COMMENTS_API}${comment.id}/`, { headers: authHeaders() });
      load();
    } catch {
      setError("Could not delete the comment.");
    }
  };

  const post = async () => {
    const body = text.trim();
    if (!body || posting) return;
    setPosting(true);
    setError(null);
    try {
      await axios.post(
        COMMENTS_API,
        { content: contentId, text: body, parent: replyTo?.id ?? null },
        { headers: authHeaders() }
      );
      setText("");
      setReplyTo(null);
      // Show the thread the reply went into (replies always attach to the top-level comment)
      if (replyTo) setOpenThreads((open) => new Set(open).add(replyTo.parent ?? replyTo.id));
      await load();
      if (!replyTo) listEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    } catch (err) {
      const data = axios.isAxiosError(err) ? err.response?.data : null;
      setError(data?.text?.join(" ") || "Could not post your comment.");
    } finally {
      setPosting(false);
    }
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="min-h-0 flex-1 overflow-y-auto px-5">
        {loading ? (
          <p className="muted py-6 text-center">Loading comments…</p>
        ) : comments.length === 0 ? (
          <div className="py-10 text-center">
            <p className="font-semibold text-stone-900">No comments yet</p>
            <p className="muted mt-1">Start the conversation.</p>
          </div>
        ) : (
          <ul className="divide-y divide-stone-100">
            {comments.map((c) => (
              <CommentItem
                key={c.id}
                comment={c}
                repliesOpen={openThreads.has(c.id)}
                onToggleReplies={toggleThread}
                onReply={handleReply}
                onLike={handleLike}
                onDelete={handleDelete}
              />
            ))}
          </ul>
        )}
        <div ref={listEndRef} />
      </div>

      <div className="border-t border-stone-200 px-5 py-3">
        {error && <p className="mb-2 text-xs text-red-600">{error}</p>}
        {user ? (
          <>
            {replyTo && (
              <div className="mb-2 flex items-center justify-between rounded-lg bg-stone-100 px-3 py-1.5 text-xs text-stone-600">
                <span>
                  Replying to <span className="font-semibold">{replyTo.author?.username ?? "comment"}</span>
                </span>
                <button
                  onClick={() => {
                    setReplyTo(null);
                    setText("");
                  }}
                  className="font-semibold hover:text-stone-900"
                >
                  Cancel
                </button>
              </div>
            )}
            <div className="flex items-end gap-3">
              <span
                className="mb-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-[11px] font-semibold text-white"
                aria-hidden
              >
                {initials([user.first_name, user.last_name].filter(Boolean).join(" ") || user.username)}
              </span>
              <MentionInput
                ref={inputRef}
                value={text}
                onChange={setText}
                onSubmit={post}
                disabled={posting}
                placeholder={replyTo ? "Add a reply… Type @ to tag someone" : "Add a comment… Type @ to tag someone"}
              />
              <button
                onClick={post}
                disabled={!text.trim() || posting}
                className="mb-1.5 text-sm font-semibold text-primary transition hover:text-primary-hover disabled:opacity-40"
              >
                {posting ? "Posting…" : "Post"}
              </button>
            </div>
          </>
        ) : (
          <p className="py-1 text-center text-sm text-stone-500">
            <Link to="/login" state={{ from: "/education" }} className="link">
              Log in
            </Link>{" "}
            to like and comment.
          </p>
        )}
      </div>
    </div>
  );
}
