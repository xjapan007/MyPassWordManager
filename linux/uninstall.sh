#!/bin/bash

echo "Désinstallation de My Pass Manager..."
sudo echo "Permissions administrateur obtenues."

# 1. Supprimer le dossier de l'application
APP_DIR="/opt/MyPassManager"
echo "Suppression du dossier $APP_DIR..."
sudo rm -rf $APP_DIR

# 2. Supprimer le fichier .desktop du menu
DESKTOP_FILE="/usr/share/applications/mypassmanager.desktop"
echo "Suppression du menu des applications..."
sudo rm -f $DESKTOP_FILE

# 3. Note sur les données utilisateur
echo ""
echo "-----------------------------------------------------"
echo "Désinstallation terminée."
echo "Note : Vos données (coffre-fort) ne sont PAS supprimées."
echo "Elles se trouvent dans ~/.config/MyPassManager"
echo "-----------------------------------------------------"