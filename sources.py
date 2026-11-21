import os

FILE_PATH = os.path.join(os.path.dirname(__file__), "domains.txt")

def load_domains() -> list:
    """Загружает список доменов из файла, игнорируя пустые строки"""
    if not os.path.exists(FILE_PATH):
        # Если файла нет — создаем пустой
        open(FILE_PATH, "w", encoding="utf-8").close()
        return []
    
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        # Читаем, убираем пробелы по краям и отбрасываем пустые строки
        lines = [line.strip() for line in f.readlines() if line.strip()]
        return lines

def save_domains(domains: list):
    """Перезаписывает файл списком доменов"""
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        for d in domains:
            f.write(f"{d}\n")

def add_domain(domain: str) -> bool:
    """Добавляет домен. Возвращает True, если добавил, False если уже есть."""
    domains = load_domains()
    # Очищаем от протоколов
    clean_domain = domain.replace("https://", "").replace("http://", "").split("/")[0].strip().lower()
    
    if clean_domain in domains:
        return False
        
    # Дописываем в конец файла (чтобы не перезаписывать всё каждый раз)
    with open(FILE_PATH, "a", encoding="utf-8") as f:
        f.write(f"{clean_domain}\n")
        
    return True
    
    
def delete_domain(domain: str) -> bool:
    domains = load_domains()
    clean_domain = domain.replace("https://", "").replace("http://", "").split("/")[0].strip().lower()
    
    if clean_domain in domains:
        domains.remove(clean_domain)
        save_domains(domains)
        return True
    return False
