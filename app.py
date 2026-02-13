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
        
        # ✅ ИСПРАВЛЕНО: f"{число:3d}" вместо {число:3d}
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
<html><head><meta charset="utf-8">
<title>Калькулятор ленты ПКТ для МОГ</title>
<style>
body { font-family: Arial; max-width: 400px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
.container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
h2 { color: #333; text-align: center; margin-bottom: 30px; }
input { width: 80px; text-align: center; padding: 10px; margin: 10px 5px; border: 2px solid #ddd; border-radius: 5px; font-size: 16px; }
button { background: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin: 10px 5px; }
button:hover { background: #45a049; }
button.reset { background: #f44336; }
button.reset:hover { background: #da190b; }
button.author { background: #ff6b6b; padding: 8px 16px; font-size: 14px; }
button.author:hover { background: #ff5252; }
.result { background: #e8f5e8; padding: 20px; margin-top: 20px; border-radius: 5px; font-family: 'Consolas', monospace; white-space: pre; border-left: 4px solid #4CAF50; }
.error { background: #ffebee; color: #c62828; padding: 15px; margin-top: 20px; border-radius: 5px; border-left: 4px solid #f44336; }
.info { font-size: 12px; color: #666; text-align: center; margin-top: 20px; }
.buttons { text-align: center; margin-top: 15px; }
</style></head>
<body>
<div class="container">
<h2>🔫 Расчёт ленты ПКТ для МОГ</h2>
<form method="POST">
    <div style="text-align: center;">
    Отрезок (1-10): <input name="segment" type="number" min="1" max="10" value="{{ request.form.segment if request.form else '' }}" required><br><br>
    Осталось (0-25): <input name="remaining" type="number" min="0" max="25" value="{{ request.form.remaining if request.form else '' }}" required><br><br>
    <button type="submit">🧮 РАСЧИТАТЬ</button>
    <button type="reset" class="reset">🔄 СБРОСИТЬ</button>
    </div>
</form>

<div class="buttons">
    <a href="https://t.me/wtfneponn"><button class="author">💚 Автор (заслон 5)</button></a>
</div>

{% if error %}
<div class="error">{{ error }}</div>
{% endif %}

{% if result %}
<div class="result">{{ result }}</div>
{% endif %}

<div class="info">250 патронов (🟢Т>🔴БР>⚪️ЛПС)</div>
</div>
</body></html>
    '''
    return render_template_string(html, result=result, error=error)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
