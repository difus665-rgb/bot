from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="Sky-Impacte Python Backend")

# Файл для збереження бази даних
DB_FILE = "si_db.json"

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def read_index():
    # Автоматически находит файл index.html в той же папке, где лежит op.py
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Помилка: файл index.html не знайдено в папці з скриптом!</h1>"

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("op:app", host="0.0.0.0", port=port)
