from cryptography.fernet import Fernet

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.status import Status

console = Console()

# ------ Password Logic ------

class Tessera:
    def __init__(self):
        self.key = None
        self.password_file = None
        self.password_dict = {}

    def create_key(self, path):
        self.key = Fernet.generate_key()
        with open(path, 'wb') as f:
            f.write(self.key)

    def load_key(self, path):
        with open(path, 'rb') as f:
            self.key = f.read()

    def create_password_file(self, path, initial_values=None):
        self.password_file = path
        
        if initial_values is not None:
            for key, values in initial_values.items():
                self.add_password(key, values)

    def load_password_file(self, path):
        self.password_file = path

        with open(path, 'r') as f:
            for line in f:
                 site, encrypted = line.split(":")
                 self.password_dict[site] = Fernet(self.key).decrypt(encrypted.encode()).decode()

    def add_password(self, site, password):
        self.password_dict[site] = password

        if self.password_file is not None:
            with open(self.password_file, 'a+') as f:
                encrypted = Fernet(self.key).encrypt(password.encode())
                f.write(site + ":" + encrypted.decode() + "\n")
 
    def get_password(self, site):
        return self.password_dict[site]

# ------ Terminal UI Logic ------

def cmd_create_key(path):
    if not path:
        path = Prompt.ask("What would you like to call this key? (Please use a lowercase name, and no spaces)")

    Tessera().create_key(path)
    console.print(f"\nThe encryption key [green]{path}[/green] was created successfully!\n")

def cmd_load_key():
    path = Prompt.ask("Please enter the path to the key file)")
    Tessera().load_key(path)

def cmd_create_pw_file():
    path = Prompt.ask("What would you like to call this password file? (Please use a lowercase name, and no spaces)")
    Tessera().create_password_file(path)

def cmd_load_pw_file(path):
    if not path:
        path = Prompt.ask("Please enter the path to the password file")
    console.print("[bold green]Password file was loaded successfully!\n[/bold green]")
    Tessera().load_password_file(path)

def cmd_add_password():
    site = Prompt.ask("Please enter the website name for the password that you wish to add")
    password = Prompt.ask("Please enter the password for the website that you entered")
    Tessera().add_password(site, password)

def cmd_fetch_password():
    site = Prompt.ask("Please enter the website name for the password that you want to fetch")
    console.print(f"[green]Password for {site} is {Tessera().get_password(site)}")

    
def main():

    console.clear()
    console.print(
        Panel(
            "[bold cyan]Tessera[/bold cyan]\nTerminal Password Vault",
            title="[bold magenta]Welcome[/bold magenta]",
            subtitle="Type 'help' to see available commands",
        )
    )
    
    done = False

    while not done:

        raw = Prompt.ask("tess >").strip()
        if not raw:
            continue

        parts = raw.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        if command == "create-key":
            cmd_create_key(args[0] if args else None)
        elif command == "load-key":
            cmd_load_key()
        elif command == "pass-file":
            cmd_create_pw_file()
        elif command == "load-pass-file":
            cmd_load_pw_file(args[0] if args else None)
        elif command == "add":
            cmd_add_password()
        elif command == "fetch":
            cmd_fetch_password()
        elif command == "q":
            done = True
            print("Goodbye! Thank you for using Tessera!")
        else:
            print("Hmm. Looks like that option doesn't exist. Please try again!")
        
if __name__ == "__main__":
    main()