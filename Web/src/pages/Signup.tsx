import { API_URL } from "../config";
import { useState } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import { formatNida, nidaProblem } from "../nida";
import SocialLogin from "../components/SocialLogin";

const API_BASE = `${API_URL}/api/auth/register/`;

type AccountType = "buyer" | "seller";

type FormState = {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  id_number: string;
};

type Field = {
  name: keyof FormState;
  label: string;
  type: string;
  autoComplete?: string;
  // Which account types must fill this field in
  requiredFor: AccountType[];
};

const accountFields: Field[] = [
  { name: "username", label: "Username", type: "text", autoComplete: "username", requiredFor: ["buyer", "seller"] },
  { name: "email", label: "Email", type: "email", autoComplete: "email", requiredFor: ["buyer", "seller"] },
  { name: "password", label: "Password", type: "password", autoComplete: "new-password", requiredFor: ["buyer", "seller"] },
  { name: "password2", label: "Confirm password", type: "password", autoComplete: "new-password", requiredFor: ["buyer", "seller"] },
];

const personalFields: Field[] = [
  { name: "first_name", label: "First name", type: "text", autoComplete: "given-name", requiredFor: ["seller"] },
  { name: "last_name", label: "Last name", type: "text", autoComplete: "family-name", requiredFor: ["seller"] },
  { name: "phone_number", label: "Phone number", type: "tel", autoComplete: "tel", requiredFor: ["seller"] },
];

const accountTypes: { value: AccountType; title: string; text: string }[] = [
  { value: "buyer", title: "I want to buy", text: "Browse the marketplace and use all farming tools." },
  { value: "seller", title: "I want to sell", text: "List your produce. Requires your NIDA number." },
];

export default function Signup() {
  const [accountType, setAccountType] = useState<AccountType>("buyer");
  const [form, setForm] = useState<FormState>({
    username: "",
    email: "",
    password: "",
    password2: "",
    first_name: "",
    last_name: "",
    phone_number: "",
    id_number: "",
  });
  const [fieldErrors, setFieldErrors] = useState<Partial<Record<string, string>>>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const isSeller = accountType === "seller";

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: name === "id_number" ? formatNida(value) : value });
    setFieldErrors((prev) => ({ ...prev, [name]: undefined }));
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setFieldErrors({});

    const problem = form.id_number ? nidaProblem(form.id_number) : null;
    if (problem) {
      setFieldErrors({ id_number: problem });
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post(API_BASE, {
        ...form,
        account_type: accountType,
        id_number: form.id_number || null,
      });
      navigate("/login", {
        state: {
          registered: res.data.user?.username ?? form.username,
          from: isSeller ? "/products" : "/",
        },
      });
    } catch (err) {
      const data = axios.isAxiosError(err) ? err.response?.data : null;
      if (data && typeof data === "object") {
        const errors: Record<string, string> = {};
        for (const [key, value] of Object.entries(data)) {
          errors[key] = Array.isArray(value) ? value.join(" ") : String(value);
        }
        setFieldErrors(errors);
        const known = new Set([...accountFields, ...personalFields].map((f) => f.name as string).concat("id_number"));
        const other = Object.entries(errors).filter(([k]) => !known.has(k));
        if (other.length) setError(other.map(([, v]) => v).join(" "));
      } else {
        setError("Signup failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };


  const renderField = (f: Field) => {
    const required = f.requiredFor.includes(accountType);
    return (
      <div key={f.name}>
        <label htmlFor={f.name} className="label">
          {f.label}
          {!required && <span className="font-normal text-stone-400"> (optional)</span>}
        </label>
        <input
          id={f.name}
          type={f.type}
          name={f.name}
          autoComplete={f.autoComplete}
          value={form[f.name]}
          onChange={handleChange}
          className={`input ${fieldErrors[f.name] ? "border-red-400" : ""}`}
          required={required}
        />
        {fieldErrors[f.name] && <p className="mt-1 text-xs text-red-600">{fieldErrors[f.name]}</p>}
      </div>
    );
  };

  return (
    <div className="mx-auto w-full max-w-2xl px-4 py-16">
      <h1 className="page-title">Create an account</h1>
      <p className="page-subtitle">Join AgroSmart to buy, sell and get farming advice.</p>

      <form onSubmit={handleSignup} className="card mt-8 p-6">
        <fieldset>
          <legend className="label">Account type</legend>
          <div className="grid gap-3 sm:grid-cols-2">
            {accountTypes.map((t) => {
              const active = accountType === t.value;
              return (
                <label
                  key={t.value}
                  className={`cursor-pointer rounded-xl border-2 p-4 transition ${
                    active ? "border-primary bg-primary-soft" : "border-stone-200 hover:border-stone-300"
                  }`}
                >
                  <input
                    type="radio"
                    name="account_type"
                    value={t.value}
                    checked={active}
                    onChange={() => setAccountType(t.value)}
                    className="sr-only"
                  />
                  <span className={`block font-semibold ${active ? "text-primary" : "text-stone-900"}`}>
                    {t.title}
                  </span>
                  <span className="mt-1 block text-sm text-stone-600">{t.text}</span>
                </label>
              );
            })}
          </div>
        </fieldset>

        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
          {accountFields.map(renderField)}
          {personalFields.map(renderField)}

          <div className={isSeller ? "sm:col-span-2" : ""}>
            <label htmlFor="id_number" className="label">
              NIDA number
              {!isSeller && <span className="font-normal text-stone-400"> (optional)</span>}
            </label>
            <input
              id="id_number"
              name="id_number"
              inputMode="numeric"
              placeholder="YYYYMMDD-XXXXX-XXXXX-XX"
              value={form.id_number}
              onChange={handleChange}
              className={`input font-mono tracking-wide ${fieldErrors.id_number ? "border-red-400" : ""}`}
              required={isSeller}
            />
            {fieldErrors.id_number ? (
              <p className="mt-1 text-xs text-red-600">{fieldErrors.id_number}</p>
            ) : (
              <p className="mt-1 text-xs text-stone-500">
                {isSeller
                  ? "Your 20-digit National ID number. We use it to confirm sellers are real people, and it cannot be changed later."
                  : "Add it now if you may want to sell later."}
              </p>
            )}
          </div>
        </div>

        {error && <p className="alert-error mt-4">{error}</p>}

        <button type="submit" disabled={loading} className="btn-primary mt-6 w-full py-2.5">
          {loading ? "Creating account…" : isSeller ? "Create seller account" : "Create account"}
        </button>

      </form>

      {isSeller ? (
        <p className="mt-4 text-center text-xs text-stone-500">
          Google and Facebook sign-up create buyer accounts. To sell, sign up with the form above,
          or add your NIDA number in your profile afterwards.
        </p>
      ) : (
        <SocialLogin redirectTo="/" label="or sign up with" />
      )}

      <p className="mt-6 text-center text-sm text-stone-600">
        Already have an account?{" "}
        <Link to="/login" className="link">Log in</Link>
      </p>
    </div>
  );
}
