from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

class AmmoCalculator:
    def get_ammo_type(self, position):
        cycle = (position - 1) % 3
        if cycle == 0: return "🟢Т"
        elif cycle == 1: return "🔴БР"
        else: return "⚪️ЛПС"

    def count_ammo_by_position(self, total_used):
        t = total_used // 3 + (1 if total_used % 3 >= 1 else 0)
        br = total_used // 3 + (1 if total_used % 3 >= 2 else 0)
        lps = total_used // 3
        return t, br, lps

    def calculate(self, segment, remaining):
        if not (1 <= segment <= 10):
            return "Ошибка: Отрезок 1-10"
        if not (0 <= remaining <= 25):
            return "Ошибка: Патроны 0-25"
        
        used_in_segment = 25 - remaining
        total_used = (segment - 1) * 25 + used_in_segment
        last_fired = self.get_ammo_type(total_used) if total_used > 0 else "-"
        next_pos = total_used + 1
        next_type = self.get_ammo_type(next_pos) if remaining > 0 else "-"
        t_used, br_used, lps_used = self.count_ammo_by_position(total_used)
        
        return f"""Отрезок: {segment:2d}
Осталось: {remaining:2d}
В отрезке: {used_in_segment:2d}
Всего: {total_used:3d}/250
Ленте осталось: {250-total_used:3d}
Последний: {last_fired}
Следующий: {next_type}
🟢Т: {t_used:3d}
🔴БР: {br_used:3d}
⚪️ЛПС: {lps_used:3d}"""

calc = AmmoCalculator()

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    error = ""
    
    if request.method == 'POST':
        try:
            segment = int(request.form['segment'])
            remaining = int(request.form['remaining'])
            result = calc.calculate(segment, remaining)
        except:
            error = "Только числа!"
    
    html = '''
<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Калькулятор ленты ПКТ для МОГ</title>
<style>
* { box-sizing: border-box; }
body { 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
    margin: 0; padding: 10px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    min-height: 100vh;
}
.container { 
    background: white; 
    padding: 25px; 
    border-radius: 20px; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    max-width: 100%; 
    margin: 0 auto;
}
h2 { 
    color: #2c3e50; 
    text-align: center; 
    margin: 0 0 30px 0; 
    font-size: 24px;
    font-weight: 700;
}
.input-row {
    display: flex; 
    flex-direction: column; 
    gap: 20px; 
    margin-bottom: 25px;
}
.label-input {
    display: flex; 
    flex-direction: column; 
    align-items: center; 
    gap: 8px;
}
input { 
    width: 100%; 
    max-width: 120px;
    text-align: center; 
    padding: 15px; 
    border: 2px solid #e1e5e9; 
    border-radius: 12px; 
    font-size: 18px; 
    background: #f8f9fa;
    transition: all 0.2s;
}
input:focus { 
    outline: none; 
    border-color: #4CAF50; 
    box-shadow: 0 0 0 3px rgba(76,175,80,0.1);
}
.buttons-row {
    display: flex; 
    gap: 15px; 
    justify-content: center; 
    flex-wrap: wrap;
}
button { 
    background: linear-gradient(145deg, #4CAF50, #45a049); 
    color: white; 
    padding: 15px 30px; 
    border: none; 
    border-radius: 12px; 
    font-size: 16px; 
    font-weight: 600;
    cursor: pointer; 
    transition: all 0.2s;
    min-width: 140px;
    box-shadow: 0 4px 15px rgba(76,175,80,0.3);
}
button:hover { 
    transform: translateY(-2px); 
    box-shadow: 0 6px 20px rgba(76,175,80,0.4);
}
button:active { transform: translateY(0); }
button.reset { 
    background: linear-gradient(145deg, #f44336, #da190b); 
    box-shadow: 0 4px 15px rgba(244,67,54,0.3);
}
button.reset:hover { 
    box-shadow: 0 6px 20px rgba(244,67,54,0.4); 
}
.result { 
    background: linear-gradient(145deg, #e8f5e8, #c8e6c9); 
    padding: 25px; 
    margin-top: 25px; 
    border-radius: 15px; 
    font-family: 'SF Mono', Monaco, 'Consolas', monospace; 
    white-space: pre; 
    border-left: 5px solid #4CAF50;
    font-size: 15px;
    line-height: 1.6;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.05);
}
.error { 
    background: linear-gradient(145deg, #ffebee, #ffcdd2); 
    color: #c62828; 
    padding: 20px; 
    margin-top: 20px; 
    border-radius: 12px; 
    border-left: 5px solid #f44336;
    text-align: center;
    font-weight: 500;
}
.footer { 
    font-size: 13px; 
    color: #7f8c8d; 
    text-align: center; 
    margin-top: 25px; 
    padding-top: 20px; 
    border-top: 1px solid #ecf0f1;
}
.author-link {
    color: #e74c3c;
    text-decoration: none;
    font-weight: 600;
}
.author-link:hover {
    text-decoration: underline;
}
@media (max-width: 480px) {
    body { padding: 5px; }
    .container { padding: 20px 15px; margin: 5px; border-radius: 15px; }
    h2 { font-size: 20px; margin-bottom: 25px; }
    input { padding: 18px; font-size: 20px; max-width: 140px; }
    button { padding: 18px 25px; font-size: 17px; min-width: 130px; }
    .result { padding: 20px; font-size: 16px; }
}
</style>
</head>
<body>
<div class="container">
<h2>🔫 Расчёт ленты ПКТ для МОГ</h2>

<form method="POST">
    <div class="input-row">
        <div class="label-input">
            <label>Отрезок (1-10)</label>
            <input name="segment" type="number" min="1" max="10" value="{{ request.form.segment if request.form else '' }}" required>
        </div>
        <div class="label-input">
            <label>Осталось (0-25)</label>
            <input name="remaining" type="number" min="0" max="25" value="{{ request.form.remaining if request.form else '' }}" required>
        </div>
    </div>
    
    <div class="buttons-row">
        <button type="submit">🔢 РАСЧИТАТЬ</button>
        <button type="reset" class="reset">🔄 СБРОСИТЬ</button>
    </div>
</form>

{% if error %}
<div class="error">{{ error }}</div>
{% endif %}

{% if result %}
<div class="result">{{ result }}</div>
{% endif %}

<div class="footer">
    250 патронов (🟢Т>🔴БР>⚪️ЛПС) | 
    <a href="https://t.me/wtfneponn" class="author-link" target="_blank">💚 Автор (заслон 5)</a>
</div>
</div>
</body>
</html>
    '''
    return render_template_string(html, result=result, error=error)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
