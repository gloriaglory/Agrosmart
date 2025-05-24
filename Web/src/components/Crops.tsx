import rice from "../assets/images/rice.png";
import soybeans from "../assets/images/soybeans.png";
import wheat from "../assets/images/wheat.png";
import maize from "../assets/images/maize.png";
import nuts from "../assets/images/nuts.png";


type crop = {
  name: string;
  image: string;
  price: string;
  seller: string;
  date: string;
  contact: string;
  wholesale: boolean;
  category: string;
  region: string;
  status: string;
};

// Sample crop data
export const crops: crop[] = [
 {
  name: 'Maize',
  image: maize,
  price: 'TZS 1800/kg',
  seller: 'Mkulima Asha',
  date: '2025-07-22',
  contact: '+255123456789',
  wholesale: true,
  category: 'cereals',
  region: 'Dodoma',
  status: 'Sold',
 },
    {
    name: "Beans",
    price: "TZS 2000/kg",
    image: soybeans,
    seller: "Neema John",
    date: "2025-08-19",
    wholesale: false,
    contact: "0789123456",
    category: 'cereals',
    region: 'Mwanza',
    status: 'Available',
  },
  {
    name: "Rice",
    price: "TZS 2000/kg",
    image: rice,
    seller: "James zaki",
    date: "2025-04-20",
    wholesale: true,
    contact: "0712345678",
    category: 'cereals',
    region: 'Kahama',
    status: 'Available',
  },
   {
  name: 'Maize',
  image: maize,
  price: 'TZS 1400/kg',
  seller: 'Mkulima Asha',
  date: '2025-07-22',
  contact: '+255123456789',
  wholesale: true,
  category: 'cereals',
  region: 'Dodoma',
  status: 'Sold',
 },  

  {
    name: "Beans",
    price: "TZS 2000/kg",
    image: soybeans,
    seller: "Asha",
    date: "2025-01-19",
    wholesale: false,
    contact: "0789123456",
    category: 'cereals',
    region: 'Arusha',
    status: 'Available',
  },
     {
    name: "Rice",
    price: "TZS 2300/kg",
    image: rice,
    seller: "James zaki",
    date: "2025-06-20",
    wholesale: true,
    contact: "0712345678",
    category: 'cereals',
    region: 'Kahama',
    status: 'Available',
  },

   {
    name: "Beans",
    price: "TZS 2800/kg",
    image: soybeans,
    seller: "Asha",
    date: "2025-08-19",
    wholesale: false,
    contact: "0789123456",
    category: 'cereals',
    region: 'Dodoma',
    status: 'Available',
  },

  {
    name: "Wheat",
    price: "TZS 1000/kg",
    image: wheat,
    seller: "John",
    date: "2025-05-20",
    wholesale: true,
    contact: "0712345678",
    category: 'cereals',
    region: 'Mbeya',
    status: 'Available',
  },
  {
    name: "Millet",
    price: "TZS 900/kg",
    image: maize,
    seller: "John",
    date: "2025-05-20",
    wholesale: true,
    contact: "0712345678",
    category: 'cereals',
    region: 'Shinyanga',
    status: 'Available',
  },
     {
    name: "Rice",
    price: "TZS 1500/kg",
    image: rice,
    seller: "James zaki",
    date: "2025-01-20",
    wholesale: true,
    contact: "0712345678",
    category: 'cereals',
    region: 'Kahama',
    status: 'Available',
  },
     {
    name: "Beans",
    price: "TZS 1800/kg",
    image: soybeans,
    seller: "Asha",
    date: "2025-05-19",
    wholesale: false,
    contact: "0789123456",
    category: 'cereals',
    region: 'Arusha',
    status: 'Available',
  },
  
  {
    name: "Ground Nuts",
    price: "TZS 1200/kg",
    image: nuts,
    seller: "John",
    date: "2025-05-20",
    wholesale: true,
    contact: "0712345678",
    category: 'Nuts',
    region: 'Dodoma',
    status: 'Available',
  },
   {
  name: 'Maize',
  image: maize,
  price: 'TZS 1100/kg',
  seller: 'Mkulima Asha',
  date: '2025-03-22',
  contact: '+255123456789',
  wholesale: true,
  category: 'cereals',
  region: 'Kahama',
  status: 'Available',
 },
   {
    name: "Rice",
    price: "TZS 2200/kg",
    image: rice,
    seller: "John",
    date: "2025-02-20",
    wholesale: true,
    contact: "0712345678",
    category: 'cereals',
    region: 'Kahama',
    status: 'Available',
  },
   {
  name: 'Maize',
  image: maize,
  price: 'TZS 2400/kg',
  seller: 'Mkulima Asha',
  date: '2025-09-22',
  contact: '+255123456789',
  wholesale: true,
  category: 'cereals',
  region: 'Tanga',
  status: 'Available',
 },

 
];
