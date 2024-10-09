#Para criar e ativar o ambiente virtual no Windows

python -m venv .venv

#PowerShell

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.venv\Scripts\Activate.ps1

Estrutura

project_root/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── game.py
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── add_game.html
│       ├── add_to_wishlist.html
│       ├── edit_wishlist.html
│       ├── list_games.html
│       └── login.html
│   └── static/
│       ├── css/
│       │   └── styles.css
│
├── venv/  (diretório do ambiente virtual)
├── run.py
├── config.py
└── requirements.txt
