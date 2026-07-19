import api from "./axios";

const getAuthHeader = () => ({
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access")}`,
  },
});

export const createInvitation = async (workspaceId, values) => {
  const response = await api.post(
    `/workspaces/${workspaceId}/invitations/`,
    values,
    getAuthHeader()
  );

  return response.data;
};

export const getInvitation = async (token) => {
  const response = await api.get(
    `/invitations/${token}/`
  );

  return response.data;
};

export const acceptInvitation = async (token) => {
  const response = await api.post(
    `/invitations/${token}/accept/`,
    {},
    getAuthHeader()
  );

  return response.data;
};

export const rejectInvitation = async (token) => {
  const response = await api.post(
    `/invitations/${token}/reject/`,
    {},
    getAuthHeader()
  );

  return response.data;
};