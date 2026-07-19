import { useEffect, useState } from "react";
import Button from "../../../components/ui/Button";

function ChangeRoleModal({
  isOpen,
  onClose,
  member,
  currentUserRole,
  onUpdate,
}) {
  const [role, setRole] = useState("");

  useEffect(() => {
    if (member) {
      setRole(member.role);
    }
  }, [member]);

  if (!isOpen || !member) {
    return null;
  }

  const roleOptions =
    currentUserRole === "OWNER"
      ? ["ADMIN", "MEMBER", "VIEWER"]
      : ["MEMBER", "VIEWER"];

  const handleSubmit = async (event) => {
    event.preventDefault();

    await onUpdate(member.user_id, role);

    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">

        <h2 className="text-xl font-semibold">
          Change Role
        </h2>

        <form
          className="mt-6 space-y-4"
          onSubmit={handleSubmit}
        >

          <div>
            <label className="mb-1 block text-sm font-medium">
              Member
            </label>

            <input
              disabled
              value={member.username}
              className="w-full rounded-md border border-slate-300 bg-slate-100 px-3 py-2"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">
              Role
            </label>

            <select
              value={role}
              onChange={(event) =>
                setRole(event.target.value)
              }
              className="w-full rounded-md border border-slate-300 px-3 py-2"
            >
              {roleOptions.map((item) => (
                <option
                  key={item}
                  value={item}
                >
                  {item}
                </option>
              ))}
            </select>
          </div>

          <div className="flex justify-end gap-3">

            <Button
              type="button"
              className="w-auto"
              onClick={onClose}
            >
              Cancel
            </Button>

            <Button
              className="w-auto"
              type="submit"
            >
              Update Role
            </Button>

          </div>

        </form>

      </div>
    </div>
  );
}

export default ChangeRoleModal;