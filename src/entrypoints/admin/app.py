from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from bootstrap.container import get_container

admin_app = FastAPI(title="AI Platform Admin Dashboard")


@admin_app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Interactive Admin Dashboard for traces, prompts, and datasets."""
    container = get_container()
    feedbacks = await container.relational_repo.get_feedbacks()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>AI Platform - Admin Console</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: #0f172a; color: #f8fafc; }}
            header {{ background: #1e293b; padding: 1.5rem 2rem; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }}
            h1 {{ margin: 0; font-size: 1.5rem; color: #38bdf8; }}
            .container {{ max-width: 1200px; margin: 2rem auto; padding: 0 1rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem; }}
            .card {{ background: #1e293b; border-radius: 8px; border: 1px solid #334155; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }}
            h2 {{ margin-top: 0; font-size: 1.2rem; color: #94a3b8; border-bottom: 1px solid #334155; padding-bottom: 0.5rem; }}
            .badge {{ display: inline-block; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }}
            .badge-green {{ background: #065f46; color: #34d399; }}
            .badge-blue {{ background: #1e3a8a; color: #60a5fa; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; font-size: 0.9rem; }}
            th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #334155; }}
            th {{ color: #94a3b8; }}
        </style>
    </head>
    <body>
        <header>
            <h1>AI Platform Production Console</h1>
            <span class="badge badge-green">SYSTEM HEALTHY</span>
        </header>
        <div class="container">
            <div class="card">
                <h2>Quản lý Traces & Observability</h2>
                <p>Theo dõi thời gian thực các span, latency, và chi phí USD cho từng model.</p>
                <p>Endpoint Metrics: <a href="/metrics" style="color: #38bdf8;">/metrics</a></p>
                <span class="badge badge-blue">OpenTelemetry Tracing: Enabled</span>
            </div>
            <div class="card">
                <h2>Prompt Registry & Versioning</h2>
                <p>Duyệt và phân phối template prompt đa phiên bản:</p>
                <ul>
                    <li><code>rag_answer:v1</code> (Production baseline)</li>
                    <li><code>rag_answer:v2</code> (Staging / CoT enabled)</li>
                </ul>
            </div>
            <div class="card">
                <h2>Phản hồi người dùng (Feedback)</h2>
                <table>
                    <tr><th>Trace ID</th><th>Đánh giá</th><th>Ghi chú</th></tr>
                    {"".join(f"<tr><td>{f.trace_id}</td><td>{'👍 Thumbs Up' if f.rating == 1 else '👎 Thumbs Down'}</td><td>{f.comment or ''}</td></tr>" for f in feedbacks) if feedbacks else "<tr><td colspan='3'>Chưa có phản hồi nào</td></tr>"}
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
