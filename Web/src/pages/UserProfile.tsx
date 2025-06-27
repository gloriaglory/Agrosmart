import { useState, useEffect } from "react";
import axios from "axios";

interface UserProfileData {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  id_number?: string;
}

const API_BASE = "http://localhost:8000/api/auth/profile/";

export default function UserProfile() {
  const [user, setUser] = useState<UserProfileData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    phone_number: "",
    id_number: ""
  });

  useEffect(() => {
    const fetchUserProfile = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          setError("Not authenticated");
          setLoading(false);
          return;
        }

        const res = await axios.get<UserProfileData>(API_BASE, {
          headers: {
            Authorization: `Token ${token}`,
          },
        });
        setUser(res.data);
        setFormData({
          username: res.data.username,
          email: res.data.email,
          first_name: res.data.first_name || "",
          last_name: res.data.last_name || "",
          phone_number: res.data.phone_number || "",
          id_number: res.data.id_number || "",
        });
      } catch (err: any) {
        setError("Failed to load user profile.");
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleUpdate = async () => {
    setError(null);
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("Not authenticated");
        return;
      }
      // Assuming your update endpoint is /api/auth/profile/update/
      const res = await axios.put(
        `${API_BASE}update/`,
        formData,
        {
          headers: { Authorization: `Token ${token}` },
        }
      );
      setUser(res.data);
      setEditMode(false);
      alert("Profile updated successfully");
    } catch (err: any) {
      setError("Failed to update profile");
    }
  };

  if (loading) return <p>Loading profile...</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!user) return <p>No user data found.</p>;

  return (
    <div className="max-w-md mx-auto mt-10 bg-white p-6 rounded shadow">
      <h2 className="text-2xl font-bold mb-4">User Profile</h2>

      {!editMode ? (
        <>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>First Name:</strong> {user.first_name || "-"}</p>
          <p><strong>Last Name:</strong> {user.last_name || "-"}</p>
          <p><strong>Phone Number:</strong> {user.phone_number || "-"}</p>
          <p className="mb-4"><strong>ID Number:</strong> {user.id_number || "-"}</p>

          <button
            onClick={() => setEditMode(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Edit Profile
          </button>
        </>
      ) : (
        <>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="Username"
            className="w-full mb-3 p-2 border rounded"
          />
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Email"
            className="w-full mb-3 p-2 border rounded"
          />
          <input
            type="text"
            name="first_name"
            value={formData.first_name}
            onChange={handleChange}
            placeholder="First Name"
            className="w-full mb-3 p-2 border rounded"
          />
          <input
            type="text"
            name="last_name"
            value={formData.last_name}
            onChange={handleChange}
            placeholder="Last Name"
            className="w-full mb-3 p-2 border rounded"
          />
          <input
            type="text"
            name="phone_number"
            value={formData.phone_number}
            onChange={handleChange}
            placeholder="Phone Number"
            className="w-full mb-3 p-2 border rounded"
          />
          <input
            type="text"
            name="id_number"
            value={formData.id_number}
            onChange={handleChange}
            placeholder="ID Number"
            className="w-full mb-4 p-2 border rounded"
          />
          <div className="flex justify-between">
            <button
              onClick={() => setEditMode(false)}
              className="px-4 py-2 border rounded hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              onClick={handleUpdate}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Save Changes
            </button>
          </div>
        </>
      )}
    </div>
  );
}
