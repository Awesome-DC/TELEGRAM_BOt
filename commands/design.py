from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from db import get_all_users

console = Console()

def show_dashboard():
    console.clear()
    
    # Title Panel
    console.print(Panel("[bold green]Normans Game Bot[/bold green]\n[cyan]Status: Active[/cyan]", style="bold white", expand=False))
    
    # Coins table
    table = Table(title="User Balances", box=box.DOUBLE_EDGE)
    table.add_column("User ID", style="cyan", justify="center")
    table.add_column("Username", style="magenta", justify="center")
    table.add_column("Coins", style="green", justify="right")
    
    users = get_all_users()
    for u in users:
        table.add_row(str(u["user_id"]), u["username"] or "None", str(u["coins"]))
    
    console.print(table)

import time
import os 
import sys
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def clear_console():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

# def slow_print(text, delay=0.05, color=Fore.WHITE):
#     """Print text one character at a time with color."""
#     for char in text:
#         sys.stdout.write(color + char)
#         sys.stdout.flush()
#         time.sleep(delay)
#     print()  # Newline at end

# def design_screen():
#     border = "=" * 50

#     # Border
#     slow_print(border, 0.01, Fore.MAGENTA)
    
#     # Title
#     slow_print("🎮  NORMANS GAME BOT  🎮", 0.1, Fore.CYAN + Style.BRIGHT)
    
#     # Subtitle
#     slow_print("✨ Welcome to your ultimate game bot ✨", 0.05, Fore.YELLOW)
    
#     # Border again
#     slow_print(border, 0.01, Fore.MAGENTA)
#     print()
    
#     # Intro steps
#     slow_print("Loading modules...", 0.05, Fore.GREEN)
#     time.sleep(0.5)
#     slow_print("Connecting to database...", 0.05, Fore.BLUE)
#     time.sleep(0.5)
#     slow_print("Initializing commands...", 0.05, Fore.CYAN)
#     time.sleep(0.5)
#     slow_print("Bot is live and running! Enjoy the games 🕹️", 0.05, Fore.YELLOW + Style.BRIGHT)
    
#     # Final border
#     slow_print(border, 0.01, Fore.MAGENTA)

# import time
# from rich.console import Console
# from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

# console = Console()
# def slow_print(text, delay=0.05, color=Fore.WHITE):
#     """Print text one character at a time with color."""
#     for char in text:
#         sys.stdout.write(color + char)
#         sys.stdout.flush()
#         time.sleep(delay)
#     print()  # Newline at end
# def design_screen():
#     steps = [
#         ("Loading modules...", 7),
#         ("Connecting to database...", 6),
#         ("Initializing commands...", 5),
#         ("Final check...", 5),
#     ]

#     def design_scren():
#         border = "=" * 50

#         # Border
#         slow_print(border, 0.01, Fore.MAGENTA)
        
#         # Title
#         slow_print("🎮  NORMANS GAME BOT  🎮", 0.1, Fore.CYAN + Style.BRIGHT)
        
#         # Subtitle
#         slow_print("✨ Welcome to your ultimate game bot ✨", 0.05, Fore.YELLOW)
        
#         # Border again
#         slow_print(border, 0.01, Fore.MAGENTA)
#         print()
#     console.clear()
#     console.print("🎮 [bold cyan]NORMANS GAME BOT[/bold cyan] 🎮")
#     console.print("✨ Welcome to your ultimate game bot ✨\n")

#     # Create a progress bar
#     with Progress(
#         TextColumn("[progress.description]{task.description}"),
#         BarColumn(bar_width=None),
#         TimeRemainingColumn(),
#         console=console
#     ) as progress:

#         task = progress.add_task("Starting...", total=len(steps))

#         for step, duration in steps:
#             progress.update(task, description=step)
#             for i in range(100):
#                 time.sleep(duration/100)
#                 progress.advance(task, 0.01)
#             progress.update(task, description=step)
#             time.sleep(0.3)  # Small pause before next step
#             console.clear()

#     def slow_print(text, delay=0.05, color=Fore.WHITE):
#     """Print text one character at a time with color."""
#     for char in text:
#         sys.stdout.write(color + char)
#         sys.stdout.flush()
#         time.sleep(delay)
#     print()  # Newline at end

#     console.print("\n✅ [bold green]Bot is live and running! Enjoy the games 🕹️[/bold green]")
import time
import sys
import os
from colorama import init, Fore, Style
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

# Initialize colorama for colored text
init(autoreset=True)
console = Console()

def slow_print(text, delay=0.05, color=Fore.WHITE):
    for char in text:
        sys.stdout.write(color + char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def clear_console():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def design_screen():
    clear_console()

    border = "=" * 50

    # Initial splash
    slow_print(border, 0.01, Fore.MAGENTA)
    slow_print("🎮  NORMANS GAME BOT  🎮", 0.1, Fore.CYAN + Style.BRIGHT)
    slow_print("✨ Welcome to your ultimate game bot ✨", 0.05, Fore.YELLOW)
    slow_print(border, 0.01, Fore.MAGENTA)
    print()

    steps = [
        ("Loading modules...", 3),
        ("Connecting to database...", 2),
        ("Starting Bot 1...", 2),
        ("Starting Bot 2...", 2),
        ("Initializing commands...", 2),
        ("Final check...", 1),
    ]

    # Show progress bar
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        TimeRemainingColumn(),
        console=console,
    ) as progress:

        task = progress.add_task("Starting...", total=len(steps))

        for step, duration in steps:
            progress.update(task, description=step)
            for i in range(100):
                time.sleep(duration / 100)
                progress.advance(task, 0.01)
            time.sleep(0.3)

    # ✅ CLEAR the progress bar after it finishes
    clear_console()

    # Final splash

    print(Fore.MAGENTA + border,)
    print(Fore.CYAN + Style.BRIGHT + "🎮  NORMANS GAME BOT  🎮")
    print( Fore.YELLOW + "✨ Welcome to your ultimate game bot ✨",)
    print(Fore.MAGENTA + border)
    slow_print("✅ Bot is live and running! Enjoy the games 🕹️", 0.05, Fore.GREEN + Style.BRIGHT)
    slow_print(border, 0.01, Fore.MAGENTA)

if __name__ == "__main__":
    design_screen()
