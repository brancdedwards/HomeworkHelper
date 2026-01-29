#!/usr/bin/env python3
"""
Topic Import Wizard
Interactive wizard that guides through the entire import process

Usage:
    python tools/import_wizard.py
"""

import os
import sys
import subprocess
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import print as rprint

console = Console()


def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')


def show_welcome():
    clear_screen()
    welcome = """
    [bold cyan]📚 Grammar Topic Import Wizard[/bold cyan]

    This wizard will help you:
    1. Choose or create a topic list
    2. Generate metadata using AI
    3. Review the generated topics
    4. Import approved topics to database

    [dim]Press Ctrl+C at any time to exit[/dim]
    """
    console.print(Panel(welcome, border_style="cyan"))


def list_csv_files():
    """List available CSV files"""
    import_dir = Path("data/imports")
    csv_files = list(import_dir.glob("*.csv"))
    return [f for f in csv_files if f.name != "grammar_topics_template.csv"]


def choose_csv_file():
    """Let user choose or create CSV file"""
    console.print("\n[bold]Step 1: Choose your topic list[/bold]\n")

    csv_files = list_csv_files()

    if csv_files:
        console.print("Available CSV files:")
        for i, file in enumerate(csv_files, 1):
            console.print(f"  {i}. {file.name}")
        console.print(f"  {len(csv_files) + 1}. Create new file")

        choice = Prompt.ask(
            "Select a file",
            choices=[str(i) for i in range(1, len(csv_files) + 2)]
        )

        choice_idx = int(choice) - 1

        if choice_idx < len(csv_files):
            return csv_files[choice_idx]

    # Create new file
    console.print("\n[yellow]Creating new CSV file...[/yellow]")
    filename = Prompt.ask("Enter filename (without .csv)")

    new_file = Path(f"data/imports/{filename}.csv")

    # Copy template
    template = Path("data/imports/grammar_topics_template.csv")
    if template.exists():
        import shutil
        shutil.copy(template, new_file)
        console.print(f"\n[green]✓ Created {new_file}[/green]")
        console.print(f"\n[yellow]Please edit {new_file} and add your topics, then run this wizard again.[/yellow]")
        sys.exit(0)

    return new_file


def run_generation(csv_file):
    """Run the generation script"""
    console.print("\n[bold]Step 2: Generating metadata with AI[/bold]\n")
    console.print(f"Processing: {csv_file.name}\n")

    if not Confirm.ask("Ready to generate?"):
        return False

    try:
        result = subprocess.run(
            ["python", "tools/import_topics.py", str(csv_file)],
            check=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError:
        console.print("[red]❌ Generation failed[/red]")
        return False


def run_review():
    """Run the review script"""
    console.print("\n[bold]Step 3: Review generated topics[/bold]\n")

    if not Confirm.ask("Ready to review?"):
        return False

    try:
        result = subprocess.run(
            ["python", "tools/review_topics.py"],
            check=False  # review_topics.py handles its own exit
        )
        return True
    except Exception as e:
        console.print(f"[red]❌ Review failed: {e}[/red]")
        return False


def run_import():
    """Run the import script"""
    console.print("\n[bold]Step 4: Import to database[/bold]\n")

    if not Confirm.ask("Import approved topics to database?"):
        console.print("[yellow]Import cancelled[/yellow]")
        return False

    try:
        result = subprocess.run(
            ["python", "tools/import_to_db.py"],
            check=False  # import_to_db.py handles its own exit
        )
        return True
    except Exception as e:
        console.print(f"[red]❌ Import failed: {e}[/red]")
        return False


def show_completion():
    """Show completion message"""
    console.print("\n" + "="*60)
    console.print("[bold green]✅ Import process complete![/bold green]")
    console.print("\nNext steps:")
    console.print("1. Visit http://localhost:3000")
    console.print("2. Start a new practice session")
    console.print("3. Try out your new topics!")
    console.print("="*60 + "\n")


def main():
    try:
        show_welcome()

        # Step 1: Choose CSV
        csv_file = choose_csv_file()

        if not csv_file.exists():
            console.print(f"[red]File not found: {csv_file}[/red]")
            return

        # Step 2: Generate metadata
        if not run_generation(csv_file):
            console.print("[yellow]Stopping at generation step[/yellow]")
            return

        # Step 3: Review
        console.print("\n[dim]Review completed. Continuing...[/dim]")

        # Step 4: Import
        run_import()

        # Done!
        show_completion()

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Wizard cancelled[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
