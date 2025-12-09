#
# https://github.com/wntrblm/nox/
# Documentation: https://nox.thea.codes/
#
import nox
from nox.sessions import Session


PYTHON_VERSIONS = ('3.14', '3.13', '3.12', '3.11')


@nox.session(
    python=PYTHON_VERSIONS,
    venv_backend='uv',
    download_python='auto',
)
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
