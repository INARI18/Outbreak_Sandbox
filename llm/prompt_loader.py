from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"

def load_prompt(filename: str, **kwargs) -> str:
    path = PROMPTS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {filename}")

    content = path.read_text()

    if not kwargs:
        return content

    try:
        return content.format(**kwargs)
    except KeyError as e:
        # If prompt contains many literal JSON braces the simple format may fail
        # (templates should escape braces). To avoid crashing the app at runtime,
        # fall back to returning the raw template and warn in the console.
        print(f"Warning: prompt formatting failed for {filename}, missing {e}. Returning raw template.")
        return content
