import toml
import socket
import ssl
import random
import RPi.GPIO as GPIO

erlaubt = [''] #Trage hier die Twitchnamen derer ein, welche das Licht steuern dürfen, wenn mods die Steuerung generell freigegeben haben. Mods müssen hier nicht extra eingetragen werden.
mods = [''] #Trage hier den Twitchnamen derer ein, welche bestimmen dürfen, wann das Licht gesteuert werden darf. Füge bei mehreren Person jede Person in ein Listenelement
mein_licht = False
r_pin = 27
g_pin = 22
b_pin = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(g_pin,GPIO.OUT)
GPIO.setup(r_pin,GPIO.OUT)
GPIO.setup(b_pin,GPIO.OUT)


def send(irc:ssl.SSLSocket, message:str):
    irc.send(bytes(f'{message}\r\n','UTF-8'))

def send_pong(irc:ssl.SSLSocket):
    send(irc, 'PONG :tmi.twitch.tv')

def send_chat(irc:ssl.SSLSocket, message:str, channel:str):
    send(irc, f'PRIVMSG {channel} :{message}')

def handle_chat(irc:ssl.SSLSocket, raw_message:str):
    global erlaubt
    global mods
    global mein_licht
    comp = raw_message.split()
    user, host = comp[0].split('!')[1].split('@')
    channel = comp[2]
    message = ' '.join(comp[3:])[1:]

    if message.startswith('!'):
        msg_comp = message.split()
        cmd = msg_comp[0][1:]
        
        if cmd == 'meinLicht':
            if user in mods:
                if mein_licht:
                    mein_licht = False
                    send_chat(irc, 'Das Licht kann nun gesteuert werden',channel)
                else:
                    mein_licht = True
                    send_chat(irc, 'Das Licht kann nun nichtmehr gesteuert werden',channel)
            else:
                send_chat(irc, f'{user}, dazu hast du keine Rechte!', channel)
        elif cmd == 'licht':
            if user in erlaubt or user in mods:
                try:
                    if mein_licht == False:
                        r, g, b = msg_comp[1:]
                        if r == 'T':
                            GPIO.output(r_pin, GPIO.HIGH)
                        else:
                            GPIO.output(r_pin, GPIO.LOW)

                        if g == 'T':
                            GPIO.output(g_pin, GPIO.HIGH)
                        else:
                            GPIO.output(g_pin, GPIO.LOW)

                        if b == 'T':
                            GPIO.output(b_pin, GPIO.HIGH)
                        else:
                            GPIO.output(b_pin, GPIO.LOW)

                        send_chat(irc, f'{user}, die Farbe wurde eingestellt!',channel)
                    else:
                        send_chat(irc, f'{user}, das Licht kann aktuell nicht gesteuert werden!',channel)
                except:
                    send_chat(irc, f'{user}, das ist keine gültige Verwendung! Nutze !help für Hilfe.',channel)
            else:
                send_chat(irc, f'{user}, dazu hast du keine Rechte!', channel)
        elif cmd == 'aus':
            if user in mods:
                send_chat(irc,'Wenn ihr mich nicht wollt, schalte ich mich halt aus. Bis zum nächsten Mal. :(',channel)
                exit()
            else:
                send_chat(irc,f'{user}, dazu hast du keine Rechte!',channel)
        elif cmd == 'help':
            send_chat(irc, f'{user}, nutze !licht um meine RGB zu steuern. Du musst mit leerzeichen getrennt die drei Farbwerte für Rot, Grün und Blau angeben. Dabei steht T für an und F für aus. Beispiel: "!licht T F F" würde die Farbe Rot einstellen.', channel)

config = toml.load('config.toml')
name = config['botname']
token = config['token']
channelname = config['channelname']

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
irc = context.wrap_socket(socket)

irc.connect(('irc.chat.twitch.tv',6697))

send(irc, f'PASS oauth:{token}')
send(irc, f'NICK {name}')
send(irc, f'JOIN #{channelname}')

print('started')
while True:
    data = irc.recv(1024)
    raw_message = data.decode('UTF-8')
    for line in raw_message.splitlines():
        if line.startswith('PING :tmi.twitch.tv'):
            send_pong(irc)
        else:
            cmd = line.split()[1]

            if cmd == 'PRIVMSG':
                handle_chat(irc,line)
