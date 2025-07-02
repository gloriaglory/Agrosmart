import { type FC } from "react";
import { useNavigate } from "react-router-dom";
import { ShoppingCart, Leaf, Bug, Smartphone } from "lucide-react";

const OurServices: FC = () => {
  const navigate = useNavigate();

  const services = [
    {
      name: "Crop Marketplace",
      description: "Buy and sell fresh produce from trusted local farmers.",
      icon: ShoppingCart,
      path: "/market",
    },
    {
      name: "Crop Recommendation",
      description: "Get the best crops to grow based on your location and soil.",
      icon: Leaf,
      path: "/crop_recommendation",
    },
    {
      name: "Disease Detection",
      description: "Use AI to detect diseases in your crops with an image.",
      icon: Bug,
      path: "/disease_detection",
    },
    {
      name: "Offline SMS Services",
      description: "Dial *100# on your phone to access our services without internet.",
      icon: Smartphone, 
      path: null,
    },
  ];

  return (
    <section className="my-8">
      <h2 className="text-2xl font-bold text-center mb-6 text-green-900">Our Services</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {services.map((service, idx) => {
          const Icon = service.icon;
          const clickable = !!service.path;

          return (
            <div
              key={idx}
              className={`p-4 border rounded-lg hover:shadow transition ${
                clickable ? "cursor-pointer hover:bg-green-50" : ""
              }`}
              onClick={() => {
                if (clickable && service.path) navigate(service.path);
              }}
              role={clickable ? "button" : undefined}
              tabIndex={clickable ? 0 : undefined}
              onKeyDown={(e) => {
                if (clickable && (e.key === "Enter" || e.key === " ")) {
                  navigate(service.path!);
                }
              }}
            >
              <Icon className="h-8 w-8 text-green-600 mb-2" />
              <h3 className="text-lg font-bold">{service.name}</h3>
              <p className="text-sm text-gray-600">{service.description}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default OurServices;
