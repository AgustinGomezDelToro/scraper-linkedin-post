from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re
import csv


# Configuración inicial
chrome_options = webdriver.ChromeOptions()
username = ""  # Replace with your email
password = ""  # Replace with your password
#page = 'https://www.linkedin.com/in/agustingomezdeltoro/recent-activity/all/'
#page = 'https://www.linkedin.com/in/aminekhalladin/recent-activity/all/'

# Inicialización de WebDriver
browser = webdriver.Chrome(options=chrome_options)

# Inicio de sesión en LinkedIn
browser.get('https://www.linkedin.com/login')
browser.find_element(By.ID, "username").send_keys(username)
browser.find_element(By.ID, "password").send_keys(password)
browser.find_element(By.ID, "password").submit()
WebDriverWait(browser, 10000).until(EC.presence_of_element_located((By.ID, "global-nav-typeahead")))

# Navegación a la página de publicaciones
#post_page = page + '/posts'
post_page = page
browser.get(post_page)
WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.feed-shared-update-v2")))

# Extracción de datos
posts_data = []
post_containers = browser.find_elements(By.CSS_SELECTOR, "div.feed-shared-update-v2")


for container in post_containers:
    # Extracción del texto de la publicación
    post_texts = container.find_elements(By.CSS_SELECTOR, "span.break-words")
    post_text = " ".join([elem.text for elem in post_texts if elem.text]) if post_texts else "Texto no encontrado"

    # Extracción de likes
    likes_elements = container.find_elements(By.CSS_SELECTOR,
                                             "span.social-details-social-counts__reactions-count, span.social-details-social-counts__social-proof-text")
    num_likes = 0
    for element in likes_elements:
        # Intenta extraer directamente el número
        num_likes_text = element.text.replace('\xa0', '').replace(' ', '')
        likes_match = re.findall(r'\d+', num_likes_text)
        if likes_match:
            # Si encuentra números, suma cada número encontrado (en caso de números separados por espacio)
            num_likes += sum([int(match) for match in likes_match])
            break  # Sale del ciclo si encuentra un match

    # Extracción de comentarios
    comments_element = container.find_elements(By.CSS_SELECTOR,
                                               ".social-details-social-counts__comments .social-details-social-counts__count-value")
    if comments_element:
        comments_text = comments_element[0].text.replace('\xa0', '').replace(' ', '')
        comments_numbers = re.findall(r'\d+', comments_text)  # Encuentra todos los grupos de dígitos
        num_comments = ''.join(comments_numbers)  # Concatena todos los grupos de dígitos para formar el número completo
        num_comments = int(num_comments) if num_comments else 0  # Convierte a entero
    else:
        num_comments = 0

    # Agregando datos al diccionario
    posts_data.append({
        "Post Text": post_text,
        "Likes": num_likes,
        "Comments": num_comments
    })

# Cierre del navegador
browser.quit()

# Creación del DataFrame y exportación a CSV
df = pd.DataFrame(posts_data)
csv_file = "profil_posts.csv"
df.to_csv(csv_file, index=False, quoting=csv.QUOTE_NONNUMERIC)  # Asegúrate de citar los no numéricos
print(f"Datos exportados a {csv_file}")
print(df)

