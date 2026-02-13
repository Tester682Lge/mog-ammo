from flask import Flask, request, render_template_string, session, redirect, url_for
import os
import secrets

app = Flask(__name__)

# --- БЕЗОПАСНОСТЬ ---
# Если в Railway не задана переменная SECRET_KEY, генерируем случайную строку для защиты сессий
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(24))

# Получаем список паролей из Railway (например: "pass1,pass2,pass3")
# Если переменная не задана, список будет пустым, и войти никто не сможет
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

# --- ВЕРСТКА ---
BASE_HTML = '''
<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Калькулятор ПКТ</title>
<style>
* { box-sizing: border-box; }
body { 
    font-family: -apple-system, system-ui, sans-serif; 
    margin: 0; padding: 10px; background: #f0f2f5;
    min-height: 100vh; display: flex; align-items: center; justify-content: center;
}
.container { 
    background: white; padding: 25px; border-radius: 15px; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 100%; max-width: 380px;
}
h2, h3 { color: #2c3e50; text-align: center; margin-bottom: 20px; }
input { 
    width: 100%; padding: 12px; border: 2px solid #eee; 
    border-radius: 8px; margin-bottom: 12px; font-size: 16px;
}
button { 
    width: 100%; padding: 14px; border: none; border-radius: 8px; 
    background: #28a745; color: white; font-weight: bold; cursor: pointer; transition: 0.2s;
}
button:active { transform: scale(0.98); }
.logout { background: #6c757d; margin-top: 20px; font-size: 12px; padding: 8px; }
.result { 
    background: #f8f9fa; padding: 15px; border-radius: 8px; 
    font-family: monospace; white-space: pre; margin-top: 15px; border: 1px solid #ddd;
}
.error { color: #dc3545; text-align: center; margin-bottom: 10px; font-weight: bold; }
label { font-size: 14px; color: #666; margin-bottom: 4px; display: block; }
</style>
</head>
<body>
<div class="container">
    {{ content | safe }}
</div>
</body>
</html>
'''

# --- МАРШРУТЫ ---
@app.route('/', methods=['GET', 'POST'])
def index():
    # Проверка авторизации
    if 'auth' not in session:
        if request.method == 'POST' and 'pwd' in request.form:
            if request.form['pwd'] in ALLOWED_PASSWORDS:
                session['auth'] = True
                return redirect(url_for('index'))
            else:
                return render_template_string(BASE_HTML, content='''
                    <h2>Вход</h2>
                    <p class="error">Неверный пароль!</p>
                    <form method="POST"><input type="password" name="pwd" autofocus><button>ВОЙТИ</button></form>
                ''')
        return render_template_string(BASE_HTML, content='''
            <h2>Доступ закрыт</h2>
            <form method="POST"><input type="password" name="pwd" placeholder="Введите пароль" autofocus><button>ВОЙТИ</button></form>
        ''')

    # Основная логика калькулятора
    result = ""
    if request.method == 'POST':
        try:
            s = int(request.form['s'])
            r = int(request.form['r'])
            res = calc.calculate(s, r)
            result = f'<div class="result">{res}</div>'
        except:
            result = '<p class="error">Ошибка ввода данных!</p>'

    calc_content = f'''
        <h3>🐍 ПКТ Калькулятор</h3>
        <form method="POST">
            <label>Отрезок (1-10):</label>
            <input name="s" type="number" min="1" max="10" value="{request.form.get('s','')}" required>
            <label>Осталось в отрезке (0-25):</label>
            <input name="r" type="number" min="0" max="25" value="{request.form.get('r','')}" required>
            <button type="submit">РАССЧИТАТЬ</button>
        </form>
        {result}
        <form action="/logout" method="POST"><button class="logout">ВЫЙТИ</button></form>
    '''
    return render_template_string(BASE_HTML, content=calc_content)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('auth', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Стандартный запуск для Railway
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
