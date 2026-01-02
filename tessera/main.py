from cryptography.fernet import Fernet

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box

import os
import time
import json

console = Console()

BASE_DIR = os.path.join(os.path.expanduser("~"), ".tessera")
KEY_DIR = os.path.join(BASE_DIR, "Keys")
DATA_DIR = os.path.join(BASE_DIR, "Data")

os.makedirs(KEY_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# ------ Password Logic ------

class Tessera:
    def __init__(self):
        self.key = None
        self.fernet = None
        self.password_file = None
        self.password_dict = {}

    def generate_key(self):
        timestamp = int(time.time())
        path = os.path.join(KEY_DIR, f"tessera_key_{timestamp}.key")

        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)

        with open(path, 'wb') as f:
            f.write(self.key)

        console.print(f"[green]Encryption key generated:[/green] {path}")
        return path

    def load_key(self, path):
        if not os.path.exists(path):
            console.print(f"[red]Key file {path} not found[/red]")
            return False
        with open(path, 'rb') as f:
            self.key = f.read()
            self.fernet = Fernet(self.key)
        console.print(f"[green]Encryption key loaded:[/green] {path}")
        return True

    def create_password_file(self):
        timestamp = int(time.time())
        path = os.path.join(DATA_DIR, f"tessera_pw_{timestamp}.json")
        self.password_file = path
        with open(path, 'w') as f:
            json.dump({},f)
        console.print(f"[green]Password file created:[/green] {path}\n")
        return path

    def load_password_file(self, path):
        if not os.path.exists(path):
            console.print(f"[red]Password file {path} not found[/red]\n")
            return False

        self.password_file = path
        self.password_dict.clear()

        with open(path, 'r') as f:
            vault_data = json.load(f)

        for site, encrypted in vault_data.items():
            decrypted = self.fernet.decrypt(encrypted.encode()).decode()
            entry = json.loads(decrypted)
            self.password_dict[site] = entry

        console.print(f"[green]Password file loaded:[/green] {path}\n")
        return True

    def save_vault(self):
        if not self.password_file:
            return
        encrypted_vault = {}

        for site, entry in self.password_dict.items():
            encrypted = self.fernet.encrypt(json.dumps(entry).encode())
            encrypted_vault[site] = encrypted.decode()

        with open(self.password_file, "w") as f:
            json.dump(encrypted_vault, f, indent=2)

    def add_password(self, site, password, username=None, email=None, entry_type="password"):
        entry = {
            "site": site,
            "username": username,
            "email": email,
            "type": entry_type,
            "secret": password
        }

        self.password_dict[site] = entry
        self.save_vault()

        console.print(f"[green]Entry for {site} added![/green]")

    def delete_password(self, site):
        if site in self.password_dict:
            del self.password_dict[site]
        else:
            console.print(f"[red]No password found for {site}[/red]")
            return

        if self.password_file is not None:
            with open(self.password_file, "r") as f:
                lines = f.readlines()
            with open(self.password_file, "w") as f:
                for line in lines:
                    if not line.startswith(site + ":"):
                        f.write(line)
        console.print(f"[green]Password for {site} deleted![/green]")
 
    def get_password(self, site):
        return self.password_dict.get(site, None)

# ------ Terminal UI Logic ------

manager = Tessera()

def cmd_generate_key():
    manager.generate_key()

def cmd_create_pw_file():
    manager.create_password_file()

def cmd_add_password():
    site = Prompt.ask("\nPlease enter the website name for the password that you wish to add")
    password = Prompt.ask("Please enter the password for the website that you entered", password=True)
    username = Prompt.ask("Please enter the username for this website")
    email = Prompt.ask("Please enter the email associated with this account")
    entry_choice = Prompt.ask("Is this (1) an API key, or (2) a password? (Enter the corresponding number)", choices=["1", "2"])

    entry_type = "api_key" if entry_choice == "1" else "password"

    manager.add_password(
        site=site,
        password=password,
        username=username or None,
        email=email or None,
        entry_type=entry_type
    )

def cmd_fetch_password():
    site = Prompt.ask("\nPlease enter the website name for the password that you want to fetch")
    entry = manager.get_password(site)

    if not entry:
        console.print("\n")
        console.print(f"[red]No entry was found for {site}[/red]")
        console.print("\n")

    table = Table(
        title=f"Entry for {site}",
        show_lines=True,
        box=box.HORIZONTALS
    )

    table.add_column("Field", style="bold cyan3")
    table.add_column("Value")

    for key, value in entry.items():
        if value is not None:
            table.add_row(key.capitalize(), value)

    console.print("\n")
    console.print(table)
    console.print("\n")

def cmd_delete_password():
    site = Prompt.ask("\nPlease enter the website name for the password that you wish to delete")
    manager.delete_password(site)

def cmd_help():
    table = Table(title="All commands available for Tessera",
                  show_lines=True,
                  box=box.HORIZONTALS)

    table.add_column("Command", justify="left")
    table.add_column("Usage", justify="left")

    table.add_row("generate", "Generate a new encryption key")
    table.add_row("new", "Create a new password file")
    table.add_row("add", "Add a new password")
    table.add_row("delete", "Delete a password")
    table.add_row("fetch", "Fetch a password")
    table.add_row("quit", "Close Tessera")
    table.add_row("help", "Shows this help message again")

    console.print("\n")
    console.print(table)
    console.print("\n")

def main():
    console.clear()
    console.print(
        Panel(
            "\nTessera - A terminal password manager, built simply\n",
            title="[bold dark_cyan]Tessera Interface[/bold dark_cyan]",
            title_align="left",
            subtitle="Type 'help' to see available commands",
            subtitle_align="left",
            expand=False,
            border_style="cyan3"
        )
    )
    console.print("\n")

    key_files = sorted(
        f for f in os.listdir(KEY_DIR)
        if f.startswith("tessera_key_") and f.endswith(".key")
    )

    pw_files = sorted(
        f for f in os.listdir(DATA_DIR)
        if f.startswith("tessera_pw_") and f.endswith(".json")
    )

    if key_files:
        manager.load_key(os.path.join(KEY_DIR, key_files[-1]))
    else:
        manager.generate_key()

    if pw_files:
        manager.load_password_file(os.path.join(DATA_DIR, pw_files[-1]))
    else:
        manager.create_password_file()

    done = False

    while not done:

        cmd = Prompt.ask("[bold cyan3]tessera >[/bold cyan3]").strip().lower()
        if cmd == "generate":
            cmd_generate_key()
        elif cmd == "new":
            cmd_create_pw_file()
        elif cmd == "add":
            cmd_add_password()
        elif cmd == "delete":
            cmd_delete_password()
        elif cmd == "fetch":
            cmd_fetch_password()
        elif cmd == "quit":
            done = True
            print("Goodbye! Thank you for using Tessera!")
        elif cmd == "help":
            cmd_help()
        else:
            print("Hmm. Looks like that option doesn't exist. Please try again!")

if __name__ == "__main__":
    main()