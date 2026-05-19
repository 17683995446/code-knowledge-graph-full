#!/usr/bin/env python3
"""
CLI interface
"""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from core import UserService, ProductService, OrderService, Logger


def list_users(args):
    """List all users"""
    service = UserService()
    users = service.get_all()
    print(f"Users ({len(users)}):")
    for user in users:
        print(f"  - {user.username} ({user.email})")


def create_user(args):
    """Create a new user"""
    service = UserService()
    user = service.create(args.username, args.email, args.password)
    print(f"Created user: {user.username} with ID {user.id}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Application CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # User commands
    user_parser = subparsers.add_parser("users", help="User management")
    user_subparsers = user_parser.add_subparsers(dest="user_command")
    
    list_parser = user_subparsers.add_parser("list", help="List users")
    list_parser.set_defaults(func=list_users)
    
    create_parser = user_subparsers.add_parser("create", help="Create user")
    create_parser.add_argument("username")
    create_parser.add_argument("email")
    create_parser.add_argument("password")
    create_parser.set_defaults(func=create_user)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
