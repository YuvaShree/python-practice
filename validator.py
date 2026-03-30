import os
import re
import sys

FILE_RULES = {
    ".py": "snake_case",
    ".tf": "snake_case",
    ".js": "camelCase",
    ".yaml": "kebab-case",
    ".yml": "kebab-case"
}

PATTERNS = {
    "snake_case": r"^[a-z_][a-z0-9_]*$",
    "camelCase": r"^[a-z][a-zA-Z0-9]*$",
    "kebab-case": r"^[a-z0-9\-]+$",
    "SCREAMING_SNAKE_CASE": r"^[A-Z_][A-Z0-9_]*$"
}

def is_valid(var, rule):
    if re.match(PATTERNS[rule], var):
        return True
    if re.match(PATTERNS["SCREAMING_SNAKE_CASE"], var):
        return True
    return False


def extract_variables(file_path):
    variables = set()

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if ":" in line and not line.startswith("-"):
                var = line.split(":")[0].strip()
                if re.match(r"^[a-zA-Z0-9\-]+$", var):
                    variables.add(var)

            elif "=" in line:
                var = line.split("=")[0].strip()
                if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", var):
                    variables.add(var)

    return list(variables)


REPORT = []

def validate_file(file_path):
    ext = os.path.splitext(file_path)[1]

    if ext not in FILE_RULES:
        return

    rule = FILE_RULES[ext]
    variables = extract_variables(file_path)

    for var in variables:
        status = "OK" if is_valid(var, rule) else "FAIL"
        REPORT.append((file_path, var, status))


def run_validator():
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith((".py", ".js", ".tf", ".yaml", ".yml")):
                validate_file(os.path.join(root, file))


if __name__ == "__main__":
    run_validator()

    failed = any(status == "FAIL" for _, _, status in REPORT)

    if failed:
        print("❌ Naming violations found")
        sys.exit(1)
    else:
        print("✅ No violations")
        sys.exit(0)