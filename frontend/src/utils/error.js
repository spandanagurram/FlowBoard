export function getErrorMessage(error) {
  const data = error.response?.data;
  if (!data) {
    return "Something went wrong. Please try again.";
  }

  if (Array.isArray(data) && data.length > 0) {
    return data[0];
  }

  if (typeof data === "string") {
    return data;
  }

  if (data.detail) {
    return data.detail;
  }

  if (data.message) {
    return data.message;
  }

  if (data.non_field_errors?.length) {
    return data.non_field_errors[0];
  }

  const firstKey = Object.keys(data)[0];

  if (firstKey && Array.isArray(data[firstKey])) {
    return data[firstKey][0];
  }

  return "Something went wrong. Please try again.";
}