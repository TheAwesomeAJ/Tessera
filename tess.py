import os
import json
import base64
import getpass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.status import Status

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

console = Console()

VAULT_PATH = os.path.expanduser("~/.tessera.vault")
ITERATIONS = 390_000

def derive_key(password: str, salt:bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS
    )
    return base64.urlsafe_b64decode(kdf.derive(password.encode()))

def encrypt_vault(data:dict, password: str, salt: bytes) -> bytes:
    key = derive_key(password, salt)
    fernet = Fernet(key)
    return fernet.encrypt(json.dumps(data).encode())

def decrypt_vault(blob: bytes, password: str, salt:bytes) -> dict:
    key = derive_key(password, salt)
    fernet = Fernet(key)
    decrypted = fernet.decrypt(blob)
    return json.loads(decrypted.decode())

def vault_exists() -> bool:
    return os.path.exists(VAULT_PATH)

def load_vault(password: str) -> dict:
    with open(VAULT_PATH, "rb") as f:
        salt = f.read(16)
        encrypted = f.read()
    
    try:
        return decrypt_vault(encrypted, password, salt)
    except Exception:
        raise ValueError("Invalid password or corrupted vault")
    
def save_vault(data: dict, password: str, salt: bytes):
    encrypted = encrypt_vault(data, password, salt)
    with open(VAULT_PATH, "wb") as f:
        f.write(salt)
        f.write(encrypted)

def welcome():
    console.clear()
    console.print(
        Panel(
            "[bold cyan]TESSERA[/bold cyan]\nTerminal Password Vault",
            title="[bold magenta]Welcome[/bold magenta]",
            subtitle="Type 'help' to see available commands",
        )
    )

def cmd_help():
    table = Table()

    table.add_column("Command", style="green")
    table.add_column("Description", style="green")

    table.add_row("init", "Initialize the vault")
    table.add_row("add <name>", "Add a new entry")
    table.add_row("get <name>", "Retrieve an entry")
    table.add_row("list", "List all entries")
    table.add_row("delete <name>", "Delete an entry")
    table.add_row("exit", "Close the application")
    table.add_row("help", "Show this help messsage again!")

    console.print(table)

def cmd_init():
    if vault_exists():
        console.print("[red]Vault already exists![/red]")
        return
    pw1 = getpass.getpass("Create master password: ")
    pw2 = getpass.getpass("Confirm master password: ")

    if pw1 != pw2:
        console.print("[red]Passwords do not match[/red]")
        return
    
    salt = os.urandom(16)
    save_vault({}, pw1, salt)

    console.print("[bold green]Vault was created![/bold green]")

def cmd_add(name):
    if not name:
        console.print("[bold red]Please provide a name for the entry.[/bold red]")
        return

    if name in vault:
        console.print("[yellow]This entry already exists!")
        return
    
    username = Prompt.ask("Username")
    password = Prompt.ask("Password", password=True)

    with Status("Saving entry...", spinner="dots"):
        vault[name] = {
            "username": username,
            "password": password
        }
    
    console.print(f"[bold green]Your entry, '{name}' was added![/bold green]")

def cmd_get(name):
    if not name:
        console.print("[bold red]Please provide a valid name to search for.[/bold red]")
    
    if name not in vault:
        console.print("[red]Hmm... This entry was not found.")

    entry = vault[name]

    panel = Panel(
        f"[cyan]Username:[/cyan] {entry['username']}\n"
        f"[cyan]Password:[/cyan] {entry['password']}",
        title=f"[bold] Entry - {name}"
    )

    console.print(panel)

def cmd_list():
    if not vault:
        console.print("[yellow]Vault is empty[/yellow]")
        return
    
    table = Table()
    table.add_column("Name", style="cyan")
    
    for name in vault:
        table.add_row(name)

    console.print(table)

def cmd_delete(name):
    if not name:
        console.print("[red]Please provide a entry name[/red]")
        return
    
    if name not in vault:
        console.print("[red]Please provide an entry name[/red]")
        return
    
    if Confirm.ask(f"Delete entry '{name}'?"):
        del vault[name]
        console.print(f"[bold green]Entry '{name}' deleted[/bold green]")
    else:
        console.print("[yellow]Deletion cancelled.")

def main():
    welcome()
    while True:
        raw = Prompt.ask("tess >").strip()
        if not raw:
            continue

        parts = raw.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        if command == "help":
            cmd_help()
        elif command == "init":
            cmd_init()
        elif command == "add":
            cmd_add(args[0] if args else None)
        elif command == "get":
            cmd_get(args[0] if args else None)
        elif command == "list":
            cmd_list()
        elif command == "delete":
            cmd_delete(args[0] if args else None)
        elif command == "exit":
            console.print("[bold magenta]Goodbye![/bold magenta]")
            break
        else:
            console.print(f"[bold red]Unknown command:[/bold red] {command}")


if __name__ == "__main__":
    main()