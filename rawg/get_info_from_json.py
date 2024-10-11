import json
import os
import pandas as pd

def load_json(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as json_file:
            try:
                return json.load(json_file)
            except json.JSONDecodeError:
                return []  # Retorna uma lista vazia se o arquivo estiver corrompido ou vazio
    return []


def transform_platform_list(data_list):
    transformed_data = []
    
    # Itera sobre cada dicionário na lista
    for item in data_list:
        # Para cada plataforma na lista 'platform_list', cria uma nova entrada no dicionário
        for platform in item['platform_list']:
            new_entry = {
                'platform': platform,
                'slug': item['slug'],
                'name': item['name'],
                'released': item['released'],
                'background_image': item['background_image'],
                'genre': item['genre']
            }
            transformed_data.append(new_entry)
    
    return transformed_data

platform_list = [187, 18, 7, 1, 186, 14, 80, 16, 15, 27, 8, 9, 13]
for platform_id in platform_list:
    json_requests = f'json/all_requests_data_{platform_id}.json'
    games = load_json(json_requests)

    games_data = []
    # Exibe os jogos coletados
    for info in games:
        for game in info:
            data = {}
            data['platform_list'] = []
            data['genres_list'] = []

            for key, value in game.items():
                #platforms [{'platform': {'id': 4, 'name': 'PC', 'slug': 'pc'}},
                if key == 'platforms':
                    for platform_name in value:
                        platform = platform_name['platform'].get('name')
                        data['platform_list'].append(platform)
                    
                    platform = ', '.join(data['platform_list'])
                    data['platform'] = platform

                #genres ([{'id': 4, 'name': 'Action', 'slug': 'action'}])
                if key == 'genres':
                    for genres in value:
                        genre = genres.get('name')
                        data['genres_list'].append(genre)

                    genre = ', '.join(data['genres_list'])
                    data['genre'] = genre

                if key == 'background_image':
                    data['background_image'] = value
                #name (Grand Theft Auto V)
                if key == 'name':
                    data['name'] = value
                #slug (grand-theft-auto-v)
                if key == 'slug':
                    data['slug'] = value
                #released (2013-09-17)
                if key == 'released':
                    data['released'] = value

            games_data.append(data)

    # Aplicar a transformação
    result = transform_platform_list(games_data)

    df = pd.DataFrame(result)
    df.to_csv(f'csv/lista_de_jogos_{platform_id}.csv', sep=';', encoding='UTF-8', index=False)
        