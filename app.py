# --- 1. Importaciones ---
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import joblib 
import pandas as pd 
import os # Importamos 'os' para manejar rutas de archivos

# --- 2. Definición de la App ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi-llave-secreta-muy-dificil-de-adivinar'

# --- 3. "Base de datos" de usuarios ---
user_database = {
    "analista": {
        'password': generate_password_hash("1234"), 
        'email': 'analista@gamepulse.ai'
    }
}

# --- 4. Cargar el modelo de ML ---
model_path = 'game_predictor_model.pkl'
model = None

try:
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        print("Modelo de predicción cargado exitosamente.")
    else:
        print(f"ADVERTENCIA: No se encontró '{model_path}'.")
        print("Por favor, ejecuta 'python train_model.py' para crearlo.")
except Exception as e:
    print(f"Error al cargar el modelo: {e}")


# --- ¡DATOS FALTANTES AÑADIDOS! ---
# --- DATOS DE EJEMPLO PARA MÉTRICAS ---
GAME_METRICS_DATA = {
    "hollow-knight-silksong": {
        "name": "Hollow Knight: Silksong",
        "platform_icon": "🎮",
        "country_data": [
            {"pais": "Estados Unidos", "jugadores": "123,848", "total": "21.2%", "tendencia": "Sube"},
            {"pais": "China", "jugadores": "82,594", "total": "14.2%", "tendencia": "Sube"},
            {"pais": "Otros", "jugadores": "65,164", "total": "11.2%", "tendencia": "Sube"},
            {"pais": "Alemania", "jugadores": "49,747", "total": "8.5%", "tendencia": "Baja"},
            {"pais": "Brasil", "jugadores": "40,523", "total": "7.8%", "tendencia": "Sube"},
        ]
    },
    "counter-strike-2": {
        "name": "Counter-Strike 2",
        "platform_icon": "🎮",
        "country_data": [
            {"pais": "Estados Unidos", "jugadores": "310,450", "total": "17.2%", "tendencia": "Sube"},
            {"pais": "Rusia", "jugadores": "205,100", "total": "11.4%", "tendencia": "Estable"},
            {"pais": "Alemania", "jugadores": "150,300", "total": "8.3%", "tendencia": "Sube"},
        ]
    },
    "god-of-war-ragnarok": {
        "name": "God of War Ragnarök",
        "platform_icon": "🔵",
        "country_data": [
            {"pais": "Estados Unidos", "jugadores": "450,000", "total": "30.1%", "tendencia": "Estable"},
            {"pais": "Reino Unido", "jugadores": "180,000", "total": "12.0%", "tendencia": "Estable"},
        ]
    },
    "forza-horizon-5": {
        "name": "Forza Horizon 5",
        "platform_icon": "🟢",
        "country_data": [
            {"pais": "Estados Unidos", "jugadores": "112,000", "total": "24.0%", "tendencia": "Sube"},
            {"pais": "México", "jugadores": "98,000", "total": "21.0%", "tendencia": "Sube"},
        ]
    }
}

GAME_LIST = [
    {"slug": "counter-strike-2", "name": "Counter-Strike 2", "platform": "Steam", "icon": "🛡️"},
    {"slug": "apex-legends", "name": "Apex Legends", "platform": "Steam", "icon": "⚔️", "disabled": True},
    {"slug": "baldurs-gate-3", "name": "Baldur's Gate 3", "platform": "Steam", "icon": "❓", "disabled": True},
    {"slug": "cyberpunk-2077", "name": "Cyberpunk 2077", "platform": "Steam", "icon": "🤖", "disabled": True},
    {"slug": "hollow-knight-silksong", "name": "Hollow Knight: Silksong", "platform": "Steam", "icon": "🕷️"},
    {"slug": "rust", "name": "Rust", "platform": "Steam", "icon": "🛡️", "disabled": True},
    {"slug": "god-of-war-ragnarok", "name": "God of War Ragnarök", "platform": "PlayStation", "icon": "🪓"},
    {"slug": "marvels-spider-man-2", "name": "Marvel's Spider-Man 2", "platform": "PlayStation", "icon": "🕷️", "disabled": True},
    {"slug": "elden-ring", "name": "Elden Ring", "platform": "PlayStation", "icon": "👑", "disabled": True},
    {"slug": "forza-horizon-5", "name": "Forza Horizon 5", "platform": "Xbox", "icon": "🚗"},
    {"slug": "halo-infinite", "name": "Halo Infinite", "platform": "Xbox", "icon": "🤖", "disabled": True},
]
# --- FIN DE DATOS DE EJEMPLO ---


