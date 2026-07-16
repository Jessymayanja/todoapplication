import { useState } from "react";
import { loginUser } from "../services/authService";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    password: "",
  });

  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();

    const newErrors = {};

    if (!form.username.trim()) {
      newErrors.username = "Username is required";
    }

    if (!form.password.trim()) {
      newErrors.password = "Password is required";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      setErrors({});

      await loginUser(form);

      setForm({
        username: "",
        password: "",
      });

      navigate("/home");
    } catch (error) {
      setErrors({
        detail:
          error.response?.data?.detail ||
          error.response?.data?.message ||
          error.response?.data?.non_field_errors?.[0] ||
          "Invalid username or password",
      });
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-stone-100">
      <div className="bg-white w-full max-w-sm p-8 rounded-xl shadow">
        <h1 className="text-2xl font-bold mb-6 text-center">
          Welcome to your todo app. Please login.
        </h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Username"
            className={`w-full border rounded p-2 ${
              errors.username ? "border-red-500" : ""
            }`}
            value={form.username}
            onChange={(e) => {
              setForm({ ...form, username: e.target.value });

              if (errors.username) {
                setErrors({ ...errors, username: null });
              }
            }}
          />

          {errors.username && (
            <p className="text-red-500 text-sm mt-1">{errors.username}</p>
          )}

          <div className="relative">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              className={`w-full border rounded p-2 pr-10 ${
                errors.password ? "border-red-500" : ""
              }`}
              value={form.password}
              onChange={(e) => {
                setForm({ ...form, password: e.target.value });

                if (errors.password) {
                  setErrors({ ...errors, password: null });
                }
              }}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-xl text-stone-600 hover:text-stone-800"
              title={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? "👁" : "👁"}
            </button>
          </div>

          {errors.password && (
            <p className="text-red-500 text-sm mt-1">{errors.password}</p>
          )}
          {errors.detail && (
            <div className="bg-red-100 text-red-700 p-2 rounded text-sm">
              {errors.detail}
            </div>
          )}
          <button className="w-full bg-teal-700 text-white py-2 rounded">
            Login
          </button>
        </form>

        <p className="mt-4 text-center text-sm">
          No account?
          <Link to="/register" className="text-teal-700 ml-2">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
