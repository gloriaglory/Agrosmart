import { Link } from "react-router-dom";
import Reveal from "./Reveal";
import { useUser } from "../UserContext";
import logoMarkWhite from "../assets/images/logo-mark-white.png";

const columns = [
  {
    title: "Quick Links",
    links: [
      { to: "/", label: "Home" },
      { to: "/market", label: "Marketplace" },
      { to: "/education", label: "Learn" },
    ],
  },
  {
    title: "Services",
    links: [
      { to: "/crop_recommendation", label: "Crop Recommendation" },
      { to: "/disease_detection", label: "Disease Detection" },
      { to: "/products", label: "Sell Your Produce" },
    ],
  },
  {
    title: "Account",
    links: [
      { to: "/login", label: "Log in" },
      { to: "/register", label: "Sign up" },
      { to: "/profile", label: "Profile" },
    ],
  },
];

// Call-to-action shown in the footer card, depending on who is logged in
const useFooterCta = () => {
  const { user } = useUser();
  if (!user) return { to: "/register", label: "Create a free account" };
  if (user.is_seller) return { to: "/products", label: "List your produce" };
  return { to: "/market", label: "Explore the marketplace" };
};

const Footer = () => {
  const cta = useFooterCta();
  return (
    <footer className="relative mt-2">
      {/* Call-to-action blob overlapping the top edge */}
      <div className="container-x relative z-10 -mb-14 flex justify-center">
        <Reveal className="w-full max-w-xl">
          <div className="blob border-[6px] border-white bg-primary-soft px-8 py-8 text-center shadow-2xl shadow-stone-900/10 sm:px-14 sm:py-9">
            <h2 className="font-display text-2xl font-bold text-primary sm:text-3xl">
              Grow smarter with AgroSmart
            </h2>
            <p className="mx-auto mt-3 max-w-sm text-sm text-stone-600 sm:text-base">
              Get crop advice, check leaf diseases and sell your produce in one
              place.
            </p>
            <Link to={cta.to} className="btn-primary mt-5 px-7 py-2.5">
              {cta.label}
            </Link>
          </div>
        </Reveal>
      </div>

      <div className="pattern-dark bg-primary-hover pt-24 text-white">
        <div className="container-x">
          <div className="grid gap-8 border-b border-white/15 pb-8 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <Link
                to="/"
                className="flex items-center gap-2.5 font-display text-2xl font-bold tracking-tight"
                aria-label="AgroSmart home"
              >
                <img src={logoMarkWhite} alt="" className="h-9 w-auto" />
                <span>
                  Agro<span className="text-green-300">Smart</span>
                </span>
              </Link>
              <p className="mt-4 max-w-xs text-sm leading-relaxed text-white/75">
                Tools for farmers in Tanzania, from choosing what to plant to
                selling the harvest.
              </p>
              <p className="mt-3 text-sm text-white/75">
                No internet? Dial{" "}
                <span className="font-semibold text-white">*100#</span> on any
                phone.
              </p>
            </div>

            {columns.map((col) => (
              <div key={col.title}>
                <h3 className="font-display text-base font-semibold">
                  {col.title}
                </h3>
                <ul className="mt-3 space-y-2 text-sm">
                  {col.links.map((l) => (
                    <li key={l.to}>
                      <Link
                        to={l.to}
                        className="text-white/75 transition hover:pl-1 hover:text-white"
                      >
                        • {l.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="flex flex-col gap-2 py-4 text-xs text-white/60 sm:flex-row sm:items-center sm:justify-between">
            <p>© {new Date().getFullYear()} AgroSmart. All rights reserved.</p>
            <p>Smart farming for Tanzania</p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
