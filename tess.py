from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()

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
    table.add_row("exit", "Close the application")
    table.add_row("help", "Show this help messsage again!")
    console.print(table)

def cmd_init():
    console.print("[bold green]Vault has been initialized![/bold green] (mock)")

def cmd_add(name):
    if not name:
        console.print("[bold red]Please provide a name for the entry.[/bold red]")
    else:
        console.print(f"[bold green]Entry '{name}' added to yoor local vault![/bold green]")

def cmd_get(name):
    if not name:
        console.print("[bold red]Please provide a valid name to search for.[/bold red]")
    else:
        console.print(f"[bold yellow]Retrieved entry '{name}'[/bold yellow]")

def cmd_list():
    table = Table()
    table.add_column("Name", style="cyan")
    
    for entry in ["github", "email", "school"]:
        table.add_row(entry)
    console.print(table)

def main():
    welcome()
    while True:
        cmd = Prompt.ask("tess >").strip()
        if not cmd:
            continue
        parts = cmd.split()
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
        elif command == "exit":
            console.print("[bold magenta]Goodbye![/bold magenta]")
            break
        else:
            console.print(f"[bold red]Unknown command:[/bold red] {command}")


if __name__ == "__main__":
    main()