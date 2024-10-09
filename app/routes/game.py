from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Game, UserGameAssociation

bp = Blueprint('game', __name__)

@bp.route('/')
@login_required
def index():
    desired_games = UserGameAssociation.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', games=desired_games)

@bp.route('/add_game', methods=['GET', 'POST'])
@login_required
def add_game():
    if request.method == 'POST':
        name = request.form['name']
        platform = request.form['platform']
        release_year = request.form['release_year']
        developer = request.form['developer']
        style = request.form['style']
        publisher = request.form['publisher']  # Novo campo publisher
        description = request.form['description']

        new_game = Game(
            name=name,
            platform=platform,
            release_year=release_year,
            developer=developer,
            style=style,
            publisher=publisher,  # Salvar publisher
            description=description
        )

        db.session.add(new_game)
        db.session.commit()
        return redirect(url_for('game.index'))  # Redirecionar para a página de index de jogos

    return render_template('add_game.html')

@bp.route('/list_games')
@login_required
def list_games():
    all_games = Game.query.all()
    return render_template('list_games.html', games=all_games)

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
