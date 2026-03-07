# patch_djongo.py
import os
import sys

try:
    base_path = os.path.join(sys.prefix, "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages", "djongo", "base.py")
    with open(base_path, "r") as f:
        content = f.read()
    content = content.replace("if self.connection:", "if self.connection is not None:")
    with open(base_path, "w") as f:
        f.write(content)
    print("Djongo patch applied successfully!")
except Exception as e:
    print(f"Failed to patch Djongo: {e}")