import re


def get_public_input(path):
    """
      component main = T();
      component main {public [in1, in2]} = T();
    """
    pattern = re.compile(
        r"^component\s+(\w+)" 
        r"(?:\s*\{public\s*\[([^\]]*)\]\})?" 
        r"\s*=\s*(\w+)\s*\(\s*\);$",
        re.IGNORECASE
    )

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in reversed(lines):
        stripped = line.strip()
        match = pattern.match(stripped)
        if match:
            name = match.group(1)
            ports = match.group(2)
            target = match.group(3)
            ports = [f'{target}[0].{p.strip()}' for p in ports.split(",")] if ports else []
            return ports
    return []
