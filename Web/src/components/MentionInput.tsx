import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";
import axios from "axios";
import { API_URL, authHeaders } from "../config";

export type MentionUser = {
  username: string;
  name: string;
  is_seller: boolean;
  nida_verified: boolean;
};

type Props = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  placeholder?: string;
  disabled?: boolean;
};

export type MentionInputHandle = { focus: () => void };

// The "@word" being typed right before the cursor, if any
const tokenBeforeCaret = (text: string, caret: number) => {
  const match = /(^|\s)@([\w.+-]*)$/.exec(text.slice(0, caret));
  return match ? { query: match[2], start: caret - match[2].length - 1 } : null;
};

const initials = (name: string) =>
  name
    .split(/\s+/)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase() ?? "")
    .join("");

// Comment box that suggests accounts to tag when you type "@"
const MentionInput = forwardRef<MentionInputHandle, Props>(
  ({ value, onChange, onSubmit, placeholder, disabled }, ref) => {
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const [token, setToken] = useState<{ query: string; start: number } | null>(null);
    const [suggestions, setSuggestions] = useState<MentionUser[]>([]);
    const [active, setActive] = useState(0);

    useImperativeHandle(ref, () => ({
      focus: () => {
        const el = textareaRef.current;
        if (!el) return;
        el.focus();
        el.setSelectionRange(el.value.length, el.value.length);
      },
    }));

    // Grow with the text, up to a few lines
    useEffect(() => {
      const el = textareaRef.current;
      if (!el) return;
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
    }, [value]);

    // Look up accounts for the word being typed (debounced)
    useEffect(() => {
      if (!token || token.query.length < 1) {
        setSuggestions([]);
        return;
      }
      const controller = new AbortController();
      const timer = setTimeout(() => {
        axios
          .get<MentionUser[]>(`${API_URL}/api/auth/users/search/`, {
            params: { q: token.query },
            headers: authHeaders(),
            signal: controller.signal,
          })
          .then((res) => {
            setSuggestions(res.data);
            setActive(0);
          })
          .catch(() => {});
      }, 200);
      return () => {
        clearTimeout(timer);
        controller.abort();
      };
    }, [token]);

    const updateToken = (text: string, caret: number) => setToken(tokenBeforeCaret(text, caret));

    const pick = (user: MentionUser) => {
      if (!token) return;
      const el = textareaRef.current;
      const caret = el?.selectionStart ?? value.length;
      const next = `${value.slice(0, token.start)}@${user.username} ${value.slice(caret)}`;
      onChange(next);
      setToken(null);
      setSuggestions([]);
      const pos = token.start + user.username.length + 2;
      requestAnimationFrame(() => {
        el?.focus();
        el?.setSelectionRange(pos, pos);
      });
    };

    const open = suggestions.length > 0;

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (open) {
        if (e.key === "ArrowDown" || e.key === "ArrowUp") {
          e.preventDefault();
          const step = e.key === "ArrowDown" ? 1 : -1;
          setActive((i) => (i + step + suggestions.length) % suggestions.length);
          return;
        }
        if (e.key === "Enter" || e.key === "Tab") {
          e.preventDefault();
          pick(suggestions[active]);
          return;
        }
        if (e.key === "Escape") {
          setSuggestions([]);
          setToken(null);
          return;
        }
      }
      // Enter posts, Shift+Enter adds a new line
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        onSubmit();
      }
    };

    return (
      <div className="relative flex-1">
        {open && (
          <ul
            role="listbox"
            className="absolute bottom-full left-0 z-10 mb-2 max-h-64 w-full overflow-y-auto rounded-xl border border-stone-200 bg-white py-1 shadow-xl"
          >
            {suggestions.map((u, i) => (
              <li key={u.username} role="option" aria-selected={i === active}>
                <button
                  type="button"
                  onMouseDown={(e) => {
                    e.preventDefault();
                    pick(u);
                  }}
                  onMouseEnter={() => setActive(i)}
                  className={`flex w-full items-center gap-3 px-3 py-2 text-left ${
                    i === active ? "bg-stone-100" : ""
                  }`}
                >
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-soft text-xs font-semibold text-primary">
                    {initials(u.name)}
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-semibold text-stone-900">
                      {u.username}
                      {u.nida_verified && <span className="ml-1.5 text-xs font-medium text-primary">Verified</span>}
                    </span>
                    <span className="block truncate text-xs text-stone-500">
                      {u.name}
                      {u.is_seller && " · Seller"}
                    </span>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
        <textarea
          ref={textareaRef}
          rows={1}
          value={value}
          disabled={disabled}
          placeholder={placeholder}
          onChange={(e) => {
            onChange(e.target.value);
            updateToken(e.target.value, e.target.selectionStart);
          }}
          onClick={(e) => updateToken(value, e.currentTarget.selectionStart)}
          onKeyDown={handleKeyDown}
          onBlur={() => setTimeout(() => setSuggestions([]), 150)}
          className="block w-full resize-none bg-transparent py-2 text-sm text-stone-900 placeholder:text-stone-400 focus:outline-none"
          aria-label="Add a comment"
        />
      </div>
    );
  }
);

MentionInput.displayName = "MentionInput";

export default MentionInput;
