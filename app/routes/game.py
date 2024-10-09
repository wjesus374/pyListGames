from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from app import db
from app.models import *
import os
import pandas as pd

bp = Blueprint('game', __name__)

@bp.route('/')
@login_required
def index():
    desired_games = UserGameAssociation.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', games=desired_games)

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

@bp.route('/add_game_old', methods=['GET', 'POST'])
@login_required
def add_game_old():
    if not current_user.is_admin:  # Verifica se o usuário é administrador
        flash('Você não tem permissão para adicionar jogos.', 'danger')
        return redirect(url_for('game.index'))  # Redireciona para a página de jogos

    if request.method == 'POST':
        name = request.form['name']
        platform = request.form['platform']
        release_year = request.form['release_year']
        developer = request.form['developer']
        style = request.form['style']
        publisher = request.form['publisher']
        description = request.form['description']

        new_game = Game(
            name=name,
            platform=platform,
            release_year=release_year,
            developer=developer,
            style=style,
            publisher=publisher,
            description=description
        )

        db.session.add(new_game)
        db.session.commit()
        flash('Jogo adicionado com sucesso!', 'success')
        return redirect(url_for('game.index'))

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

@bp.route('/list_and_add_games_old')
@login_required
def list_and_add_games_old():
    all_games = Game.query.all()
    return render_template('list_and_add_games_old.html', games=all_games)

@bp.route('/list_and_add_games')
@login_required
def list_and_add_games():
    page = request.args.get('page', 1, type=int)  # Obtém o número da página da query string, padrão é 1
    per_page = 3  # Número de jogos por página
    games = Game.query.paginate(page=page, per_page=per_page)  # Pagina os jogos

    return render_template('list_and_add_games.html', games=games)

@bp.route('/search_and_add_games')
@login_required
def search_and_add_games():
    all_games = Game.query.all()
    return render_template('search_and_add_games.html', games=all_games)

@bp.route('/add_to_wishlist/<int:game_id>', methods=['GET', 'POST'])
@login_required
def add_to_wishlist(game_id):
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

    return render_template('add_to_wishlist.html', game=game)

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
