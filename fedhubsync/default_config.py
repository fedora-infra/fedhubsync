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

'''
Default configuration for the fedhubsync Flask application.
'''

## Admin to which emails are sent when exceptions are triggered
MAIL_ADMIN = 'pingou@pingoured.fr'

## SMTP server to use to send the emails (see MAIL_ADMIN)
SMTP_SERVER = 'localhost'

## Folder in which the git repositories will be cloned
GIT_FOLDER = '.'

## A secret key known only by the project allowed to mirror on fedorahosted
API_KEY = '123'
