@echo off
:: 1. Nos ubicamos en la carpeta del proyecto
cd /d "%~dp0"

:: 2. Levantamos el servidor en silencio (en segundo plano)
docker-compose up -d

:: 3. Esperamos 8 segundos a que arranque la base de datos
timeout /t 8 /nobreak >nul

:: 4. Abrimos Chrome en MODO APP (Sin barra de navegación, parece un programa real)
start chrome --app=http://localhost:8000/turnos/

:: 5. El script se cierra, pero el servidor sigue andando
exit