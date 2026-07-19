import { Crown, Pencil, Trash2 } from "lucide-react";
import Button from "../../../components/ui/Button";
import { removeWorkspaceMember } from "../../../api/member";
import { getErrorMessage } from "../../../utils/error";
import { useParams } from "react-router-dom";

function MemberCard({
  member,
  currentUserRole,
  onRemove,
  onChangeRole,
  onTransferOwnership,
}) {
  const { workspaceId } = useParams();

  const roleStyles = {
    OWNER: "bg-purple-100 text-purple-700",
    ADMIN: "bg-blue-100 text-blue-700",
    MEMBER: "bg-green-100 text-green-700",
    VIEWER: "bg-slate-100 text-slate-700",
  };

  const canRemove = () => {
    if (member.role === "OWNER") {
      return false;
    }

    if (currentUserRole === "OWNER") {
      return true;
    }

    if (
      currentUserRole === "ADMIN" &&
      (member.role === "MEMBER" ||
        member.role === "VIEWER")
    ) {
      return true;
    }

    return false;
  };

  const canChangeRole = () => {
    if (member.role === "OWNER") {
      return false;
    }

    if (currentUserRole === "OWNER") {
      return true;
    }

    if (
      currentUserRole === "ADMIN" &&
      (member.role === "MEMBER" ||
        member.role === "VIEWER")
    ) {
      return true;
    }

    return false;
  };

  const canTransferOwnership = () => {
    return (
      currentUserRole === "OWNER" &&
      member.role !== "OWNER"
    );
  };

  const handleRemove = async () => {
    const confirmed = window.confirm(
      `Remove ${member.username} from this workspace?`
    );

    if (!confirmed) {
      return;
    }

    try {
      const response =
        await removeWorkspaceMember(
          workspaceId,
          member.id
        );

      alert(response.message);

      await onRemove();
    } catch (error) {
      alert(getErrorMessage(error));
    }
  };

  return (
    <div className="rounded-lg border border-slate-200 p-4 flex items-center justify-between">

      <div>
        <h3 className="font-semibold">
          {member.username}
        </h3>

        <p className="text-sm text-slate-500">
          {member.email}
        </p>
      </div>

      <div className="flex items-center gap-3">

        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold ${
            roleStyles[member.role]
          }`}
        >
          {member.role}
        </span>

        {canChangeRole() && (
          <Button
            className="w-auto"
            onClick={() => onChangeRole(member)}
          >
            <Pencil size={16} />
          </Button>
        )}

        {canTransferOwnership() && (
          <Button
            className="w-auto"
            onClick={() =>
              onTransferOwnership(member)
            }
          >
            <Crown size={16} />
          </Button>
        )}

        {canRemove() && (
          <Button
            variant="danger"
            className="w-auto"
            onClick={handleRemove}
          >
            <Trash2 size={16} />
          </Button>
        )}

      </div>

    </div>
  );
}

export default MemberCard;