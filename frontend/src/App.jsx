import React, { useState } from "react";
import axios from "axios";
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { dracula } from '@uiw/codemirror-theme-dracula';
import "bootstrap/dist/css/bootstrap.min.css";
import './index.css';
import ExportPDFButton from './export';

export const BASE_URL = import.meta.env.MODE === "development" ? "http://127.0.0.1:5000/api" : "/api";

const App = () => {
  const [code, setCode] = useState("");
  const [tokens, setTokens] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post("/analyze", { code });
      setTokens(response.data);
    } catch (error) {
      setError("Failed to analyze code. Please try again.");
      console.error("Error analyzing code:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-vh-100 bg-light py-5">
      <div className="container">
        <div className="border border-dark-subtle bg-white rounded-3 shadow-sm p-4 p-md-5" style={{ minWidth: '1280px' }}>
          <h1 className="text-center mb-4 text-primary fw-bold">
            SOOP Lexical Analyzer
          </h1>
          <div className="row g-4">
            <div className="col-md-6">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-header bg-primary text-white py-3">
                  <h5 className="card-title mb-0">Input Code</h5>
                </div>
                <div className="card-body p-0">
                  <CodeMirror
                    value={code}
                    height="400px"
                    theme={dracula}
                    extensions={[python()]}
                    onChange={(value) => setCode(value)}
                    basicSetup={{
                      lineNumbers: true,
                      highlightActiveLineGutter: true,
                      highlightSpecialChars: true,
                      history: true,
                      foldGutter: true,
                      drawSelection: true,
                      dropCursor: true,
                      allowMultipleSelections: true,
                      indentOnInput: true,
                      bracketMatching: true,
                      closeBrackets: true,
                      rectangularSelection: true,
                      crosshairCursor: true,
                      highlightActiveLine: true,
                      highlightSelectionMatches: true,
                      closeBracketsKeymap: true,
                      defaultKeymap: true,
                      searchKeymap: true,
                      historyKeymap: true,
                      foldKeymap: true,
                      completionKeymap: true,
                      lintKeymap: true,
                    }}
                  />
                </div>
                <div className="card-footer bg-white border-0 text-center py-3">
                  <button
                    className="btn btn-primary px-4 py-2"
                    onClick={handleAnalyze}
                    disabled={isLoading || !code.trim()}
                  >
                    {isLoading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" />
                        Analyzing...
                      </>
                    ) : (
                      "Analyze Code"
                    )}
                  </button>
                  {tokens.length > 0 && <ExportPDFButton tokens={tokens} />}
                </div>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-header bg-primary text-white py-3">
                  <h5 className="card-title mb-0">Lexemes</h5>
                </div>
                <div className="card-body p-0">
                  {error && (
                    <div className="alert alert-danger m-3" role="alert">
                      {error}
                    </div>
                  )}
                  <div
                    className="list-group list-group-flush overflow-auto"
                    style={{ maxHeight: "400px" }}
                  >
                    {tokens.length === 0 ? (
                      <div className="text-center p-4 text-muted">
                        <i className="bi bi-code-square fs-4 d-block mb-2"></i>
                        Write some code and click Analyze!
                      </div>
                    ) : (
                      tokens.map((token, index) => (
                        <div
                          key={index}
                          className="list-group-item list-group-item-action d-flex justify-content-between align-items-center py-3"
                        >
                          <div>
                            <span className="fw-bold text-primary">Value: </span>
                            <span className="font-monospace">{token.value}</span>
                          </div>
                          <span className="badge bg-light text-primary border border-primary">
                            {token.type}
                          </span>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;