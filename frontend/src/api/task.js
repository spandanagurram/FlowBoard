import api from "./axios";

const getAuthHeader = () => ({
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access")}`,
  },
});

export const getTasks = async (projectId) => {
  const response = await api.get(
    `/projects/${projectId}/tasks/`,
    getAuthHeader()
  );

  return response.data;
};

export const createTask = async (projectId, data) => {
  const response = await api.post(
    `/projects/${projectId}/tasks/`,
    data,
    getAuthHeader()
  );

  return response.data;
};

export const getTask = async (taskId) => {
  const response = await api.get(
    `/tasks/${taskId}/`,
    getAuthHeader()
  );

  return response.data;
};

export const updateTask = async (taskId, data) => {
  const response = await api.patch(
    `/tasks/${taskId}/`, 
    data, 
    getAuthHeader()
  );

  return response.data;
};

export const deleteTask = async (taskId) => {
  const response = await api.delete(
    `/tasks/${taskId}/`, 
    getAuthHeader()
  );

  return response.data;
};