# Practica-1-Tipologia-y-ciclo-de-vida-datos
Realización de la práctica 1 de la asignatura Tipología y Ciclo de Vida de los Datos del Máster de Ciencia de Datos de la UOC.

# Proyecto de Web Scraping: Ofertas de Empleo en el Sector Tecnológico (Tecnoempleo, 2025)

## 👩‍💻 Integrantes del grupo
- **Rocío Argüelles Coro**, **Javier Maciá Davó**
- **Máster Universitario en Ciencia de Datos (UOC)**  
- Práctica 1 — M2.851: ¿Cómo podemos capturar los datos de la web?

---

## 📂 Descripción de los archivos del repositorio

| Archivo | Descripción |
|----------|--------------|
| `main_scraper.py` | Script principal de scraping. Recolecta ofertas de empleo desde *Tecnoempleo.com* en varias categorías tecnológicas, extrayendo datos clave como título, empresa, ubicación, contrato, experiencia, habilidades y fecha de publicación. |
| `tecnoempleo_ofertas_nov.csv` | Dataset final generado con los resultados del scraping. Contiene las ofertas estructuradas y listas para análisis posteriores (Práctica 2). |
| `requirements.txt` | Lista de dependencias necesarias para ejecutar correctamente el script. |
| `README.md` | Documento informativo del proyecto, con instrucciones de uso y referencias. |

---

## 🚀 Cómo usar el código del repositorio

### 🔧 Requisitos previos
Antes de ejecutar el script, asegúrate de tener **Python 3.9+** instalado.  
Se recomienda crear un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate     # En Linux o macOS
venv\Scripts\activate        # En Windows
