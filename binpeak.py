#!/usr/bin/env python3

import numpy as np
import time
from binance.client import Client
from reprint import output
import sys
import argparse
import configparser

import pandas as pd
from matplotlib import pyplot as plt
import subprocess as notif
import requests 


parser = argparse.ArgumentParser(description='Доступные параметры!')
parser.add_argument("-p", default=True, nargs='?', type=bool, help="Использовать проценты для сортировки (по умолчанию НЕТ)")
parser.add_argument("-t", default=True, nargs='?', type=bool, help="Использовать тестовые данные (по умолчанию НЕТ)")
parser.add_argument("-g", default="", type=str, help="Рисовать графики и сохранять по указанному пути")
parser.add_argument("-l", default=True, nargs='?', type=bool, help="Вывести список доступных пар и выйти")
parser.add_argument("-s", default=5, type=int, choices=[1, 2, 3, 5, 10, 15], help="Частота обновления данных в секундах (по умолчанию 5)")
parser.add_argument("-top", default=3, type=int, choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], help="Количество монет в топе (по умолчанию 3)")
args = parser.parse_args()

#Settings
delay = args.s
top = args.top
test = not args.t
get_list = not args.l
plots = args.g
percent_sort = not args.p

config_file = 'config.cfg'
config = configparser.ConfigParser()
conf = config.read(config_file)
if (conf):
	api_key = config["API"]["key"]
	secret_key = config["API"]["secret"]

	if config["COINS"]["coinpairs"] == '':
		print("Неверно указан список монет в конфигурационном файле {}".format(config_file))
		sys.exit()
	else:
		ncoins = list(set(config["COINS"]["coinpairs"].replace(' ', '').replace('\'', '').split(",")))
		print("Отслеживается пар монет:{}".format(len(ncoins)))

	contacts = config["CONTACTS"]["telegram"].replace(' ', '').replace('\'', '').split(",")

else:
	print("Создан конфигурационный файл {}.Добавьте в него ключи доступа и список отслеживаемых монет. Список можно получить запустив программу с ключём -l".format(config_file))
	config = configparser.ConfigParser()
	config.add_section("API")
	config.set("API", "key", "")
	config.set("API", "secret", "")
	config.add_section("COINS")
	config.set("COINS", "coinpairs", "BTCUSDT, ETHUSDT")

	api_key = ""
	secret_key = ""

	with open(config_file, "w") as config_file:
		config.write(config_file)

if (not api_key or not secret_key) and not test:
	print("Не указаны ключи доступа в файле {}. Доступны только тестовые данные.".format(config_file))
	test = True
elif ((api_key and secret_key) and not test) and get_list:
	client = Client(api_key, secret_key)
	exchange_info = client.get_exchange_info()
	pairs = []
	for pair in exchange_info['symbols']:
		if (pair['symbol'][-4:] == 'USDT'):
			pairs.append(pair['symbol'])
	print(pairs)
	print("Всего доступно пар:{}".format(len(pairs)))
	sys.exit()

def ols(data):
	global percent_sort
	betas = ['nd']
	#print(data)
	if percent_sort:
		ln = len(data)
		if ln > 1:
			min_data = min(data)
			betas = [((data[0] - min_data) / min_data * 100), 0]
	else:
		if len(data) > 1:
			x = []
			x.append(range(len(data)))                 #Time variable
			x.append([1 for ele in range(len(data))]) #This adds the intercept, use range in Python3

			y = np.matrix(data).T
			x = np.matrix(x).T

			betas = ((x.T*x).I*x.T*y)
			betas = [betas.item(0), 0]

	return betas
