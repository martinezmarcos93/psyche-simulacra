@echo off
REM Construye el instalador de PSYCHE SIMULACRA en Windows.
REM Requisitos: Python 3.11+ en el PATH e Inno Setup 6 instalado.
cd /d "%~dp0\.."

echo [1/4] Entorno virtual de build...
if not exist .venv-build (python -m venv .venv-build || goto :error)
call .venv-build\Scripts\activate.bat || goto :error

echo [2/4] Dependencias...
python -m pip install --upgrade pip || goto :error
pip install -r requirements.txt -r requirements-build.txt || goto :error

echo [3/4] PyInstaller...
rmdir /s /q build dist\PsycheSimulacra 2>nul
pyinstaller packaging\psyche.spec --noconfirm || goto :error

echo [4/4] Inno Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" packaging\instalador.iss || goto :error

echo.
echo Listo: dist\instalador\PsycheSimulacra-Setup-*.exe
pause
exit /b 0

:error
echo.
echo FALLO el build (paso anterior). Revisar el mensaje de arriba.
pause
exit /b 1
