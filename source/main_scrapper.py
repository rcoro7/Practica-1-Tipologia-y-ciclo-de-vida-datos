#!/usr/bin/env python
# coding: utf-8

# In[4]:


# =========================================================
# IMPORTACIÓN DE LIBRERÍAS
# =========================================================
# Librerías estándar para manipular texto, tiempo y expresiones regulares
import re
import csv
import time
import logging
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime

# =========================================================
# CONFIGURACIÓN INICIAL DEL SCRAPER
# =========================================================

# URL base del portal de empleo
BASE = "https://www.tecnoempleo.com"

# Categorías de búsqueda a recorrer de forma automática
CATEGORIES = [
    "big-data",
    "data-science",
    "inteligencia-artificial",
    "machine-learning",
    "analisis-de-datos",
    "python",
    "business-intelligence"
]

# ---------------------------------------------------------
# CONFIGURACIÓN DEL LOGGING (compatible con Jupyter/Anaconda)
# ---------------------------------------------------------
# Se eliminan posibles manejadores duplicados (evita logs repetidos)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Definición del formato de salida para el seguimiento del proceso
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)

# Cabeceras HTTP para simular un navegador real y evitar bloqueos del servidor
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/141.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
}

# Creación de sesión persistente para mantener cabeceras y cookies
session = requests.Session()
session.headers.update(HEADERS)

# =========================================================
# FUNCIÓN 1: obtener enlaces de una categoría con paginación
# =========================================================
def get_offer_links(category):
    """
    Devuelve una lista de tuplas (url, fecha) para una categoría.
    Implementa un sistema de paginación robusto con detección de repeticiones
    y control de errores para evitar bloqueos o bucles infinitos.
    """
    results = []          # Lista final con los pares (link, fecha)
    seen_last = set()     # Control de duplicados entre páginas
    page = 1              # Página inicial
    empty_streak = 0      # Contador para detectar ausencia de resultados consecutivos

    while True:
        # Construcción dinámica de la URL con parámetros de categoría y página
        url = f"{BASE}/ofertas-trabajo/?te={category.replace('-', '+')}&pagina={page}"
        r = session.get(url, timeout=15)

        # Si el servidor devuelve un código distinto de 200, se interrumpe el proceso
        if r.status_code != 200:
            logging.warning(f"[{category}] Fin o error {r.status_code} en {url}")
            break

        soup = BeautifulSoup(r.text, "html.parser")

        # Buscar todos los enlaces con patrón "/rf-" (identificador único de oferta)
        anchors = soup.find_all("a", href=re.compile(r"/rf-", re.I))

        # Eliminar duplicados utilizando un conjunto
        unique_links = list({urljoin(BASE, a["href"]) for a in anchors})

        # Si no se detectan resultados, se asume el fin de la categoría
        if not unique_links:
            logging.info(f"[{category}] Sin resultados en página {page}. Fin.")
            break

        new_links = []
        for link in unique_links:
            # Se busca la fecha de publicación en el bloque HTML donde se encuentra el enlace
            block = soup.find("a", href=re.compile(re.escape(link.replace(BASE, ""))))
            fecha = "N/D"
            if block:
                parent = block.find_parent("div")
                if parent:
                    match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", parent.get_text(" ", strip=True))
                    if match:
                        fecha = match.group(1)

            # Conversión al formato ISO (YYYY-MM-DD)
            try:
                fecha = datetime.strptime(fecha, "%d/%m/%Y").strftime("%Y-%m-%d")
            except Exception:
                pass

            new_links.append((link, fecha))

        # Condiciones de parada para evitar repeticiones o páginas vacías
        current_set = {l for l, _ in new_links}
        if not new_links:
            logging.info(f"[{category}] Página {page} vacía. Fin.")
            break
        if current_set == seen_last:
            logging.info(f"[{category}] Repetición detectada en página {page}. Fin.")
            break

        results.extend(new_links)
        seen_last = current_set
        logging.info(f"[{category}] Página {page}: {len(new_links)} ofertas detectadas")

        # Pasar a la siguiente página con retardo para evitar sobrecarga
        page += 1
        time.sleep(0.6)

        # Si las últimas páginas muestran pocos resultados, se detiene la iteración
        if len(current_set) < 10:
            empty_streak += 1
            if empty_streak >= 2:
                logging.info(f"[{category}] Fin por falta de crecimiento.")
                break
        else:
            empty_streak = 0

    logging.info(f"{len(results)} ofertas recopiladas para {category}")
    return results

