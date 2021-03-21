Um die main.py benutzen zu können, brauchst du im gleichen Ordner eine Datei mit dem namen config.toml, in der du folgende Sachen einträgst:

botname = '' #Accountname vom Account, welcher als Bot genutzt werden soll
token = '' #Ein gültiger OAuth Token des Botaccounts
channelname = '' #Der Twitchchannel, wessen Chat benutzt werden soll


Weiter brauchst du einen Raspberry Pi (ich benutze einen 4B), wo der Code drauf läuft. Teste welche GPIO pins du benutzen möchtest und ändere die pin Variablen am Anfang des Codes.

Der Code basiert auf dem YouTube-Tutorial zum Thema Twitchbot von vojay.
