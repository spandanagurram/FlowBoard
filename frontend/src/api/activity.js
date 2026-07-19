import api from "./axios";

const getAuthHeader = () => ({
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access")}`,
  },
});

export const getActivities = async (workspaceId, page = 1) => {
  const response = await api.get(
    `/workspaces/${workspaceId}/activities/?page=${page}`,
    getAuthHeader()
  );

  return response.data;
};