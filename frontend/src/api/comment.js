import api from "./axios";

const getAuthHeader = () => ({
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access")}`,
  },
});

export const getComments = async (taskId) => {
  const response = await api.get(
    `/tasks/${taskId}/comments/`,
    getAuthHeader()
  );

  return response.data;
};

export const createComment = async (taskId, data) => {
  const response = await api.post(
    `/tasks/${taskId}/comments/`,
    data,
    getAuthHeader()
  );

  return response.data;
};

export const updateComment = async (commentId, data) => {
  const response = await api.patch(
    `/comments/${commentId}/`,
    data,
    getAuthHeader()
  );

  return response.data;
};

export const deleteComment = async (commentId) => {
  await api.delete(
    `/comments/${commentId}/`,
    getAuthHeader()
  );
};