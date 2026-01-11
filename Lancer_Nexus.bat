@echo off
:: ========================================
:: NEXUS - Lanceur d'interface
:: Double-cliquez sur ce fichier pour lancer Nexus
:: ========================================

echo.
echo ============================================
echo    NEXUS - Lancement de l'interface
echo ============================================
echo.

:: Lancement via WSL
wsl bash -c "cd ~/Nexus && source .venv/bin/activate && python interface.py"

:: Si erreur, afficher un message
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================
    echo ERREUR lors du lancement
    echo ============================================
    echo.
    echo Verifiez que :
    echo  - WSL est installe
    echo  - Le dossier ~/Nexus existe
    echo  - L'environnement virtuel .venv est cree
    echo.
    pause
)
```

### **Étape 3 : Sauvegarder**
```
Ctrl+X
Y
Entrée
