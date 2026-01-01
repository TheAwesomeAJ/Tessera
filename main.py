from cryptography.fernet import Fernet

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from rich import box

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

    def delete_password(self, site):
        if site in self.password_dict:
            del self.password_dict[site]
        else:
            return False

        if self.password_file is not None:
            with open(self.password_file, "r") as f:
                lines = f.readlines()
            with open(self.password_file, "w") as f:
                for line in lines:
                    if not line.startswith(site + ":"):
                        f.write(line)
        return True
 
    def get_password(self, site):
        return self.password_dict[site]

# ------ Terminal UI Logic ------

manager = Tessera()

def cmd_create_key(path):
    if not path:
        path = Prompt.ask("\n[bold cyan]What would you like to call this key? (Please use a lowercase name, and no spaces)[/bold cyan]")

    manager.create_key(path)
    console.print(f"\nThe encryption key [green]{path}[/green] was created successfully!\n")

def cmd_load_key():
    path = Prompt.ask("\nPlease enter the path to the key file)")
    manager.load_key(path)

def cmd_create_pw_file():
    path = Prompt.ask("\nWhat would you like to call this password file? (Please use a lowercase name, and no spaces)")
    manager.create_password_file(path)

def cmd_load_pw_file(path):
    if not path:
        path = Prompt.ask("\nPlease enter the path to the password file")
    console.print("\n[bold green]Password file was loaded successfully!\n[/bold green]")
    manager.load_password_file(path)

def cmd_add_password():
    site = Prompt.ask("\nPlease enter the website name for the password that you wish to add")
    password = Prompt.ask("Please enter the password for the website that you entered")
    manager.add_password(site, password)

def cmd_fetch_password():
    site = Prompt.ask("\nPlease enter the website name for the password that you want to fetch")
    console.print(f"\n[green]Password for {site} is {manager.get_password(site)}")

def cmd_delete_password(site):
    if not site:
        site = Prompt.ask("\nPlease enter the website name for the password that you wish to delete")
    manager.delete_password(site)
    console.print(f"\nPassword {site} was deleted successfully!")

def cmd_help():
    table = Table(title="All commands available for Tessera",
                  show_lines=True,
                  box=box.HORIZONTALS)

    table.add_column("Command", justify="left")
    table.add_column("Usage", justify="left")

    table.add_row("generate", "Generate a new encryption key")
    table.add_row("load-key", "Load a existing encryption key")
    table.add_row("new", "Create a new password file")
    table.add_row("load-pw-file", "Load an existing password file")
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
            title="[bold magenta]Welcome[/bold magenta]",
            title_align="left",
            subtitle="Type 'help' to see available commands",
            subtitle_align="left",
            expand=False,
        )
    )
    console.print("\n")
    
    done = False

    while not done:

        raw = Prompt.ask("[bold white]tessera >[/bold white]").strip()
        if not raw:
            continue

        parts = raw.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        if command == "generate":
            cmd_create_key(args[0] if args else None)
        elif command == "load-key":
            cmd_load_key()
        elif command == "new":
            cmd_create_pw_file()
        elif command == "load-pass-file":
            cmd_load_pw_file(args[0] if args else None)
        elif command == "add":
            cmd_add_password()
        elif command == "delete":
            cmd_delete_password(args[0] if args else None)
        elif command == "fetch":
            cmd_fetch_password()
        elif command == "quit":
            done = True
            print("Goodbye! Thank you for using Tessera!")
        elif command == "help":
            cmd_help()
        else:
            print("Hmm. Looks like that option doesn't exist. Please try again!")

if __name__ == "__main__":
    main()