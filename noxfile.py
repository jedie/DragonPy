import nox
from nox.sessions import Session


PYTHON_VERSIONS = ['3.13', '3.12', '3.11']


@nox.session(python=PYTHON_VERSIONS)
def tests(session: Session):
    session.install('uv')
    session.run(
        'uv',
        'sync',
        '--all-extras',
        '--python',
        session.python,
        env={'UV_PROJECT_ENVIRONMENT': session.virtualenv.location},
    )
    session.run('python', '-m', 'coverage', 'run', '--context', f'py{session.python}')


@nox.session
def lint(session: Session):
    session.install('flake8', 'flake8-bugbear')
    session.run('flake8', 'manage_django_project')
