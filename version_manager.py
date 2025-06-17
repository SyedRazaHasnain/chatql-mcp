#!/usr/bin/env python3
"""
Version management script for Natural Language SQL MCP Server.

This script provides utilities for version bumping, tagging, and release management.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Tuple, Optional


def get_current_version() -> str:
    """Get the current version from __version__.py"""
    version_file = Path("__version__.py")
    if not version_file.exists():
        raise FileNotFoundError("__version__.py not found")
    
    content = version_file.read_text()
    match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Version not found in __version__.py")
    
    return match.group(1)


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse version string into major, minor, patch tuple"""
    try:
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError("Version must be in format major.minor.patch")
        return tuple(int(part) for part in parts)
    except ValueError as e:
        raise ValueError(f"Invalid version format: {version}") from e


def bump_version(version: str, bump_type: str) -> str:
    """Bump version based on type (major, minor, patch)"""
    major, minor, patch = parse_version(version)
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}. Must be major, minor, or patch")


def update_version_file(new_version: str) -> None:
    """Update the version in __version__.py"""
    version_file = Path("__version__.py")
    content = version_file.read_text()
    
    # Update the version
    updated_content = re.sub(
        r'__version__ = ["\'][^"\']+["\']',
        f'__version__ = "{new_version}"',
        content
    )
    
    # Update version_info tuple
    major, minor, patch = parse_version(new_version)
    updated_content = re.sub(
        r'__version_info__ = tuple\(map\(int, __version__\.split\("\."\)\)\)',
        f'__version_info__ = ({major}, {minor}, {patch})',
        updated_content
    )
    
    version_file.write_text(updated_content)
    print(f"✅ Updated __version__.py to {new_version}")


def run_command(command: list, check: bool = True) -> Optional[subprocess.CompletedProcess]:
    """Run a shell command"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(command)}")
        print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return None


def git_tag_exists(tag: str) -> bool:
    """Check if a git tag exists"""
    result = run_command(["git", "tag", "-l", tag], check=False)
    return result and tag in result.stdout


def create_git_tag(version: str, message: str = None) -> None:
    """Create a git tag for the version"""
    tag = f"v{version}"
    
    if git_tag_exists(tag):
        print(f"⚠️  Tag {tag} already exists")
        return
    
    if message is None:
        message = f"Release version {version}"
    
    # Create annotated tag
    run_command(["git", "tag", "-a", tag, "-m", message])
    print(f"✅ Created git tag: {tag}")


def commit_version_change(new_version: str) -> None:
    """Commit version change to git"""
    # Add the version file
    run_command(["git", "add", "__version__.py"])
    
    # Commit the change
    commit_message = f"Bump version to {new_version}"
    run_command(["git", "commit", "-m", commit_message])
    print(f"✅ Committed version change: {commit_message}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Version management for Natural Language SQL MCP Server")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Show current version
    subparsers.add_parser("current", help="Show current version")
    
    # Bump version
    bump_parser = subparsers.add_parser("bump", help="Bump version")
    bump_parser.add_argument("type", choices=["major", "minor", "patch"], help="Type of version bump")
    bump_parser.add_argument("--no-commit", action="store_true", help="Don't commit the version change")
    bump_parser.add_argument("--no-tag", action="store_true", help="Don't create a git tag")
    bump_parser.add_argument("--message", "-m", help="Tag message")
    
    # Set specific version
    set_parser = subparsers.add_parser("set", help="Set specific version")
    set_parser.add_argument("version", help="Version to set (e.g., 1.2.3)")
    set_parser.add_argument("--no-commit", action="store_true", help="Don't commit the version change")
    set_parser.add_argument("--no-tag", action="store_true", help="Don't create a git tag")
    set_parser.add_argument("--message", "-m", help="Tag message")
    
    # Create tag for current version
    tag_parser = subparsers.add_parser("tag", help="Create git tag for current version")
    tag_parser.add_argument("--message", "-m", help="Tag message")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        current_version = get_current_version()
        
        if args.command == "current":
            print(f"Current version: {current_version}")
        
        elif args.command == "bump":
            new_version = bump_version(current_version, args.type)
            print(f"Bumping version from {current_version} to {new_version}")
            
            update_version_file(new_version)
            
            if not args.no_commit:
                commit_version_change(new_version)
            
            if not args.no_tag:
                create_git_tag(new_version, args.message)
        
        elif args.command == "set":
            new_version = args.version
            # Validate version format
            parse_version(new_version)
            
            print(f"Setting version from {current_version} to {new_version}")
            
            update_version_file(new_version)
            
            if not args.no_commit:
                commit_version_change(new_version)
            
            if not args.no_tag:
                create_git_tag(new_version, args.message)
        
        elif args.command == "tag":
            create_git_tag(current_version, args.message)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 