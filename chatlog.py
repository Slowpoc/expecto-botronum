import config
import core

import pathlib
from datetime import datetime
import pytz
import html

####### chatlog.py #######
## handles logging chat ##
## by Annika            ##
##########################

class Chatlogger:
    """Class for logging chat
    """
    def __init__(self, path):
        """Creates a new Chatlogger

        Args:
            path (string): the path to the logging directory
        """
        self.path = pathlib.Path(path)
        if not self.path.exists(): self.path.mkdir()
        if not self.path.is_dir(): core.log(f"E: Chatlogger(): logging directory is a file: {str(self.path.resolve())}")

    def handleMessage(self, message):
        """Handles logging a message to chatlogs

        Args:
            message (Message): the Message
        """
        room = message.room.id if message.room else 'global'
        logFile = self.getFile(room, 'a')
        logFile.write(self.formatMessage(message))

    def getFile(self, roomid, perms):
        """Returns a file object corresponding to the room's chatlog file.

        Args:
            roomid (string that is an ID): the room
            perms (string): the file perms (for example, 'r' or 'w')

        Returns:
            File: a file for the log file for that room and day
        """
        roomFolderPath = self.path.joinpath(roomid)
        if not roomFolderPath.exists(): roomFolderPath.mkdir()
        if not roomFolderPath.is_dir(): 
            return core.log(f"E: Chatlogger(): logging directory is a file: {str(roomFolderPath.resolve())}")
        filePath = roomFolderPath.joinpath(f"{str(datetime.now().date())}.txt")
        return filePath.open(perms)

    def formatMessage(self, message):
        """Formats a message for logging.
        Format: userid|time|type|senderName|body
        Args:
            message (Message): the message to format

        Returns:
            (string): the formatted message
        """
        return "|".join([
            str(message.sender.id) if message.sender else '',
            str(int(datetime.utcfromtimestamp(int(message.time)).astimezone(pytz.utc).timestamp())) if message.time else str(int(datetime.timestamp(datetime.utcnow()))),
            str(message.type) if message.type else '',
            str(message.senderName) if message.senderName else '',
            f"{str(message.body) if message.body else ''}\n"
        ])

    def search(self, roomid="", userid="", keyword="", includeJoins=False):
        """Searches chatlogs

        Args:
            roomid (str, optional): The ID of the room to search in. Defaults to "".
            userid (str, optional): The ID of the user whose messages are being searched for. Defaults to "".
            keyword (str, optional): [description]. Defaults to "".

        Returns:
            dictionary: a dictionary of matched messages (formatted as {date (string): [userid|time|type|senderName|body] (list of day's results)})
        """
        results = {}
        searchDir = self.path.joinpath(roomid)
        userSearch = f"{userid}|" if userid else ""
        if roomid and searchDir.is_dir():
            for logFilePath in searchDir.iterdir():
                date = logFilePath.name.strip(".txt")
                if not logFilePath.is_file(): continue
                for line in logFilePath.open('r').readlines():
                    try:
                        split = line.lower().split('|',4)
                        if line[:len(userSearch)] == userSearch and \
                            keyword in split[-1] and \
                            (includeJoins or (split[2] not in ['join', 'leave'])):
                            if date not in results.keys():
                                results[date] = [line]
                            else:
                                results[date].append(line)
                    except IndexError:
                        pass
        return results

    def formatData(self, data, isHTML=False):
        """Formats data to text

        Args:
            data (string of form userid|time|type|senderName|body): the data
            isHTML (bool, optional): Whether to format as HTML. Defaults to False.

        Returns:
            string: a human-readable version of the message
        """
        splitData = data.split("|", 4)
        if len(splitData) == 5:
            userid, time, msgType, senderName, body = splitData
        elif len(splitData) == 3:
            userid, msgType, body = splitData
            time = ""
            senderName = userid
        else:
            core.log(f"DEBUG: unexpected number of data items (expected 5 or 3, got {str(len(splitData))}; data: f{data})")
            return "Unparseable message (bad format)"
            # TODO: figure out what to do about |html|, |raw|, etc
        try:
            time = f"[{str(datetime.utcfromtimestamp(int(time)).time())}] "
            if isHTML: time = f"<small>{html.escape(time)}</small>"
        except ValueError:
            time = ""
        body = body.strip().strip('\n')
        sender = senderName.strip()
        if isHTML:
            body = html.escape(body)
            sender = html.escape(sender)

        isAdmin = sender[:5] == '&amp;' if sender else False
        htmlRankSet = set(config.roomRanksInOrder)
        htmlRankSet.discard('&') # '&' rank is already handled with isAdmin
        if sender and (isAdmin or sender[0] in htmlRankSet.union(set('+%@*#~'))):
            rank = sender[:5] if isAdmin else sender[0]
            sender = f"<small>{rank}</small><b>{sender[len(rank):]}</b>" if isHTML else rank + sender[len(rank):]
        else:
            sender = f"<b>{sender}</b>"
        if msgType in ['chat', 'pm']:
            return f"{time}{sender}: {body}"
        elif msgType == 'join':
            return f"{time}{sender} joined"
        elif msgType == 'leave':
            return f"{time}{sender} left"
        else:
            return "Unparseable message"

    def __str__(self):
        return f"Chatlogger logging to path {str(self.path.resolve())}/"
