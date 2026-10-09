export const formatPrice = (price: number | string) =>
  `TZS ${Number(price).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
