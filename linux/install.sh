#!/bin/bash

# Demande le mot de passe admin au début
echo "Installation de My Pass Manager..."
sudo echo "Permissions administrateur obtenues."

# 1. Créer le dossier de l'application
APP_DIR="/opt/MyPassManager"
echo "Création du dossier dans $APP_DIR..."
sudo mkdir -p $APP_DIR

# 2. Copier les fichiers de l'application
# (On suppose que le script est lancé depuis le dossier du projet)
echo "Copie des fichiers de l'application..."
sudo cp ./coffre_final.py $APP_DIR/
sudo cp ./votre_icone.png $APP_DIR/

# 3. Copier le fichier .desktop dans le menu des applications
DESKTOP_FILE="/usr/share/applications/mypassmanager.desktop"
echo "Ajout au menu des applications..."
sudo cp ./mypassmanager.desktop $DESKTOP_FILE

# 4. Donner les bonnes permissions
sudo chmod 755 $APP_DIR/coffre.py
sudo chmod 644 $DESKTOP_FILE
sudo chmod 644 $APP_DIR/coffre.png

echo ""
echo "-----------------------------------------------------"
echo "Installation terminée !"
echo "Vous pouvez maintenant trouver 'My PassWord Manager' dans votre menu d'applications."
echo "-----------------------------------------------------"