import { Link } from "react-router-dom";

function WorkspaceCard({ workspace }) {
  return (
    <Link
      to={`/workspaces/${workspace.id}`}
      className="block rounded-xl bg-white p-5 shadow-sm transition hover:shadow-md"
    >
      <h2 className="text-lg font-semibold">
        {workspace.name}
      </h2>

      <p className="mt-2 text-sm text-slate-500">
        {workspace.description || "No description"}
      </p>
    </Link>
  );
}

export default WorkspaceCard;