##
# Copyright (C) 2012 by Konstantin Ryabitsev and contributors
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
import logging
import totpcgi

import exceptions

logger = logging.getLogger('totpcgi')

class BackendNotSupported(exceptions.Exception):
    def __init__(self, message):
        exceptions.Exception.__init__(self, message)
        logger.debug('!BackendNotSupported: %s' % message)

class Backends:
    
    def __init__(self):
        self.secret_backend  = None
        self.pincode_backend = None
        self.state_backend   = None

    def load_from_config(self, config):
        secret_backend_engine = config.get('secret_backend', 'engine')

        if secret_backend_engine == 'file':
            import totpcgi.backends.file
            secrets_dir = config.get('secret_backend', 'secrets_dir')
            self.secret_backend = totpcgi.backends.file.GASecretBackend(secrets_dir)

        elif secret_backend_engine == 'pgsql':
            import totpcgi.backends.pgsql
            pg_connect_string = config.get('secret_backend', 'pg_connect_string')
            self.secret_backend = totpcgi.backends.pgsql.GASecretBackend(pg_connect_string)

        else:
            raise BackendNotSupported(
                    'secret_backend engine not supported: %s' % secret_backend_engine)

        pincode_backend_engine = config.get('pincode_backend', 'engine')

        if pincode_backend_engine == 'file':
            import totpcgi.backends.file
            pincode_file = config.get('pincode_backend', 'pincode_file')
            self.pincode_backend = totpcgi.backends.file.GAPincodeBackend(pincode_file)

        elif pincode_backend_engine == 'pgsql':
            import totpcgi.backends.pgsql
            pg_connect_string = config.get('pincode_backend', 'pg_connect_string')
            self.pincode_backend = totpcgi.backends.pgsql.GAPincodeBackend(pg_connect_string)

        elif pincode_backend_engine == 'ldap':
            import totpcgi.backends.ldap
            ldap_url    = config.get('pincode_backend', 'ldap_url')
            ldap_dn     = config.get('pincode_backend', 'ldap_dn')
            ldap_cacert = config.get('pincode_backend', 'ldap_cacert')

            self.pincode_backend = totpcgi.backends.ldap.GAPincodeBackend(ldap_url, ldap_dn, ldap_cacert)
        else:
            raise BackendNotSupported(
                    'pincode_engine not supported: %s' % pincode_backend_engine)


        state_backend_engine = config.get('state_backend', 'engine')

        if state_backend_engine == 'file':
            import totpcgi.backends.file
            state_dir = config.get('state_backend', 'state_dir')
            self.state_backend = totpcgi.backends.file.GAStateBackend(state_dir)

        elif state_backend_engine == 'pgsql':
            import totpcgi.backends.pgsql
            pg_connect_string = config.get('state_backend', 'pg_connect_string')
            self.state_backend = totpcgi.backends.pgsql.GAStateBackend(pg_connect_string)

        else:
            syslog.syslog(syslog.LOG_CRIT, 
                    'state_backend engine not supported: %s' % state_backend_engine)

############################### API STUBS #################################

class GAStateBackend:
    def __init__(self):
        pass

    def get_user_state(self, user):
        pass

    def update_user_state(self, user, state):
        pass

    def delete_user_state(self, user):
        pass

class GASecretBackend:
    def __init__(self):
        pass

    def get_user_secret(self, user, pincode=None):
        pass

    def save_user_secret(self, user, gaus, pincode=None):
        pass 

    def delete_user_secret(self, user):
        pass

class GAPincodeBackend:
    def __init__(self):
        pass

    def verify_user_pincode(self, user, pincode):
        pass

    def save_user_hashcode(self, user, pincode, makedb=True):
        pass

    def delete_user_hashcode(self, user):
        pass

    def _verify_by_hashcode(self, pincode, hashcode):
        logger.debug('Will test against %s' % hashcode)
        from passlib.apps import custom_app_context as pwd_context

        try:
            if not pwd_context.verify(pincode, hashcode):
                raise totpcgi.UserPincodeError('Pincode did not match.')

            return True

        except ValueError:
            raise totpcgi.UserPincodeError('Unsupported hashcode format')

