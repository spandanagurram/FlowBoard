import api from "./axios";

export const registerUser = async (data) => {
  const response = await api.post("/auth/register/", data);
  return response.data;
};

export const loginUser = async (data) => {
  const response = await api.post("/auth/login/", data);
  return response.data;
};

export const googleLogin = async (idToken) => {
  const response = await api.post("/auth/google/", {
    id_token: idToken,
  });

  return response.data;
};

export const getProfile = async (accessToken) => {
  const response = await api.get("/auth/profile/", {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return response.data;
};

export const logout = async () => {
  try {
    await api.post("/auth/logout/", {
      refresh: localStorage.getItem("refresh"),
    });
  } finally {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("user");

    window.location.href = "/login";
  }
}