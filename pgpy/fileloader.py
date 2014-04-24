""" fileloader.py

File-based metaclass to reduce duplicate code.
"""
import os
import os.path
import requests

try:
    e = FileNotFoundError
except NameError:
    e = IOError


class FileLoader(object):
    @staticmethod
    def is_path(ppath):
        if bytes is not str and type(ppath) is bytes:
            return False

        # if we get to this point, testing will need to be a little more involved
        # the POSIX specification (http://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap03.html#tag_03_276)
        # for what constitutes a valid filename includes the following characters:
        # A-Z, a-z, 0-9, ., _, -
        #
        # path separators are / on POSIX and \ on Windows
        #
        # lots of other characters that are not present here can indeed be part of a filename

        # this should be adequate most of the time
        # we'll detect all unprintable and extended ASCII characters as 'bad' - their presence will denote 'not a path'
        badchars = [ chr(c) for c in range(0, 32) ]
        badchars += [ chr(c) for c in range(128, 256) ]

        # Windows also specifies some reserved characters
        if os.name == "nt":
            badchars += ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

        if any(c in ppath for c in badchars):
            return False

        return True

    def __init__(self, lfile):
        self.bytes = bytes()
        self.path = None

        # None means we're creating a new file, probably in-memory
        if lfile is None:
            pass

        # we have been passed a file-like object
        elif hasattr(lfile, "read"):
            self.bytes = bytes(lfile.read())

            # try to extract the path, too
            if hasattr(lfile, "name") and os.path.exists(os.path.realpath(lfile.name)):
                self.path = lfile.name

        # str without NUL bytes means this is likely a file path or URL
        # because in 2.x, bytes is just an alias of str
        elif FileLoader.is_path(lfile):
            # is this a URL?
            if "://" in lfile and '\n' not in lfile:
                r = requests.get(lfile, verify=True)

                if not r.ok:
                    raise e(lfile)

                self.bytes = r.content

            # this may be a file path, then
            # does the path already exist?
            elif os.path.exists(lfile):
                self.path = os.path.realpath(lfile)

                with open(lfile, 'rb') as lf:
                    self.bytes = bytes(lf.read())

            # if the file does not exist, does the directory pointed to exist?
            elif os.path.isdir(os.path.dirname(lfile)):
                self.path = os.path.realpath(lfile)

            # if the file does not exist and its directory path does not exist,
            # you're gonna have a bad time
            else:
                raise e(lfile)

        # we have been passed the contents of a file that were read elsewhere
        elif type(lfile) in [str, bytes]:
            self.bytes = bytes(lfile)

        # some other thing
        else:
            raise TypeError(type(lfile) + "Not expected")

        # try to kick off the parser
        # this only works on properly implemented children of this type
        if self.bytes != bytes():
            try:
                self.parse()

            except NotImplementedError:
                pass

    def parse(self):
        raise NotImplementedError()