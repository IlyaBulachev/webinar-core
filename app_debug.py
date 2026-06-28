from flask import Flask, render_template
import os
import sys

# Выводим всю информацию для диагностики
print("=" * 60)
print("🔍 ДИАГНОСТИКА:")
print(f"📁 Текущая директория: {os.getcwd()}")
print(f"📁 Путь к файлу: {__file__}")
print(f"📁 Базовая директория: {os.path.dirname(os.path.abspath(__file__))}")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

print(f"📁 TEMPLATE_DIR: {TEMPLATE_DIR}")
print(f"📁 STATIC_DIR: {STATIC_DIR}")
print(f"📁 templates существует: {os.path.exists(TEMPLATE_DIR)}")
print(f"📁 static существует: {os.path.exists(STATIC_DIR)}")

if os.path.exists(TEMPLATE_DIR):
    print(f"📄 Файлы в templates: {os.listdir(TEMPLATE_DIR)}")
else:
    print("❌ Папка templates НЕ СУЩЕСТВУЕТ!")

print("=" * 60)

# Создаем приложение
app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"❌ Ошибка рендеринга: {str(e)}"

@app.route('/test')
def test():
    return "✅ Сервер работает!"

@app.route('/info')
def info():
    return f"""
    <h1>Информация о сервере</h1>
    <p>Базовая директория: {BASE_DIR}</p>
    <p>Папка templates: {TEMPLATE_DIR}</p>
    <p>templates существует: {os.path.exists(TEMPLATE_DIR)}</p>
    <p>Файлы в templates: {os.listdir(TEMPLATE_DIR) if os.path.exists(TEMPLATE_DIR) else 'Нет папки'}</p>
    """

if __name__ == '__main__':
    app.run(debug=True, port=5005)