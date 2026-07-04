from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from models.schemas import ReportRequest
from services.github_service import get_repo_data
from services.analytics import calculate_bus_factor
from services.pdf_builder import build_report
import base64

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

@app.get("/ping")
def ping():
    return {"status": "alive"}

@app.post("/generate-report")
def generate_report(request: ReportRequest):
    data = get_repo_data(request.token, request.repo)

    if "error" in data:
        return {"error": data["error"]}

    analytics = calculate_bus_factor(
        data["contributors"],
        data["commits"]
    )

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

    pdf_bytes = pdf_buffer.read()
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    return JSONResponse(content={
        "pdf": pdf_base64,
        "filename": f"gitdigest-report.pdf"
    })
