import { useState } from "react";
import { Link, useLocation } from "react-router-dom";

import AuthLayout from "../../../layouts/AuthLayout";
import Logo from "../../../components/common/Logo";
import Button from "../../../components/ui/Button";
import Input from "../../../components/ui/Input";

import GoogleButton from "../components/GoogleButton";
import PasswordInput from "../components/PasswordInput";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../../../api/auth";
import { googleLogin } from "../../../api/auth";

function Login() {
  const [values, setValues] = useState({
    email: "",
    password: "",
  });

  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.redirectTo || "/dashboard";

  const handleChange = (event) => {
    setValues((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      const response = await loginUser({
        email: values.email,
        password: values.password,
      });

      localStorage.setItem("access", response.access);
      localStorage.setItem("refresh", response.refresh);
      localStorage.setItem("user", JSON.stringify(response.user));

      alert("Login successful.");

      navigate(redirectTo, { replace: true });
    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.detail ||
        "Invalid email or password."
      );
    }
  };

  const handleGoogleLogin = () => {
    window.google.accounts.id.initialize({
      client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,

      callback: async (response) => {
        try {
          const data = await googleLogin(
            response.credential
          );

          localStorage.setItem(
            "access",
            data.access
          );

          localStorage.setItem(
            "refresh",
            data.refresh
          );

          localStorage.setItem(
            "user",
            JSON.stringify(data.user)
          );

          alert("Login successful.");

          navigate(redirectTo, {
            replace: true,
          });

        } catch (error) {
          console.error(error);

          alert(
            error.response?.data?.detail ||
            "Google login failed."
          );
        }
      },
    });

    window.google.accounts.id.prompt();
  };

  return (
    <AuthLayout>
      <form onSubmit={handleSubmit} className="space-y-6">
        <Logo />

        <div className="text-center">
          <h1 className="text-3xl font-bold">
            Welcome Back 👋
          </h1>

          <p className="mt-2 text-slate-500">
            Manage your workspaces efficiently.
          </p>
        </div>

        <Input
          label="Email"
          name="email"
          type="email"
          placeholder="you@example.com"
          value={values.email}
          onChange={handleChange}
        />

        <PasswordInput
          label="Password"
          name="password"
          placeholder="Enter password"
          value={values.password}
          onChange={handleChange}
        />

        <div className="text-right">
          <Link
            to="/forgot-password"
            className="text-sm text-blue-600 hover:underline"
          >
            Forgot Password?
          </Link>
        </div>

        <Button type="submit" className="w-full">
          Login
        </Button>

        <div className="flex items-center gap-3">
          <div className="h-px flex-1 bg-slate-200" />
          <span className="text-xs uppercase text-slate-400">
            OR
          </span>
          <div className="h-px flex-1 bg-slate-200" />
        </div>

        <GoogleButton onClick={handleGoogleLogin}/>

        <p className="text-center text-sm text-slate-500">
          Don't have an account?{" "}
          <Link
            to="/register"
            className="font-semibold text-blue-600"
          >
            Register
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}

export default Login;
