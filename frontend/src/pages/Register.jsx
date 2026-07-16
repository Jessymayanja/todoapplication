import { useState } from "react";
import { registerUser } from "../services/authService";

export default function Register() {
  const [form, setForm] = useState({
    username: "",
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    password: "",
    confirm_password: "",
  });
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();

    if (isSubmitting || success) {
      return;
    }

    const validationErrors = {};

    if (!form.username.trim()) {
      validationErrors.username = "Username is required";
    }
    if (!form.first_name.trim()) {
      validationErrors.first_name = "First name is required";
    }
    if (!form.last_name.trim()) {
      validationErrors.last_name = "Last name is required";
    }

    if (!form.email.trim()) {
      validationErrors.email = "Email is required";
    }
    if (!form.phone.trim()) {
      validationErrors.phone = "your phone number is required";
    }

    if (!form.password.trim()) {
      validationErrors.password = "Password is required";
    }

    if (form.password.length < 8) {
      validationErrors.password = "Password must be at least 8 characters";
    }

    if (form.password !== form.confirm_password) {
      validationErrors.confirm_password = "Passwords do not match";
    }

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    try {
      setIsSubmitting(true);
      setErrors({});
      setSuccess(null);

      const payload = { ...form };
      delete payload.confirm_password;
      const response = await registerUser(payload);

      setSuccess({
        message:
          response.data.message ||
          "Your account has been created. Verify your email before logging in.",
        email: response.data.email,
      });

      setForm({
        username: "",
        first_name: "",
        last_name: "",
        email: "",
        phone: "",
        password: "",
        confirm_password: "",
      });
    } catch (error) {
      setErrors(error.response?.data || {});
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-stone-100">
      <div className="bg-white w-full max-w-md p-8 rounded-xl shadow">
        <h1 className="text-2xl font-bold text-center mb-6">
          Welcome to your todo application! Create Account
        </h1>

        {success ? (
          <div className="mb-4 rounded-lg border border-teal-600 bg-teal-50 px-4 py-3 text-teal-900">
            <p className="font-semibold">{success.message}</p>
            <p className="mt-2">
              Verification email sent to{" "}
              <a
                href={`mailto:${success.email}`}
                className="underline text-teal-700"
              >
                {success.email}
              </a>
              . Please click the link in your inbox to verify your account.
            </p>
            <div className="mt-4">
              <a
                href="/login"
                className="inline-block rounded bg-teal-700 px-4 py-2 text-white"
              >
                Go to login
              </a>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-3">
            {Object.keys(form).map((key) => {
              const isPasswordField = key === "password";
              const isConfirmPasswordField = key === "confirm_password";
              const showPwd = isPasswordField
                ? showPassword
                : isConfirmPasswordField
                  ? showConfirmPassword
                  : false;
              const toggleShowPwd = isPasswordField
                ? () => setShowPassword((prev) => !prev)
                : isConfirmPasswordField
                  ? () => setShowConfirmPassword((prev) => !prev)
                  : null;

              return (
                <div key={key}>
                  <div className="relative">
                    <input
                      type={
                        showPwd
                          ? "text"
                          : key.includes("password")
                            ? "password"
                            : "text"
                      }
                      placeholder={key.replace("_", " ")}
                      className={`w-full border rounded p-2 ${key.includes("password") ? "pr-10" : ""} ${errors[key] ? "border-red-500" : ""}`}
                      value={form[key]}
                      onChange={(e) => {
                        setForm({
                          ...form,
                          [key]: e.target.value,
                        });

                        if (errors[key]) {
                          setErrors({
                            ...errors,
                            [key]: null,
                          });
                        }
                      }}
                    />
                    {key.includes("password") && toggleShowPwd && (
                      <button
                        type="button"
                        onClick={toggleShowPwd}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-xl text-stone-600 hover:text-stone-800"
                        title={showPwd ? "Hide password" : "Show password"}
                      >
                        {showPwd ? "👁" : "👁"}
                      </button>
                    )}
                  </div>

                  {errors[key] && (
                    <p className="text-red-500 text-sm mt-1">
                      {Array.isArray(errors[key])
                        ? errors[key][0]
                        : errors[key]}
                    </p>
                  )}
                </div>
              );
            })}

            <button
              type="submit"
              disabled={isSubmitting || Boolean(success)}
              className={`w-full py-2 rounded text-white ${
                isSubmitting || success
                  ? "bg-teal-300 cursor-not-allowed"
                  : "bg-teal-700 hover:bg-teal-800"
              }`}
            >
              {isSubmitting
                ? "Registering..."
                : success
                  ? "Registered"
                  : "Register"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
