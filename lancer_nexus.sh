#!/bin/bash
# ========================================
# NEXUS - Lanceur d'interface (Linux/WSL)
# ========================================

echo ""
echo "============================================"
echo "   🤖 NEXUS - Lancement de l'interface"
echo "============================================"
echo ""

# Aller dans le dossier Nexus
cd ~/Nexus

# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer l'interface
python interface.py
