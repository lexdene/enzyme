# developing

## install dev requirements

    pip install -r pip-reqs/dev.txt

## run test and code check before pushing

    nosetests
    flake8
    isort --check-only --recursive .
