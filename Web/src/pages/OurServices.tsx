import { type FC } from "react";
import { Link } from "react-router-dom";
import Reveal from "../components/Reveal";
import marketImg from "../assets/images/hom.jpeg";
import recommendImg from "../assets/images/farm2.jpeg";
import diseaseImg from "../assets/images/samp4.jpg";
import smsImg from "../assets/images/farm.jpeg";

const services = [
  {
    name: "Crop Marketplace",
    description: "Buy and sell fresh produce from trusted local farmers.",
    path: "/market",
    cta: "Visit market",
    image: marketImg,
  },
  {
    name: "Crop Recommendation",
    description: "Find the best crops to grow based on your location, soil and weather.",
    path: "/crop_recommendation",
    cta: "Get advice",
    image: recommendImg,
  },
  {
    name: "Disease Detection",
    description: "Upload a photo of a leaf to identify likely diseases and treatments.",
    path: "/disease_detection",
    cta: "Check a leaf",
    image: diseaseImg,
  },
  {
    name: "Offline SMS Services",
    description: "Dial *100# on any phone to use our services without internet.",
    path: null,
    cta: null,
    image: smsImg,
  },
];

const OurServices: FC = () => (
  <section>
    <Reveal className="section-head">
      <p className="eyebrow">What we offer</p>
      <h2 className="mt-3">Our services</h2>
      <p>Everything you need from planting to selling.</p>
    </Reveal>

    <div className="grid gap-5 md:grid-cols-2">
      {services.map((service, i) => {
        const body = (
          <div
            className={`group relative h-full overflow-hidden bg-primary-soft px-8 py-10 sm:px-12 sm:py-12 ${
              i % 2 === 0 ? "clip-left" : "clip-right"
            }`}
          >
            <img
              src={service.image}
              alt=""
              className="absolute inset-0 h-full w-full object-cover opacity-[0.12] grayscale transition duration-700 group-hover:scale-105 group-hover:opacity-20"
            />
            <div className="relative">
              <span className="font-display text-sm font-bold text-primary/60">
                0{i + 1}
              </span>
              <h3 className="mt-2 font-display text-2xl font-bold text-stone-900">
                {service.name}
              </h3>
              <p className="mt-3 max-w-sm text-stone-600">{service.description}</p>
              {service.cta && (
                <span className="link-arrow mt-6">
                  {service.cta} <span aria-hidden>→</span>
                </span>
              )}
            </div>
          </div>
        );
        return (
          <Reveal key={service.name} delay={i * 100}>
            {service.path ? (
              <Link to={service.path} className="block h-full">
                {body}
              </Link>
            ) : (
              body
            )}
          </Reveal>
        );
      })}
    </div>
  </section>
);

export default OurServices;
