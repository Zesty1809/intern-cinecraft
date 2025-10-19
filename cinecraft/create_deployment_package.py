#!/usr/bin/env python3
"""
Django Project Deployment Package Creator
Creates a clean zip file of the Django project for deployment on another machine.
Excludes: .md files, virtual environments, __pycache__, .pyc files, etc.
"""

import os
import sys
import zipfile
from datetime import datetime


def should_exclude(path, base_dir):
    """
    Determine if a file or directory should be excluded from the zip.
    """
    # Convert to relative path for easier checking
    try:
        rel_path = os.path.relpath(path, base_dir)
    except ValueError:
        return True
    
    # List of patterns to exclude
    exclude_patterns = [
        # Documentation
        '.md',
        '.MD',
        
        # Python cache and compiled files
        '__pycache__',
        '.pyc',
        '.pyo',
        '.pyd',
        
        # Virtual environments
        'venv',
        'env',
        '.venv',
        '.env',
        'ENV',
        
        # IDE and editor files
        '.vscode',
        '.idea',
        '.vs',
        '*.swp',
        '*.swo',
        '*~',
        '.DS_Store',
        
        # Git
        '.git',
        '.gitignore',
        '.gitattributes',
        
        # Database (optional - comment out if you want to include it)
        # 'db.sqlite3',
        
        # Static files (will be regenerated)
        'staticfiles',
        
        # This script itself
        'create_deployment_package.py',

    # Long readme/setup docs – keep package minimal with only RUN_STEPS.txt
    'DEPLOYMENT_README.txt',
    'DEPLOYMENT_PACKAGE_DOCUMENTATION.md',
    'DEPLOYMENT_SUCCESS.txt',
    'DEPLOYMENT_QUICK_REFERENCE.txt',
        
        # Log files
        '*.log',
        
        # Temporary files
        'tmp',
        'temp',
        '.tmp',
        
        # OS files
        'Thumbs.db',
        'desktop.ini',
    ]
    

    # Always include any templates directory and its contents (project-level, app-level, or nested)
    # Also always include root-level templates/ and its subdirs/files
    rel_parts = rel_path.split(os.sep)
    if 'templates' in rel_parts or (rel_parts and rel_parts[0] == 'templates'):
        return False

    # Always include any 'templates' directory and its contents
    # (root-level or nested in any app)
    if 'templates' in rel_path.split(os.sep):
        return False

    # Check if path matches any exclude pattern
    path_str = str(path)
    rel_path_str = str(rel_path)
    for pattern in exclude_patterns:
        # Check file extension
        if pattern.startswith('.') and path_str.endswith(pattern):
            return True
        # Check if pattern is in the path
        if pattern in rel_path_str or pattern in path_str:
            return True
        # Check directory name
        if os.path.isdir(path):
            dir_name = os.path.basename(path)
            if dir_name == pattern or dir_name.startswith('.'):
                return True
    return False

def create_deployment_zip(project_dir, output_name=None):
    """
    Create a deployment zip file of the Django project.
    """
    project_dir = os.path.abspath(project_dir)
    
    if not os.path.exists(project_dir):
        print(f"❌ Error: Project directory '{project_dir}' does not exist!")
        return False
    
    # Generate output filename if not provided
    if output_name is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        project_name = os.path.basename(project_dir)
        output_name = f"{project_name}_deployment_{timestamp}.zip"
    
    # Ensure .zip extension
    if not output_name.endswith('.zip'):
        output_name += '.zip'
    
    output_path = os.path.join(os.path.dirname(project_dir), output_name)
    
    print("📦 Creating deployment package...")
    print(f"📁 Project directory: {project_dir}")
    print(f"💾 Output file: {output_path}")
    print()
    
    files_added = 0
    files_excluded = 0
    
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_dir):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), project_dir)]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Skip excluded files
                    if should_exclude(file_path, project_dir):
                        files_excluded += 1
                        continue
                    
                    # Calculate the archive name (relative path)
                    arcname = os.path.relpath(file_path, project_dir)
                    
                    # Add file to zip
                    zipf.write(file_path, arcname)
                    files_added += 1
                    
                    # Print progress for every 10 files
                    if files_added % 10 == 0:
                        print(f"  Added {files_added} files...", end='\r')

            # Also include a sibling 'templates' directory (project-root level)
            parent_templates_dir = os.path.join(os.path.dirname(project_dir), 'templates')
            if os.path.isdir(parent_templates_dir):
                for root, _, files in os.walk(parent_templates_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Archive path should be under 'templates/'
                        rel_from_templates = os.path.relpath(file_path, parent_templates_dir)
                        arcname = os.path.join('templates', rel_from_templates)
                        zipf.write(file_path, arcname)
                        files_added += 1
        
        print("\n")
        print("✅ Deployment package created successfully!")
        print("📊 Statistics:")
        print(f"   - Files included: {files_added}")
        print(f"   - Files excluded: {files_excluded}")
        print(f"   - Package size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
        print(f"   - Location: {output_path}")
        print()
        print("📝 Next steps on the target machine:")
        print(f"   1. Unzip the package: unzip {os.path.basename(output_path)}")
        print("   2. Create virtual environment: python3 -m venv venv")
        print("   3. Activate virtual environment: source venv/bin/activate  (Linux/Mac)")
        print("                                   or: venv\\Scripts\\activate  (Windows)")
        print("   4. Install dependencies: pip install -r requirements.txt")
        print("   5. Run migrations: python manage.py migrate")
        print("   6. Create superuser: python manage.py createsuperuser")
        print("   7. (Optional) Collect static: python manage.py collectstatic --noinput")
        print("   8. Run server: python manage.py runserver")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating zip file: {e}")
        return False

def main():
    """
    Main function to run the script.
    """
    print("=" * 70)
    print("  Django Project Deployment Package Creator")
    print("=" * 70)
    print()
    
    # Get the directory where this script is located (should be project root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if manage.py exists (confirm it's a Django project)
    if not os.path.exists(os.path.join(script_dir, 'manage.py')):
        print("❌ Error: manage.py not found!")
        print("   This script should be placed in the Django project root directory.")
        print(f"   Current directory: {script_dir}")
        sys.exit(1)
    
    # Custom output name (optional)
    output_name = None
    if len(sys.argv) > 1:
        output_name = sys.argv[1]
    
    # Create the deployment package
    success = create_deployment_zip(script_dir, output_name)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
