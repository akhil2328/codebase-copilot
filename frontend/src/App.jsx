import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { FaCopy, FaSearch, FaFileCode, FaFolder, FaFolderOpen } from "react-icons/fa";

const BACKEND = "http://127.0.0.1:9000";

function FileNode({ node, onSelect }) {
  const [open, setOpen] = useState(false);

  if (node.type === "folder") {
    return (
      <div style={{ marginLeft: 8 }}>
        <div onClick={() => setOpen(!open)} style={{ cursor: "pointer" }}>
          {open ? <FaFolderOpen /> : <FaFolder />} &nbsp; {node.name}
        </div>

        {open && node.children?.map((c, i) =>
          <FileNode key={i} node={c} onSelect={onSelect} />
        )}
      </div>
    );
  }

  return (
    <div
      style={{ marginLeft: 28, cursor: "pointer" }}
      onClick={() => onSelect(node.path)}
    >
      <FaFileCode /> &nbsp; {node.name}
    </div>
  );
}

export default function App() {

  const [repoUrl, setRepoUrl] = useState("");
  const [files, setFiles] = useState([]);
  const [indexed, setIndexed] = useState(false);

  const [tabs, setTabs] = useState([]);
  const [active, setActive] = useState(null);

  const [query, setQuery] = useState("");

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const bottomRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const indexRepo = async () => {
    setIndexed(false);

    await axios.post(`${BACKEND}/index`, null, {
      params: { url: repoUrl }
    });

    const res = await axios.get(`${BACKEND}/files`);
    setFiles(res.data);

    setIndexed(true);

    alert("Repo indexed successfully!");
  };

  const openFile = async (path) => {
    const res = await axios.get(`${BACKEND}/file`, { params: { path } });
    const file = { path, content: res.data.content };

    const exists = tabs.find(t => t.path === path);
    if (!exists) setTabs([...tabs, file]);

    setActive(file);
  };

  const closeTab = (path) => {
    const left = tabs.filter(t => t.path !== path);
    setTabs(left);

    if (active?.path === path) {
      setActive(left.length ? left[left.length - 1] : null);
    }
  };

  const copyCode = () => {
    if (active) navigator.clipboard.writeText(active.content);
  };

  const ask = async () => {

    const userMsg = { role: "user", text: question };
    setMessages(m => [...m, userMsg]);

    const q = question;
    setQuestion("");

    setLoading(true);

    setMessages(m => [...m, { role: "bot", text: "" }]);

    try {

      const res = await fetch(
        `${BACKEND}/ask-stream?q=${encodeURIComponent(q)}`
      );

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let bot = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        bot += decoder.decode(value);

        setMessages(m => {
          const copy = [...m];
          copy[copy.length - 1] = { role: "bot", text: bot };
          return copy;
        });
      }

    } catch (err) {

      setMessages(m => [
        ...m,
        { role: "bot", text: "❌ Streaming failed" }
      ]);

    }

    setLoading(false);
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>

      {/* LEFT — FILES */}
      <div className="glass" style={{ width: 320, padding: 15, overflowY: "auto" }}>

        <h3>Codebase-Copilot</h3>

        <input
          value={repoUrl}
          onChange={e => setRepoUrl(e.target.value)}
          placeholder="Repo URL"
          style={{ width: "100%", marginBottom: 10 }}
        />

        <button onClick={indexRepo}>Index Repo</button>

        <div style={{ marginTop: 10 }}>
          <FaSearch /> Search
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            style={{ width: "100%" }}
            placeholder="Search files..."
          />
        </div>

        <div style={{ marginTop: 10 }}>
          {files
            .filter(f =>
              !query ||
              f.name?.toLowerCase().includes(query.toLowerCase())
            )
            .map((f, i) =>
              <FileNode key={i} node={f} onSelect={openFile} />
            )}
        </div>
      </div>

      {/* MIDDLE — CODE VIEW */}
      <div className="glass code-panel" style={{ flex: 1, margin: 10, padding: 10 }}>

        {/* TABS */}
        <div className="tab-row" style={{ display: "flex", gap: 10 }}>
          {tabs.map((t, i) =>
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                padding: "5px 10px",
                borderRadius: 10,
                cursor: "pointer",
                background: t === active ? "#333" : "#222"
              }}
            >
              <span onClick={() => setActive(t)}>
                {t.path.split("/").pop()}
              </span>

              <span
                onClick={() => closeTab(t.path)}
                style={{ cursor: "pointer", opacity: .7 }}
              >
                ✖
              </span>
            </div>
          )}
        </div>

        {active &&
          <>
            <h4 style={{ opacity: .8 }}>{active.path}</h4>

            <button onClick={copyCode}><FaCopy /> Copy</button>

            <div className="code-content">
              <SyntaxHighlighter style={oneDark} showLineNumbers>
                {active.content}
              </SyntaxHighlighter>
            </div>
          </>
        }

        {!active && <p>Select a file to view</p>}
      </div>

      {/* RIGHT — CHAT */}
      <div className="glass chat-panel" style={{ width: 350, margin: 10, padding: 10 }}>

        <h3>🤖 Ask AI</h3>

        <div className="chat-messages">
          {messages.map((m, i) =>
            <div key={i} className={`message ${m.role}`}>
              {m.text}
            </div>
          )}

          {loading && <div className="message bot">Thinking…</div>}

          <div ref={bottomRef}></div>
        </div>

        <textarea
          rows="2"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          style={{ width: "100%", marginTop: 10 }}
          placeholder="Ask about the repo…"
        />

        <button
          onClick={ask}
          disabled={!question || loading}
        >
          Send
        </button>

      </div>
    </div>
  );
}
