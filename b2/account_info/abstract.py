######################################################################
#
# File: b2/account_info/abstract.py
#
# Copyright 2016 Backblaze Inc. All Rights Reserved.
#
# License https://www.backblaze.com/using_b2_code.html
#
######################################################################

from abc import abstractmethod

import six

from ..utils import B2TraceMetaAbstract, limit_trace_arguments


@six.add_metaclass(B2TraceMetaAbstract)
class AbstractAccountInfo(object):
    """
    Holder for all account-related information that needs to be kept
    between API calls, and between invocations of the command-line
    tool.  This includes: account id, application key, auth tokens,
    API URL, download URL, and uploads URLs.

    This class must be THREAD SAFE because it may be used by multiple
    threads running in the same Python process.  It also needs to be
    safe against multiple processes running at the same time.
    """

    REALM_URLS = {
        'production': 'https://api.backblazeb2.com',
        'dev': 'http://api.backblazeb2.xyz:8180',
        'staging': 'https://api.backblaze.net',
    }

    @abstractmethod
    def clear(self):
        """
        Removes all stored information
        """

    @abstractmethod
    @limit_trace_arguments(only=['self'])
    def refresh_entire_bucket_name_cache(self, name_id_iterable):
        """
        Removes all previous name-to-id mappings and stores new ones.
        """

    @abstractmethod
    def remove_bucket_name(self, bucket_name):
        """
        Removes one entry from the bucket name cache.
        """

    @abstractmethod
    def save_bucket(self, bucket):
        """
        Remembers the ID for a bucket name.
        """

    @abstractmethod
    def get_bucket_id_or_none_from_bucket_name(self, bucket_name):
        """
        Looks up the bucket ID for a given bucket name.
        """

    @abstractmethod
    def get_bucket_name_from_allowed_or_none(self):
        """
        Looks up the bucket name from the allowed bucket Id stored in account_info.
        """

    @abstractmethod
    def clear_bucket_upload_data(self, bucket_id):
        """
        Removes all upload URLs for the given bucket.
        """

    @abstractmethod
    def get_account_id(self):
        """ returns account_id or raises MissingAccountData exception """

    @abstractmethod
    def get_account_auth_token(self):
        """ returns account_auth_token or raises MissingAccountData exception """

    @abstractmethod
    def get_api_url(self):
        """ returns api_url or raises MissingAccountData exception """

    @abstractmethod
    def get_application_key(self):
        """ returns application_key or raises MissingAccountData exception """

    @abstractmethod
    def get_download_url(self):
        """ returns download_url or raises MissingAccountData exception """

    @abstractmethod
    def get_realm(self):
        """ returns realm or raises MissingAccountData exception """

    @abstractmethod
    def get_minimum_part_size(self):
        """
        :return: returns the minimum number of bytes in a part of a large file
        """

    @abstractmethod
    def get_allowed(self):
        """
        The 'allowed' structure may be None if the account info was stored
        before the B2 service supported the field.  None should be treated
        as allowing everything.

        :return: returns the 'allowed' structure returned by B2 as a dict
        """

    @abstractmethod
    def get_allowed_bucket_id(self):
        """
        returns the bucketId from allowed or None
        """

    @abstractmethod
    def get_allowed_name_prefix(self):
        """
        returns the namePrefix from allowed or an empty string
        """

    @abstractmethod
    @limit_trace_arguments(only=['self', 'api_url', 'download_url', 'minimum_part_size', 'realm'])
    def set_auth_data(
        self, account_id, auth_token, api_url, download_url, minimum_part_size, allowed,
        application_key, realm
    ):
        """
        Stores the results of b2_authorize_account.

        All of the information returned by b2_authorize_account is saved, because all of it is
        needed by some command.

        The allowed structure is the one returned b2_authorize_account, with the addition of
        a bucketName field.  For keys with bucket restrictions, the name of the bucket is looked
        up and stored, too.  The console_tool does everything by bucket name, so it's convenient
        to have the restricted bucket name handy.
        """

    @abstractmethod
    def take_bucket_upload_url(self, bucket_id):
        """
        Returns a pair (upload_url, upload_auth_token) that has been removed
        from the pool for this bucket, or (None, None) if there are no more
        left.
        """

    @abstractmethod
    @limit_trace_arguments(only=['self', 'bucket_id'])
    def put_bucket_upload_url(self, bucket_id, upload_url, upload_auth_token):
        """
        Add an (upload_url, upload_auth_token) pair to the pool available for
        the bucket.
        """

    @abstractmethod
    @limit_trace_arguments(only=['self'])
    def put_large_file_upload_url(self, file_id, upload_url, upload_auth_token):
        pass

    @abstractmethod
    def take_large_file_upload_url(self, file_id):
        pass

    @abstractmethod
    def clear_large_file_upload_urls(self, file_id):
        pass

    @staticmethod
    def allowed_is_valid(allowed):
        """
        Returns true iff the 'allowed' dict passed in is legal.

        For now, we are assuming that what comes back from the service is legal.  The
        point of this method is to make sure that bucketName is set appropriately.
        """
        # Special case.  Some unit tests do not have 'allowed'.
        if allowed is None:
            return True

        return (
            ('bucketId' in allowed) and ('bucketName' in allowed) and
            ((allowed['bucketId'] is None) == (allowed['bucketName'] is None))
        )