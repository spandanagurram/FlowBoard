import {
  MessageCircle,
  Pencil,
  Trash2,
  CheckSquare,
  ClipboardPen,
  FolderPlus,
  FolderPen,
  FolderMinus,
  UserPlus,
  Shield,
  Building2,
  Activity,
} from "lucide-react";

const iconMap = {
  COMMENT_CREATED: MessageCircle,
  COMMENT_UPDATED: Pencil,
  COMMENT_DELETED: Trash2,

  TASK_CREATED: CheckSquare,
  TASK_UPDATED: ClipboardPen,
  TASK_DELETED: Trash2,

  PROJECT_CREATED: FolderPlus,
  PROJECT_UPDATED: FolderPen,
  PROJECT_DELETED: FolderMinus,

  MEMBER_INVITED: UserPlus,
  MEMBER_ROLE_CHANGED: Shield,

  WORKSPACE_UPDATED: Building2,
};

function ActivityCard({ activity }) {
  const Icon = iconMap[activity.action] || Activity;

  return (
    <div className="flex gap-4 rounded-lg border border-slate-200 bg-white p-4">
      <div className="mt-1">
        <Icon
          size={20}
          className="text-slate-600"
        />
      </div>

      <div className="flex-1">
        <p className="text-sm text-slate-900">
          {activity.description}
        </p>

        <p className="mt-1 text-xs text-slate-500">
          {new Date(activity.created_at).toLocaleString(
            "en-GB",
            {
              day: "2-digit",
              month: "short",
              year: "numeric",
              hour: "numeric",
              minute: "2-digit",
              hour12: true,
            }
          )}
        </p>
      </div>
    </div>
  );
}

export default ActivityCard;