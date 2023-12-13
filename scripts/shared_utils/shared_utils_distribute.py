import os
import shutil

# run this to generate shared_utils files where needed, from scripts/shared_utils
dest_dirs = [
  "../../special_message_skill/lambda",
  "../../platform-configs/terraform/lambdas"
]

def main():
  if not os.getcwd().endswith("shared_utils"):
    print("run this to generate shared_utils files where needed, from scripts/shared_utils")
    return
  for dir in dest_dirs:
    dest_path = os.path.join(dir, "shared_utils.py")
    print("Copying to", dest_path)
    shutil.copy("./shared_utils.py", dest_path)

if __name__ == "__main__":
  main()
