// NIDA numbers are 20 digits, written as YYYYMMDD-XXXXX-XXXXX-XX.
// The first 8 digits are the holder's date of birth. Mirrors authentication/nida.py.
export const NIDA_LENGTH = 20;
export const MIN_SELLER_AGE = 18;

export const nidaDigits = (value: string) => value.replace(/\D/g, "").slice(0, NIDA_LENGTH);

// Formats as the user types: 19900101-12345-00001-12
export const formatNida = (value: string) => {
  const d = nidaDigits(value);
  return [d.slice(0, 8), d.slice(8, 13), d.slice(13, 18), d.slice(18, 20)]
    .filter(Boolean)
    .join("-");
};

export const nidaBirthDate = (value: string): Date | null => {
  const d = nidaDigits(value);
  if (d.length < 8) return null;
  const [y, m, day] = [Number(d.slice(0, 4)), Number(d.slice(4, 6)), Number(d.slice(6, 8))];
  const date = new Date(y, m - 1, day);
  return date.getFullYear() === y && date.getMonth() === m - 1 && date.getDate() === day ? date : null;
};

// Returns what is wrong with the number, or null if it looks valid.
export const nidaProblem = (value: string): string | null => {
  if (nidaDigits(value).length !== NIDA_LENGTH) return "Enter a valid 20-digit NIDA number.";
  const born = nidaBirthDate(value);
  const today = new Date();
  if (!born || born > today || born.getFullYear() < 1900) {
    return "This is not a valid NIDA number. The first 8 digits should be your date of birth (YYYYMMDD).";
  }
  const adult = new Date(born.getFullYear() + MIN_SELLER_AGE, born.getMonth(), born.getDate());
  if (adult > today) return `You must be at least ${MIN_SELLER_AGE} years old to register with a NIDA number.`;
  return null;
};

export const isValidNida = (value: string) => nidaProblem(value) === null;
