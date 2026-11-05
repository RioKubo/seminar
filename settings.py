from os import environ

SESSION_CONFIGS = [
    dict(
        name='seminar',
        display_name='AIの助言と協力行動の実験',
        app_sequence=['seminar_game'],
        num_demo_participants=2,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc="",
)

PARTICIPANT_FIELDS = ['full_name']
SESSION_FIELDS = []

LANGUAGE_CODE = 'ja'
REAL_WORLD_CURRENCY_CODE = 'JPY'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = environ.get('OTREE_SECRET_KEY')

INSTALLED_APPS = ['otree']
