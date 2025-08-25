@echo off
REM Script para executar o Manga Uploader Pro no WSL
echo Executando Manga Uploader Pro...

REM Ativa ambiente virtual e executa o programa
wsl -d Ubuntu -e bash -c "cd /home/jhoorodr/Projetos/Projetos-code/up-host && source venv/bin/activate && python run.py"

pause
