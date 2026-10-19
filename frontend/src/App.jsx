import React, { useState } from 'react';
import './App.css';

function App() {
  const [expression, setExpression] = useState('2x^2 - 4x + 5');
  const [variable, setVariable] = useState('x');
  const [target, setTarget] = useState('3');
  const [loading, setLoading] = useState(false);
  const [resultData, setResultData] = useState(null);
  const [error, setError] = useState('');

  const handleCalculate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResultData(null);

    let formattedExpr = expression
      .replace(/(\d)([a-zA-Z])/g, '$1*$2')
      .replace(/\s+/g, '');

    try {
      const response = await fetch('http://192.168.1.38:8000/calculate-limit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expression: formattedExpr, variable, target }),
      });

      const data = await response.json();
      if (data.success) {
        setResultData(data);
      } else {
        setError(data.error || 'Terjadi kesalahan pada perhitungan.');
      }
    } catch (err) {
      setError('Gagal terhubung ke server backend FastAPI. Pastikan server sudah menyala.');
    } finally {
      setLoading(false);
    }
  };

  const insertShortcut = (val) => {
    setExpression((prev) => prev + val);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Kalkulator Limit Fungsi</h1>
        <p>Selesaikan perhitungan limit matematika secara simbolik &amp; bertahap</p>
      </header>

      <main className="calculator-main">
        <form onSubmit={handleCalculate} className="calc-form">
          <div className="input-group">
            <label>Variabel:</label>
            <input 
              type="text" 
              value={variable} 
              onChange={(e) => setVariable(e.target.value)} 
              maxLength={2} 
              required 
            />
          </div>

          <div className="input-group">
            <label>Mendekati Target:</label>
            <input 
              type="text" 
              value={target} 
              onChange={(e) => setTarget(e.target.value)} 
              required 
            />
          </div>

          <div className="input-group full-width">
            <label>Fungsi Matematika f({variable}):</label>
            <input 
              type="text" 
              value={expression} 
              onChange={(e) => setExpression(e.target.value)} 
              placeholder="Contoh: 2x^2 - 4x + 5" 
              required 
            />
          </div>

          <div className="shortcuts full-width">
            <span className="shortcut-label">Tombol Cepat:</span>
            <button type="button" onClick={() => insertShortcut('x')}>x</button>
            <button type="button" onClick={() => insertShortcut('^2')}>x²</button>
            <button type="button" onClick={() => insertShortcut('+')}>+</button>
            <button type="button" onClick={() => insertShortcut('-')}>-</button>
            <button type="button" onClick={() => insertShortcut('*')}>×</button>
            <button type="button" onClick={() => insertShortcut('/')}>/</button>
            <button type="button" onClick={() => insertShortcut('(')}>(</button>
            <button type="button" onClick={() => insertShortcut(')')}>)</button>
            <button type="button" onClick={() => insertShortcut('oo')}>∞</button>
            <button type="button" onClick={() => setExpression('')} style={{background: '#7f1d1d'}}>Reset</button>
          </div>

          <button type="submit" className="submit-btn full-width" disabled={loading}>
            {loading ? 'Menghitung...' : 'Hitung Limit'}
          </button>
        </form>

        {error && <div className="error-box">{error}</div>}

        {resultData && (
          <div className="result-section">
            <h2>Hasil Perhitungan</h2>
            <div className="result-card">
              <p><strong>Fungsi:</strong> f({variable}) = {expression}</p>
              <p className="final-ans"><strong>Hasil Limit:</strong> {resultData.latex_result}</p>
            </div>

            <div className="steps-container">
              <h3>Langkah perhitungan (sesuai urutan operasi matematika):</h3>
              <div className="pemdas-steps">
                {resultData.steps.map((step, idx) => (
                  <div key={idx} className="pemdas-group">
                    <h4>{step.title}</h4>
                    {step.maths && step.maths.map((m, mIdx) => (
                      <div key={mIdx} className="pemdas-math">{m}</div>
                    ))}
                    {step.subtitle && <p className="pemdas-subtitle">{step.subtitle}</p>}
                    {step.sub_maths && step.sub_maths.map((sm, smIdx) => (
                      <div key={smIdx} className="pemdas-math">{sm}</div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;