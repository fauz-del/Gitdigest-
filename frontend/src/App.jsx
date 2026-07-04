import { useState } from "react"

const API_URL = "https://gitdigest-production.up.railway.app"

export default function App() {
  const [token, setToken] = useState("")
  const [repo, setRepo] = useState("")
  const [loading, setLoading] = useState(false)
  const [stage, setStage] = useState("")
  const [error, setError] = useState("")
  const [pdfUrl, setPdfUrl] = useState(null)
  const [filename, setFilename] = useState("report.pdf")

  const base64ToBlob = (base64) => {
    const binary = atob(base64)
    const bytes = new Uint8Array(binary.length)
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i)
    }
    return new Blob([bytes], { type: "application/pdf" })
  }

  const handleGenerate = async () => {
    if (!token || !repo) {
      setError("Both fields are required")
      return
    }

    setError("")
    setPdfUrl(null)
    setLoading(true)
    setStage("Connecting to server...")

    try {
      const response = await fetch(`${API_URL}/generate-report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, repo })
      })

      setStage("Building PDF...")

      const data = await response.json()

      if (data.error) {
        setError(data.error)
        setLoading(false)
        return
      }

      const blob = base64ToBlob(data.pdf)
      const url = window.URL.createObjectURL(blob)

      setPdfUrl(url)
      setFilename(data.filename || "gitdigest-report.pdf")
      setStage("Done!")
      setLoading(false)

    } catch (err) {
      setError(`Error: ${err.message}`)
      setLoading(false)
      setStage("")
    }
  }

  return (
    <div className="min-h-screen bg-[#0D1117] text-[#C9D1D9] flex flex-col items-center px-4 py-12">

      <div className="flex items-center gap-3 mb-2">
        <svg height="28" viewBox="0 0 16 16" fill="#C9D1D9">
          <path d="M8 0a8 8 0 0 0-2.53 15.59c.4.07.55-.17.55-.38l-.01-1.49c-2.01.37-2.65-.86-2.65-1.78-.36-.84-.74-1.07-.74-1.07-.61-.42.05-.41.05-.41.67.05 1.02.69 1.02.69.6 1.03 1.58.73 1.96.56.06-.43.23-.73.42-.9-1.49-.17-3.04-.74-3.04-3.3 0-.73.26-1.32.69-1.79-.07-.17-.3-.86.07-1.79 0 0 .56-.18 1.84.68a6.4 6.4 0 0 1 3.36 0c1.28-.86 1.84-.68 1.84-.68.37.93.14 1.62.07 1.79.43.47.69 1.06.69 1.79 0 2.57-1.56 3.13-3.05 3.3.24.21.46.62.46 1.25l-.01 1.85c0 .21.15.45.55.38A8 8 0 0 0 8 0Z"/>
        </svg>
        <h1 className="text-2xl font-semibold text-white">GitDigest</h1>
      </div>
      <p className="text-[#8B949E] text-sm mb-10">
        Turn any public GitHub repo into a professional PDF report
      </p>

      <div className="w-full max-w-lg bg-[#161B22] border border-[#30363D] rounded-md p-6">

        <div className="mb-4">
          <label className="block text-sm font-semibold mb-1">
            Personal access token
            <span className="text-[#8B949E] font-normal ml-2 text-xs">public_repo scope only</span>
          </label>
          <input
            type="password"
            placeholder="ghp_••••••••••••••••••••"
            value={token}
            onChange={e => setToken(e.target.value)}
            disabled={loading}
            className="w-full bg-[#0D1117] border border-[#30363D] rounded-md px-3 py-2 text-sm font-mono text-[#C9D1D9] placeholder-[#5b6470] focus:outline-none focus:border-[#1F6FEB] focus:ring-1 focus:ring-[#1F6FEB] disabled:opacity-50"
          />
        </div>

        <div className="mb-5">
          <label className="block text-sm font-semibold mb-1">Repository</label>
          <input
            type="text"
            placeholder="facebook/react"
            value={repo}
            onChange={e => setRepo(e.target.value)}
            disabled={loading}
            className="w-full bg-[#0D1117] border border-[#30363D] rounded-md px-3 py-2 text-sm font-mono text-[#C9D1D9] placeholder-[#5b6470] focus:outline-none focus:border-[#1F6FEB] focus:ring-1 focus:ring-[#1F6FEB] disabled:opacity-50"
          />
        </div>

        {error && (
          <div className="mb-4 text-sm text-[#F85149] bg-[#F8514915] border border-[#F8514940] rounded-md px-3 py-2">
            {error}
          </div>
        )}

        {loading && (
          <div className="mb-4 text-center">
            <div className="inline-block w-5 h-5 border-2 border-[#238636] border-t-transparent rounded-full animate-spin mb-2" />
            <p className="text-xs text-[#8B949E]">{stage}</p>
            <p className="text-xs text-[#8B949E] mt-1">This may take 30-60 seconds...</p>
          </div>
        )}

        {pdfUrl && (
          <a
            href={pdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            download={filename}
            className="block w-full text-center bg-[#238636] hover:bg-[#3FB950] text-white font-semibold py-3 rounded-md text-sm transition-colors duration-150 mb-3"
          >
            ⬇ Open PDF Report
          </a>
        )}

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full bg-[#1F6FEB] hover:bg-[#388bfd] disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-2 rounded-md text-sm transition-colors duration-150"
        >
          {loading ? "Working..." : "Generate report"}
        </button>

        <p className="text-center text-xs text-[#8B949E] mt-4">
          Token is never stored — used only for this request
        </p>
      </div>

      <p className="text-[#8B949E] text-xs mt-10">
        Public repos only · Bus Factor analysis · PDF export
      </p>
    </div>
  )
}
