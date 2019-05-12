import socket
import time
import asyncio

from cnst import HOST, PORT, PWD, IDENT, CHANNEL
from TwitchAPI import TwitchApiWrapper


def get_current_time():
    return time.strftime("%H:%M:%S")


class Message:
    def __init__(self, line):
        self.line = line

        sp = self.line.split(":", 2)
        self.author = sp[1].split("!", 1)[0]
        self.content = sp[2][:-2]  # slice to remove MSG_END = \r\n

        self.time = get_current_time()

    def __repr__(self):
        return '[{}] {} : {}'.format(self.time, self.author, self.content)


class TwitchBot:
    MAX_LENGTH_MESSAGE = 500
    SPAM_PROTECTION = 2 # second
    MSG_END = '\r\n'
    MSG_TEMPLATE = 'PRIVMSG #{} :{}' + MSG_END
    PING = 'PING :tmi.twitch.tv' + MSG_END
    PONG = 'PONG :tmi.twitch.tv' + MSG_END

    def __init__(self, host, port, pwd, ident, channel):
        self.host = host
        self.port = port
        self.pwd = pwd
            self.ident = ident
        self.channel = channel
        #
        self.last_message_send_time = time.time()
        self.loop = asyncio.get_event_loop()

    # *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

    def _open_socket(self):
        self._s = socket.socket()
        self._s.connect((self.host, self.port))

    def _connect_to_twitch(self):
        self._send('PASS ' + self.pwd + self.MSG_END)
        self._send('NICK ' + self.ident + self.MSG_END)
        self._send('JOIN #' + self.channel + self.MSG_END)

    def _join_twitch_room(self):
        buffer = bytearray()
        while True:
            data = self._s.recv(1024)
            buffer.extend(data)
            print('>', data.decode())
            if "End of /NAMES list" in buffer.decode():
                break
        print('\n******Successfully joined the chat !******\n')

    def _send(self, msg):
        self._s.send(msg.encode())
        self.last_message_send_time = time.time()

    def _reception(self):
        while True:
            try:
                data = self._s.recv(1024)
            except BlockingIOError:
                pass
            else:
                line = data.decode()
                if line == self.PING:
                    self._send(self.PONG)
                else:
                    self.on_message(Message(line))

    # *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

    def run(self):
        self._open_socket()
        self._connect_to_twitch()
        self._join_twitch_room()
        self.loop.run_forever(self._reception())

    def send(self, msg, antispam=True):
        if antispam:
            dt = time.time() - self.last_message_send_time
            if dt < self.SPAM_PROTECTION:
                print('Antispam Protection activated')
                time.sleep(self.SPAM_PROTECTION - dt)
        if msg:
            if len(msg) > self.MAX_LENGTH_MESSAGE:
                print('* message too long')
                msg = msg[:self.MAX_LENGTH_MESSAGE]

            data = self.MSG_TEMPLATE.format(self.channel, msg)
            self._send(data)

        else:
            print('* message empty')

    # *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

    def on_message(self, message):
        print(message)

        # respond only to ourselves
        if message.author == self.ident:
            self.last_message_send_time = time.time()
        else:
            return

        if message.content == '!r':
            print('**run on**')
            self.send('!collect')



    # *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-


if __name__ == '__main__':
    bot = TwitchBot(host=HOST,
                    port=PORT,
                    pwd=PWD,
                    ident=IDENT,
                    channel=CHANNEL)
    bot.run()
