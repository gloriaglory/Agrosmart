import { API_URL, authHeaders } from "../config";
import PageHero from "../components/PageHero";
import profileHeroImg from "../assets/images/farm1.jpeg";
import { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { useUser } from "../UserContext";
import { formatNida, isValidNida, nidaProblem } from "../nida";

const API_BASE = `${API_URL}/api/auth/profile/update/`;
const VERIFY_URL = `${API_URL}/api/auth/nida/verify/`;

const formatBirthDate = (iso: string) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

type EditableField = "first_name" | "last_name" | "phone_number" | "id_number";

const editableFields: { name: EditableField; label: string; type: string }[] = [
  { name: "first_name", label: "First name", type: "text" },
  { name: "last_name", label: "Last name", type: "text" },
  { name: "phone_number", label: "Phone number", type: "tel" },
];

export default function UserProfile() {
  const { user, loading, refreshUser } = useUser();
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<
    Partial<Record<string, string>>
  >({});
  const [success, setSuccess] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [verifyResult, setVerifyResult] = useState<{
    kind: "ok" | "pending" | "error";
    text: string;
  } | null>(null);
  const [formData, setFormData] = useState<Record<EditableField, string>>({
    first_name: "",
    last_name: "",
    phone_number: "",
    id_number: "",
  });

  // A valid NIDA number is locked once saved
  const nidaLocked = !!user?.id_number && isValidNida(user.id_number);

  useEffect(() => {
    if (!user) return;
    setFormData({
      first_name: user.first_name || "",
      last_name: user.last_name || "",
      phone_number: user.phone_number || "",
      id_number: user.id_number ? formatNida(user.id_number) : "",
    });
  }, [user, editMode]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "id_number" ? formatNida(value) : value,
    }));
    setFieldErrors((prev) => ({ ...prev, [name]: undefined }));
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setFieldErrors({});

    const problem =
      !nidaLocked && formData.id_number
        ? nidaProblem(formData.id_number)
        : null;
    if (problem) {
      setFieldErrors({ id_number: problem });
      return;
    }

    const payload: Partial<Record<EditableField, string | null>> = {
      first_name: formData.first_name,
      last_name: formData.last_name,
      phone_number: formData.phone_number,
    };
    if (!nidaLocked) payload.id_number = formData.id_number || null;

    try {
      await axios.patch(API_BASE, payload, { headers: authHeaders() });
      await refreshUser();
      setEditMode(false);
      setSuccess("Profile updated successfully.");
    } catch (err) {
      const data = axios.isAxiosError(err) ? err.response?.data : null;
      if (data && typeof data === "object") {
        const errors: Record<string, string> = {};
        for (const [k, v] of Object.entries(data))
          errors[k] = Array.isArray(v) ? v.join(" ") : String(v);
        setFieldErrors(errors);
      } else {
        setError("Failed to update profile.");
      }
    }
  };

  const handleVerify = async () => {
    setVerifying(true);
    setVerifyResult(null);
    try {
      const res = await axios.post(VERIFY_URL, {}, { headers: authHeaders() });
      await refreshUser();
      setVerifyResult({ kind: "ok", text: res.data.message });
    } catch (err) {
      const data = axios.isAxiosError(err) ? err.response?.data : null;
      // 503 means NIDA is not connected yet: the request is pending review, not a failure
      const pending = axios.isAxiosError(err) && err.response?.status === 503;
      setVerifyResult({
        kind: pending ? "pending" : "error",
        text: data?.error || "Verification failed. Please try again.",
      });
    } finally {
      setVerifying(false);
    }
  };

  if (loading)
    return (
      <div className="page">
        <p className="muted">Loading profile…</p>
      </div>
    );
  if (!user)
    return (
      <div className="page mx-auto max-w-xl">
        <p className="muted">Log in to see your profile.</p>
        <Link to="/login" className="btn-primary mt-4">
          Log in
        </Link>
      </div>
    );

  const rows: [string, React.ReactNode][] = [
    ["Username", user.username],
    ["Email", user.email],
    ["First name", user.first_name || "—"],
    ["Last name", user.last_name || "—"],
    ["Phone number", user.phone_number || "—"],
    [
      "NIDA number",
      user.id_number ? (
        <span className="flex flex-wrap items-center gap-2">
          <span className="font-mono">{formatNida(user.id_number)}</span>
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${
              user.nida_verified
                ? "bg-green-100 text-green-800"
                : "bg-stone-100 text-stone-600"
            }`}
          >
            {user.nida_verified ? "Verified" : "Not yet verified"}
          </span>
        </span>
      ) : (
        "—"
      ),
    ],
    ["Account type", user.is_seller ? "Seller" : "Buyer"],
  ];

  return (
    <div>
      <PageHero
        image={profileHeroImg}
        title="Your Profile"
        subtitle="Manage your account details."
      >
        {!editMode && (
          <button
            onClick={() => {
              setEditMode(true);
              setSuccess(null);
            }}
            className="btn-secondary"
          >
            Edit profile
          </button>
        )}
      </PageHero>
      <div className="page mx-auto max-w-2xl">
        {success && <p className="alert-success mb-4">{success}</p>}
        {error && <p className="alert-error mb-4">{error}</p>}

        {!user.is_seller && !editMode && (
          <div className="card mb-4 flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="font-medium text-stone-900">
                Want to sell on the marketplace?
              </p>
              <p className="muted">
                Add your NIDA number to your profile to become a seller.
              </p>
            </div>
            <button
              onClick={() => setEditMode(true)}
              className="btn-primary shrink-0"
            >
              Become a seller
            </button>
          </div>
        )}

        {user.id_number && !editMode && (
          <div className="card mb-4 p-5">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-medium text-stone-900">NIDA verification</p>
                <p className="muted mt-0.5">
                  {user.nida_verified
                    ? "Your identity is confirmed. Buyers can trust your listings."
                    : "Confirm your NIDA number so buyers know you are a real, verified seller."}
                </p>
                {user.nida_birth_date && (
                  <p className="mt-2 text-xs text-stone-500">
                    Date of birth from your NIDA number:{" "}
                    <span className="font-medium text-stone-700">
                      {formatBirthDate(user.nida_birth_date)}
                    </span>
                    {!user.nida_verified &&
                      " (if this is wrong, contact support to correct your number)"}
                  </p>
                )}
              </div>
              {user.nida_verified ? (
                <span className="shrink-0 rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-800">
                  Verified
                </span>
              ) : (
                <button
                  onClick={handleVerify}
                  disabled={verifying}
                  className="btn-primary shrink-0"
                >
                  {verifying ? "Verifying…" : "Verify now"}
                </button>
              )}
            </div>
            {verifyResult && (
              <p
                className={`mt-4 ${
                  verifyResult.kind === "ok"
                    ? "alert-success"
                    : verifyResult.kind === "pending"
                      ? "rounded-xl border border-amber-200 bg-amber-50 px-3.5 py-2.5 text-sm text-amber-800"
                      : "alert-error"
                }`}
              >
                {verifyResult.text}
              </p>
            )}
          </div>
        )}

        {!editMode ? (
          <dl className="card divide-y divide-stone-100">
            {rows.map(([label, value]) => (
              <div
                key={label}
                className="grid grid-cols-3 gap-4 px-5 py-4 text-sm"
              >
                <dt className="text-stone-500">{label}</dt>
                <dd className="col-span-2 text-stone-900">{value}</dd>
              </div>
            ))}
          </dl>
        ) : (
          <form onSubmit={handleUpdate} className="card p-5">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {editableFields.map((f) => (
                <div key={f.name}>
                  <label htmlFor={f.name} className="label">
                    {f.label}
                  </label>
                  <input
                    id={f.name}
                    type={f.type}
                    name={f.name}
                    value={formData[f.name]}
                    onChange={handleChange}
                    className="input"
                  />
                  {fieldErrors[f.name] && (
                    <p className="mt-1 text-xs text-red-600">
                      {fieldErrors[f.name]}
                    </p>
                  )}
                </div>
              ))}
              <div>
                <label htmlFor="id_number" className="label">
                  NIDA number
                </label>
                <input
                  id="id_number"
                  name="id_number"
                  inputMode="numeric"
                  placeholder="YYYYMMDD-XXXXX-XXXXX-XX"
                  value={formData.id_number}
                  onChange={handleChange}
                  readOnly={nidaLocked}
                  className="input font-mono tracking-wide"
                />
                {fieldErrors.id_number ? (
                  <p className="mt-1 text-xs text-red-600">
                    {fieldErrors.id_number}
                  </p>
                ) : (
                  <p className="mt-1 text-xs text-stone-500">
                    {nidaLocked
                      ? "Your NIDA number cannot be changed. Contact support if it is wrong."
                      : "Required to sell. It cannot be changed once saved."}
                  </p>
                )}
                {user.nida_verified && (
                  <p className="mt-1 text-xs text-amber-700">
                    Changing your first or last name will remove your verified
                    status until you verify again.
                  </p>
                )}
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setEditMode(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                Save changes
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
