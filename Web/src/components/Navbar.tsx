import { useState, useEffect, useRef } from "react";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { useUser } from "../UserContext";

const links = [
  { to: "/", label: "Home" },
  { to: "/market", label: "Marketplace" },
  { to: "/crop_recommendation", label: "Recommendations" },
  { to: "/disease_detection", label: "Disease Detection" },
  { to: "/education", label: "Learn" },
];

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `relative px-3 py-2 text-[15px] font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 rounded-md
   after:absolute after:inset-x-3 after:-bottom-0.5 after:h-0.5 after:origin-left after:rounded-full after:bg-primary after:transition-transform after:duration-300 ${
     isActive
       ? "text-primary after:scale-x-100"
       : "text-stone-700 hover:text-primary after:scale-x-0 hover:after:scale-x-100"
   }`;

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const { user, logout } = useUser();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    setMenuOpen(false);
    setDropdownOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    setDropdownOpen(false);
    navigate("/");
  };

  const initials = user
    ? (
        (user.first_name?.[0] ?? user.username[0] ?? "") +
        (user.last_name?.[0] ?? "")
      ).toUpperCase()
    : "";

  return (
    <header
      className={`sticky top-0 z-40 bg-white/95 backdrop-blur transition-shadow duration-300 ${
        scrolled
          ? "shadow-[0_8px_30px_rgba(28,25,23,0.08)]"
          : "border-b border-stone-200"
      }`}
    >
      <nav
        className={`container-x grid items-center transition-[height] duration-300 md:grid-cols-[1fr_auto_1fr] grid-cols-[1fr_auto] ${
          scrolled ? "h-16" : "h-20"
        }`}
      >
        <Link
          to="/"
          className="font-display text-2xl font-bold tracking-tight"
          aria-label="AgroSmart home"
        >
          <span>
            <span className="text-stone-900">Agro</span>
            <span className="text-primary">Smart</span>
          </span>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === "/"}
              className={linkClass}
            >
              {l.label}
            </NavLink>
          ))}
        </div>

        <div className="flex items-center justify-end gap-2">
          {!user ? (
            <div className="hidden items-center gap-2 sm:flex">
              <Link to="/login" className="btn-ghost">
                Log in
              </Link>
              <Link to="/register" className="btn-primary">
                Sign up
              </Link>
            </div>
          ) : (
            <div ref={dropdownRef} className="relative">
              <button
                onClick={() => setDropdownOpen((open) => !open)}
                className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-sm font-semibold text-white ring-4 ring-primary/10 transition hover:ring-primary/25"
                aria-label="Account menu"
                aria-expanded={dropdownOpen}
              >
                {initials}
              </button>

              {dropdownOpen && (
                <div
                  className="card absolute right-0 mt-3 w-72 p-4 shadow-xl"
                  style={{ animation: "pop-in 0.2s ease-out" }}
                >
                  <div className="border-b border-stone-200 pb-3">
                    <p className="font-semibold text-stone-900">
                      {user.username}
                    </p>
                    <p className="truncate text-sm text-stone-500">
                      {user.email}
                    </p>
                  </div>
                  <dl className="space-y-2 py-3 text-sm">
                    {[
                      [
                        "Name",
                        [user.first_name, user.last_name]
                          .filter(Boolean)
                          .join(" "),
                      ],
                      ["Phone", user.phone_number],
                      ["Account", user.is_seller ? "Seller" : "Buyer"],
                    ]
                      .filter(([, v]) => v)
                      .map(([k, v]) => (
                        <div key={k} className="flex justify-between gap-4">
                          <dt className="text-stone-500">{k}</dt>
                          <dd className="truncate text-stone-800">{v}</dd>
                        </div>
                      ))}
                  </dl>
                  {user.is_seller && (
                    <Link to="/products" className="btn-secondary mb-2 w-full">
                      My products
                    </Link>
                  )}
                  <div className="flex gap-2 border-t border-stone-200 pt-3">
                    <Link to="/profile" className="btn-secondary flex-1">
                      Profile
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="btn-primary flex-1"
                    >
                      Log out
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          <button
            className="btn-ghost md:hidden"
            onClick={() => setMenuOpen((o) => !o)}
            aria-expanded={menuOpen}
          >
            {menuOpen ? "Close" : "Menu"}
          </button>
        </div>
      </nav>

      {menuOpen && (
        <div className="border-t border-stone-200 bg-white md:hidden">
          <div className="container-x flex flex-col py-3">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.to === "/"}
                className={linkClass}
              >
                {l.label}
              </NavLink>
            ))}
            {!user && (
              <div className="mt-3 flex gap-2 border-t border-stone-200 pt-3 sm:hidden">
                <Link to="/login" className="btn-secondary flex-1">
                  Log in
                </Link>
                <Link to="/register" className="btn-primary flex-1">
                  Sign up
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
