import { useState } from "react";

import Button from "../../../components/ui/Button";
import Input from "../../../components/ui/Input";

function CommentCard({
  comment,
  onUpdate,
  onDelete,
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [content, setContent] = useState(comment.content);

  const handleSave = async () => {
    if (!content.trim()) return;

    await onUpdate(comment.id, {
      content: content.trim(),
    });

    setIsEditing(false);
  };

  const handleCancel = () => {
    setContent(comment.content);
    setIsEditing(false);
  };


  return (
    <div className="rounded-lg border border-slate-200 p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-semibold">
            {comment.created_by_name}
          </p>

          <p className="text-sm text-slate-500">
            {new Date(comment.created_at).toLocaleString(
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

        {!isEditing && (
          <div className="flex gap-2">
            <Button
              className="w-auto"
              onClick={() => setIsEditing(true)}
            >
              Edit
            </Button>

            <Button
              variant="danger"
              className="w-auto"
              onClick={() => onDelete(comment.id)}
            >
              Delete
            </Button>
          </div>
        )}
      </div>

      {isEditing ? (
        <>
          <textarea
            rows={4}
            className="w-full rounded-lg border border-slate-300 p-3 outline-none focus:border-blue-500"
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />

          <div className="flex gap-2">
            <Button
              className="w-auto"
              onClick={handleSave}
            >
              Save
            </Button>

            <Button
              variant="secondary"
              className="w-auto"
              onClick={handleCancel}
            >
              Cancel
            </Button>
          </div>
        </>
      ) : (
        <p className="whitespace-pre-wrap">
          {comment.content}
        </p>
      )}
    </div>
  );
}
export default CommentCard;