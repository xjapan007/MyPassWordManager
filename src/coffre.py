import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import base64
import string
import secrets
import platform  # <-- NÉCESSAIRE POUR LA DÉTECTION D'OS
import sys  # <--- AJOUTE CET IMPORT
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# --- NOUVEAU: Fichiers de configuration cachés (Multiplateforme) ---
APP_NAME = "MyPassManager"

if platform.system() == "Windows":
    # Chemin pour Windows (ex: C:\Users\bruno\AppData\Roaming\MyPassManager)
    CONFIG_DIR = os.path.join(os.environ.get('APPDATA'), APP_NAME)
else:
    # Chemin pour Linux/macOS (ex: /home/bruno/.config/MyPassManager)
    CONFIG_DIR = os.path.join(os.path.expanduser("~/.config"), APP_NAME)

VAULT_FILE = os.path.join(CONFIG_DIR, "vault.enc")
SALT_FILE = os.path.join(CONFIG_DIR, "salt.key")

# S'assurer que le dossier de config existe
os.makedirs(CONFIG_DIR, exist_ok=True)

# --- NOUVEAU: Fonction pour trouver les fichiers "gelés" ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Configuration du Look ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- Constantes de sécurité ---
CLIPBOARD_CLEAR_TIME_MS = 30000  # 30 secondes
AUTO_LOCK_TIME_MS = 300000     # 5 minutes

