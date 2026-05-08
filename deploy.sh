# ----- Шаг 1: Установка зависимостей -----
echo "[1/4] Установка зависимостей Python..."
pip install -r requirements.txt


# ----- Шаг 2: Миграция базы данных -----
echo "[2/4] Выполнение миграции базы данных..."
python manage_sniffer.py migrate --run-syncdb


# ----- Шаг 3: Создание папки для графиков -----
echo "[3/4] Создание папки media/sniffer_charts..."
mkdir -p media/sniffer_charts


# ----- Шаг 4: Запуск сервера -----
echo "[4/4] Запуск Django-сервера на порту 3000..."
echo "       Откройте Preview для просмотра дашборда."
echo ""
echo "============================================"
echo " Сервер запущен: http://0.0.0.0:3000/"
echo " Для остановки нажмите Ctrl+C"
echo "============================================"
echo ""

python manage_sniffer.py runserver 0.0.0.0:3000