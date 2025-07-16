#!/usr/bin/env python3
"""
Requirements generation script for LARP Manager Server.

This script automates the generation of requirements.txt and requirements-dev.txt
files using pip-compile with bidirectional constraint handling.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_colored(message: str, color: str = Colors.END) -> None:
    """Print colored message to stdout."""
    print(f"{color}{message}{Colors.END}")


def print_step(message: str) -> None:
    """Print a step message."""
    print_colored(f"📋 {message}", Colors.BLUE)


def print_success(message: str) -> None:
    """Print a success message."""
    print_colored(f"✅ {message}", Colors.GREEN)


def print_warning(message: str) -> None:
    """Print a warning message."""
    print_colored(f"⚠️  {message}", Colors.YELLOW)


def print_error(message: str) -> None:
    """Print an error message."""
    print_colored(f"❌ {message}", Colors.RED)


def check_pip_tools() -> bool:
    """Check if pip-tools is installed."""
    try:
        subprocess.run(
            ["pip-compile", "--version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def backup_requirements_files() -> None:
    """Create backup of existing requirements files."""
    project_root = Path.cwd()
    backup_dir = project_root / "requirements_backup"
    
    # Create backup directory if it doesn't exist
    backup_dir.mkdir(exist_ok=True)
    
    # Backup existing files
    for filename in ["requirements.txt", "requirements-dev.txt"]:
        file_path = project_root / filename
        if file_path.exists():
            backup_path = backup_dir / f"{filename}.bak"
            shutil.copy2(file_path, backup_path)
            print_step(f"Backed up {filename} to {backup_path}")


def run_pip_compile(args: List[str]) -> subprocess.CompletedProcess:
    """
    Run pip-compile with the given arguments.
    
    Args:
        args: List of arguments to pass to pip-compile
        
    Returns:
        CompletedProcess object
        
    Raises:
        subprocess.CalledProcessError: If pip-compile fails
    """
    # Base command with common options
    cmd = [
        "pip-compile",
        "--resolver=backtracking",
        "--upgrade",
        "--generate-hashes",
        "--strip-extras",
    ] + args
    
    print_step(f"Running: {' '.join(cmd)}")
    
    # Run the command
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )
    
    # Print output for debugging
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print_warning(f"stderr: {result.stderr}")
    
    if result.returncode != 0:
        print_error(f"Command failed with return code {result.returncode}")
        raise subprocess.CalledProcessError(result.returncode, cmd)
    
    return result


def dev_first_approach() -> bool:
    """
    Try the dev-first approach: compile requirements-dev.txt first,
    then use it as a constraint for requirements.txt.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print_step("🔄 Trying dev-first approach...")
        
        # Step 1: Compile requirements-dev.txt
        print_step("Compiling requirements-dev.txt...")
        run_pip_compile([
            "--extra=dev",
            "--output-file=requirements-dev.txt",
            "pyproject.toml"
        ])
        
        # Step 2: Use requirements-dev.txt as constraint for requirements.txt
        print_step("Compiling requirements.txt with dev constraints...")
        run_pip_compile([
            "--constraint=requirements-dev.txt",
            "--output-file=requirements.txt",
            "pyproject.toml"
        ])
        
        print_success("Dev-first approach successful!")
        return True
        
    except subprocess.CalledProcessError as e:
        print_warning(f"Dev-first approach failed: {e}")
        return False


def reverse_approach() -> bool:
    """
    Try the reverse approach: compile requirements.txt first,
    then use it as a constraint for requirements-dev.txt.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print_step("🔄 Trying reverse approach...")
        
        # Step 1: Compile requirements.txt
        print_step("Compiling requirements.txt...")
        run_pip_compile([
            "--output-file=requirements.txt",
            "pyproject.toml"
        ])
        
        # Step 2: Use requirements.txt as constraint for requirements-dev.txt
        print_step("Compiling requirements-dev.txt with main constraints...")
        run_pip_compile([
            "--constraint=requirements.txt",
            "--extra=dev",
            "--output-file=requirements-dev.txt",
            "pyproject.toml"
        ])
        
        print_success("Reverse approach successful!")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Reverse approach failed: {e}")
        return False


def validate_requirements_files() -> bool:
    """
    Validate that the generated requirements files are valid.
    
    Returns:
        True if valid, False otherwise
    """
    project_root = Path.cwd()
    
    for filename in ["requirements.txt", "requirements-dev.txt"]:
        file_path = project_root / filename
        
        if not file_path.exists():
            print_error(f"{filename} was not generated")
            return False
        
        # Check if file is not empty
        if file_path.stat().st_size == 0:
            print_error(f"{filename} is empty")
            return False
        
        # Check if file contains some expected content
        content = file_path.read_text()
        if "# This file is autogenerated by pip-compile" not in content:
            print_error(f"{filename} doesn't appear to be generated by pip-compile")
            return False
    
    print_success("Requirements files validated successfully")
    return True


def main() -> int:
    """
    Main function to update requirements files.
    
    Returns:
        0 if successful, 1 if failed
    """
    print_colored("🚀 Starting requirements update process", Colors.BOLD)
    
    # Check if pip-tools is installed
    if not check_pip_tools():
        print_error("pip-tools is not installed. Please install it with: pip install pip-tools")
        return 1
    
    # Check if pyproject.toml exists
    if not Path("pyproject.toml").exists():
        print_error("pyproject.toml not found. Make sure you're in the project root.")
        return 1
    
    # Backup existing files
    backup_requirements_files()
    
    # Try dev-first approach
    if dev_first_approach():
        success = True
    else:
        # Try reverse approach if dev-first fails
        if reverse_approach():
            success = True
        else:
            print_error("Both approaches failed. Check the error messages above.")
            success = False
    
    if success:
        # Validate the generated files
        if validate_requirements_files():
            print_success("Requirements files updated successfully!")
            print_step("Next steps:")
            print("  1. Review the generated files")
            print("  2. Test with: pip install -r requirements-dev.txt")
            print("  3. Commit the changes if everything looks good")
            return 0
        else:
            print_error("Requirements files validation failed")
            return 1
    else:
        print_error("Failed to update requirements files")
        return 1


if __name__ == "__main__":
    sys.exit(main())