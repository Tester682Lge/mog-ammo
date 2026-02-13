from flask import Flask, request, render_template_string, session, redirect, url_for
import os
import secrets

app = Flask(__name__)

# --- БЕЗОПАСНОСТЬ ---
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(24))
raw_passwords = os.environ.get('ALLOWED_PASSWORDS')
ALLOWED_PASSWORDS = [p.strip() for p in raw_passwords.split(',')] if raw_passwords else []

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
        if not (1 <= segment <= 10): return "Ошибка: Отрезок 1-10"
        if not (0 <= remaining <= 25): return "Ошибка: Патроны 0-25"
        
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

# --- СТИЛИ И ФОРМЫ ---
# CSS оставлен без изменений, как в твоем исходнике
STYLE = '''
<style>
* { box-sizing: border-box; }
body { 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
    margin: 0; padding: 10px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    min-height: 100vh; display: flex; align-items: center; justify-content: center;
}
.container { 
    background: white; padding: 25px; border-radius: 20px; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.1); max-width: 100%; margin: 0 auto;
}
h2 { color: #2c3e50; text-align: center; margin: 0 0 30px 0; font-size: 24px; font-weight: 700; }
.input-row { display: flex; flex-direction: column; gap: 20px; margin-bottom: 25px; }
.label-input { display: flex; flex-direction: column; align-items: center; gap: 8px; }
input { 
    width: 100%; max-width: 150px; text-align: center; padding: 15px; 
    border: 2px solid #e1e5e9; border-radius: 12px; font-size: 18px; background: #f8f9fa;
}
input:focus { outline: none; border-color: #4CAF50; box-shadow: 0 0 0 3px rgba(76,175,80,0.1); }
.buttons-row { display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; }
button { 
    background: linear-gradient(145deg, #4CAF50, #45a049); color: white; padding: 15px 30px; 
    border: none; border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer; min-width: 140px;
}
button.reset { background: linear-gradient(145deg, #f44336, #da190b); }
button.logout { background: #7f8c8d; padding: 10px; font-size: 12px; min-width: 100px; margin-top: 20px; width: 100%; }
.result { 
    background: linear-gradient(145deg, #e8f5e8, #c8e6c9); padding: 25px; margin-top: 25px; 
    border-radius: 15px; font-family: monospace; white-space: pre; border-left: 5px solid #4CAF50;
}
.error { background: #ffebee; color: #c62828; padding: 20px; margin-top: 20px; border-radius: 12px; text-align: center; }
.footer { font-size: 13px; color: #7f8c8d; text-align: center; margin-top: 25px; padding-top: 20px; border-top: 1px solid #ecf0f1; }
.author-link { color: #e74c3c; text-decoration: none; font-weight: 600; }
@media (max-width: 480px) {
    .container { padding: 20px 15px; }
    input { padding: 18px; font-size: 20px; }
    button { padding: 18px 25px; font-size: 17px; }
}
</style>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    # 1. Экран авторизации
    if 'auth' not in session:
        error_msg = ""
        if request.method == 'POST':
            if request.form.get('pwd') in ALLOWED_PASSWORDS:
                session['auth'] = True
                return redirect(url_for('index'))
            else:
                error_msg = '<div class="error">Неверный пароль!</div>'
        
        return render_template_string(f'''
            <!DOCTYPE html><html><head><meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {STYLE}</head><body><div class="container">
                <h2>🔐 Доступ</h2>
                <form method="POST">
                    <input type="password" name="pwd" placeholder="Пароль" required autofocus style="max-width:100%">
                    <button type="submit" style="width:100%; margin-top:10px">ВОЙТИ</button>
                </form>
                {error_msg}
            </div></body></html>
        ''')

    # 2. Твой оригинальный калькулятор
    result = ""
    error = ""
    if request.method == 'POST' and 'segment' in request.form:
        try:
            res_text = calc.calculate(int(request.form['segment']), int(request.form['remaining']))
            if "Ошибка" in res_text: error = res_text
            else: result = res_text
        except:
            error = "Только числа!"

    return render_template_string(f'''
<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Калькулятор ленты ПКТ для МОГ</title>
{STYLE}</head><body>
<div class="container">
<h2>🔫 Расчёт ленты ПКТ для МОГ</h2>
<form method="POST">
    <div class="input-row">
        <div class="label-input">
            <label>Отрезок (1-10)</label>
            <input name="segment" type="number" min="1" max="10" value="{request.form.get('segment','')}" required>
        </div>
        <div class="label-input">
            <label>Осталось (0-25)</label>
            <input name="remaining" type="number" min="0" max="25" value="{request.form.get('remaining','')}" required>
        </div>
    </div>
    <div class="buttons-row">
        <button type="submit">🔢 РАСЧИТАТЬ</button>
        <button type="reset" class="reset" onclick="window.location.href='/'">🔄 СБРОСИТЬ</button>
    </div>
</form>

{'<div class="error">'+error+'</div>' if error else ''}
{'<div class="result">'+result+'</div>' if result else ''}

<div class="footer">
    250 патронов (🟢Т>🔴БР>⚪️ЛПС) | 
    <a href="https://t.me/wtfneponn" class="author-link" target="_blank">💚 Автор (заслон 5)</a>
</div>

<form action="/logout" method="POST">
    <button type="submit" class="logout">🚪 ВЫЙТИ</button>
</form>
</div>
</body></html>
''')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('auth', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
