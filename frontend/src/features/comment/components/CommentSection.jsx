import { useEffect, useState } from "react";

import Button from "../../../components/ui/Button";
import CommentCard from "./CommentCard";

import {
  getComments,
  createComment,
  updateComment,
  deleteComment,
} from "../../../api/comment";

import { getErrorMessage } from "../../../utils/error";

function CommentSection({ taskId }) {
  const [comments, setComments] = useState([]);
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchComments();
  }, [taskId]);

  const fetchComments = async () => {
    try {
      setLoading(true);

      const data = await getComments(taskId);

      setComments(data.results);
    } catch (error) {
      console.error(error);
      alert(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!content.trim()) return;

    try {
      setSubmitting(true);

      const newComment = await createComment(taskId, {
        content: content.trim(),
      });

      setComments((prev) => [...prev, newComment]);

      setContent("");
    } catch (error) {
      console.error(error);
      alert(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdate = async (commentId, values) => {
    try {
      const updated = await updateComment(commentId, values);

      setComments((prev) =>
        prev.map((comment) =>
          comment.id === commentId ? updated : comment
        )
      );
    } catch (error) {
      console.error(error);
      alert(getErrorMessage(error));
    }
  };

  const handleDelete = async (commentId) => {
    if (!window.confirm("Delete this comment?")) return;

    try {
      await deleteComment(commentId);

      setComments((prev) =>
        prev.filter((comment) => comment.id !== commentId)
      );
    } catch (error) {
      console.error(error);
      alert(getErrorMessage(error));
    }
  };

  return (
    <div className="mt-8 space-y-6">
      <h2 className="text-xl font-semibold">
        Comments
      </h2>

      <div className="space-y-4">
        {loading ? (
          <p>Loading comments...</p>
        ) : comments.length === 0 ? (
          <p className="text-slate-500">
            No comments yet.
          </p>
        ) : (
          comments.map((comment) => (
            <CommentCard
              key={comment.id}
              comment={comment}
              onUpdate={handleUpdate}
              onDelete={handleDelete}
            />
          ))
        )}
      </div>

      <div className="rounded-lg border border-slate-200 p-4 space-y-3">
        <textarea
          rows={4}
          className="w-full rounded-lg border border-slate-300 p-3 outline-none focus:border-blue-500"
          placeholder="Write a comment..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />

        <div className="flex justify-end">
          <Button
            className="w-auto"
            disabled={!content.trim() || submitting}
            onClick={handleCreate}
          >
            Post
          </Button>
        </div>
      </div>
    </div>
  );
}
export default CommentSection;