import { Trash2 } from "lucide-react";

import Button from "../../../components/ui/Button";

function PendingInvitationList({
  invitations,
  currentUserRole,
  currentUserId,
  onRevoke,
}) {
  const roleStyles = {
    OWNER: "bg-purple-100 text-purple-700",
    ADMIN: "bg-blue-100 text-blue-700",
    MEMBER: "bg-green-100 text-green-700",
    VIEWER: "bg-slate-100 text-slate-700",
  };

  const canRevoke = (invitation) => {
    if (currentUserRole === "OWNER") {
      return true;
    }

    if (currentUserRole === "ADMIN") {
      return invitation.invited_by === currentUserId;
    }

    return false;
  };

  const handleRevoke = async (invitation) => {
    const confirmed = window.confirm(
      `Revoke the invitation for ${invitation.email}?`
    );

    if (!confirmed) {
      return;
    }

    await onRevoke(invitation.id);
  };

  if (!invitations.length) {
    return (
      <p className="text-slate-500">
        No pending invitations.
      </p>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200">
      <table className="w-full text-left">
        <thead className="bg-slate-50 text-sm text-slate-500">
          <tr>
            <th className="px-4 py-3 font-medium">Email</th>
            <th className="px-4 py-3 font-medium">Role</th>
            <th className="px-4 py-3 font-medium">Expires At</th>
            <th className="px-4 py-3 font-medium">Action</th>
          </tr>
        </thead>

        <tbody className="divide-y divide-slate-200">
          {invitations.map((invitation) => (
            <tr key={invitation.id}>
              <td className="px-4 py-3 font-medium">
                {invitation.email}
              </td>

              <td className="px-4 py-3">
                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${
                    roleStyles[invitation.role]
                  }`}
                >
                  {invitation.role}
                </span>
              </td>

              <td className="px-4 py-3 text-slate-500">
                {new Date(invitation.expires_at).toLocaleString()}
              </td>

              <td className="px-4 py-3">
                {canRevoke(invitation) && (
                  <Button
                    variant="danger"
                    className="w-auto"
                    onClick={() => handleRevoke(invitation)}
                  >
                    <Trash2 size={16} />
                    Revoke
                  </Button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PendingInvitationList;
