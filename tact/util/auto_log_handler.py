from logging import handlers
from datetime import datetime
from os import path
from os import rename
from os import scandir
from os import remove
from itertools import islice
import re


class AutoReplacingFileHandler(handlers.RotatingFileHandler):

    def __init__(
            self,
            filename,
            mode='a',
            maxBytes=0,
            backupCount=0,
            encoding=None,
            delay=0):
        self.filename = filename
        self.rotate()

        # Delete old log entries
        delete = islice(self.get_matching_files(), backupCount, None)
        for entry in delete:
            # print(entry.path)
            remove(entry.path)

        handlers.RotatingFileHandler.__init__(
            self, self.filename, mode, maxBytes, backupCount, encoding, delay)

    def rotate(self):
        if (path.isfile(self.filename)):
            # rename file on system
            current_time = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
            outpath = current_time + "_" + path.basename(self.filename)
            outfile = path.dirname(self.filename) + "/" + outpath

            rename(self.filename, outfile)

    def get_matching_files(self):
        # Generate DirEntry entries that match the filename pattern.

        # The files are ordered by their last modification time, most recent
        # files first.

        matches = []
        basename = path.basename(self.filename)
        pattern = re.compile(re.sub('%[a-zA-z]', '.*', basename))

        for entry in scandir(path.dirname(self.filename)):
            if not entry.is_file():
                continue
            entry_basename = path.basename(entry.path)
            if re.search(pattern, entry_basename):
                matches.append(entry)
        matches.sort(key=lambda e: e.stat().st_mtime, reverse=True)
        return iter(matches)
