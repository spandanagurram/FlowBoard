import api from "./axios";

const getAuthHeader = () => ({
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access")}`,
  },
});

export const getWorkspaceMembers = async (workspaceId) => {
    const response = await api.get(
        `/workspaces/${workspaceId}/members/`,
        getAuthHeader()
    );

    return response.data;
}

export async function removeWorkspaceMember(workspaceId, memberId) {
  const response = await api.delete(
    `/workspaces/${workspaceId}/members/${memberId}/`,
    getAuthHeader()
  );

  return response.data;
}

export async function changeMemberRole(workspaceId, userId, values) {
  const response = await api.patch(
    `/workspaces/${workspaceId}/members/${userId}/role/`,
    values,
    getAuthHeader()
  );

  return response.data;
}

export async function transferOwnership(
    workspaceId,
    values
) {
    const response = await api.patch(
        `/workspaces/${workspaceId}/transfer-ownership/`,
        values,
        getAuthHeader()
    );

    return response.data;
}