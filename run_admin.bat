@echo off
echo Starting Admin Panel...
echo.
echo Admin Panel will open in your browser
echo Login with:
echo   Username: admin
echo   Password: 826282
echo.
call venv\Scripts\activate.bat
streamlit run admin\admin_panel.py --server.port=8502
pause
