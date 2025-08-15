import requests
from bs4 import BeautifulSoup

def buscar_precio(producto: str) -> float:
    try:
        url = f"https://listado.mercadolibre.com.ar/{producto.replace(' ', '-')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        precio = soup.find("span", class_="andes-money-amount__fraction").text
        return float(precio.replace(".", "").replace(",", "."))
    except:
        return 0.0  # Retorna 0 si hay error