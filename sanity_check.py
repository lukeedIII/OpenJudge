import os
import tools

def main():
    print("=== OpenJudge Physical Hands Sanity Check ===")
    
    # 1. Test Bash
    print("\n[1] Testing execute_bash...")
    bash_out = tools.execute_bash('echo "Bash tool is working"')
    print(f"Output: {bash_out}")
    if "Bash tool is working" not in bash_out:
        print("[!] Bash Test Failed.")
        return
        
    # 2. Test Python
    print("\n[2] Testing execute_python...")
    py_out = tools.execute_python('print("Python tool is working")')
    print(f"Output: {py_out}")
    if "Python tool is working" not in py_out:
        print("[!] Python Test Failed.")
        return
        
    # 3. Test File I/O
    print("\n[3] Testing write_file & read_file...")
    test_file = "test_sanity.txt"
    test_content = "File I/O is working perfectly."
    
    write_out = tools.write_file(test_file, test_content)
    print(f"Write Output: {write_out}")
    
    if not os.path.exists(test_file):
        print("[!] File Write Failed: File does not exist.")
        return
        
    read_out = tools.read_file(test_file)
    print(f"Read Output: {read_out}")
    
    if test_content not in read_out:
        print("[!] File Read Failed: Content mismatch.")
        return
        
    # Cleanup
    os.remove(test_file)
    print("[+] Cleanup: Temporary file deleted.")
    
    print("\n=======================================================")
    print(">>> SUCCESS: ALL PHYSICAL TOOLS ARE FULLY OPERATIONAL <<<")
    print("=======================================================")

if __name__ == "__main__":
    main()
