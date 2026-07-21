import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { resetPassword } from "../../../api/auth";
import AuthLayout from "../../../layouts/AuthLayout";
import Logo from "../../../components/common/Logo";
import Button from "../../../components/ui/Button";
import PasswordInput from "../components/PasswordInput";
import { getErrorMessage } from "../../../utils/error";

function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [values, setValues] = useState({ password: "", confirmPassword: "" });
  const [message, setMessage] = useState("");

  const handleChange = (event) => {
    setValues((current) => ({ ...current, [event.target.name]: event.target.value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (values.password !== values.confirmPassword) {
      alert("Passwords do not match.");
      return;
    }

    try {
      const response = await resetPassword({
        uid: searchParams.get("uid"),
        token: searchParams.get("token"),
        password: values.password,
      });
      setMessage(response.message);
      setTimeout(() => navigate("/login"), 1500);
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
          <h1 className="text-3xl font-bold">Reset Password</h1>
          <p className="mt-2 text-slate-500">Choose a new password for your account.</p>
        </div>

        <PasswordInput label="New Password" name="password" placeholder="Enter new password" value={values.password} onChange={handleChange} required />
        <PasswordInput label="Confirm Password" name="confirmPassword" placeholder="Confirm new password" value={values.confirmPassword} onChange={handleChange} required />

        {message && (
          <p className="rounded-lg bg-green-50 p-3 text-sm text-green-700">{message}</p>
        )}

        <Button type="submit" className="w-full">Reset Password</Button>
      </form>
    </AuthLayout>
  );
}

export default ResetPassword;
