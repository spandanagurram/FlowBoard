import api from "./axios";


const getAuthHeader = () => ({
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access")}`,
  },
});

export const getWorkspaces = async () => {
  const response = await api.get("/workspaces/", getAuthHeader());
  return response.data;
};

export const createWorkspace = async (data) => {
  const response = await api.post(
    "/workspaces/",
    data,
    getAuthHeader()
  );

  return response.data;
};

export const getWorkspace = async (workspaceId) => {
  const response = await api.get(
    `/workspaces/${workspaceId}/`,
    getAuthHeader()
  );

  return response.data;
};

export const updateWorkspace = async (workspaceId, data) => {
  const response = await api.patch(
    `/workspaces/${workspaceId}/`,
    data,
    getAuthHeader()
  );

  return response.data;
};

export const deleteWorkspace = async (workspaceId) => {
  await api.delete(
    `/workspaces/${workspaceId}/`,
    getAuthHeader()
  );
};