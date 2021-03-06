# -*- coding: utf-8 -*-
#
# Copyright © 2014  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License v.3, or (at your option) any later
# version.  This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY expressed or implied, including the
# implied warranties of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.  You
# should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Any Red Hat trademarks that are incorporated in the source
# code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission
# of Red Hat, Inc.
#

"""
Top level of the fedhubsync Flask application.
"""


import logging
import logging.handlers
import os
import sys
import urllib2

import flask

from subprocess import Popen, PIPE


__version__ = '0.1.0'
__api_version__ = '0.1.0'

APP = flask.Flask(__name__)

APP.config.from_object('fedhubsync.default_config')
if 'FEDUPSYNC_CONFIG' in os.environ:  # pragma: no cover
    APP.config.from_envvar('FEDUPSYNC_CONFIG')

if APP.config.get('LOGGER_CONFIG_FILE') \
        and os.path.exists(APP.config['LOGGER_CONFIG_FILE']):
    logging.config.fileConfig(APP.config['LOGGER_CONFIG_FILE'])

# Set up the logger
## Send emails for big exception
mail_handler = logging.handlers.SMTPHandler(
    APP.config.get('SMTP_SERVER', '127.0.0.1'),
    'nobody@fedoraproject.org',
    APP.config.get('MAIL_ADMIN', 'pingou@pingoured.fr'),
    'fedupsync error')
mail_handler.setFormatter(logging.Formatter('''
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Module:             %(module)s
    Function:           %(funcName)s
    Time:               %(asctime)s

    Message:

    %(message)s
'''))
mail_handler.setLevel(logging.ERROR)
APP.logger.addHandler(mail_handler)

# Log to stderr as well
stderr_log = logging.StreamHandler(sys.stderr)
stderr_log.setLevel(logging.INFO)
APP.logger.addHandler(stderr_log)

LOG = APP.logger


## Flask application


def allowed_user(api_key):
    """ Checks if the API key provided is the one set in the configuration
    file.
    """
    return api_key and api_key == APP.config.get('API_KEY', None)

@APP.context_processor
def inject_info():
    """ Inject some information in every page (every template).
    """
    return dict(version=__version__)


@APP.route('/')
def index():
    """ Display the index page. """
    return flask.render_template('index.html')


@APP.route('/update/', methods=['POST'])
def update_repo():
    """ Display the index page. """
    print flask.request.form
    repo = flask.request.form.get('repo', None)
    api_key = flask.request.form.get('key', None)
    httpcode = 200

    output = {}
    if not repo:
        output['output'] = 'notok'
        output['error'] = 'Invalid input submitted'
        httpcode = 400

    elif not allowed_user(api_key):
        output['output'] = 'notok'
        output['error'] = 'You are now allowed to use fedhubsync'
        httpcode = 401

    else:
        try:
            output['message'] = process_call(
                repo, APP.config.get('GIT_FOLDER', None))
            output['output'] = 'ok'
        except FedHubSync, err:
            LOG.exception(err)
            output['output'] = 'notok'
            output['error'] = str(err)
            httpcode = 500

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


## Backend

class FedHubSync(Exception):
    pass


class GitFolderException(FedHubSync):
    pass


class SyncException(FedHubSync):
    pass


def run_command(cmd):
    """ Run a command in the shell

    :arg cmd: a list of the command to run, ie:
        ['ls', '-a', '-l', '/tmp']
    :returns: a tuple containing the output in stdout, the output in stderr
        and the returned code

    """
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
    return proc.communicate() + (proc.returncode, )


def process_call(repo, git_folder):
    """ Update the provided repo present in the specified folder.

    :arg repo: the name of the repo to update, in the same format as github
        owner/repo_name.
    :arg git_folder: directory where the git repos are cloned and thus
        where to find/clone them to update them.
    :raises GitFolderException: if the git_folder specified is not found,
        not a folder
    :raises SyncException: if an error occurs while updating the git repo.
    :returns: an information message that everything went fine.

    """
    if not os.path.exists(git_folder):
        raise GitFolderException(
            'No directory "%s" could be found' % git_folder)
    if not os.path.isdir(git_folder):
        raise GitFolderException(
            'The git directory specified: "%s" does not appear to be a '
            'directory' % git_folder)

    full_git_repo = os.path.join(git_folder, repo)

    if not os.path.exists(full_git_repo):
        LOG.info('cloning new repo "%s" in "%s"', repo, git_folder)
        output = clone_repo(git_folder, repo)
    else:
        LOG.info('updating repo "%s" in "%s"', repo, git_folder)
        output = update_repo(full_git_repo)

    return output


def clone_repo(git_folder, repo):
    """ Clone the provided repo from github into the specified directory.

    :arg git_folder: the directory in which to clone the provided git repo.
    :arg repo: the name of the repository has identified on github:
        owner/repo_name.
    :raises SyncException: if an error occurs while cloning the git repo.
    :returns: an information message that everything went fine

    """
    full_git_repo = os.path.join(git_folder, repo)
    git_url = 'https://github.com/%s.git' % repo

    try:
        req = urllib2.urlopen(git_url)
    except urllib2.HTTPError, err:
        raise SyncException(str(err))

    stdout, stderr, returncode = run_command(
        ['git', 'clone', '--mirror', git_url, full_git_repo])

    LOG.info('stdout: "%s"', stdout.strip())
    LOG.info('stderr: "%s"', stderr.strip())
    if not returncode:
        output = "Repository cloned"
    else:
        output = 'Something went wrong when clonning "{0}" into {1}'.format(
            git_url, full_git_repo)
        LOG.debug(output)
        LOG.debug('stdout: "%s"', stdout.strip())
        LOG.debug('stderr: "%s"', stderr.strip())
    return output


def update_repo(full_git_repo):
    """ Pull the changes in the provided repo from github.

    :arg full_git_repo: full path to the repo cloned on the file-system.
    :returns: an information message that everything went fine

    """
    cwd = os.getcwd()
    os.chdir(full_git_repo)
    stdout, stderr, returncode = run_command(['git', 'remote', 'update'])
    os.chdir(cwd)

    LOG.info('stdout: "%s"', stdout.strip())
    LOG.info('stderr: "%s"', stderr.strip())

    if not returncode:
        output = "Repository updated"
    else:
        output = 'Something went wrong when updating repo "{0}"'.format(
            full_git_repo)
        LOG.debug(output)
        LOG.debug('stdout: "{0}"', stdout.strip())
        LOG.debug('stderr: "{0}"', stderr.strip())
    return output
