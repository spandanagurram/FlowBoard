import { useState } from "react";
import { Link } from "react-router-dom";

import AuthLayout from "../../../layouts/AuthLayout";
import Logo from "../../../components/common/Logo";
import Button from "../../../components/ui/Button";
import Input from "../../../components/ui/Input";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../../../api/auth";

import GoogleButton from "../components/GoogleButton";
import PasswordInput from "../components/PasswordInput";
import { getErrorMessage } from "../../../utils/error";

function Register() {
  const [values, setValues] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const navigate = useNavigate();

  const handleChange = (event) => {
    setValues((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (values.password !== values.confirmPassword) {
      alert("Passwords do not match.");
      return;
    }

    try {
      await registerUser({
        username: values.username,
        email: values.email,
        password: values.password,
      });

      alert("Registration successful.");

      navigate("/login");
    } catch (error) {
      console.error(error);
      alert(getErrorMessage(error));
    }
  };
  return (
    <AuthLayout>
      <form onSubmit={handleSubmit} className="space-y-6">
        <Logo/>

        <div className="text-center">
          <h1 className="text-3xl font-bold">
            Create Account
          </h1>

          <p className="mt-2 text-slate-500">
            Start managing your workspaces today.
          </p>
        </div>

        <Input
          label="Username"
          name="username"
          placeholder="Enter username"
          value={values.username}
          onChange={handleChange}
        />

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
          placeholder="Create password"
          value={values.password}
          onChange={handleChange}
        />

        <PasswordInput
          label="Confirm Password"
          name="confirmPassword"
          placeholder="Confirm password"
          value={values.confirmPassword}
          onChange={handleChange}
        />

        <Button type="submit" className="w-full">
          Create Account
        </Button>

        <div className="flex items-center gap-3">
          <div className="h-px flex-1 bg-slate-200" />

          <span className="text-xs uppercase text-slate-400">
            OR
          </span>

          <div className="h-px flex-1 bg-slate-200" />
        </div>

        <GoogleButton />

        <p className="text-center text-sm text-slate-500">
          Already have an account?{" "}
          <Link
            to="/login"
            className="font-semibold text-blue-600 hover:underline"
          >
            Login
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}

export default Register;