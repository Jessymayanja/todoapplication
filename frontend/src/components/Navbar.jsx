import { useEffect, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { isAuthenticated, logoutUser } from "../services/authService";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [authenticated, setAuthenticated] = useState(isAuthenticated());

  useEffect(() => {
    const checkAuth = () => setAuthenticated(isAuthenticated());

    checkAuth();
    const interval = setInterval(checkAuth, 30_000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setAuthenticated(isAuthenticated());
  }, [location]);

  function handleLogout() {
    logoutUser();
    setAuthenticated(false);
    navigate("/login");
  }

  return (
    <nav className="bg-white border-b border-stone-200 shadow-sm">
      <div className="max-w-5xl mx-auto px-4 py-3 flex justify-between items-center">
        {/* Left Side */}
        <div className="flex items-center gap-3">
          <img src="/dojo-logo.png" alt="Dojo Hub" className="h-8 w-auto" />
          <h1 className="font-semibold text-stone-800">Todo Application</h1>
        </div>

        {/* Right Side */}
        <div className="flex items-center gap-4">
          {!authenticated ? (
            <>
              <Link to="/login" className="text-stone-600 hover:text-red-600">
                Login
              </Link>

              <Link
                to="/register"
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
              >
                Register
              </Link>
            </>
          ) : (
            <>
              <Link to="/home" className="text-stone-600 hover:text-red-600">
                Home
              </Link>

              <button
                onClick={handleLogout}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
              >
                Logout
              </button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
