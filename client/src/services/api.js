import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

export const getAnswer = async (question, llmConfig = null) => {
  const payload = { question };
  if (llmConfig) {
    payload.provider = llmConfig.provider;
    payload.model_name = llmConfig.model_name;
    payload.api_key = llmConfig.api_key;
  }
  const response = await api.post("/answer/", payload);
  return response.data.answer;
};

export const getProviders = async () => {
  const response = await api.get("/llm/providers");
  return response.data.providers;
};

export const testLLMConnection = async (provider, modelName, apiKey) => {
  try {
    const response = await api.post("/llm/test", {
      provider,
      model_name: modelName,
      api_key: apiKey,
    });
    return response.data;
  } catch (err) {
    return {
      success: false,
      message: err.response?.data?.detail || "Connection failed",
    };
  }
};

export default api;
