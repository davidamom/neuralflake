"""
Command-line interface for NeuralFlake.

This module provides a CLI interface for interacting with the agent.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax

from .core.agent import DataAgent
from .core.config import config
from .rag.document_processor import DocumentProcessor
from .rag.retriever import DocumentRetriever
from .utils.helpers import ensure_directory, get_timestamp
from .utils.logging import logger, setup_logging

# Initialize the Typer app
app = typer.Typer(help="NeuralFlake - Data Engineering Agent CLI")
console = Console()


@app.command()
def chat(
    use_rag: bool = typer.Option(True, "--use-rag/--no-rag", help="Whether to use RAG"),
    save_history: bool = typer.Option(True, "--save/--no-save", help="Save conversation history"),
):
    """
    Start an interactive chat session with the agent.
    """
    console.print(Panel.fit(
        "NeuralFlake - Interactive Chat",
        subtitle="Type 'exit' or 'quit' to end the conversation"
    ))
    
    # Initialize the agent
    try:
        agent = DataAgent()
        console.print("[green]Agent initialized successfully[/green]")
    except Exception as e:
        console.print(f"[red]Error initializing agent: {str(e)}[/red]")
        return
    
    # Start conversation loop
    conversation_active = True
    while conversation_active:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
            
            # Check for exit commands
            if user_input.lower() in ["exit", "quit", "q", "bye"]:
                conversation_active = False
                console.print("[yellow]Ending conversation[/yellow]")
                break
            
            # Special commands
            if user_input.startswith("/"):
                handle_special_command(user_input, agent)
                continue
            
            # Process the query
            with console.status("[bold green]Thinking...[/bold green]"):
                response = agent.chat(user_input, use_rag=use_rag)
            
            # Display the response
            console.print("\n[bold green]Agent[/bold green]")
            console.print(Markdown(response))
            
        except KeyboardInterrupt:
            conversation_active = False
            console.print("[yellow]Conversation interrupted[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
    
    # Save conversation history if enabled
    if save_history and agent.conversation_history:
        try:
            history_dir = ensure_directory(Path(config.data_dir) / "conversation_history")
            timestamp = get_timestamp()
            file_path = history_dir / f"conversation_{timestamp}.json"
            
            if agent.save_conversation(file_path):
                console.print(f"[green]Conversation saved to {file_path}[/green]")
            else:
                console.print("[red]Failed to save conversation history[/red]")
        except Exception as e:
            console.print(f"[red]Error saving conversation: {str(e)}[/red]")


@app.command()
def index(
    directory: str = typer.Argument(..., help="Directory to index"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", help="Index recursively"),
):
    """
    Index documents in a directory for RAG.
    """
    console.print(f"Indexing documents in {directory}")
    
    # Validate directory
    if not os.path.exists(directory) or not os.path.isdir(directory):
        console.print(f"[red]Directory not found: {directory}[/red]")
        return
    
    try:
        # Initialize document processor and retriever
        doc_processor = DocumentProcessor()
        retriever = DocumentRetriever()
        
        # Process documents
        with console.status("[bold green]Processing documents...[/bold green]"):
            documents = doc_processor.process_directory(
                directory_path=directory,
                recursive=recursive,
                metadata={"source_type": "file_system"}
            )
        
        if not documents:
            console.print("[yellow]No documents found to index[/yellow]")
            return
        
        console.print(f"[green]Processed {len(documents)} document chunks[/green]")
        
        # Index documents
        with console.status("[bold green]Indexing documents in vector store...[/bold green]"):
            # Extract text and metadata
            texts = [doc["text"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            
            # Add to vector store
            doc_ids = retriever.add_documents(texts=texts, metadatas=metadatas)
        
        console.print(f"[green]Successfully indexed {len(doc_ids)} document chunks[/green]")
        
    except Exception as e:
        console.print(f"[red]Error indexing documents: {str(e)}[/red]")


@app.command()
def query(
    query_text: str = typer.Argument(..., help="Query to process"),
    use_rag: bool = typer.Option(True, "--use-rag/--no-rag", help="Whether to use RAG"),
):
    """
    Process a single query.
    """
    console.print(f"Processing query: {query_text}")
    
    try:
        # Initialize the agent
        agent = DataAgent()
        
        # Process the query
        with console.status("[bold green]Thinking...[/bold green]"):
            response = agent.query(query_text, use_rag=use_rag)
        
        # Display the response
        console.print("\n[bold green]Response:[/bold green]")
        console.print(Markdown(response))
        
    except Exception as e:
        console.print(f"[red]Error processing query: {str(e)}[/red]")


def handle_special_command(command: str, agent: DataAgent):
    """
    Handle special CLI commands.
    
    Args:
        command: Command string (starting with /)
        agent: DataAgent instance
    """
    cmd_parts = command.split()
    cmd = cmd_parts[0].lower()
    
    if cmd == "/help":
        show_help()
    elif cmd == "/clear":
        agent.clear_conversation()
        console.print("[green]Conversation history cleared[/green]")
    elif cmd == "/load" and len(cmd_parts) > 1:
        file_path = cmd_parts[1]
        if agent.load_conversation(file_path):
            console.print(f"[green]Loaded conversation from {file_path}[/green]")
        else:
            console.print(f"[red]Failed to load conversation from {file_path}[/red]")
    elif cmd == "/save" and len(cmd_parts) > 1:
        file_path = cmd_parts[1]
        if agent.save_conversation(file_path):
            console.print(f"[green]Saved conversation to {file_path}[/green]")
        else:
            console.print(f"[red]Failed to save conversation to {file_path}[/red]")
    else:
        console.print("[yellow]Unknown command. Type /help for available commands.[/yellow]")


def show_help():
    """Display help information about CLI commands."""
    help_text = """
    Available Commands:
    
    Chat Mode:
      /help               Show this help message
      /clear              Clear conversation history
      /save <filename>    Save conversation to a file
      /load <filename>    Load conversation from a file
      exit, quit          Exit the application
    
    CLI Commands:
      chat                Start interactive chat mode
      query <text>        Process a single query
      index <directory>   Index documents in a directory
    """
    
    console.print(Panel(help_text, title="Help", border_style="blue"))


if __name__ == "__main__":
    # Set up logging
    setup_logging("cli")
    
    # Run the app
    app()
