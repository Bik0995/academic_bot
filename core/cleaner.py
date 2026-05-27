from bs4 import BeautifulSoup

def clean_html(raw: str) -> str:
    soup = BeautifulSoup(raw, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def truncate(text: str, max_len: int = 200) -> str:
    if len(text) > max_len:
        return text[:max_len].rsplit(" ", 1)[0] + "..."
    return text