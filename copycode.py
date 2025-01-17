import os
import pyperclip
from pathlib import Path
import datetime
import argparse

def get_project_structure(start_path, max_depth=-1):
    # Extended list of ignored directories
    IGNORED_DIRS = {
        '__pycache__', '.venv', 'venv', 'env',      # Python virtual environments
        'node_modules', '.git', '.idea', '.pytest_cache',  # Dev tools
        '.vscode', 'build', 'dist', 'target',        # Build directories
        'migrations', 'coverage', '.next',           # Additional React-specific dirs
        '.cache', '.husky', '.github'                # More dev tool dirs
    }
    
    # Include React and web development files
    INCLUDED_EXTENSIONS = {
        '.py',                          # Python files
        '.jsx', '.tsx', '.js', '.ts',   # React/JavaScript files
        '.css', '.scss', '.sass',       # Styling files
        '.html',                        # HTML files
        '',                            # For files without extensions (like 'Dockerfile')
        '.yml', '.yaml',               # Docker Compose and other config files
        #'.env',                        # Environment files
        '.dockerfile',                 # Docker-specific files
        '.json',                       # JSON files including package.json
        '.lock',                       # Lock files (yarn.lock, package-lock.json)
        '.txt',                        # Text files including requirements.txt
        '.config.js'                   # Configuration files including Tailwind and PostCSS
    }
    
    # Files to ignore even if they match the extension
    IGNORED_FILES = {
        'setupTests.', 'reportWebVitals.',  # React testing files
        '.test.', '.spec.',                 # Test files
        'types.d.ts',                       # TypeScript declaration files
        '.gitignore'                        # Git ignore file
    }
    
    # Specific important files to always include
    IMPORTANT_FILES = {
        'package.json',
        'package-lock.json',
        'yarn.lock',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml',
        #'.env',
        'tailwind.config.js',           # Tailwind configuration
        'postcss.config.js'            # PostCSS configuration
    }
        
    output = ["Directory Structure:"]
    file_contents = ["\nFile Contents:\n"]
    
    for root, dirs, files in os.walk(start_path):
        # Check depth
        level = root.replace(start_path, '').count(os.sep)
        if max_depth != -1 and level > max_depth:
            dirs.clear()
            continue
            
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith('.')]
        
        # Calculate indentation
        indent = '│   ' * level
        
        # Add directory to structure
        dir_name = os.path.basename(root)
        if level > 0:
            output.append(f"{indent[:-4]}├── {dir_name}/")
        else:
            output.append(dir_name + '/')
        
        # Process files
        for file in sorted(files):
            # Skip if file should be ignored
            if any(ignore in file for ignore in IGNORED_FILES):
                continue
                
            # Include files if they match extensions, are Docker files, or are important files
            if (Path(file).suffix in INCLUDED_EXTENSIONS) or (file in IMPORTANT_FILES):
                # Add to structure
                output.append(f"{indent}├── {file}")
                
                # Add file contents
                try:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    
                    # Skip files larger than 100KB
                    if file_size > 100 * 1024:
                        file_contents.extend([
                            f"\nFile: {file} (skipped - too large, {file_size/1024:.1f}KB)",
                            ""
                        ])
                        continue
                        
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        rel_path = os.path.relpath(file_path, start_path)
                        file_contents.extend([
                            f"\nFile: {rel_path}",
                            "-" * 40,
                            content,
                            "-" * 40,
                            ""
                        ])
                except Exception as e:
                    file_contents.extend([
                        f"Error reading {file}: {str(e)}",
                        ""
                    ])
    
    # Combine structure and contents
    full_output = "\n".join(output + file_contents)
    return full_output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Copy project structure and contents')
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('--depth', type=int, default=4, help='Maximum depth to traverse (-1 for unlimited)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"Directory not found: {args.directory}")
        exit(1)
    
    result = get_project_structure(args.directory, args.depth)
    
    # Copy to clipboard
    pyperclip.copy(result)
    
    # Save to file with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"project_structure_{timestamp}.txt"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, output_file)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"Project structure and contents have been:")
    print(f"1. Copied to clipboard")
    print(f"2. Saved to file: {output_path}")