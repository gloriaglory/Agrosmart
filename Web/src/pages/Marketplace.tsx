import { useEffect, useState } from "react";
import { callApi } from "../services/api";
import { useTranslation } from "react-i18next";

export default function Marketplace() {
  const [items, setItems] = useState([]);
  const { t } = useTranslation();

  useEffect(() => {
    callApi("marketplace/items").then(setItems);
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-4">{t("marketplace")}</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {items.map((item, idx) => (
          <div key={idx} className="border p-2 rounded">
            <img src={item.image_url} alt="" className="w-full h-32 object-cover" />
            <p className="font-bold">{item.name}</p>
            <p>{item.price} TZS</p>
          </div>
        ))}
      </div>
    </div>
  );
}
