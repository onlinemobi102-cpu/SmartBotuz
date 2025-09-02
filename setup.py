#!/usr/bin/env python3
"""
Setup script for SmartBot.uz deployment
This ensures data directories and default files are created
"""

import os
import json

def create_directories():
    """Create necessary directories"""
    directories = ['data', 'static/uploads']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def create_default_data_files():
    """Create default data files if they don't exist"""
    data_files = {
        'data/services.json': [],
        'data/portfolio.json': [],
        'data/blog.json': [],
        'data/messages.json': []
    }
    
    for file_path, default_content in data_files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_content, f, ensure_ascii=False, indent=2)
            print(f"Created file: {file_path}")

if __name__ == "__main__":
    create_directories()
    create_default_data_files()
    print("Setup completed successfully!")