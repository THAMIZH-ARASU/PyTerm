from file_system.virtual_file_system import VirtualFileSystem

def debug_mkdir():
    fs = VirtualFileSystem()
    
    print("Testing mkdir functionality...")
    print(f"Current path: {fs.current_path}")
    print(f"Root exists: {fs.root is not None}")
    print(f"Root is directory: {fs.root.is_directory}")
    print(f"Root children: {fs.root.children}")
    
    # Test creating /test
    result = fs.mkdir("/test")
    print(f"mkdir('/test') returned: {result}")
    print(f"After mkdir, root children: {fs.root.children}")
    print(f"/test exists: {fs.exists('/test')}")
    print(f"/test is directory: {fs.is_directory('/test')}")

if __name__ == "__main__":
    debug_mkdir()