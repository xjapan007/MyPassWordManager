# My PassWord Manager (Mon Manager De PassWord)

Un gestionnaire de mots de passe de bureau, simple, sécurisé et multiplateforme (Windows & Linux) construit en Python.

![Capture d'écran de My PassWord Manager](https://github.com/xjapan007/MyPassWordManager/issues/1#issue-3566326248)

## 📖 Description

Ce projet est un gestionnaire de mots de passe local. Il ne synchronise rien sur le cloud. Votre coffre-fort est un fichier **chiffré** stocké localement sur votre machine, protégé par un **mot de passe maître**.

Construit avec :
* **Python 3**
* **CustomTkinter** pour l'interface graphique moderne.
* **Cryptography** (Fernet) pour un chiffrement AES-256 robuste.

## ✨ Fonctionnalités

* 🔒 **Coffre-fort Chiffré :** Vos données sont illisibles sans votre mot de passe maître.
* 💻 **Multiplateforme :** Fonctionne sous Windows et Linux avec un stockage des données adapté à chaque OS.
* 🎲 **Générateur de Mots de Passe :** Créez des mots de passe forts directement depuis l'application.
* 📋 **Presse-papiers Sécurisé :** Copiez vos identifiants et mots de passe (effacement automatique après 30s).
* ⏱️ **Verrouillage Automatique :** L'application se verrouille seule après 5 minutes d'inactivité.
* 🔐 **Double Vérification :** Demande à nouveau le mot de passe maître pour afficher les informations sensibles.
* 🔎 **Recherche Instantanée :** Trouvez rapidement vos services.

---

## ⬇️ Installation

### 🖥️ Pour Windows

La méthode la plus simple est d'utiliser l'installateur.

1.  Allez sur la page **[Releases](https://github.com/TON_NOM_UTILISATEUR/TON_REPO/releases)** de ce projet.
2.  Téléchargez le dernier `setup-MyPassManager.exe`.
3.  Lancez l'installateur et suivez les instructions.
4.  L'application sera disponible dans votre Menu Démarrer.

### 🐧 Pour Linux (Testé sur Debian/Ubuntu)

Vous pouvez utiliser le script d'installation pour l'installer proprement.

1.  **Clonez ce dépôt (ou téléchargez le ZIP) :**
    ```bash
    git clone [https://github.com/TON_NOM_UTILISATEUR/TON_REPO.git](https://github.com/TON_NOM_UTILISATEUR/TON_REPO.git)
    cd MyPassManager
    ```

2.  **Installez les dépendances Python :**
    ```bash
    sudo pip3 install -r requirements.txt
    ```

3.  **Lancez le script d'installation :**
    (Le script va copier les fichiers dans `/opt/MyPassManager` et ajouter une icône au menu des applications)
    ```bash
    chmod +x ./linux/install.sh
    sudo ./linux/install.sh
    ```

4.  Vous pouvez maintenant lancer "My PassWord Manager" depuis votre menu d'applications !

---

## 🛠️ Pour les Développeurs (Construire depuis la source)

Si vous voulez simplement lancer le script sans l'installer :

1.  **Clonez le dépôt :**
    ```bash
    git clone [https://github.com/TON_NOM_UTILISATEUR/TON_REPO.git](https://github.com/TON_NOM_UTILISATEUR/TON_REPO.git)
    cd MyPassManager
    ```

2.  **Créez un environnement virtuel (recommandé) :**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Sur Linux/macOS
    .\venv\Scripts\activate   # Sur Windows
    ```

3.  **Installez les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Lancez l'application :**
    ```bash
    python3 src/coffre_final.py
    ```