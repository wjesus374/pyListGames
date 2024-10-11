from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from app import db
from app.models import *
import os
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import joinedload

bp = Blueprint('game', __name__)

@bp.route('/')
@login_required
def index():
    # Filtros
    game_name = request.args.get('name', '', type=str)
    selected_platforms = request.args.getlist('platform')
    developer = request.args.get('developer', '', type=str)
    release_year = request.args.get('release_year', '', type=int)
    genre = request.args.get('genre', '', type=str)

    favorites = UserGameAssociation.query.filter_by(user_id=current_user.id) # Obtém os jogos favoritos do usuário
    # Cria uma lista para armazenar os dados dos jogos favoritos
    data = []

    for favorite in favorites:
        query = Game.query
        query = query.filter_by(id = favorite.game_id)

        if game_name:
            query = query.filter(Game.name.ilike(f'%{game_name}%'))
        if selected_platforms:
            query = query.filter(Game.platform.in_(selected_platforms))
        if developer:
            query = query.filter(Game.developer.ilike(f'%{developer}%'))
        if release_year:
            query = query.filter_by(release_year=release_year)
        if genre:
            query = query.filter(Game.genre.ilike(f'%{genre}%'))

        for game in query:
            data.append({
                    'id': game.id,
                    'name': game.name,
                    'platform': game.platform,
                    'release_year': game.release_year,
                    'developer': game.developer,
                    'genre': game.genre,
                    'description': game.description,
                    'rating': favorite.rating,
                    'media': favorite.media,
                })
        
        #for game in query:
        #    print(f"ID: {game.id}, Nome: {game.name}, Ano de Lançamento: {game.release_year}, Publisher: {game.publisher}")

    # Obter plataformas únicas para o filtro
    platforms = Game.query.with_entities(Game.platform).distinct().all()
    platforms = [platform[0] for platform in platforms]
    platforms = sorted(platforms)

    #for game in query:
    #    print(f"ID: {game.id}, Nome: {game.name}, Ano de Lançamento: {game.release_year}, Publisher: {game.publisher}")

    return render_template('index.html', games=data, filters={
        'name': game_name,
        'platform': selected_platforms,
        'developer': developer,
        'release_year': release_year,
        'genre': genre
    }, platforms=platforms)
    
    #desired_games = UserGameAssociation.query.filter_by(user_id=current_user.id).all()
    #return render_template('index.html', games=desired_games)

@bp.route('/search_games', methods=['GET'])
def search_games():
    query = request.args.get('q', '')
    games = Game.query.filter(Game.name.ilike(f'%{query}%')).all()
    return jsonify([{'id': game.id, 'name': game.name, 'platform': game.platform } for game in games])

