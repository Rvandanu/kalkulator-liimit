from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sympy as sp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class LimitRequest(BaseModel):
    expression: str
    variable: str
    target: str

@app.post("/calculate-limit")
def calculate_limit(req: LimitRequest):
    try:
        x = sp.Symbol(req.variable)
        expr_str = req.expression.replace("^", "**")
        expr = sp.sympify(expr_str)
        
        # Format target nilai limit
        target_str = req.target.strip().lower()
        if target_str in ["oo", "inf", "infinity", "∞"]:
            target_val = sp.oo
        elif target_str in ["-oo", "-inf", "-infinity", "-∞"]:
            target_val = -sp.oo
        else:
            target_val = sp.sympify(req.target.replace("^", "**"))
        
        steps = []
        
        # Langkah 1: Tuliskan Soal
        steps.append({
            "title": "Langkah 1: Bentuk Limit Awal",
            "description": f"Substitusikan nilai variabel mendekati target ke dalam fungsi:",
            "math": f"\\lim_{{{req.variable} \\to {req.target}}} \\left({sp.latex(expr)}\\right)"
        })
        
        # Langkah 2: Substitusi Angka Langsung
        # Membuat ekspresi dengan mengganti variabel x menjadi nilai target
        sub_expr = expr.subs(x, target_val)
        
        steps.append({
            "title": "Langkah 2: Substitusi Nilai Variabel",
            "description": f"Ganti setiap nilai {req.variable} dengan {req.target}:",
            "math": f"= {sp.latex(expr).replace(req.variable, f'({req.target})')}"
        })
        
        # Langkah 3: Hitung Hasil Operasi
        steps.append({
            "title": "Langkah 3: Hitung Hasil Akhir",
            "description": "Selesaikan operasi aritmatika dari substitusi di atas:",
            "math": f"= {sp.latex(sub_expr)}"
        })

        # Hitung hasil limit via SymPy (mencakup kasus limit khusus/faktor jika tak tentu)
        result = sp.limit(expr, x, target_val)

        return {
            "success": True,
            "latex_expression": sp.latex(expr),
            "latex_result": sp.latex(result),
            "steps": steps
        }
    except Exception as e:
        return {"success": False, "error": f"Format penulisan belum sesuai: {str(e)}"}