import requests

# Defina sua chave da API RAWG
api_key = ''

# Defina o endpoint para plataformas
url = f'https://api.rawg.io/api/platforms?key={api_key}'

try:
    # Fazer a requisição GET para a API
    response = requests.get(url)
    response.raise_for_status()  # Checa se houve algum erro

    # Parse o conteúdo JSON retornado
    platforms_data = response.json()

    # Pega a lista de plataformas
    platforms = platforms_data['results']

    # Exibe as plataformas
    for platform in platforms:
        print(f"ID: {platform['id']} - Nome: {platform['name']}")

except requests.exceptions.HTTPError as err:
    print(f"Erro HTTP: {err}")
except Exception as err:
    print(f"Outro erro ocorreu: {err}")
