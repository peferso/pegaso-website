#!/bin/bash

cd ${PEGASO_WEBST_DIR}

source ../bin/activate

python manage.py runserver

cd ${OLDPWD}
