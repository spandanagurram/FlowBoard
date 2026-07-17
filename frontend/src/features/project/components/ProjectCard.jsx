import { Link } from "react-router-dom";

function ProjectCard({ project, workspaceId }) {
  return (
    <Link
      to={`/projects/${project.id}`}
      className="block rounded-xl bg-white p-5 shadow-sm transition hover:shadow-md"
    >
      <h3 className="text-lg font-semibold">
        {project.name}
      </h3>

      <p className="mt-2 text-sm text-slate-500">
        {project.description || "No description"}
      </p>

      <span className="mt-4 inline-block rounded bg-slate-100 px-2 py-1 text-xs font-medium">
        {project.key}
      </span>
    </Link>
  );
}

export default ProjectCard;