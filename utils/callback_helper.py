from urllib.parse import quote

from urllib.parse import quote

def make_callback(action: str, data: str):
    encoded = quote(data)
    result = f"{action}:{encoded}"
    if len(result) > 64:
        raise ValueError(f"Слишком длинный callback_data: {result}")
    return result


def parse_callback(callback_data: str) -> tuple[str, str]:
    if ':' not in callback_data:
        return "", ""
    prefix, encoded = callback_data.split(":", 1)
    from urllib.parse import unquote
    return prefix, unquote(encoded)
