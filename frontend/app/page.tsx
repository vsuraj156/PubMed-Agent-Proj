"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

type Event =
  | { type: "status"; message: string }
  | { type: "turn"; message: string }
  | { type: "tool_call"; tool: string; args: Record<string, unknown> }
  | { type: "tool_result"; count: number }
  | { type: "tool_error"; message: string }
  | { type: "result"; content: string }
  | { type: "error"; message: string };

type LogLine = { text: string; isError?: boolean };

export default function Home() {
  const [question, setQuestion] = useState("");
  const [maxTurns, setMaxTurns] = useState(10);
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<LogLine[]>([]);
  const [result, setResult] = useState("");
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  function eventToLogLine(event: Event): LogLine | null {
    switch (event.type) {
      case "status":
      case "turn":
        return { text: event.message };
      case "tool_call":
        return { text: `  ${event.tool} — ${JSON.stringify(event.args)}` };
      case "tool_result":
        return { text: `  Found ${event.count} articles` };
      case "tool_error":
        return { text: `  Error: ${event.message}`, isError: true };
      case "error":
        return { text: event.message, isError: true };
      default:
        return null;
    }
  }

  async function handleSearch() {
    if (!question.trim() || loading) return;
    setLoading(true);
    setLogs([]);
    setResult("");

    try {
      const response = await fetch("http://localhost:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question.trim(), max_turns: maxTurns }),
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const data = line.slice(6).trim();
          if (data === "[DONE]") {
            setLoading(false);
            return;
          }
          try {
            const event: Event = JSON.parse(data);
            if (event.type === "result") {
              setResult(event.content);
            } else {
              const logLine = eventToLogLine(event);
              if (logLine) setLogs((prev) => [...prev, logLine]);
            }
          } catch {
            // malformed SSE line, skip
          }
        }
      }
    } catch (err) {
      setLogs((prev) => [
        ...prev,
        { text: `Failed to connect to backend: ${err}`, isError: true },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="max-w-2xl mx-auto py-16 px-4">
      <h1 className="text-2xl font-semibold mb-1">PubMed Research Agent</h1>
      <p className="text-sm text-gray-500 mb-8">
        Ask a clinical question and get an evidence-based summary from PubMed literature.
      </p>

      <textarea
        className="w-full border border-gray-300 rounded-lg p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
        rows={4}
        placeholder="e.g. What are the current treatment recommendations for type 2 diabetes in adults?"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSearch();
        }}
      />

      <div className="flex items-center gap-3 mt-3">
        <label className="text-sm text-gray-600 flex items-center gap-2">
          Max turns
          <input
            type="number"
            min={1}
            max={20}
            value={maxTurns}
            onChange={(e) => setMaxTurns(Number(e.target.value))}
            className="w-16 border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </label>
        <button
          onClick={handleSearch}
          disabled={loading || !question.trim()}
          className="ml-auto bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {logs.length > 0 && (
        <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4 font-mono text-xs space-y-0.5 max-h-48 overflow-y-auto">
          {logs.map((line, i) => (
            <div key={i} className={line.isError ? "text-red-500" : "text-gray-600"}>
              {line.text}
            </div>
          ))}
          {loading && (
            <div className="text-gray-400 animate-pulse">...</div>
          )}
          <div ref={logEndRef} />
        </div>
      )}

      {result && (
        <div className="mt-8 border-t pt-8 text-sm text-gray-800 leading-relaxed">
          <ReactMarkdown
            components={{
              h1: ({ children }) => <h1 className="text-2xl font-bold mt-6 mb-3 text-gray-900">{children}</h1>,
              h2: ({ children }) => <h2 className="text-lg font-semibold mt-6 mb-2 text-gray-900">{children}</h2>,
              h3: ({ children }) => <h3 className="text-base font-semibold mt-4 mb-1 text-gray-900">{children}</h3>,
              p: ({ children }) => <p className="mb-3">{children}</p>,
              ul: ({ children }) => <ul className="list-disc list-outside pl-5 mb-3 space-y-1">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal list-outside pl-5 mb-3 space-y-1">{children}</ol>,
              li: ({ children }) => <li>{children}</li>,
              strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
              a: ({ href, children }) => <a href={href} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">{children}</a>,
              hr: () => <hr className="my-5 border-gray-200" />,
              blockquote: ({ children }) => <blockquote className="border-l-4 border-gray-200 pl-4 italic text-gray-600 my-3">{children}</blockquote>,
              code: ({ children }) => <code className="bg-gray-100 rounded px-1 py-0.5 text-xs font-mono">{children}</code>,
            }}
          >
            {result}
          </ReactMarkdown>
        </div>
      )}
    </main>
  );
}
