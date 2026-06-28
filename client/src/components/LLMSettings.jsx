import React, { useState, useEffect } from "react";
import { getProviders, testLLMConnection } from "../services/api";
import "./LLMSettings.css";

const LLMSettings = ({ onClose, onSave, currentConfig }) => {
  const [providers, setProviders] = useState({});
  const [provider, setProvider] = useState(currentConfig?.provider || "");
  const [modelName, setModelName] = useState(currentConfig?.model_name || "");
  const [apiKey, setApiKey] = useState(currentConfig?.api_key || "");
  const [testStatus, setTestStatus] = useState(null);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    getProviders().then(setProviders);
  }, []);

  useEffect(() => {
    if (provider && providers[provider]) {
      setModelName(providers[provider].models[0]?.id || "");
    }
    setTestStatus(null);
  }, [provider, providers]);

  const handleTest = async () => {
    if (!provider || !modelName || !apiKey) {
      setTestStatus({ success: false, message: "All fields are required" });
      return;
    }
    setTesting(true);
    setTestStatus(null);
    const result = await testLLMConnection(provider, modelName, apiKey);
    setTestStatus(result);
    setTesting(false);
  };

  const handleSave = () => {
    if (!provider || !modelName || !apiKey) return;
    onSave({ provider, model_name: modelName, api_key: apiKey });
    onClose();
  };

  const handleReset = () => {
    onSave(null);
    onClose();
  };

  const models = provider && providers[provider] ? providers[provider].models : [];

  return (
    <div className="llm-overlay" onClick={onClose}>
      <div className="llm-modal" onClick={(e) => e.stopPropagation()}>
        <div className="llm-header">
          <h2>LLM Settings</h2>
          <button className="llm-close" onClick={onClose}>
            &times;
          </button>
        </div>

        <div className="llm-body">
          {currentConfig && (
            <div className="llm-active">
              Active: {providers[currentConfig.provider]?.name} / {currentConfig.model_name}
            </div>
          )}
          {!currentConfig && (
            <div className="llm-active llm-default">
              Using default (Google Gemini Pro from server config)
            </div>
          )}

          <label>Provider</label>
          <select value={provider} onChange={(e) => setProvider(e.target.value)}>
            <option value="">Select provider...</option>
            {Object.entries(providers).map(([key, val]) => (
              <option key={key} value={key}>
                {val.name}
              </option>
            ))}
          </select>

          <label>Model</label>
          <select
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
            disabled={!provider}
          >
            {models.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>

          <label>API Key</label>
          <input
            type="password"
            placeholder="Enter your API key"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />

          {testStatus && (
            <div className={`llm-status ${testStatus.success ? "success" : "error"}`}>
              {testStatus.message}
            </div>
          )}

          <div className="llm-actions">
            <button
              className="llm-btn test"
              onClick={handleTest}
              disabled={testing || !provider || !modelName || !apiKey}
            >
              {testing ? "Testing..." : "Test Connection"}
            </button>
            <button
              className="llm-btn save"
              onClick={handleSave}
              disabled={!testStatus?.success}
            >
              Save & Use
            </button>
            <button className="llm-btn reset" onClick={handleReset}>
              Reset to Default
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LLMSettings;