class PasswordManager(ctk.CTk):
    def __init__(self, key):
        super().__init__()
        
        # --- NOUVEAU: Définir l'icône de la fenêtre ---
        # Remplace "votre_icone.ico" par le VRAI nom de ton fichier .ico
        try:
            icon_path = resource_path("coffre.ico") 
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Erreur chargement icône: {e}") # Au cas où
        # --- Fin de l'ajout ---
        
        self.key = key
        self.fernet = Fernet(key)
        self.passwords = {}
        self.lock_timer = None

        self.title("My PassWord Manager by xjapan (v1.0)")
        self.geometry("600x650")
        
        self.bind("<Key>", self.reset_lock_timer)
        self.bind("<Button>", self.reset_lock_timer)
        
        self.load_passwords()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- 1. Cadre de recherche ---
        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(search_frame, text="🔎").grid(row=0, column=0, padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Rechercher...")
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.update_listbox)

        # --- 2. Cadre des champs de saisie ---
        entry_frame = ctk.CTkFrame(self)
        entry_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        entry_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(entry_frame, text="Service:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.service_entry = ctk.CTkEntry(entry_frame, width=300)
        self.service_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(entry_frame, text="Identifiant:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.username_entry = ctk.CTkEntry(entry_frame, width=300)
        self.username_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        
        ctk.CTkButton(entry_frame, text="📋", width=30, command=self.copy_username).grid(row=1, column=3, padx=(0,10), pady=5)

        ctk.CTkLabel(entry_frame, text="Mot de passe:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.password_entry = ctk.CTkEntry(entry_frame, width=300, show="*")
        self.password_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        
        ctk.CTkButton(entry_frame, text="📋", width=30, command=self.copy_password).grid(row=2, column=3, padx=(0,10), pady=5)
        
        self.show_pass_var = ctk.BooleanVar()
        ctk.CTkCheckBox(entry_frame, text="Afficher", variable=self.show_pass_var, command=self.toggle_password).grid(row=3, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkButton(entry_frame, text="🎲 Générer", command=self.generate_password).grid(row=3, column=2, padx=10, pady=5, sticky="w")

        # --- 3. Liste des services ---
        self.listbox = tk.Listbox(self, height=15, bg="#2D2D2D", fg="white", selectbackground="#1F6AA5", borderwidth=0, highlightthickness=0)
        self.listbox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # --- 4. Cadre des boutons d'action ---
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        button_frame.grid_columnconfigure((0,1,2,3), weight=1)

        ctk.CTkButton(button_frame, text="Ajouter", command=self.add_password).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(button_frame, text="Éditer", command=self.edit_password).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(button_frame, text="Supprimer", command=self.delete_password, fg_color="#D32F2F", hover_color="#B71C1C").grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkButton(button_frame, text="Infos Sécurisées", command=self.view_in_new_window).grid(row=0, column=3, padx=5, pady=5)

        self.status_bar = ctk.CTkLabel(self, text="Prêt.", text_color="gray", anchor="w")
        self.status_bar.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        self.update_listbox()
        self.reset_lock_timer()

    def save_passwords(self):
        try:
            data = json.dumps(self.passwords).encode('utf-8')
            encrypted_data = self.fernet.encrypt(data)
            with open(VAULT_FILE, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            messagebox.showerror("Erreur sauvegarde", f"Impossible de sauvegarder le coffre-fort: {e}")

    def load_passwords(self):
        try:
            with open(VAULT_FILE, 'rb') as f:
                encrypted_data = f.read()
            if not encrypted_data:
                 self.passwords = {}
                 return
            decrypted_data = self.fernet.decrypt(encrypted_data)
            self.passwords = json.loads(decrypted_data.decode('utf-8'))
        except FileNotFoundError:
            self.passwords = {}
        except (InvalidToken, Exception):
            messagebox.showerror("Erreur chargement", "Mot de passe maître invalide ou fichier corrompu.")
            self.quit()

    def add_password(self):
        service = self.service_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not service or not username or not password:
            messagebox.showwarning("Erreur", "Tous les champs sont obligatoires.")
            return
        if service in self.passwords:
            messagebox.showwarning("Erreur", f"Le service '{service}' existe déjà. Utilisez 'Éditer'.")
            return
        self.passwords[service] = {"username": username, "password": password}
        self.save_passwords()
        self.update_listbox()
        self.clear_entries()
        self.status_bar.configure(text=f"Service '{service}' ajouté.")

    def edit_password(self):
        service = self.service_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not service or not username or not password:
            messagebox.showwarning("Erreur", "Tous les champs sont obligatoires.")
            return
        if service not in self.passwords:
            messagebox.showwarning("Erreur", f"Le service '{service}' n'existe pas. Utilisez 'Ajouter'.")
            return
        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment mettre à jour '{service}' ?"):
            self.passwords[service] = {"username": username, "password": password}
            self.save_passwords()
            self.update_listbox()
            self.clear_entries()
            self.status_bar.configure(text=f"Service '{service}' mis à jour.")

    def delete_password(self):
        try:
            selected_service = self.listbox.get(self.listbox.curselection())
        except tk.TclError:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un service dans la liste.")
            return
        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer '{selected_service}' ?"):
            del self.passwords[selected_service]
            self.save_passwords()
            self.update_listbox()
            self.clear_entries()
            self.status_bar.configure(text=f"Service '{selected_service}' supprimé.")

    def clear_entries(self):
        self.service_entry.delete(0, 'end')
        self.username_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.show_pass_var.set(False)
        self.toggle_password()

    def on_select(self, event):
        try:
            selected_service = self.listbox.get(self.listbox.curselection())
            data = self.passwords[selected_service]
            self.clear_entries()
            self.service_entry.insert(0, selected_service)
            self.username_entry.insert(0, data["username"])
            self.password_entry.insert(0, data["password"])
        except (tk.TclError, IndexError):
            pass

    def update_listbox(self, event=None):
        search_term = self.search_entry.get().lower()
        self.listbox.delete(0, 'end')
        
        for service in sorted(self.passwords.keys()):
            if search_term in service.lower():
                self.listbox.insert('end', service)

    def toggle_password(self):
        if self.show_pass_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")

    def generate_password(self):
        alphabet = string.ascii_letters + string.digits + string.punctuation
        alphabet = ''.join(c for c in alphabet if c not in 'lIO0')
        
        while True:
            password = ''.join(secrets.choice(alphabet) for i in range(18))
            if (any(c.islower() for c in password)
                    and any(c.isupper() for c in password)
                    and any(c.isdigit() for c in password)
                    and any(c in string.punctuation for c in password)):
                break
        
        self.password_entry.delete(0, 'end')
        self.password_entry.insert(0, password)
        self.status_bar.configure(text="Nouveau mot de passe généré.")

    def copy_to_clipboard(self, data, data_type):
        self.clipboard_clear()
        self.clipboard_append(data)
        self.status_bar.configure(text=f"{data_type} copié ! Effacement dans 30s...")
        self.after(CLIPBOARD_CLEAR_TIME_MS, self.clear_clipboard)

    def copy_username(self):
        self.copy_to_clipboard(self.username_entry.get(), "Identifiant")
        
    def copy_password(self):
        self.copy_to_clipboard(self.password_entry.get(), "Mot de passe")

    def clear_clipboard(self):
        self.clipboard_clear()
        self.status_bar.configure(text="Presse-papiers effacé.")
        
    def reset_lock_timer(self, event=None):
        if self.lock_timer:
            self.after_cancel(self.lock_timer)
        self.lock_timer = self.after(AUTO_LOCK_TIME_MS, self.lock_app)
        
    def lock_app(self):
        self.status_bar.configure(text="Application verrouillée.")
        self.withdraw()
        
        while True:
            master_password = simpledialog.askstring("Application Verrouillée", "Entrez votre mot de passe maître pour déverrouiller:", show='*')
            
            if not master_password:
                self.quit()
                return
                
            if check_master_password(master_password):
                self.deiconify()
                self.status_bar.configure(text="Déverrouillé.")
                self.reset_lock_timer()
                return
            else:
                messagebox.showerror("Erreur", "Mot de passe maître incorrect.")

    def view_in_new_window(self):
        try:
            selected_service = self.listbox.get(self.listbox.curselection())
        except tk.TclError:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un service dans la liste.")
            return
            
        # --- DÉBUT DE LA MODIFICATION ---
        # 1. Demander le mot de passe maître
        master_password = simpledialog.askstring("Vérification", "Entrez votre mot de passe maître pour voir les détails:", show='*')
        if not master_password:
            return # L'utilisateur a annulé

        # 2. Vérifier le mot de passe
        # On appelle la fonction globale 'check_master_password'
        if not check_master_password(master_password):
            messagebox.showerror("Erreur", "Mot de passe maître incorrect.")
            return
        # --- FIN DE LA MODIFICATION ---
            
        data = self.passwords[selected_service]
        
        win = ctk.CTkToplevel(self)
        win.title(f"Détails - {selected_service}")
        win.geometry("450x200")
        win.transient(self)
        win.grab_set()

        win.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(win, text="Service:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        ctk.CTkEntry(win, textvariable=ctk.StringVar(value=selected_service), state="readonly").grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(win, text="Identifiant:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        ctk.CTkEntry(win, textvariable=ctk.StringVar(value=data["username"]), state="readonly").grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(win, text="Mot de passe:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        ctk.CTkEntry(win, textvariable=ctk.StringVar(value=data["password"]), state="readonly").grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkButton(win, text="Fermer", command=win.destroy).grid(row=3, column=0, columnspan=2, pady=10)


def get_key_from_master_password(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))

def get_salt():
    if os.path.exists(SALT_FILE):
        with open(SALT_FILE, 'rb') as f:
            salt = f.read()
    else:
        salt = os.urandom(16)
        with open(SALT_FILE, 'wb') as f:
            f.write(salt)
    return salt

def check_master_password(master_password):
    if not master_password:
        return False
        
    salt = get_salt()
    try:
        key = get_key_from_master_password(master_password, salt)
    except Exception:
        return False

    if os.path.exists(VAULT_FILE) and os.path.getsize(VAULT_FILE) > 0:
        try:
            with open(VAULT_FILE, 'rb') as f:
                encrypted_data = f.read()
            Fernet(key).decrypt(encrypted_data)
            return key
        except InvalidToken:
            return False
        except Exception:
            return False
    return key

def main():
    key = False
    while not key:
        master_password = simpledialog.askstring("Mot de Passe Maître", "Entrez votre mot de passe maître:", show='*')
        if not master_password:
            return
        key = check_master_password(master_password)
        if not key:
            messagebox.showerror("Erreur", "Mot de passe maître incorrect ou coffre-fort corrompu.")
        
    app = PasswordManager(key)
    app.mainloop()

if __name__ == "__main__":
    main()