import { useState } from "react";
import { Link } from "react-router-dom";

import { forgotPassword } from "../../../api/auth";
import AuthLayout from "../../../layouts/AuthLayout";
import Logo from "../../../components/common/Logo";
import Button from "../../../components/ui/Button";
import Input from "../../../components/ui/Input";
import { getErrorMessage } from "../../../utils/error";

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      const response = await forgotPassword({ email });
      setMessage(response.message);
    } catch (error) {
      console.error(error);
      setMessage("");
      alert(getErrorMessage(error));
    }
  };

  return (
    <AuthLayout>
      <form onSubmit={handleSubmit} className="space-y-6">
        <Logo />

        <div className="text-center">
          <h1 className="text-3xl font-bold">Forgot Password?</h1>
          <p className="mt-2 text-slate-500">
            Enter your email and we will send you a reset link.
          </p>
        </div>

        <Input
          label="Email"
          name="email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />

        {message && (
          <p className="rounded-lg bg-green-50 p-3 text-sm text-green-700">
            {message}
          </p>
        )}

        <Button type="submit" className="w-full">
          Send Reset Link
        </Button>

        <p className="text-center text-sm text-slate-500">
          Remember your password?{" "}
          <Link to="/login" className="font-semibold text-blue-600 hover:underline">
            Login
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}

export default ForgotPassword;
