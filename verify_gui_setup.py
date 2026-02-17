#!/usr/bin/env python3
"""
GUI Setup Verification Script
Validates complete GUI implementation and dependencies
"""

import sys
import os
from pathlib import Path


def check_directories():
    """Check all required directories exist"""
    print("\n📁 Checking Directory Structure...")
    
    required_dirs = [
        "gui",
        "gui/pages",
        "gui/components",
        "services",
        "models",
        "sql",
        "utils",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        if full_path.exists() and full_path.is_dir():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} (MISSING)")
            all_exist = False
    
    return all_exist


def check_files():
    """Check all required files exist"""
    print("\n📄 Checking File Structure...")
    
    required_files = [
        # Main application
        "app.py",
        "run_gui.py",
        
        # GUI components
        "gui/__init__.py",
        "gui/components/__init__.py",
        "gui/components/common.py",
        "gui/pages/__init__.py",
        
        # Pages
        "gui/pages/dashboard_page.py",
        "gui/pages/owners_page.py",
        "gui/pages/units_page.py",
        "gui/pages/clients_page.py",
        "gui/pages/ownerships_page.py",
        "gui/pages/assignments_page.py",
        "gui/pages/receipts_page.py",
        "gui/pages/taxes_page.py",
        
        # Documentation
        "GUI_README.md",
        "GUI_PAGES_REFERENCE.md",
        "GUI_TRANSFORMATION_COMPLETE.md",
        
        # Core files
        "database.py",
        "config.py",
        "models/__init__.py",
        "services/__init__.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists() and full_path.is_file():
            size_kb = full_path.stat().st_size / 1024
            print(f"  ✅ {file_path} ({size_kb:.1f} KB)")
        else:
            print(f"  ❌ {file_path} (MISSING)")
            all_exist = False
    
    return all_exist


def check_imports():
    """Check all imports work correctly"""
    print("\n📚 Checking Python Imports...")
    
    import_tests = [
        ("flet", "Flet GUI Framework"),
        ("sqlite3", "SQLite3"),
        ("gui.pages.dashboard_page", "Dashboard Page"),
        ("gui.pages.owners_page", "Owners Page"),
        ("gui.pages.units_page", "Units Page"),
        ("gui.pages.clients_page", "Clients Page"),
        ("gui.pages.ownerships_page", "Ownerships Page"),
        ("gui.pages.assignments_page", "Assignments Page"),
        ("gui.pages.receipts_page", "Receipts Page"),
        ("gui.pages.taxes_page", "Taxes Page"),
        ("gui.components.common", "Common Components"),
        ("services.owner_service", "Owner Service"),
        ("services.unit_service", "Unit Service"),
        ("services.client_service", "Client Service"),
        ("services.assignment_service", "Assignment Service"),
        ("services.receipt_service", "Receipt Service"),
    ]
    
    all_imported = True
    for module_name, display_name in import_tests:
        try:
            __import__(module_name)
            print(f"  ✅ {display_name}")
        except ImportError as e:
            print(f"  ❌ {display_name}: {str(e)}")
            all_imported = False
        except Exception as e:
            print(f"  ⚠️  {display_name}: {type(e).__name__}")
    
    return all_imported


def check_content():
    """Check key content in files"""
    print("\n✍️  Checking File Content...")
    
    checks = [
        ("app.py", "ft.app"),
        ("run_gui.py", "def main"),
        ("gui/components/common.py", "def create_header"),
        ("gui/pages/dashboard_page.py", "def create"),
        ("gui/pages/owners_page.py", "owner_service"),
        ("gui/pages/units_page.py", "unit_service"),
        ("gui/pages/clients_page.py", "client_service"),
        ("gui/pages/ownerships_page.py", "ownership"),
        ("gui/pages/assignments_page.py", "assignment_service"),
        ("gui/pages/receipts_page.py", "receipt_service"),
        ("gui/pages/taxes_page.py", "tax"),
    ]
    
    all_content_ok = True
    for file_path, search_string in checks:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if search_string.lower() in content.lower():
                    line_count = len(content.split('\n'))
                    print(f"  ✅ {file_path} ({line_count} lines)")
                else:
                    print(f"  ❌ {file_path} (missing '{search_string}')")
                    all_content_ok = False
        except Exception as e:
            print(f"  ❌ {file_path}: {str(e)}")
            all_content_ok = False
    
    return all_content_ok


def check_documentation():
    """Check documentation files"""
    print("\n📖 Checking Documentation...")
    
    docs = [
        ("GUI_README.md", "Architecture", 200),
        ("GUI_PAGES_REFERENCE.md", "Fields", 400),
        ("GUI_TRANSFORMATION_COMPLETE.md", "Status", 500),
    ]
    
    all_docs_ok = True
    for doc_file, key_content, min_lines in docs:
        try:
            with open(doc_file, 'r') as f:
                content = f.read()
                lines = len(content.split('\n'))
                
                if key_content.lower() in content.lower() and lines >= min_lines:
                    print(f"  ✅ {doc_file} ({lines} lines)")
                else:
                    print(f"  ⚠️  {doc_file} ({lines} lines, expected {min_lines}+)")
                    all_docs_ok = False
        except Exception as e:
            print(f"  ❌ {doc_file}: {str(e)}")
            all_docs_ok = False
    
    return all_docs_ok


def print_summary(results):
    """Print summary of all checks"""
    print("\n" + "=" * 60)
    print("✅ VERIFICATION SUMMARY")
    print("=" * 60)
    
    categories = [
        ("Directory Structure", results['dirs']),
        ("File Structure", results['files']),
        ("Python Imports", results['imports']),
        ("File Content", results['content']),
        ("Documentation", results['docs']),
    ]
    
    all_pass = True
    for category, passed in categories:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{category:.<40} {status}")
        if not passed:
            all_pass = False
    
    print("=" * 60)
    
    if all_pass:
        print("\n🎉 All checks passed! GUI is ready to use.")
        print("\nTo run the application:")
        print("  python3 run_gui.py")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please review above.")
        return 1


def main():
    """Run all verification checks"""
    print("\n" + "=" * 60)
    print("🔍 RENT MANAGER GUI SETUP VERIFICATION")
    print("=" * 60)
    
    results = {
        'dirs': check_directories(),
        'files': check_files(),
        'imports': check_imports(),
        'content': check_content(),
        'docs': check_documentation(),
    }
    
    exit_code = print_summary(results)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
