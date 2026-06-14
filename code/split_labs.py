import os

labs_dir = '/home/i5l3m/Desktop/CTF/tutorials/z3-tutorial/code/08_labs'
solvers_dir = os.path.join(labs_dir, 'solvers')
os.makedirs(solvers_dir, exist_ok=True)

for filename in os.listdir(labs_dir):
    if not filename.startswith('lab') or not filename.endswith('.py'):
        continue
    filepath = os.path.join(labs_dir, filename)
    with open(filepath, 'r') as f:
        content = f.read()
    
    if 'def solve():' not in content:
        continue
        
    parts = content.split('def solve():')
    header_and_validate = parts[0]
    solver_part = 'def solve():' + parts[1]
    
    # Write the challenge
    challenge_content = header_and_validate + """
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Usage: python3 {filename} <password>")
        sys.exit(1)
    if validate_password(sys.argv[1]):
        print("[+] Correct!")
    else:
        print("[-] Wrong.")
"""
    with open(filepath, 'w') as f:
        f.write(challenge_content)
        
    # Write the solver
    solver_content = "#!/usr/bin/env python3\nimport z3\n\n" + solver_part
    
    # Remove the assert validate_password from the solver main block
    import re
    solver_content = re.sub(r'if __name__ == "__main__":\n.*$', 'if __name__ == "__main__":\n    solve()', solver_content, flags=re.DOTALL)
    
    solver_filename = f"solve_{filename}"
    with open(os.path.join(solvers_dir, solver_filename), 'w') as f:
        f.write(solver_content)
    
    print(f"Split {filename}")

