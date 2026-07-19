import { useState } from "react";
import Button from "../../../components/ui/Button";

function InviteMemberModal({
  isOpen,
  onClose,
  onInvite,
  currentUserRole,
}) {
  const [values, setValues] = useState({
    email: "",
    role: "MEMBER",
  });

  const [loading, setLoading] = useState(false);

  if (!isOpen) {
    return null;
  }

  const roleOptions =
    currentUserRole === "OWNER"
      ? ["ADMIN", "MEMBER", "VIEWER"]
      : ["MEMBER", "VIEWER"];

  const handleChange = (event) => {
    setValues((currentValues) => ({
      ...currentValues,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      setLoading(true);

      await onInvite(values);

      setValues({
        email: "",
        role: roleOptions[0],
      });

      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
        <h2 className="text-xl font-semibold">
          Invite Member
        </h2>

        <form
          onSubmit={handleSubmit}
          className="mt-6 space-y-4"
        >
          <div>
            <label className="mb-1 block text-sm font-medium">
              Email
            </label>

            <input
              type="email"
              name="email"
              value={values.email}
              onChange={handleChange}
              required
              className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">
              Role
            </label>

            <select
              name="role"
              value={values.role}
              onChange={handleChange}
              className="w-full rounded-md border border-slate-300 px-3 py-2"
            >
              {roleOptions.map((role) => (
                <option
                  key={role}
                  value={role}
                >
                  {role}
                </option>
              ))}
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button
              type="button"
              className="w-auto"
              onClick={onClose}
            >
              Cancel
            </Button>

            <Button
              type="submit"
              className="w-auto"
              disabled={loading}
            >
              {loading
                ? "Sending..."
                : "Send Invitation"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default InviteMemberModal;