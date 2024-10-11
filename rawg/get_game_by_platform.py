import requests
import json
import os
import time
import pandas as pd

# Defina sua chave da API RAWG
api_key = ''

# Função para carregar dados existentes do arquivo JSON (se existir)
def load_json(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as json_file:
            try:
                return json.load(json_file)
            except json.JSONDecodeError:
                return []  # Retorna uma lista vazia se o arquivo estiver corrompido ou vazio
    return []

# Função para salvar o JSON de volta no arquivo
def save_json(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


# Função para coletar jogos de uma plataforma
def get_games_by_platform(platform_id, api_key, page_size=100, page=1):
    url = f'https://api.rawg.io/api/games?platforms={platform_id}&key={api_key}&page_size={page_size}&page={page}'

    # Salvar todos os resultados em JSON
    json_requests = f'json/all_requests_data_{platform_id}.json'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Checa se houve algum erro
        
        games_data = response.json()
        games = games_data['results']  # Lista de jogos

        #Bloco para ler e gravar novas informações do JSON
        data = load_json(json_requests)
        data.append(games)
        save_json(data, json_requests)

        x = 1
        while True:
            print(f'Página: {x}')
            
            next_url = response.json().get('next')
            print(next_url)
            response = requests.get(next_url)
            response.raise_for_status()  # Checa se houve algum erro

            games_data = response.json()
            games = games_data['results']  # Lista de jogos

            #Bloco para ler e gravar novas informações do JSON
            data = load_json(json_requests)
            data.append(games)
            save_json(data, json_requests)

            x += 1
            
        #return games
    
    except requests.exceptions.HTTPError as err:
        print(f"Erro HTTP: {err}")
        time.sleep(5)
    except Exception as err:
        print(f"Outro erro ocorreu: {err}")
        time.sleep(5)

platform_list = [187, 18, 7, 1, 186, 14, 80, 16, 15, 27, 8, 9, 13]
for platform_id in platform_list:
    # Obtenha os jogos da plataforma
    games = get_games_by_platform(platform_id, api_key)
