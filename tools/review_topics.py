#!/usr/bin/env python3
"""
Review Topics Script
Displays generated topic metadata in a readable format for review

Usage:
    python tools/review_topics.py
"""

import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def display_topic(topic: dict, index: int):
    """Display a single topic with nice formatting"""

    # Create a panel for each topic
    content = f"""
**Name:** {topic['name']}
**Category:** {topic['category']}
**Grade Level:** {topic['grade_level']}
**Source:** {topic.get('source', 'N/A')}

**Prompt Template:**
{topic['prompt_template']}

**Example:**
{topic['example']}
"""

    panel = Panel(
        Markdown(content),
        title=f"Topic {index + 1}",
        border_style="blue" if index % 2 == 0 else "green"
    )

    console.print(panel)


def main():
    review_file = Path("data/imports/topics_review.json")

    if not review_file.exists():
        console.print("[red]❌ Review file not found![/red]")
        console.print("Run: python tools/import_topics.py <csv_file> first")
        return

    # Load topics
    with open(review_file, 'r') as f:
        topics = json.load(f)

    console.print(f"\n[bold cyan]📚 Reviewing {len(topics)} Topics[/bold cyan]\n")

    # Display summary table first
    table = Table(title="Topics Overview")
    table.add_column("№", style="cyan", justify="right")
    table.add_column("Name", style="green")
    table.add_column("Category", style="yellow")
    table.add_column("Grade", style="magenta")

    for i, topic in enumerate(topics, 1):
        table.add_row(
            str(i),
            topic['name'],
            topic['category'],
            topic['grade_level']
        )

    console.print(table)
    console.print()

    # Ask if user wants detailed view
    show_details = console.input("\n[bold]Show detailed view? (y/n): [/bold]")

    if show_details.lower() == 'y':
        console.print("\n" + "="*60 + "\n")
        for i, topic in enumerate(topics):
            display_topic(topic, i)
            if i < len(topics) - 1:
                console.input("\n[dim]Press Enter for next topic...[/dim]\n")

    # Ask about approval
    console.print("\n" + "="*60 + "\n")
    approve = console.input("[bold green]Approve these topics for import? (y/n): [/bold green]")

    if approve.lower() == 'y':
        console.print("\n[green]✅ Topics approved![/green]")
        console.print("Run: [cyan]python tools/import_to_db.py[/cyan] to import to database")
    else:
        console.print("\n[yellow]📝 Edit data/imports/topics_review.json and run this script again[/yellow]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Review cancelled[/yellow]")
