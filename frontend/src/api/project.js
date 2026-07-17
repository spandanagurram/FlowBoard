import api from "./axios";

const getAuthHeader = () => ({
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access")}`,
  },
});

export const getProjects = async (workspaceId) => {
  const response = await api.get(
    `/workspaces/${workspaceId}/projects/`,
    getAuthHeader()
  );

  return response.data;
};

export const createProject = async (workspaceId, data) => {
  const response = await api.post(
    `/workspaces/${workspaceId}/projects/`,
    data,
    getAuthHeader()
  );

  return response.data;
};

export const getProject = async (projectId) => {
  const response = await api.get(
    `/projects/${projectId}/`,
    getAuthHeader()
  );

  return response.data;
};

export const updateProject = async (projectId, data) => {
  const response = await api.patch(
    `/projects/${projectId}/`,
    data,
    getAuthHeader()
  );

  return response.data;
};

export const deleteProject = async (projectId) => {
  await api.delete(
    `/projects/${projectId}/`,
    getAuthHeader()
  );
};