@bp.route('/add_game', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        name = request.form['name']
        platform = request.form['platform']
        release_year = request.form['release_year']
        developer = request.form['developer']
        genre = request.form['genre']
        publisher = request.form['publisher']
        description = request.form['description']

        # Salvando a imagem de capa
        cover_image = request.files['cover_image']
        #cover_image_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_image.filename)
        cover_image_path = os.path.join('app\\static\\uploads', cover_image.filename)
        cover_image.save(cover_image_path)

        # Criar o jogo
        new_game = Game(
            name=name,
            platform=platform,
            release_year=release_year,
            developer=developer,
            genre=genre,
            publisher=publisher,
            description=description,
            cover_image=cover_image.filename  # Armazenar o nome da imagem
        )

        db.session.add(new_game)
        db.session.commit()

        # Salvar imagens adicionais (se houver)
        additional_images = request.files.getlist('additional_images')
        for img in additional_images:
            if img:
                #image_path = os.path.join(app.config['UPLOAD_FOLDER'], img.filename)
                image_path = os.path.join('app\\static\\uploads', img.filename)
                img.save(image_path)

                # Criar e associar a imagem adicional ao jogo
                game_image = GameImage(game_id=new_game.id, image_path=img.filename)
                db.session.add(game_image)

        db.session.commit()
        return redirect(url_for('game.index'))  # Redirecionar para a página inicial ou outra

    return render_template('add_game.html')

@bp.route('/download_favorites_csv')
@login_required  # Certifique-se de que o usuário está logado
def download_favorites_csv():
    user_id = current_user.id  # Obtém o ID do usuário atual
    favorites = UserGameAssociation.query.filter_by(user_id=user_id).all()  # Obtém os jogos favoritos do usuário
    # Cria uma lista para armazenar os dados dos jogos favoritos
    data = []

    for favorite in favorites:
        game = Game.query.get(favorite.game_id)
        if game:  # Verifica se o jogo existe
            data.append({
                'Nome': game.name,
                'Plataforma': game.platform,
                'Ano de Lançamento': game.release_year,
                'Desenvolvedora': game.developer,
                'Gênero': game.genre,
                'Descrição': game.description,
                'Nota': favorite.rating
            })

    # Cria um DataFrame do pandas
    df = pd.DataFrame(data)

    # Cria a resposta #utf-8-sig #ISO-8859-1
    output = make_response(df.to_csv(index=False, sep=';', encoding='ISO-8859-1'))
    output.headers["Content-Disposition"] = "attachment; filename=Meus Jogos.csv"
    output.headers["Content-Type"] = "text/csv; charset=ISO-8859-1"

    return output

@bp.route('/list_and_add_games')
@login_required
def list_and_add_games():
    page = request.args.get('page', 1, type=int)  # Obtém o número da página da query string, padrão é 1
    per_page = 30  # Número de jogos por página

    # Filtros
    game_name = request.args.get('name', '', type=str)
    selected_platforms = request.args.getlist('platform')
    developer = request.args.get('developer', '', type=str)
    release_year = request.args.get('release_year', '', type=int)
    genre = request.args.get('genre', '', type=str)

    # Query dinâmica
    query = Game.query
    if game_name:
        query = query.filter(Game.name.ilike(f'%{game_name}%'))
    if selected_platforms:
        query = query.filter(Game.platform.in_(selected_platforms))
    if developer:
        query = query.filter(Game.developer.ilike(f'%{developer}%'))
    if release_year:
        query = query.filter_by(release_year=release_year)
    if genre:
        query = query.filter(Game.genre.ilike(f'%{genre}%'))

    # Paginação da query
    games = query.paginate(page=page, per_page=per_page)

    # Calcular os valores de start_page e end_page
    start_page = max(1, games.page - 2)
    end_page = min(games.pages, games.page + 2)

    # Obter plataformas únicas para o filtro
    platforms = Game.query.with_entities(Game.platform).distinct().all()
    platforms = [platform[0] for platform in platforms]
    platforms = sorted(platforms)

    # Renderizar o template com as variáveis necessárias
    return render_template('list_and_add_games.html', games=games, filters={
        'name': game_name,
        'platform': selected_platforms,
        'developer': developer,
        'release_year': release_year,
        'genre': genre
    }, platforms=platforms, start_page=start_page, end_page=end_page)


@bp.route('/search_and_add_games')
@login_required
def search_and_add_games():
    all_games = Game.query.all()
    return render_template('search_and_add_games.html', games=all_games)

@bp.route('/add_to_wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    selected_game_ids = request.form.getlist('selected_games')

    if not selected_game_ids:
        flash('Nenhum jogo foi selecionado.', 'warning')
        return redirect(url_for('game.list_and_add_games'))

    # Obtenha os jogos selecionados do banco de dados
    selected_games = Game.query.filter(Game.id.in_(selected_game_ids)).all()

    return render_template('add_to_wishlist.html', selected_games=selected_games)

@bp.route('/add_to_wishlist_search', methods=['POST'])
@login_required
def add_to_wishlist_search():
    selected_games_ids = request.form.get('selected_games_ids').split(',')
    selected_games = Game.query.filter(Game.id.in_(selected_games_ids)).all()

    return render_template('add_to_wishlist.html', selected_games=selected_games)

@bp.route('/save_wishlist', methods=['POST'])
@login_required
def save_wishlist():
    game_ids = request.form.getlist('game_ids')

    for game_id in game_ids:
        media = request.form.get(f'media_{game_id}')
        rating = request.form.get(f'rating_{game_id}')

        # Verifica se o jogo já está na lista de desejos do usuário
        wishlist_entry = UserGameAssociation.query.filter_by(user_id=current_user.id, game_id=game_id).first()

        if wishlist_entry:
            wishlist_entry.media = media
            wishlist_entry.rating = rating
        else:
            new_entry = UserGameAssociation(user_id=current_user.id, game_id=game_id, media=media, rating=rating)
            db.session.add(new_entry)

    db.session.commit()
    flash('Jogos adicionados à sua lista de desejos com sucesso!', 'success')

    return redirect(url_for('game.index'))


@bp.route('/add_to_wishlist_one/<int:game_id>', methods=['GET', 'POST'])
@login_required
def add_to_wishlist_one(game_id):
    game = Game.query.get_or_404(game_id)
    if request.method == 'POST':
        media = request.form['media']
        rating = request.form['rating']

        if not UserGameAssociation.query.filter_by(user_id=current_user.id, game_id=game_id).first():
            user_game = UserGameAssociation(
                user_id=current_user.id,
                game_id=game_id,
                media=media,
                rating=int(rating)
            )
            db.session.add(user_game)
            db.session.commit()

        return redirect(url_for('game.index'))

    return render_template('add_to_wishlist_one.html', game=game)

@bp.route('/edit_wishlist/<int:game_id>', methods=['GET', 'POST'])
@login_required
def edit_wishlist(game_id):
    user_game = UserGameAssociation.query.filter_by(user_id=current_user.id, game_id=game_id).first_or_404()

    if request.method == 'POST':
        user_game.media = request.form['media']
        user_game.rating = int(request.form['rating'])

        db.session.commit()
        return redirect(url_for('game.index'))

    return render_template('edit_wishlist.html', user_game=user_game)

@bp.route('/remove_from_wishlist/<int:game_id>', methods=['POST'])
@login_required
def remove_from_wishlist(game_id):
    user_game = UserGameAssociation.query.filter_by(user_id=current_user.id, game_id=game_id).first_or_404()
    db.session.delete(user_game)
    db.session.commit()
    return redirect(url_for('game.index'))

@bp.route('/edit_games')
@login_required
def edit_games():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Número de jogos por página

    # Filtros
    game_name = request.args.get('name', '', type=str)
    selected_platforms = request.args.getlist('platform')
    developer = request.args.get('developer', '', type=str)
    release_year = request.args.get('release_year', '', type=int)
    genre = request.args.get('genre', '', type=str)

    # Query dinâmica
    query = Game.query
    if game_name:
        query = query.filter(Game.name.ilike(f'%{game_name}%'))
    if selected_platforms:
        query = query.filter(Game.platform.in_(selected_platforms))
    if developer:
        query = query.filter(Game.developer.ilike(f'%{developer}%'))
    if release_year:
        query = query.filter_by(release_year=release_year)
    if genre:
        query = query.filter(Game.genre.ilike(f'%{genre}%'))

    games = query.paginate(page=page, per_page=per_page)

    # Calcular os valores de start_page e end_page
    start_page = max(1, games.page - 2)
    end_page = min(games.pages, games.page + 2)

    # Obter plataformas únicas para o filtro
    platforms = Game.query.with_entities(Game.platform).distinct().all()
    platforms = [platform[0] for platform in platforms]
    platforms = sorted(platforms)

    return render_template('edit_games.html', games=games, filters={
        'name': game_name,
        'platform': selected_platforms,
        'developer': developer,
        'release_year': release_year,
        'genre': genre
    }, platforms=platforms, start_page=start_page, end_page=end_page)

    #return render_template('edit_games.html', games=games, start_page=start_page, end_page=end_page)

@bp.route('/save_game', methods=['POST'])
def save_game():
    data = request.get_json()
    game = Game.query.get(data['id'])
    
    if game:
        game.name = data['name']
        game.platform = data['platform']
        #game.release_year = data['release_year']
        game.publisher = data['publisher']
        game.genre = data['genre']

        try:
            release_year = datetime.strptime(data['release_year'], '%d-%m-%Y').date()
            game.release_year = release_year
        except Exception as e:
            print("Erro ao salvar data")
        
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@bp.route('/save_all_games', methods=['POST'])
def save_all_games():
    games_data = request.get_json()

    for game_data in games_data:
        game = Game.query.get(game_data['id'])
        if game:
            game.name = game_data['name']
            game.platform = game_data['platform']
            #game.release_year = game_data['release_year']
            game.publisher = game_data['publisher']
            game.genre = game_data['genre']

            try:
                release_year = datetime.strptime(game_data['release_year'], '%Y-%m-%d').date()
                game.release_year = release_year
            except Exception as e:
                print("Erro ao salvar data")
    
    db.session.commit()
    return jsonify({'success': True})

