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
        
        target_str = req.target.strip().lower()
        if target_str in ["oo", "inf", "infinity", "∞"]:
            target_val = sp.oo
        elif target_str in ["-oo", "-inf", "-infinity", "-∞"]:
            target_val = -sp.oo
        else:
            target_val = sp.sympify(req.target.replace("^", "**"))
        
        result = sp.limit(expr, x, target_val)

        steps = []
        
        # Cek jika fungsi merupakan polinomial dan target numerik
        poly = sp.Poly(expr, x)
        if target_val.is_number:
            coeffs = poly.all_coeffs() # list koefisien dari pangkat tertinggi ke terendah
            degree = poly.degree()
            target_num = int(target_val) if target_val.is_integer else float(target_val)
            
            # 1. Pangkat
            pangkat_maths = []
            pangkat_dict = {}
            for p in range(degree, 1, -1):
                pow_val = target_num ** p
                pangkat_dict[p] = pow_val
                pangkat_maths.append(f"{target_num}^{p} = {pow_val}")
            
            if pangkat_maths:
                steps.append({
                    "title": "1. Pangkat:",
                    "maths": pangkat_maths
                })
            
            # 2. Perkalian
            perkalian_maths = []
            substituted_terms = []
            
            for idx, c in enumerate(coeffs):
                curr_pow = degree - idx
                c_num = int(c) if c.is_integer else float(c)
                
                if curr_pow > 1:
                    pow_res = pangkat_dict[curr_pow]
                    term_res = c_num * pow_res
                    if c_num != 1 and c_num != -1:
                        perkalian_maths.append(f"{abs(c_num)} × {pow_res} = {abs(term_res)}")
                    else:
                        term_res = pow_res if c_num == 1 else -pow_res
                    substituted_terms.append(term_res)
                elif curr_pow == 1:
                    term_res = c_num * target_num
                    if c_num != 1 and c_num != -1:
                        perkalian_maths.append(f"{abs(c_num)} × {target_num} = {abs(term_res)}")
                    substituted_terms.append(term_res)
                else: # suku konstanta (pangkat 0)
                    substituted_terms.append(c_num)

            # Susun string persamaan setelah perkalian
            eq_str = ""
            for idx, t in enumerate(substituted_terms):
                if idx == 0:
                    eq_str += f"{t}"
                else:
                    if t >= 0:
                        eq_str += f" + {t}"
                    else:
                        eq_str += f" - {abs(t)}"

            step2_dict = {"title": "2. Perkalian:" if pangkat_maths else "1. Perkalian:"}
            if perkalian_maths:
                step2_dict["maths"] = perkalian_maths
            step2_dict["subtitle"] = "Persamaan menjadi:"
            step2_dict["sub_maths"] = [eq_str]
            steps.append(step2_dict)
            
            # 3. Pengurangan dan Penjumlahan bertahap
            arith_maths = []
            curr_val = substituted_terms[0]
            for t in substituted_terms[1:]:
                next_val = curr_val + t
                sign_str = "+" if t >= 0 else "-"
                arith_maths.append(f"{curr_val} {sign_str} {abs(t)} = {next_val}")
                curr_val = next_val
                
            steps.append({
                "title": f"{len(steps) + 1}. Pengurangan dan Penjumlahan (dikerjakan dari kiri ke kanan):",
                "maths": arith_maths
            })
        else:
            sub_expr = expr.subs(x, target_val)
            steps.append({
                "title": "Penjabaran Perhitungan:",
                "maths": [f"= {sp.latex(sub_expr)}"]
            })

        return {
            "success": True,
            "latex_expression": sp.latex(expr),
            "latex_result": sp.latex(result),
            "steps": steps
        }
    except Exception as e:
        return {"success": False, "error": f"Format penulisan belum sesuai: {str(e)}"}