#!/usr/bin/python
import os
from appdirs import user_data_dir
from appdirs import user_config_dir
from appdirs import site_config_dir

def check_directory_existance(dirpath):
    if not os.path.exists(dirpath):
            os.makedirs(dirpath)

def create_if_not_exist(filepath):
    if not os.path.exists(filepath):
        open(filepath, 'a').close()

def _get_user_dir(path):
    return '%s/%s' % (USER_CONFIG_DIR, path)

def _get_global_dir(path):
    return '%s/%s' % (GLOBAL_CONFIG_DIR, path)

def _get_path(path):
    fullpath = _get_user_dir(path)
    if os.path.exists(fullpath):
        return fullpath
    fullpath = _get_global_dir(path)
    if os.path.exists(fullpath):
        return fullpath
    raise AttributeError

def get_database_file():
    db_file = _get_user_dir('database.sqlite')
    create_if_not_exist(db_file)
    return db_file

def get_config_file():
    return _get_path('firmapiu.conf')

def get_library_file():
    return _get_path('libraries.xml')

def get_certificate_dir():
    return _get_path('certs')

os.environ['XDG_CONFIG_DIRS'] = '/etc'
APPLICATION_NAME = 'firmapiu'
GLOBAL_CONFIG_DIR = site_config_dir(APPLICATION_NAME)
USER_CONFIG_DIR = user_config_dir(APPLICATION_NAME)

CONFIG_FILE = get_config_file()
DATABASE_FILE = get_database_file()
LIBRARY_FILE = get_library_file()
CERTIFICATE_DIR = get_certificate_dir()
check_directory_existance(CERTIFICATE_DIR)