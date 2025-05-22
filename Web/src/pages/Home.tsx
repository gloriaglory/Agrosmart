import {  useState, useEffect, useRef } from "react";
import rice from "../assets/images/rice.png";
import soybeans from "../assets/images/soybeans.png";
import wheat from "../assets/images/wheat.png";
import maize from "../assets/images/maize.png";
import nuts from "../assets/images/nuts.png";


// Define a type for crop
type Crop = {
  name: string;
  price: string;
  image: string;
  seller: string;
  date: string;
  wholesale: boolean;
  contact: string;
};

// Sample crop data
const crops: Crop[] = [
  {
    name: "Maize",
    price: "TZS 800/kg",
    image: rice,
    seller: "John",
    date: "2025-05-20",
    wholesale: true,
    contact: "0712345678",
  },
  {
    name: "Beans",
    price: "TZS 2000/kg",
    image: soybeans,
    seller: "Asha",
    date: "2025-05-19",
    wholesale: false,
    contact: "0789123456",
  },
  {
    name: "Wheat",
    price: "TZS 1000/kg",
    image: wheat,
    seller: "John",
    date: "2025-05-20",
    wholesale: true,
    contact: "0712345678",
  },
  {
    name: "Millet",
    price: "TZS 900/kg",
    image: maize,
    seller: "John",
    date: "2025-05-20",
    wholesale: true,
    contact: "0712345678",
  },
  {
    name: "Ground Nuts",
    price: "TZS 1200/kg",
    image: nuts,
    seller: "John",
    date: "2025-05-20",
    wholesale: true,
    contact: "0712345678",
  },
  {
    name: "Maize",
    price: "TZS 800/kg",
    image: rice,
    seller: "John",
    date: "2025-05-20",
    wholesale: true,
    contact: "0712345678",
  },
  {
    name: "Beans",
    price: "TZS 2000/kg",
    image: soybeans,
    seller: "Asha",
    date: "2025-05-19",
    wholesale: false,
    contact: "0789123456",
  },
  {
    name: "Wheat",
    price: "TZS 1000/kg",
    image: wheat,
    seller: "John",
    date: "2025-05-20",
    wholesale: true,
    contact: "0712345678",
  },
  {
    name: "Millet",
    price: "TZS 900/kg",
    image: maize,
    seller: "John",
    date: "2025-05-20",
    wholesale: true,
    contact: "0712345678",
  },
];