# --- 5. Decorador de Login ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- 6. Rutas de Autenticación (Login, Logout, Register) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_info = user_database.get(username) 
        if user_info and check_password_hash(user_info['password'], password):
            session['logged_in'] = True
            session['username'] = username
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form.get('email')
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if not username or not email or not password or not confirm_password:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('register'))
        if username in user_database:
            flash('El nombre de usuario ya existe.', 'danger')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        user_database[username] = {'password': hashed_password, 'email': email}
        print("Base de datos de usuarios actualizada:", user_database)
        flash('¡Registro exitoso! Por favor, inicia sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


# -----------------------------------------------
# 7. RUTAS DE LA APLICACIÓN
# -----------------------------------------------

@app.route('/')
@login_required
def dashboard():
    summary_data = {
        'juegos_analizados': 13,
        'predicciones_activas': 57,
        'precision_modelo': "89.4%",
        'jugadores_monitoreados': "23.5M"
    }
    
    chart_data = {
        "labels": ["Feb", "Abr", "Jun", "Jul", "Ago", "Oct", "Dic"],
        "datasets": [
            {
                "label": "Juego A (Pico)",
                "data": [2000, 10000, 4000, 5000, 4500, 8500, 9500],
                "borderColor": "#3e95cd",
                "fill": False,
                "tension": 0.1
            },
            {
                "label": "Juego B (Resurgimiento)",
                "data": [4000, 2500, 2000, 3000, 4000, 3000, 4500],
                "borderColor": "#8e5ea2",
                "fill": False,
                "tension": 0.1
            },
            {
                "label": "Juego C (Estable)",
                "data": [2000, 2500, 2000, 2500, 2500, 2500, 3000],
                "borderColor": "#3cba9f",
                "fill": False,
                "tension": 0.1
            }
        ]
    }
    
    return render_template('dashboard.html', 
                           summary=summary_data, 
                           active_page='dashboard',
                           chart_data=chart_data) 

@app.route('/juegos')
@login_required
def juegos_page():
    return render_template('juegos.html', active_page='juegos')

# --- ¡RUTA DE MÉTRICAS ACTUALIZADA! ---
@app.route('/metricas')
@login_required
def metricas_page():
    # Pasa la lista de juegos a la plantilla
    return render_template('metricas.html', 
                           active_page='metricas',
                           game_list=GAME_LIST) # <-- ¡Pasa la lista de juegos!

# --- ¡NUEVA RUTA DE DETALLE DE MÉTRICAS AÑADIDA! ---
@app.route('/metricas/<string:game_slug>')
@login_required
def metricas_detalle(game_slug):
    game_data = GAME_METRICS_DATA.get(game_slug)
    if not game_data:
        flash("Métricas no encontradas para este juego.", "danger")
        return redirect(url_for('metricas_page'))
    
    return render_template('metricas_detalle.html', 
                           active_page='metricas', 
                           game=game_data)

@app.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze_page():
    
    # Si la petición es POST (el usuario envió el formulario)
    if request.method == 'POST':
        # 1. Obtenemos los datos de texto del formulario
        game_title = request.form.get('game_title')
        platform = request.form.get('platform')
        release_date = request.form.get('release_date')
        info_adicional = request.form.get('info_adicional')
  # --- SIMULACIÓN DE IA (Aquí iría la llamada a Gemini) ---
        # ----------------------------------------------------
        # Por ahora, solo simulamos una respuesta basada en el título
        # para que veas que funciona.
        # ----------------------------------------------------
      
        print(f"Iniciando análisis de IA para: {game_title}")
        print(f"Información recibida: {info_adicional}")
        
        simulated_result = {
            "titulo_analizado": game_title,
            "factores_clave": [
                "Fuerte expectativa en redes sociales (Hype).",
                f"Lanzamiento en plataforma popular ({platform}).",
                "Mecánicas de juego innovadoras (basado en 'info_adicional')."
            ],
            "prediccion_patron": "Se predice un 'Apogeo en Lanzamiento' (Pico de demanda inicial) similar al caso de Hollow Knight: Silksong."
        }
        # ----------------------------------------------------

        # 3. Devolvemos el resultado como JSON
        # (El JavaScript en analyze.html lo recibirá)
        return jsonify(simulated_result)

    # Si la petición es GET, solo mostramos la página con el formulario
    return render_template('analyze.html', 
                           active_page='analyze')

# ... (tus otras rutas, como /proyecciones, /probar, /perfil) ...

@app.route('/proyecciones')
@login_required
def proyecciones_page():
    return render_template('proyecciones.html', active_page='proyecciones')

@app.route('/probar')
@login_required
def probar_page():
    return render_template('probar.html', active_page='probar')

# --- ¡RUTA DE PERFIL AÑADIDA! ---
@app.route('/perfil')
@login_required
def perfil_page():
    return render_template('perfil.html', active_page='perfil') 

# --- 8. Ejecutar la App ---
if __name__ == '__main__':
    app.run(debug=True)