# =========================================================
# FUNCIÓN 2: extraer detalles de una oferta individual
# =========================================================
def extract_offer_details(link, category):
    """
    Extrae los campos más relevantes de cada oferta: título, empresa,
    ubicación, tipo de contrato, experiencia, habilidades y descripción.
    Incluye detección adicional de fecha de publicación en la página individual.
    """
    try:
        d = session.get(link, timeout=15)
        if d.status_code != 200:
            return None

        detail = BeautifulSoup(d.text, "html.parser")

        # Obtiene el título principal de la oferta
        title = detail.find("h1").get_text(strip=True) if detail.find("h1") else "N/D"

        # Extrae la descripción general de la oferta
        desc_tag = detail.find("div", class_=re.compile("description", re.I))
        desc = desc_tag.get_text(" ", strip=True) if desc_tag else detail.get_text(" ", strip=True)[:300]

        # Detección de fecha en el contenido textual
        date_tag = detail.find(text=re.compile(r"Publicad", re.I))
        fecha = "N/D"
        if date_tag:
            match_date = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", date_tag)
            if match_date:
                fecha = match_date.group(1)
                try:
                    fecha = datetime.strptime(fecha, "%d/%m/%Y").strftime("%Y-%m-%d")
                except Exception:
                    pass

        # Extracción del nombre de la empresa mediante expresiones regulares
        company = "N/D"
        match = re.search(r"en\s+([a-zA-ZÁÉÍÓÚÜÑ0-9/&.,\s]+?)\s*-\s*tecnoempleo", desc, re.IGNORECASE)
        if match:
            company = match.group(1).strip()
            # Limpieza de palabras no deseadas (ubicaciones o modos de trabajo)
            bad_words = ["remoto", "híbrido", "madrid", "barcelona", "sevilla", "valencia",
                         "málaga", "bilbao", "teletrabajo", "spain", "hibrido"]
            for w in bad_words:
                company = re.sub(rf"\b{w}\b", "", company, flags=re.IGNORECASE)
            company = company.strip(" -.,").title()
        if not company or len(company) < 2:
            company = "N/D"

        # Extrae todo el texto visible para buscar patrones adicionales
        text_all = detail.get_text(" ", strip=True).lower()

        # Inicialización de los campos
        contrato = "N/D"
        salario = "N/D"
        experiencia = "N/D"

        # Búsqueda de tipo de contrato
        m_contrato = re.search(r"(temporal|indefinido|prácticas|freelance|autónomo|fijo|híbrido|remoto|teletrabajo)", text_all)
        if m_contrato:
            contrato = m_contrato.group(1).capitalize()

        # Búsqueda de rangos salariales
        m_salario = re.search(r"(\d{1,3}(?:[.,]\d{3})*(?: ?€| euros|k))", text_all)
        if m_salario:
            salario = m_salario.group(1).replace(" ", "")

        # Búsqueda de experiencia requerida
        m_exp = re.search(r"(\d{1,2}) ?años? de experiencia", text_all)
        if m_exp:
            experiencia = f"{m_exp.group(1)} años"
        elif "sin experiencia" in text_all:
            experiencia = "Sin experiencia"

        # Detección de ubicación basada en palabras clave
        location = next((c.capitalize() for c in [
            "madrid", "barcelona", "sevilla", "valencia", "bilbao",
            "remoto", "teletrabajo", "híbrido", "malaga"
        ] if c in text_all), "N/D")

        # Extracción de habilidades técnicas relevantes
        skills = [kw for kw in [
            "python", "sql", "aws", "azure", "gcp", "spark", "docker",
            "tensorflow", "pandas", "r", "power bi", "ml", "ai", "java",
            "linux", "git", "big data", "scikit", "airflow", "kubernetes"
        ] if kw in text_all]
        skills = ", ".join(sorted(set(skills))) if skills else "N/D"

        # Devuelve los datos estructurados como diccionario
        return {
            "Categoría": category,
            "Título": title,
            "Empresa": company,
            "Ubicación": location,
            "Contrato": contrato,
            "Salario": salario,
            "Experiencia": experiencia,
            "Fecha publicación": fecha,
            "Habilidades": skills,
            "Descripción": desc[:250],
            "Enlace": link
        }

    # En caso de error en la conexión o parsing, se omite la oferta
    except Exception:
        return None

# =========================================================
# FUNCIÓN 3: guardar los datos en un archivo CSV
# =========================================================
def save_to_csv(rows, filename="tecnoempleo_final_avanzado.csv"):
    """Guarda los resultados en un archivo CSV codificado en UTF-8."""
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Categoría", "Título", "Empresa", "Ubicación", "Contrato",
            "Salario", "Experiencia", "Fecha publicación",
            "Habilidades", "Descripción", "Enlace"
        ])
        writer.writeheader()
        writer.writerows(rows)
    logging.info(f"{len(rows)} ofertas guardadas en {filename}")

# =========================================================
# EJECUCIÓN PRINCIPAL DEL PROCESO
# =========================================================
all_rows = []  # Lista global con todas las ofertas recolectadas

for category in CATEGORIES:
    logging.info(f"\nCategoría: {category}")

    # Recolección de enlaces por categoría
    offers = get_offer_links(category)
    logging.info(f"  {len(offers)} ofertas encontradas en total para {category}")

    # Extracción detallada de cada oferta individual
    for link, fecha in offers:
        data = extract_offer_details(link, category)
        if data:
            # Si no se detectó fecha en la página individual, usar la del listado
            if data["Fecha publicación"] == "N/D" and fecha != "N/D":
                data["Fecha publicación"] = fecha
            all_rows.append(data)
        time.sleep(0.5)  # Espera para evitar sobrecarga al servidor

# Guardado final del dataset resultante
save_to_csv(all_rows)
logging.info("Scraping completado con éxito")

