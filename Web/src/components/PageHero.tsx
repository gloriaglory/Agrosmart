import type { ReactNode } from "react";

type Props = {
  title: string;
  subtitle?: string;
  // Optional background photo, shown faded behind the text
  image?: string;
  // "soft": faded and blurred, suits wide field photos.
  // "texture": black-and-white with a green tint, suits close-ups with strong colours.
  imageStyle?: "soft" | "texture";
  // CSS object-position for the photo, e.g. "bottom" to show the lower part
  imagePosition?: string;
  children?: ReactNode;
};

// Centered header band used at the top of inner pages.
const PageHero = ({
  title,
  subtitle,
  image,
  imageStyle = "soft",
  imagePosition = "center",
  children,
}: Props) => (
  <section className={`page-hero overflow-hidden ${image ? "bg-none" : ""}`}>
    {image && (
      <>
        <img
          src={image}
          alt=""
          aria-hidden
          style={{ objectPosition: imagePosition }}
          className={`hero-zoom absolute inset-0 h-full w-full object-cover ${
            imageStyle === "texture"
              ? "opacity-[0.18] contrast-125 grayscale"
              : "opacity-[0.22] blur-[2px]"
          }`}
        />
        {imageStyle === "texture" && (
          // Brand-green tint over the black-and-white photo
          <div className="absolute inset-0 bg-primary/[0.11]" />
        )}
        {/* Soft white wash keeps the text readable over any photo */}
        <div className="absolute inset-0 bg-gradient-to-b from-white/30 via-white/10 to-white/50" />
      </>
    )}
    <div className="page-hero-inner relative">
      <h1 className="animate-[pop-in_0.6s_ease-out]">{title}</h1>
      {subtitle && <p className="animate-[pop-in_0.8s_ease-out]">{subtitle}</p>}
      {children && <div className="mt-6 flex flex-wrap justify-center gap-3">{children}</div>}
    </div>
    <div className="page-hero-rule relative" />
  </section>
);

export default PageHero;
