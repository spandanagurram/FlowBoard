import { useEffect, useState } from "react";
import { ArrowLeft } from "lucide-react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import DashboardLayout from "../../../layouts/DashboardLayout";
import Button from "../../../components/ui/Button";
import ActivityTimeline from "../components/ActivityTimeline";
import { getActivities } from "../../../api/activity";
import { getErrorMessage } from "../../../utils/error";

function WorkspaceActivity() {
  const navigate = useNavigate();
  const location = useLocation();
  const { workspaceId } = useParams();
  const workspaceName = location.state?.workspaceName || "Workspace";

  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetchActivities(page);
  }, [page]);

  const fetchActivities = async (pageNumber) => {
    try {
      setLoading(true);

      const data = await getActivities(
        workspaceId,
        pageNumber
      );

      setActivities(data.results);
      setCount(data.count);
    } catch (error) {
      console.error(error);
      alert(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(count / 5);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <Button
          className="w-auto flex items-center gap-2"
          onClick={() => navigate(-1)}
        >
          <ArrowLeft size={18} />
          Back
        </Button>

        <div>
          <h1 className="text-3xl font-bold">
            {workspaceName} Activity
          </h1>

          <p className="text-slate-500">
            View all activity logs within this workspace.
          </p>
        </div>

        {loading ? (
          <p>Loading...</p>
        ) : (
          <>
            <ActivityTimeline
              activities={activities}
            />

            {totalPages > 1 && (
              <div className="flex items-center justify-between pt-4">
                <Button
                  className="w-auto"
                  disabled={page === 1}
                  onClick={() =>
                    setPage((prev) => prev - 1)
                  }
                >
                  Previous
                </Button>

                <span>
                  Page {page} of {totalPages}
                </span>

                <Button
                  className="w-auto"
                  disabled={page === totalPages}
                  onClick={() =>
                    setPage((prev) => prev + 1)
                  }
                >
                  Next
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}

export default WorkspaceActivity;