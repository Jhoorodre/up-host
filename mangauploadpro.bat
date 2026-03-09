@echo off
REM Muda para pasta do usuario para evitar problema com caminho UNC
cd /d %USERPROFILE%
REM Script para executar o Manga Uploader Pro no WSL
echo Executando Manga Uploader Pro...

REM Executa via WSL com configuracao de display
wsl -d Ubuntu-24.04 -e bash -l -c "cd ~/projetos/up-host && source venv/bin/activate && export QT_QPA_PLATFORM=wayland && python run.py"

pause
