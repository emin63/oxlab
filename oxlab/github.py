"""Tools for getting data from GitHub.
"""

import typing
import sys
import logging
import os
import subprocess


def prep_ssh_files(ssh_deploy_key: str, ssh_deploy_key_file: str,
                   ssh_dir: str = '~/.ssh'):
    """Prepare ssh files.

    :param ssh_deploy_key:   String reprsesenting SSH deploy key from
                             GitHub.

    :param ssh_deploy_key_file:  Path to where to store ssh_deploy_key.

    :param ssh_dir:   SSH directory (so we can fix known_hosts).

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:  Create various files needed for ssh to interact with
              GitHub.

    """
    ssh_deploy_key_file = os.path.expanduser(ssh_deploy_key_file)
    ssh_dir = os.path.expanduser(ssh_dir)
    if not os.path.exists(ssh_dir):
        print(f'Creating new directory in {ssh_dir}')
        os.makedirs(ssh_dir)

    # Create the key file if necessary
    if not os.path.exists(ssh_deploy_key_file):
        print(f'Creating SSH deploy key in {ssh_deploy_key_file}')
        with open(ssh_deploy_key_file, 'w', encoding='utf8') as fdesc:
            fdesc.write(ssh_deploy_key)
        os.chmod(ssh_deploy_key_file, 0o600)

    known_hosts_file = os.path.expanduser('~/.ssh/known_hosts')
    if os.path.exists(known_hosts_file):
        logging.warning('Using existing known hosts file %s',
                        known_hosts_file)
    else:
        logging.warning('Creating new known hosts file %s',
                        known_hosts_file)
        process = subprocess.run('ssh-keyscan github.com', check=False,
                                 shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        if process.returncode != 0:
            raise ValueError('Error running process: {process}')
        with open(known_hosts_file, 'a', encoding='utf8') as fdesc:
            fdesc.write(process.stdout.decode('utf8'))


def get_repo(owner: str, repo: str, ssh_deploy_key_file: typing.Union[
        bool, str] = True, working_dir: str = '~/code'):
    """Get the repo from GitHub (either clone or pull).

    :param owner:  String representing owner of repo (e.g., 'emin63').

    :param repo:   String representing repo name (e.g., 'oxlab').

    :param ssh_deploy_key_file:  Either `True` indicating to automatically
                                 generate deploy key file name or string
                                 path to deploy key file.

    :param working_dir='~/code':  Working directory to inside which the
                                  repo will live once we clone/pull it.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:  Get the repo from GitHub (using clone if we don't have it
              or pull if we do).

    """
    if ssh_deploy_key_file is True:
        ssh_deploy_key_file = f'~/.ssh/ssh_{owner}_{repo}_deploy_key'
    ssh_deploy_key_file = os.path.expanduser(ssh_deploy_key_file)
    assert os.path.exists(ssh_deploy_key_file), (
        'Could not find {ssh_deploy_key_file=}; did you `prep_ssh_files`?')
    working_dir = os.path.expanduser(working_dir)
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    repo_dir = os.path.join(os.path.expanduser(working_dir), repo)
    my_env = {'GIT_SSH_COMMAND': f'ssh  -i {ssh_deploy_key_file}'}
    if os.path.exists(repo_dir):
        process = subprocess.run(
            'git pull'.split(' '), env=my_env, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd=repo_dir, check=False)
    else:
        process = subprocess.run(
            f'git clone git@github.com:{owner}/{repo}'.split(' '),
            env=my_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, cwd=working_dir)

    if process.returncode != 0:
        raise ValueError(f'Error running process: {process}')
    if repo_dir not in sys.path:
        sys.path.insert(0, repo_dir)


def add_github_repo(owner: str, repo: str, ssh_deploy_key: str,
                    ssh_dir: str = '~/.ssh', working_dir: str = '~/code',
                    ssh_deploy_key_file: typing.Union[bool, str] = True,
                    only_colab=True):
    """Add a GitHub repo into our python environment.

    :param owner:  String representing owner of repo (e.g., 'emin63').

    :param repo:   String representing repo name (e.g., 'oxlab').

    :param ssh_deploy_key:  String deploy key for project on GitHub.

    :param working_dir='~/code':  Working directory to inside which the
                                  repo will live once we clone/pull it.

    :param ssh_deploy_key_file=True:  Either `True` indicating to
                                      auto-generate deploy key file name
                                      or string path to deploy key file.

    :param only_colab=True:  If True, and not running in Google Colab, then
                             do nothing (except pring an info log message).

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:  Add the latest version of the desired GitHub repo to our
              environment.
    """
    if only_colab:
        if 'google.colab' not in sys.modules:
            logging.info(
                'Skip add_github_repo since only_colab=True and not in colab')
            return
    ssh_dir = os.path.expanduser(ssh_dir)
    prep_ssh_files(ssh_deploy_key, ssh_deploy_key_file, ssh_dir)
    get_repo(owner, repo, ssh_deploy_key_file, working_dir)
