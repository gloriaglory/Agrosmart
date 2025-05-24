import { useEffect, useState } from 'react';
import { crops } from '../components/Crops';
import nuts from "../assets/images/nuts.png";

type Crop = {
  name: string;
  image: string;
  price: string;
  seller: string;
  date: string;
  contact: string;
  wholesale: boolean;
  category: string;
  region: string;
};

const categories = [
  { label: 'Cereals', icon: nuts },
  { label: 'Fruits', icon: nuts },
  { label: 'Spices', icon: nuts },
  { label: 'Vegetables', icon: nuts },
  { label: 'Nuts', icon: nuts},
];

const CropCard = ({
  crop,
  onViewDetails,
}: {
  crop: Crop;
  onViewDetails: (crop: Crop) => void;
}) => (
  <div
    className="bg-white shadow-md rounded-xl p-2 cursor-pointer transform transition-transform duration-300 hover:scale-105"
    onClick={() => onViewDetails(crop)}
  >
    <img
      src={crop.image}
      alt={crop.name}
      className="h-20 w-full object-cover rounded"
    />
    <h4 className="text-sm font-semibold mt-1">{crop.name}</h4>
    <div className="text-xs text-gray-600 flex justify-between mt-1">
      <span>{crop.seller}</span>
      <span>{crop.date}</span>
    </div>
    <p className="text-green-700 font-bold mt-1 text-sm">{crop.price}</p>
    <button
      onClick={(e) => {
        e.stopPropagation();
        onViewDetails(crop);
      }}
      className="mt-1 bg-green-600 text-white w-full py-1 rounded hover:bg-green-700 text-xs"
    >
      View Details
    </button>
  </div>
);

const Modal = ({
  crop,
  onClose,
}: {
  crop: Crop | null;
  onClose: () => void;
}) => {
  if (!crop) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-40" onClick={onClose} />
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-xl shadow-lg max-w-md w-full max-h-[90vh] overflow-y-auto p-6 relative">
          <button onClick={onClose} className="absolute top-3 right-3 text-gray-600 hover:text-gray-900 font-bold text-xl">
            &times;
          </button>
          <img src={crop.image} alt={crop.name} className="w-full h-48 object-cover rounded" />
          <h2 className="text-2xl font-bold mt-4 mb-2">{crop.name}</h2>
          <p className="text-green-700 font-bold text-lg">{crop.price}</p>
          <div className="mt-4 space-y-1">
            <p><strong>Seller:</strong> {crop.seller}</p>
            <p><strong>Date:</strong> {crop.date}</p>
            <p><strong>Region:</strong> {crop.region}</p>
            <p><strong>Contact:</strong> {crop.contact}</p>
            <p><strong>Wholesale:</strong> {crop.wholesale ? 'Yes' : 'No'}</p>
          </div>
          <button
            onClick={() => window.location.href = `tel:${crop.contact}`}
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
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [regionList, setRegionList] = useState<string[]>([]);
  const [filters, setFilters] = useState({
    type: '',
    region: '',
    date: '',
  });

  const handleViewDetails = (crop: Crop) => setSelectedCrop(crop);
  const handleCloseModal = () => setSelectedCrop(null);

  const filteredCrops = crops.filter((crop) => {
    const typeMatch = !filters.type || (filters.type === 'wholesale' ? crop.wholesale : !crop.wholesale);
    const regionMatch = !filters.region || crop.region === filters.region;
    const dateMatch = !filters.date || crop.date === filters.date;
    const categoryMatch = !selectedCategory || crop.category === selectedCategory;
    return typeMatch && regionMatch && dateMatch && categoryMatch;
  });

  useEffect(() => {
    type Region = {
      name: string;
    };

    fetch('https://api.tanzaniaregions.com/api/v1/regions')
      .then((res) => res.json())
      .then((data) => {
        const regions: Region[] = data.data;
        setRegionList(regions.map((r) => r.name));
      })
      .catch((err) => console.error('Error fetching regions:', err));
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <h3 className="text-2xl font-semibold text-center mb-6">Crops for Sale</h3>

      {/* Top Bar: Categories Left, Filters Right */}
      <div className="flex justify-between items-center flex-wrap gap-4 mb-6">
        {/* Category Selector */}
        <div className="flex gap-4 overflow-x-auto">
          {categories.map((cat) => (
            <div
              key={cat.label}
              onClick={() => setSelectedCategory(cat.label.toLowerCase())}
              className={`flex flex-col items-center cursor-pointer ${
                selectedCategory === cat.label.toLowerCase() ? 'opacity-100' : 'opacity-60'
              }`}
            >
              <img src={cat.icon} alt={cat.label} className="h-12 w-12 rounded-full border border-gray-300" />
              <span className="text-sm mt-1">{cat.label}</span>
            </div>
          ))}
        </div>

        {/* Filters */}
        <div className="flex gap-4 flex-wrap">
          <select
            value={filters.type}
            onChange={(e) => setFilters({ ...filters, type: e.target.value })}
            className="border border-gray-300 rounded px-3 py-1"
          >
            <option value="">Type</option>
            <option value="wholesale">Wholesale</option>
            <option value="retail">Retail</option>
          </select>

          <select
            value={filters.region}
            onChange={(e) => setFilters({ ...filters, region: e.target.value })}
            className="border border-gray-300 rounded px-3 py-1"
          >
            <option value="">Region</option>
            {regionList.map((region, idx) => (
              <option key={idx} value={region}>
                {region}
              </option>
            ))}
          </select>

          <input
            type="date"
            value={filters.date}
            onChange={(e) => setFilters({ ...filters, date: e.target.value })}
            className="border border-gray-300 rounded px-3 py-1"
          />
        </div>
      </div>

      {/* Crop Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
        {filteredCrops.map((crop, idx) => (
          <CropCard key={idx} crop={crop} onViewDetails={handleViewDetails} />
        ))}
      </div>

      <Modal crop={selectedCrop} onClose={handleCloseModal} />
    </div>
  );
};

export default CropMarket;
