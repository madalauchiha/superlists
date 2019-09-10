"""
运行该脚本的环境须满足以下条件：
1. 已经安装python3, 同时通过pip3安装了virtualenv;
2. 已经安装了git, 可以更新github仓库;
"""

from fabric.api import env, run, local
from fabric.contrib import files

REPO_URL = 'https://github.com/madalauchiha/superlists.git'
site_name = 'superlists'


def deploy():
    site_folder = '/home/%s/sites/%s' % (env.user, site_name)
    source_folder = site_folder + '/source'
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)


def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('database', 'static', 'source', 'virtualenv'):
        run('mkdir -p %s/%s' % (site_folder, subfolder))


def _get_latest_source(source_folder):
    if files.exists(source_folder + '/.git'):
        run('cd %s && git fetch' % source_folder)
    else:
        run('git clone %s %s' % (REPO_URL, source_folder))

    current_commit = local('git log -n 1 format=%H', capture=True)
    run('cd %s && git reset --hard %s' % (source_folder, current_commit))


def _update_settings(source_folder, host):
    settings_path = source_folder + '/superlists/settings.py'
    files.sed(settings_path,
              'ALLOWED_HOSTS = .+$',
              'ALLOWED_HOSTS = ["%s"]' % host)


def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '../virtualenv'
    if not files.exists(virtualenv_folder + '/bin/pip'):
        run('virtualenv --python=python3 %s' % virtualenv_folder)

    run('%s/bin/pip3 install -r %s/requirements.txt', (virtualenv_folder, source_folder))


def _update_static_files(source_folder):
    run('cd %s && ../virtualenv/bin/python3 manage.py collectstatic --noinput' % source_folder)


def _update_database(source_folder):
    run('cd %s && ../virtualenv/bin/python3 manage.py migrate --noinput' % source_folder)
