from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from models.schemas import ReportRequest
from services.github_service import get_repo_data
from services.analytics import calculate_bus_factor
from services.pdf_builder import build_report

app = FastAPI(title="GitDigest API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "Content-Disposition"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "GitDigest backend is running"}

@app.post("/generate-report")
def generate_report(request: ReportRequest):
    # Step 1 — fetch data from GitHub
    data = get_repo_data(request.token, request.repo)

    if "error" in data:
        return {"error": data["error"]}

    # Step 2 — run Bus Factor analytics
    analytics = calculate_bus_factor(
        data["contributors"],
        data["commits"]
    )

    # Step 3 — build the PDF
    try:
        pdf_buffer = build_report(
            request.repo,
            analytics,
            data["metadata"],
            data["commits"]
        )
        if pdf_buffer is None:
            return {"error": "PDF generation failed"}
    except Exception as e:
        return {"error": f"PDF generation error: {str(e)}"}

    # Get size for progress tracking
    pdf_bytes = pdf_buffer.read()
    pdf_size = len(pdf_bytes)

    def iter_pdf():
        yield pdf_bytes

    return StreamingResponse(
        iter_pdf(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="gitdigest-report.pdf"',
            "Content-Length": str(pdf_size),
        }
    )
