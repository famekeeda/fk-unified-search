#!/usr/bin/env python3
"""
Direct patch for mcp_use.logging without importing
"""
import os
import sys

def find_mcp_use_path():
    """Find mcp_use package path without importing"""
    
    # Check common locations
    for path in sys.path:
        mcp_use_path = os.path.join(path, 'mcp_use')
        if os.path.isdir(mcp_use_path):
            return mcp_use_path
    
    # Try site-packages specifically
    import site
    for site_path in site.getsitepackages():
        mcp_use_path = os.path.join(site_path, 'mcp_use')
        if os.path.isdir(mcp_use_path):
            return mcp_use_path
    
    return None

def patch_mcp_logging_direct():
    """Directly patch mcp_use logging file"""
    
    mcp_use_path = find_mcp_use_path()
    if not mcp_use_path:
        print("Could not find mcp_use package")
        return False
    
    logging_file = os.path.join(mcp_use_path, 'logging.py')
    
    if not os.path.exists(logging_file):
        print(f"Logging file not found: {logging_file}")
        return False
    
    print(f"Patching mcp_use logging at: {logging_file}")
    
    try:
        # Read current content
        with open(logging_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already patched
        if 'PATCHED_FOR_COMPATIBILITY' in content:
            print("mcp_use logging already patched")
            return True
        
        # Replace the problematic import
        old_import = "from langchain.globals import set_debug as langchain_set_debug"
        new_import = """# PATCHED_FOR_COMPATIBILITY
try:
    from langchain.globals import set_debug as langchain_set_debug
except ImportError:
    # Fallback for compatibility
    def langchain_set_debug(debug: bool = True) -> None:
        pass"""
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            
            # Write the patched content
            with open(logging_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("Successfully patched mcp_use logging")
            return True
        else:
            print("Import pattern not found, checking content...")
            print("First 500 chars of file:")
            print(content[:500])
            return False
            
    except Exception as e:
        print(f"Error patching mcp_use logging: {e}")
        return False

def test_mcp_import():
    """Test mcp_use import after patching"""
    
    try:
        # Clear any cached imports
        modules_to_clear = ['mcp_use', 'mcp_use.logging', 'mcp_use.client']
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        print("Testing mcp_use import...")
        from mcp_use.client import MCPClient
        print("✓ mcp_use.client import successful")
        return True
        
    except Exception as e:
        print(f"❌ mcp_use import failed: {e}")
        return False

def main():
    """Main patching process"""
    print("Directly patching mcp_use logging...")
    
    if patch_mcp_logging_direct():
        print("Patch applied, testing import...")
        if test_mcp_import():
            print("🎉 mcp_use import working!")
        else:
            print("⚠️ Import still failing")
    else:
        print("❌ Patch failed")

if __name__ == "__main__":
    main()