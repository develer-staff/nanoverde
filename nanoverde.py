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

class Led:
    def __init__(self):
        if not os.path.isdir("/sys/class/gpio/pioA27"):
            file = open("/sys/class/gpio/export", "w")
            file.write("27")
            file.close()
        if not os.path.isdir("/sys/class/gpio/pioA26"):
            file = open("/sys/class/gpio/export", "w")
            file.write("26")
            file.close()

        file = open("/sys/class/gpio/pioA27/direction", "w")
        file.write("out")
        file.close()
        file = open("/sys/class/gpio/pioA27/value", "w")
        file.write("0")
        file.close()

        file = open("/sys/class/gpio/pioA26/direction", "w")
        file.write("out")
        file.close()
        file = open("/sys/class/gpio/pioA26/value", "w")
        file.write("0")
        file.close()

        self.erogaCredito(1)
        self.ledErrore(1, 10)


    def __del__(self):
        file = open("/sys/class/gpio/pioA27/value", "w")
        file.write("0")
        file.close()
        file = open("/sys/class/gpio/unexport", "w")
        file.write("27")
        file.close()

        file = open("/sys/class/gpio/pioA26/value", "w")
        file.write("0")
        file.close()
        file = open("/sys/class/gpio/unexport", "w")
        file.write("26")
        file.close()

    def erogaCredito(self, sec):
        file = open("/sys/class/gpio/pioA27/value", "w")
        file.write("1")
        file.flush()
        time.sleep(sec)
        file.write("0")
        file.flush()
        time.sleep(sec)
        file.close()

    def ledErrore(self, sec, count):
        file = open("/sys/class/gpio/pioA26/value", "w")
        for i in range(0, count):
            file.write("1")
            file.flush()
            time.sleep(sec/2.0)
            file.write("0")
            file.flush()
            time.sleep(sec/2.0)
        file.close()

    def ledOk(self):
        file = open("/sys/class/gpio/pioA26/value", "w")
        for i in range(0, 2):
            file.write("1")
            file.flush()
            time.sleep(sec/2.0)
            file.write("0")
            file.flush()
            time.sleep(sec/2.0)
        file.close()

    def ledRitirato(self):
        file = open("/sys/class/gpio/pioA26/value", "w")
        for i in range(0, count):
            file.write("1")
            file.flush()
            time.sleep(sec/2.0)
            file.write("0")
            file.flush()
            time.sleep(sec/2.0)
        file.close()

    def ledNoVenerdi(self, sec, count):
        file = open("/sys/class/gpio/pioA26/value", "w")
        for i in range(0, count):
            file.write("1")
            file.flush()
            time.sleep(sec/2.0)
            file.write("0")
            file.flush()
            time.sleep(sec/2.0)
        file.close()

    def ledNoOre(self, sec, count):
        file = open("/sys/class/gpio/pioA26/value", "w")
        for i in range(0, count):
            file.write("1")
            file.flush()
            time.sleep(sec/2.0)
            file.write("0")
            file.flush()
            time.sleep(sec/2.0)
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
    today = datetime.datetime.today()
    oneday = datetime.timedelta(days=4)
    day=datetime.timedelta(days=5)
    v = today-day  # messo in modo che funzioni dato che oggi non e venerdi e ho
    l = v-oneday
    v = v.strftime("%y-%m-%d")
    l = l.strftime("%y-%m-%d")
    slunedi = "20"+str(l)
    svenerdi = "20"+str(v)
    try:
        r = requests.get("https://showtime.develer.com/summary/" +
                         user+"?from_date="+slunedi+"&to_date="+svenerdi)
    except requests.exceptions.ConnectionError:
        print "Impossibile contattare il server."
        return False

    if r.status_code == 200:
        a = r.json()
        totaleOre = 0
        for k, v in a.items():
            v = str(v)
            v = v.split('.')
            ore = float(v[1])/60
            totaleOre = totaleOre+ore+float(v[0])

        if totaleOre >= 35 and a[svenerdi] >= 6:
            return True

        print "Ore non sufficienti per %s" % utente
        return False

    print "Errore nella richiesta al server [%s]" % r.status_code
    return False


def registraPremioUtente(user):
    today = datetime.datetime.today()
    today = "20"+today.strftime("%y-%m-%d")
    print("RITIRARE PREMIO")  # EROGAZIONE PREMIO
    f = open('/home/root/documento.txt', 'a')
    f.write(user+';'+str(today)+'\n')
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

    l=Led()
    utenti_dict = creazioneDizionario("utenti")
    while True:
        sys.stdout.flush()
        sys.stderr.write("prova\n")
        timenow=strftime('%H:%M')
        if (datetime.date.today().weekday()==4 and timenow=="18:00") or (options.venerdi):
            print "Oggi è venerdi prova a ritirare il premio.."
            key = letturaTag()
            print("Tag: %s" % key)
            utente = controlloKey(key, utenti_dict)
            if key is not None:
                if utente is not None:
                    print("Tag Trovato!")
                    if premioErogato(utente):
                        print("Utente abilitato al ritirato il premio")
                        # chiedo al server per sapere se ha registrato le ore
                        lavoro = verificaOreRegistrate(utente)
                        if lavoro:
                            print("Ok utente %s, ha inserito le ore!" % utente)
                            l.erogaCredito(1)
                            registraPremioUtente(utente)
                            print("Erogato premio a %s" % utente)
                        else:
                            print "%s non ha lavorato abbastanza.." % utente
                            l.ledErrore(1,2)
                else:
                    print "Tag non nel DB.. %s" % key
                    l.ledErrore(1,3)
        else:
            l.ledErrore(1,1)

#FUNZIONAMENTO LED:
#1)tutto bene = led verde
#2)utente ha gia' ritirato il premio = lampeggia 3 volte led rosso
#3)ore non corrette = lampeggia 2 volte led ross
#4)non venerdi', non sono passate le 18 = lampeggia una volta