// Crop slider component
const CropSlider = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const scrollSpeed = 0.5; // Adjust for smoother/faster scroll
    let animationFrameId: number;

    const scroll = () => {
      if (container.scrollLeft >= container.scrollWidth / 2) {
        container.scrollLeft = 0; // reset to start
      } else {
        container.scrollLeft += scrollSpeed;
      }
      animationFrameId = requestAnimationFrame(scroll);
    };

    animationFrameId = requestAnimationFrame(scroll);

    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  return (
    <div className="relative w-full overflow-hidden py-4">
      <h3 className="text-lg font-semibold text-center mb-4">Featured Crops</h3>
      <div
        ref={containerRef}
        className="flex gap-4 overflow-x-auto whitespace-nowrap scroll-smooth no-scrollbar"
      >
        {[...crops, ...crops].map((crop, index) => (
          <div
            key={index}
            className="inline-block min-w-[160px] bg-white rounded-xl shadow p-2"
          >
            <img
              src={crop.image}
              alt={crop.name}
              className="h-24 w-full object-cover rounded"
            />
            <h4 className="text-sm font-semibold mt-2">{crop.name}</h4>
            <p className="text-xs text-green-700">{crop.price}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

// Graph placeholder
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const priceData = [
  { date: "May 1", price: 800 },
  { date: "May 5", price: 850 },
  { date: "May 10", price: 900 },
  { date: "May 15", price: 870 },
  { date: "May 20", price: 890 },
];

// Prepare pie data from crops array (make sure `crops` is in scope)
// Parse prices to numbers (remove "TZS " and "/kg")
const pieData = crops.map((crop) => ({
  name: crop.name,
  value: Number(crop.price.replace(/[^\d]/g, "")), // extract number from "TZS 800/kg"
}));

// Colors for pie slices
const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#AA336A"];

const PriceTrendsGraph = () => (
  <div className="my-8">
    <h3 className="text-lg font-semibold text-center mb-4">Price Trends & Crop Prices</h3>
    <div className="flex gap-6">
      {/* Line Chart */}
      <div style={{ flex: 1, height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={priceData}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis domain={["dataMin - 50", "dataMax + 50"]} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#16a34a"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Pie Chart */}
      <div style={{ flex: 1, height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={pieData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={100}
              fill="#8884d8"
              label
            >
              {pieData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend verticalAlign="bottom" height={36} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  </div>
);


// CropMarket component
const CropCard = ({
  crop,
  onViewDetails,
}: {
  crop: Crop;
  onViewDetails: (crop: Crop) => void;
}) => (
  <div
    className="bg-white shadow-md rounded-xl p-4 cursor-pointer transform transition-transform duration-300 hover:scale-105"
    onClick={() => onViewDetails(crop)}
  >
    <img
      src={crop.image}
      alt={crop.name}
      className="h-32 w-full object-cover rounded"
    />
    <h4 className="text-lg font-semibold mt-2">{crop.name}</h4>
    <div className="text-sm text-gray-600 flex justify-between mt-1">
      <span>{crop.seller}</span>
      <span>{crop.date}</span>
    </div>
    <p className="text-green-700 font-bold mt-2">{crop.price}</p>
    <button
      onClick={(e) => {
        e.stopPropagation(); // prevent card click event
        onViewDetails(crop);
      }}
      className="mt-2 bg-green-600 text-white w-full py-1 rounded hover:bg-green-700"
    >
      View Details
    </button>
  </div>
);

// Modal component
// Modal component
const Modal = ({
  crop,
  onClose,
}: {
  crop: Crop | null;
  onClose: () => void;
}) => {
  if (!crop) return null;

  const handleContactSeller = () => {
    window.location.href = `tel:${crop.contact}`;
  };

  return (
    <>
      {/* Background overlay with blur */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-40"
        onClick={onClose}
      ></div>

      {/* Modal content */}
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-xl shadow-lg max-w-md w-full max-h-[90vh] overflow-y-auto p-6 relative">
          <button
            onClick={onClose}
            className="absolute top-3 right-3 text-gray-600 hover:text-gray-900 font-bold text-xl"
            aria-label="Close modal"
          >
            &times;
          </button>
          <img
            src={crop.image}
            alt={crop.name}
            className="w-full h-48 object-cover rounded"
          />
          <h2 className="text-2xl font-bold mt-4 mb-2">{crop.name}</h2>
          <p className="text-green-700 font-bold text-lg">{crop.price}</p>
          <div className="mt-4 space-y-1">
            <p>
              <span className="font-semibold">Seller:</span> {crop.seller}
            </p>
            <p>
              <span className="font-semibold">Date:</span> {crop.date}
            </p>
            <p>
              <span className="font-semibold">Contact:</span> {crop.contact}
            </p>
            <p>
              <span className="font-semibold">Wholesale:</span>{" "}
              {crop.wholesale ? "Yes" : "No"}
            </p>
          </div>

          {/* Contact Seller Button */}
          <button
            onClick={handleContactSeller}
            className="mt-6 w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded"
          >
            Contact Seller
          </button>
        </div>
      </div>
    </>
  );
};


const CropMarket = () => {
  const [selectedCrop, setSelectedCrop] = useState<Crop | null>(null);

  const handleViewDetails = (crop: Crop) => {
    setSelectedCrop(crop);
  };

  const handleCloseModal = () => {
    setSelectedCrop(null);
  };

  return (
    <>
      <div className="my-8">
        <h3 className="text-lg font-semibold text-center mb-4">Crops for Sale</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {crops.map((crop, idx) => (
            <CropCard key={idx} crop={crop} onViewDetails={handleViewDetails} />
          ))}
        </div>
      </div>

      {/* Modal */}
      <Modal crop={selectedCrop} onClose={handleCloseModal} />
    </>
  );
};

// Home component
function Home() {
  


  return (
    <div className="px-4 py-6">
      <CropSlider />
      <PriceTrendsGraph />
      <CropMarket />
    </div>
  );
}

export default Home;
