#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import string
import sys
import binascii
import serial
import datetime
import requests
import time
import os
from optparse import OptionParser
from time import strftime

LED_VERDE="/sys/class/gpio/pioA27"
LED_ROSSO="/sys/class/gpio/pioA26"
class Led:
    def __init__(self):
        if not os.path.isdir(LED_VERDE + "/"):
            file = open("/sys/class/gpio/export", "w")
            file.write("27")
            file.close()
        if not os.path.isdir(LED_ROSSO + "/"):
            file = open("/sys/class/gpio/export", "w")
            file.write("26")
            file.close()

        file = open(LED_VERDE+ "/direction", "w")
        file.write("out")
        file.close()
        file = open(LED_VERDE + "/value", "w")
        file.write("0")
        file.close()

        file = open(LED_ROSSO + "/direction", "w")
        file.write("out")
        file.close()
        file = open(LED_ROSSO + "/value", "w")
        file.write("0")
        file.close()

        self.ledStart()


    def __del__(self):
        file = open(LED_VERDE + "/value", "w")
        file.write("0")
        file.close()
        file = open("/sys/class/gpio/unexport", "w")
        file.write("27")
        file.close()

        file = open(LED_VERDE + "/value", "w")
        file.write("0")
        file.close()
        file = open("/sys/class/gpio/unexport", "w")
        file.write("26")
        file.close()

    def ledOk(self):
        file = open(LED_VERDE + "/value", "w")
        file.write("1")
        file.flush()
        time.sleep(1)
        file.write("0")
        file.close()

    def ledRitirato(self):
        file = open(LED_ROSSO + "/value", "w")
        for i in range(0, 2):
            file.write("1")
            file.flush()
            time.sleep(0.7)
            file.write("0")
            file.flush()
            time.sleep(0.3)
        file.close()

    def ledErrore(self):
        file = open(LED_ROSSO + "/value", "w")
        file.write("1")
        file.flush()
        time.sleep(0.3)
        file.write("0")
        file.close()

        file = open(LED_ROSSO + "/value", "w")
        file.write("1")
        file.flush()
        time.sleep(0.3)
        file.write("0")
        file.close()

    def ledNoVenerdi(self):
        file = open(LED_ROSSO + "/value", "w")
        for i in range(0, 3):
            file.write("1")
            file.flush()
            time.sleep(0.3)
            file.write("0")
            file.flush()
            time.sleep(0.15)
        file.close()

    def ledNoOre(self):
        file = open(LED_ROSSO + "/value", "w")
        file.write("1")
        file.flush()
        time.sleep(1.5)
        file.write("0")
        file.close()

    def ledStart(self):
        file = open(LED_ROSSO + "/value", "w")
        for i in range(0, 2):
            file.write("1")
            file.flush()
            time.sleep(1)

            file.write("0")
            file.flush()
            time.sleep(0.25)

            file.write("1")
            file.flush()
            time.sleep(0.5)

            file.write("0")
            file.flush()
            time.sleep(0.5)
        file.close()


def controlloKey(key, utenti_dict):
    if key in utenti_dict:
        return utenti_dict[key]
    return None


def premioErogato(key):
    doc_dict = creazioneDizionario("documento")
    oggi = datetime.datetime.today()
    stoday = oggi.strftime("%y-%m-%d")
    stoday = "20"+stoday
    print(stoday)
    if key in doc_dict:
        return (stoday != doc_dict[key])

    return True


def verificaOreRegistrate(user):
    print("Verifico ore per %s" % user)
    if user == "test":
        return True

    today = datetime.datetime.today()
    delta_l = datetime.timedelta(days=5)

    l = today - delta_l
    v = today.strftime("%Y-%m-%d")
    l = l.strftime("%Y-%m-%d")
    try:
        r = requests.get("https://showtime.develer.com/summary/" +
                         user+"?from_date="+l+"&to_date="+v)
    except requests.exceptions.ConnectionError:
        print "Impossibile contattare il server."
        return False

    if r.status_code == 200:
        a = r.json()
        totaleOre = 0
        for k, o in a.items():
            o = str(o)
            o = o.split('.')
            ore = float(o[1])/60
            totaleOre = totaleOre+ore+float(o[0])

        print totaleOre
        if totaleOre >= 35 and a[v] >= 6:
            return True

        print "Ore non sufficienti per %s" % utente
        return False

    print "Errore nella richiesta al server [%s]" % r.status_code
    return False


