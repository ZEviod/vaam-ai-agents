@echo off
echo =====================================================
echo   AUTOMATED AI ACCOUNTING AGENT - SETUP
echo =====================================================
echo.

echo 📦 Installing dependencies...
python -m pip install schedule requests pandas python-dateutil
if errorlevel 1 (
    echo ❌ Failed to install some dependencies
    echo 💡 Try running as administrator or check Python installation
    pause
    exit /b 1
)

echo.
echo ✅ Dependencies installed successfully!

echo.
echo 📋 Setting up configuration...
if not exist .env (
    copy .env.example .env
    echo ✅ Configuration file created (.env)
    echo 🔧 Please edit .env file with your credentials
) else (
    echo ✅ Configuration file already exists
)

echo.
echo 🚀 Setup complete! 
echo.
echo To start the agent:
echo   python accounting_assistant.py
echo.
echo Or use the launcher:
echo   python run_agent.py
echo.
pause
