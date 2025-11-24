#!/usr/bin/env python3
"""
AI Governance Assessor CLI
Command-line interface for managing AI governance assessments
"""

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from typing import Optional
import os
from cli.api_client import APIClient

app = typer.Typer(help="AI Governance Assessor CLI")
console = Console()

# Token storage file
TOKEN_FILE = os.path.expanduser("~/.ai_governance_token")


def get_stored_token() -> Optional[str]:
    """Get stored authentication token"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return f.read().strip()
    return None


def store_token(token: str):
    """Store authentication token"""
    with open(TOKEN_FILE, 'w') as f:
        f.write(token)


def get_client() -> APIClient:
    """Get authenticated API client"""
    token = get_stored_token()
    if not token:
        console.print("[red]Not authenticated. Please run 'login' command first.[/red]")
        raise typer.Exit(1)
    return APIClient(token)


@app.command()
def login(
    email: str = typer.Option(..., prompt=True, help="Your email address"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Your password")
):
    """Login to the AI Governance Assessor"""
    try:
        client = APIClient()
        result = client.login(email, password)
        store_token(result["access_token"])
        console.print("[green]✓ Successfully logged in![/green]")
    except Exception as e:
        console.print(f"[red]Login failed: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def logout():
    """Logout and clear stored credentials"""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    console.print("[green]✓ Successfully logged out![/green]")


@app.command()
def list():
    """List all assessments"""
    try:
        client = get_client()
        assessments = client.list_assessments()
        
        if not assessments:
            console.print("[yellow]No assessments found.[/yellow]")
            return
        
        table = Table(title="Assessments")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Created", style="blue")
        
        for assessment in assessments:
            table.add_row(
                str(assessment["id"]),
                assessment["title"],
                assessment["status"],
                assessment["created_at"][:10]
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Failed to list assessments: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def create(
    title: str = typer.Option(..., prompt=True, help="Assessment title"),
    description: Optional[str] = typer.Option(None, help="Assessment description")
):
    """Create a new assessment"""
    try:
        client = get_client()
        assessment = client.create_assessment(title, description)
        console.print(f"[green]✓ Created assessment #{assessment['id']}: {assessment['title']}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to create assessment: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def show(assessment_id: int = typer.Argument(..., help="Assessment ID")):
    """Show assessment details"""
    try:
        client = get_client()
        assessment = client.get_assessment(assessment_id)
        
        console.print(f"\n[bold cyan]Assessment #{assessment['id']}[/bold cyan]")
        console.print(f"[bold]Title:[/bold] {assessment['title']}")
        console.print(f"[bold]Status:[/bold] {assessment['status']}")
        console.print(f"[bold]Created:[/bold] {assessment['created_at']}")
        
        if assessment.get('description'):
            console.print(f"[bold]Description:[/bold] {assessment['description']}")
        
        if assessment.get('results'):
            console.print(f"\n[bold]Results:[/bold] {len(assessment['results'])} / 4 categories completed")
    except Exception as e:
        console.print(f"[red]Failed to get assessment: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def report(assessment_id: int = typer.Argument(..., help="Assessment ID")):
    """Show assessment report summary"""
    try:
        client = get_client()
        summary = client.get_summary(assessment_id)
        
        console.print(f"\n[bold cyan]Assessment Report: {summary['assessment']['title']}[/bold cyan]\n")
        
        # Overall score
        console.print(f"[bold]Overall Score:[/bold] [green]{summary['overall_score']}[/green]")
        console.print(f"[bold]Overall Maturity:[/bold] [yellow]{summary['overall_maturity'].title()}[/yellow]\n")
        
        # Category scores
        if summary.get('category_scores'):
            table = Table(title="Category Scores")
            table.add_column("Category", style="cyan")
            table.add_column("Score", style="green")
            
            for category, score in summary['category_scores'].items():
                table.add_row(category.replace('_', ' ').title(), str(score))
            
            console.print(table)
    except Exception as e:
        console.print(f"[red]Failed to get report: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def export(
    assessment_id: int = typer.Argument(..., help="Assessment ID"),
    format: str = typer.Option("csv", help="Export format (csv or pdf)"),
    output: Optional[str] = typer.Option(None, help="Output file path")
):
    """Export assessment report"""
    try:
        client = get_client()
        
        if not output:
            output = f"assessment_{assessment_id}.{format}"
        
        if format.lower() == "csv":
            client.export_csv(assessment_id, output)
        elif format.lower() == "pdf":
            client.export_pdf(assessment_id, output)
        else:
            console.print(f"[red]Invalid format: {format}. Use 'csv' or 'pdf'.[/red]")
            raise typer.Exit(1)
        
        console.print(f"[green]✓ Exported to {output}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to export: {str(e)}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
