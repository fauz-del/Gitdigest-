import { useState } from "react"

export default function App() {
  const [token, setToken] = useState("")
  const [repo, setRepo] = useState("")
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [stage, setStage] = useState("")
  const [error, setError] = useState("")

  const handleGenerate = async () => {
    if (!token || !repo) {
      setError("Both fields are required")
      return
    }

    setError("")
    setLoading(true)
    setProgress(0)
    setStage("Connecting to GitHub...")

    try {
      const response = await fetch("http://localhost:8000/generate-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, repo })
      })

      if (!response.ok) {
        const err = await response.json()
        setError(err.error || "Something went wrong")
        setLoading(false)
        return
      }

      setStage("Analyzing repository...")
      setProgress(20)

      const contentLength = response.headers.get("Content-Length")
      const total = contentLength ? parseInt(contentLength) : null
      const reader = response.body.getReader()
      const chunks = []
      let received = 0

      setStage("Generating PDF...")
      setProgress(40)

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        chunks.push(value)
        received += value.length

        if (total) {
          const percent = Math.min(40 + Math.round((received / total) * 55), 95)
          setProgress(percent)
          setStage("Downloading report...")
        }
      }

      setProgress(100)
      setStage("Done!")

      // Trigger download
      const blob = new Blob(chunks, { type: "application/pdf" })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `gitdigest-${repo.replace("/", "-")}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)

      setTimeout(() => {
        setLoading(false)
        setProgress(0)
        setStage("")
      }, 2000)

    } catch (err) {
      setError("Could not connect to backend")
      setLoading(false)
      setProgress(0)
      setStage("")
    }
  }

  return (
    <div className="min-h-screen bg-[#0D1117] text-[#C9D1D9] flex flex-col items-center px-4 py-12">

      {/* Header */}
      <div className="flex items-center gap-3 mb-2">
        <svg height="28" viewBox="0 0 16 16" fill="#C9D1D9">
          <path d="M8 0a8 8 0 0 0-2.53 15.59c.4.07.55-.17.55-.38l-.01-1.49c-2.01.37-2.65-.86-2.65-1.78-.36-.84-.74-1.07-.74-1.07-.61-.42.05-.41.05-.41.67.05 1.02.69 1.02.69.6 1.03 1.58.73 1.96.56.06-.43.23-.73.42-.9-1.49-.17-3.04-.74-3.04-3.3 0-.73.26-1.32.69-1.79-.07-.17-.3-.86.07-1.79 0 0 .56-.18 1.84.68a6.4 6.4 0 0 1 3.36 0c1.28-.86 1.84-.68 1.84-.68.37.93.14 1.62.07 1.79.43.47.69 1.06.69 1.79 0 2.57-1.56 3.13-3.05 3.3.24.21.46.62.46 1.25l-.01 1.85c0 .21.15.45.55.38A8 8 0 0 0 8 0Z"/>
        </svg>
        <h1 className="text-2xl font-semibold text-white">GitDigest</h1>
      </div>
      <p className="text-[#8B949E] text-sm mb-10">
        Turn any public GitHub repo into a professional PDF report
      </p>

      {/* Card */}
      <div className="w-full max-w-lg bg-[#161B22] border border-[#30363D] rounded-md p-6">

        {/* Token input */}
        <div className="mb-4">
          <label className="block text-sm font-semibold mb-1">
            Personal access token
            <span className="text-[#8B949E] font-normal ml-2 text-xs">
              public_repo scope only
            </span>
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

        {/* Repo input */}
        <div className="mb-5">
          <label className="block text-sm font-semibold mb-1">
            Repository
          </label>
          <input
            type="text"
            placeholder="facebook/react"
            value={repo}
            onChange={e => setRepo(e.target.value)}
            disabled={loading}
            className="w-full bg-[#0D1117] border border-[#30363D] rounded-md px-3 py-2 text-sm font-mono text-[#C9D1D9] placeholder-[#5b6470] focus:outline-none focus:border-[#1F6FEB] focus:ring-1 focus:ring-[#1F6FEB] disabled:opacity-50"
          />
        </div>

        {/* Error */}
        {error && (
          <div className="mb-4 text-sm text-[#F85149] bg-[#F8514915] border border-[#F8514940] rounded-md px-3 py-2">
            {error}
          </div>
        )}

        {/* Progress bar */}
        {loading && (
          <div className="mb-4">
            <div className="flex justify-between text-xs text-[#8B949E] mb-1">
              <span>{stage}</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full h-1.5 bg-[#0D1117] rounded-full overflow-hidden border border-[#30363D]">
              <div
                className="h-full bg-[#238636] rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Button */}
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full bg-[#238636] hover:bg-[#3FB950] disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-2 rounded-md text-sm transition-colors duration-150"
        >
          {loading ? "Working..." : "Generate report"}
        </button>

        <p className="text-center text-xs text-[#8B949E] mt-4">
          Token is never stored — used only for this request
        </p>
      </div>

      {/* Footer */}
      <p className="text-[#8B949E] text-xs mt-10">
        Public repos only · Bus Factor analysis · PDF export
      </p>
    </div>
  )
}
