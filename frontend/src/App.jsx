import { Routes, Route } from "react-router-dom";

import Login from "./features/auth/pages/Login";
import Register from "./features/auth/pages/Register";
import ForgotPassword from "./features/auth/pages/ForgotPassword";
import ResetPassword from "./features/auth/pages/ResetPassword";
import NotFound from "./pages/NotFound";
import Dashboard from "./features/dashboard/pages/Dashboard";
import ProtectedRoute from "./routes/ProtectedRoute";
import Workspaces from "./features/workspace/pages/Workspaces";
import WorkspaceDetails from "./features/workspace/pages/WorkspaceDetails";
import ProjectDetails from "./features/project/pages/ProjectDetails";
import TaskDetails from "./features/task/pages/TaskDetails";
import WorkspaceActivity from "./features/activity/pages/WorkspaceActivity";
import WorkspaceMembers from "./features/member/pages/WorkspaceMembers";
import InvitationPage from "./features/invitation/pages/InvitationPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="*" element={<NotFound />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/workspaces"
        element={
          <ProtectedRoute>
            <Workspaces />
          </ProtectedRoute>
        }
      />
      <Route
        path="/workspaces/:workspaceId"
        element={
            <ProtectedRoute>
                <WorkspaceDetails />
            </ProtectedRoute>
        }
      />
      <Route
        path="/projects/:projectId"
        element={
          <ProtectedRoute>
            <ProjectDetails />
          </ProtectedRoute>
        }
      />
      <Route
        path="/tasks/:taskId"
        element={
          <ProtectedRoute>
            <TaskDetails />
          </ProtectedRoute>
        }
      />

      <Route
          path="/workspaces/:workspaceId/activities"
          element={<WorkspaceActivity />}
      />

      <Route
        path="/workspaces/:workspaceId/members"
        element={<WorkspaceMembers />}
      />
      
      <Route
        path="/invitations/:token"
        element={<InvitationPage />}
      />
    </Routes>
  );
}

export default App;
