# Práctica 1 — Tipología y Ciclo de Vida de los Datos  
**Proyecto de Web Scraping: Ofertas de Empleo en el Sector Tecnológico (Tecnoempleo, 2025)**  

Realización de la Práctica 1 de la asignatura **Tipología y Ciclo de Vida de los Datos** del **Máster Universitario en Ciencia de Datos (UOC)**.  

---

## Integrantes del grupo
- **Rocío Argüelles Coro**  
- **Javier Maciá Davó**

---

## Descripción de los archivos del repositorio

| Archivo | Descripción |
|----------|-------------|
| `source/main_scraper.py` | Script principal de scraping. Recolecta ofertas de empleo desde *Tecnoempleo.com* en varias categorías tecnológicas, extrayendo datos clave como título, empresa, ubicación, contrato, experiencia, habilidades y fecha de publicación. |
| `dataset/tecnoempleo_ofertas_nov.csv` | Dataset final generado con los resultados del scraping. Contiene las ofertas estructuradas y listas para análisis posteriores (Práctica 2). |
| `requirements.txt` | Lista de dependencias necesarias para ejecutar correctamente el script. |
| `README.md` | Documento informativo del proyecto, con instrucciones de uso y referencias. |

---

## Cómo usar el código del repositorio

### Requisitos previos
Asegúrate de tener instalado **Python 3.9 o superior**.

---

### Instalación de dependencias

Instala las librerías necesarias ejecutando:

```bash
pip install -r requirements.txt

### Ejecución del script

Ejecuta el script principal desde la carpeta raíz del proyecto:

```bash
python source/main_scraper.py

Esto descargará los datos de ofertas de empleo del portal Tecnoempleo.com, recorriendo categorías como Big Data, Data Science, Inteligencia Artificial o Machine Learning, y generará el archivo CSV final dentro de la carpeta dataset/.

## DOI del dataset

El dataset resultante ha sido publicado en Zenodo bajo licencia abierta: https://doi.org/10.5281/zenodo.17566247


## Licencia

Este proyecto y los datos generados se distribuyen bajo licencia Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).
Esto permite compartir y adaptar el contenido siempre que se reconozca la autoría original y se mantenga la misma licencia.