def registraPremioUtente(user):
    today = datetime.datetime.today()
    today = "20"+today.strftime("%y-%m-%d")
    print("RITIRARE PREMIO")  # EROGAZIONE PREMIO

    doc_dict=creazioneDizionario('documento')
    doc_dict[user]=str(today)

    f = open('/home/root/documento.txt', 'w')
    for k,v in doc_dict.items():
        f.write("%s;%s\n" % (k, v))
    f.close()


def creazioneDizionario(nome):
    f = open("/home/root/" + nome+'.txt', 'r')
    utenti_dict = {}
    for line in f:
        line = line.strip()
        try:
            if line != "":
                l = line.split(';')
                k = l[0].strip()
                v = l[1].strip()

                utenti_dict[k] = v
        except IndexError:
            continue

    return utenti_dict


def letturaTag():
    try:
        ser = serial.Serial("/dev/ttyS2", 9600)
    except IOError as e:
        print(e)
        sys.exit("Error connecting device")

    tag = ""
    startTag = False

    while True:
        c = ser.read(1)
        if startTag:
            tag += c
        if c == '\x02':
            startTag = True
        if c == '\x03':
            break
    if len(tag) == 15:
        tag = tag[:10]
        return tag
    return None


    return options.value

if __name__ == "__main__":
    parser=OptionParser()
    parser.add_option("-v", action="store_true", dest="venerdi", default=False)
    (options, args)=parser.parse_args()

    print "Abilito led"
    l=Led()
    print "Leggo dizionario utenti."
    utenti_dict = creazioneDizionario("utenti")
    while True:
        sys.stdout.flush()
        sys.stderr.flush()
        open_time = 18
        timenow=int(strftime('%H')) + 2
        daynow=datetime.date.today().weekday()
        key = letturaTag()
        out_file = open("tagpassed.txt","r")
        f_tag=out_file.readlines()
        f.close()
        f_tag.append(key + '\n')
        print("Tag: %s" % key)
        utente = controlloKey(key, utenti_dict)
        if key is not None:
            if utente is not None:
                print("Tag Trovato!")
                #if (daynow==4 and timenow>=open_time) or utente == "test":
                if (daynow==4) or utente == "test":
                    print "Oggi è venerdi prova a ritirare il premio.."
                    if premioErogato(utente) or utente == "test":
                        print("Utente abilitato al ritirato il premio")
                        # chiedo al server per sapere se ha registrato le ore
                        lavoro = verificaOreRegistrate(utente)
                        if lavoro:
                            print("Ok utente %s, ha inserito le ore!" % utente)
                            l.ledOk()
                            registraPremioUtente(utente)
                            print("Erogato premio a %s" % utente)
                        else:
                            print "%s non ha lavorato abbastanza.." % utente
                            l.ledNoOre()
                    else:
                        print "%s ha già ritirato il premio" % utente
                        l.ledRitirato()
                else:
                    print "%s distributore non abilitato giorno:%s!=%s ora:%s!=%s" % (utente, daynow, 4, timenow, open_time)
                    l.ledNoVenerdi()
            else:
                print "Tag non nel DB.. %s" % key
                l.ledErrore()
        out_file = open("tagpassed.txt","w")
        out_file.write("")
        out_file.close()

#FUNZIONAMENTO LED:
#1)tutto bene = led verde
#2)utente ha gia' ritirato il premio = lampeggia 3 volte led rosso
#3)ore non corrette = lampeggia 2 volte led ross
#4)non venerdi', non sono passate le 18 = lampeggia una volta
