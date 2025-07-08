
from file_system.virtual_file_system import VirtualFileSystem


def run_tests():
    """Run basic tests."""
    print("Running basic tests...")
    
    # Test file system
    fs = VirtualFileSystem()
    assert fs.mkdir("/test")
    assert fs.touch("/test/file.txt", "Hello World")
    assert fs.read_file("/test/file.txt") == "Hello World"
    assert fs.is_directory("/test")
    assert fs.is_file("/test/file.txt")
