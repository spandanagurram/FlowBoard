import api from "./axios";


const getAuthHeader = () => ({
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access")}`,
  },
});

export const getDashboardSummary = async () => {
  const response = await api.get("/dashboard/summary/", getAuthHeader());
  return response.data;
};
