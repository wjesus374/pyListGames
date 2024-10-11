from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import User
from app import db
from flask_login import login_required, current_user

bp = Blueprint('admin', __name__)

@bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not current_user.is_admin:  # Certifique-se de que apenas administradores possam acessar
        flash('Você não tem permissão para acessar essa página.', 'danger')
        return redirect(url_for('game.index'))

    users = User.query.all()  # Obtém todos os usuários

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        if user:
            user.is_admin = not user.is_admin  # Alterna o status de administrador
            db.session.commit()
            flash('O status do usuário foi atualizado com sucesso.', 'success')

    return render_template('admin_dashboard.html', users=users)
