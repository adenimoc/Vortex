@echo off
:: Cambiar al directorio del script para evitar problemas de ruta de trabajo
cd /d "%~dp0"

echo ==============================================
echo   Iniciando Vortex Asset HUD (Escritorio)
echo   Directorio de trabajo: %CD%
echo ==============================================
echo.

:: Verificar si python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no está instalado o no se encuentra en el PATH de Windows.
    echo Por favor instala Python para poder ejecutar esta aplicación.
    echo.
    pause
    exit /b
)

:: Verificar si las dependencias básicas están instaladas
python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Instalando dependencias necesarias - esto puede tardar unos momentos...
    python -m pip install -r requirements.txt
)

:: Ejecutar la aplicación de escritorio
echo [INFO] Lanzando interfaz gráfica...
python app.py

echo.
echo ==============================================
echo   Ejecución terminada.
echo ==============================================
pause
