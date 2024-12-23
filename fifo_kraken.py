import logging
from collections import deque
import math
import csv
from dateparser import parse
import sys

zyskTotal = 0
btcTotal = 0
totalCounter = 0

# zyskBitbayTotal = 0
# zyskBitbayKrakenTotal = 0
# btcBitbayTotal = 0
# btcBitbayKrakenTotal = 0
# bitbayCounter = 0

zyskKrakenTotal = 0
btcKrakenTotal = 0
krakenCounter = 0

class Trans:
    datetime = None
    initialAmount = None
    amount = None
    price = None
    exchange = None
    row = None

    def __init__(self, datetime, amount, price, exchange, row):
        self.datetime = datetime
        self.initialAmount = amount
        self.amount = amount
        self.price = price
        self.exchange = exchange
        self.row = row

    def getInfo(self):
        if (self.amount > 0):
            tranName = "Transakcja kupna"
        else:
            tranName = "Transakcja sprzedazy"
        return (
                str(tranName) + "; " +
                str(self.exchange) + "; " +
                str(self.datetime) + "; " +
                "Left: " +str(self.amount) + "BTC; " +
                "Price: " + str(self.price)
        ) + "; "
        # return (str(self.datetime) + "; " +
        #         str(self.amount) + "; " +
        #         str(self.price)) + "; "


def balanceFifo(all_trans):
    qTransactions = deque()

    for t in all_trans:
        # Add first element to the queue
        if len(qTransactions) == 0:
            logging.debug('Added the first element: %s', t.getInfo())
            qTransactions.append(t)
            continue

        while (t.amount != 0 and len(qTransactions) > 0):
            # investigate the first element from the queue
            tq = qTransactions.popleft()
            # the same type of transaction: both sell or both buy
            if tq.amount * t.amount > 0:
                # return the first element back to the same place
                qTransactions.appendleft(tq)
                # add the new element to the list
                qTransactions.append(t)
                logging.debug('Added: %s', t.getInfo())
                break

            # contrary transactions: (sell and buy) or (buy and sell)
            if tq.amount * t.amount < 0:
                logging.debug('Transaction : %s', t.getInfo())
                logging.debug('... try to balance with: %s', tq.getInfo())

                # The element in the queue have more units and takes in the current transaction
                if abs(tq.amount) > abs(t.amount):
                    # insertTransaction(tq.datetime, tq.exchange, t.datetime, t.exchange, math.copysign(t.amount, tq.amount), tq.initialAmount, tq.price, t.price, tq.row, t.row)
                    amount = math.copysign(t.amount, tq.amount)
                    insertTransaction(dateBuy=tq.datetime, exchangeBuy=tq.exchange, dateSell=t.datetime,
                                      exchangeSell=t.exchange, amount=amount, amountBuy=tq.initialAmount,
                                      priceStart=tq.price, priceEnd=t.price, posBuy=tq.row, posSell=t.row)
                    # update the amount of the element in the queue
                    tq.amount = tq.amount + t.amount
                    # return the element back to the same place
                    qTransactions.appendleft(tq)
                    logging.debug('Removed transaction: %s', t.getInfo())
                    # the transaction has been balanced, take a new transaction
                    break

                # The element from the queue and transaction have the same amount of units
                if abs(tq.amount) == abs(t.amount):
                    # insertTransaction(tq.datetime, tq.exchange, t.datetime, t.exchange, math.copysign(t.amount, tq.amount), tq.initialAmount, tq.price, t.price, tq.row, t.row)
                    amount = math.copysign(t.amount, tq.amount)
                    insertTransaction(dateBuy=tq.datetime, exchangeBuy=tq.exchange, dateSell=t.datetime,
                                      exchangeSell=t.exchange, amount=amount, amountBuy=tq.initialAmount,
                                      priceStart=tq.price, priceEnd=t.price, posBuy=tq.row, posSell=t.row)
                    # update the amount in the transaction
                    t.amount = 0
                    logging.debug('Balanced, removed transaction: %s', t.getInfo())
                    logging.debug('Balanced, removed from the queue: %s', tq.getInfo())
                    # the transaction has been balanced, take a new transaction
                    continue
                # The transaction has more units
                if abs(tq.amount) < abs(t.amount):
                    # update the units in transaction, (remove element from the queue)
                    t.amount = t.amount + tq.amount
                    amount = tq.amount
                    insertTransaction(dateBuy=tq.datetime, exchangeBuy=tq.exchange, dateSell=t.datetime,
                                      exchangeSell=t.exchange, amount=amount, amountBuy=tq.initialAmount,
                                      priceStart=tq.price, priceEnd=t.price, posBuy=tq.row, posSell=t.row)
                    logging.debug('Removed from queue: %s', tq.getInfo())

                    # the transaction has not been balanced,
                    # take a new element from the queue (t.amount>0)
                    continue

        # We have unbalanced transaction but the queue is empty
        if (t.amount != 0 and len(qTransactions) == 0):
            # Add unbalanced transaction to the queue
            # The queue changes polarisation
            qTransactions.append(t)
            logging.debug('Left element: %s', t.getInfo())

    # If something remained in the queue, treat it as open or part-open transactions
    while (len(qTransactions) > 0):
        tq = qTransactions.popleft()
        logging.debug('Remained on list transaction: %s', tq.getInfo())
        sys.stdout.write("Remained on list transaction: %s\n" % tq.getInfo())


def insertTransaction(dateBuy, exchangeBuy, dateSell, exchangeSell, amount, amountBuy, priceStart, priceEnd, posBuy,
                      posSell):
    # global zyskBitbayTotal, zyskBitbayKrakenTotal
    # global btcBitbayTotal, btcBitbayKrakenTotal
    # global bitbayCounter

    global zyskKrakenTotal
    global btcKrakenTotal
    global krakenCounter

    global zyskTotal
    global btcTotal
    global totalCounter

    zysk = amount * (priceEnd - priceStart)
    zyskTotal += zysk
    btcTotal += amount

    # BITBAY ZYSK - START
    # bitbaySprzedaz = exchangeSell == 'bitbay'
    # bitbayKupno = exchangeBuy == 'bitbay'
    #
    # if (bitbaySprzedaz):
    #     zyskBitbayTotal += zysk
    #     btcBitbayTotal += amount
    #
    # # if (exchangeSell == 'kraken' and exchangeBuy == 'bitbay'):
    # if (bitbayKupno):
    #     zyskBitbayKrakenTotal += zysk
    #     btcBitbayKrakenTotal += amount
    # BITBAY ZYSK - END

    # KRAKEN ZYSK - START
    krakenSprzedaz = exchangeSell == 'kraken'
    # krakenKupno = exchangeBuy == 'kraken'

    if (krakenSprzedaz):
        zyskKrakenTotal += zysk
        btcKrakenTotal += amount

    # if (exchangeSell == 'kraken' and exchangeBuy == 'bitbay'):
    # if (krakenKupno):
    #     zyskBitbayKrakenTotal += zysk
    #     btcBitbayKrakenTotal += amount
    # KRAKEN ZYSK - END

    priceStart = round(priceStart, 2)
    priceEnd = round(priceEnd, 2)
    zysk = round(zysk, 2)

    amount = round(amount, 8)
    amountBuy = round(amountBuy, 8)

    dateSell = parse(dateSell).strftime('%Y-%m-%d %H:%M:%S')
    dateBuy = parse(dateBuy).strftime('%Y-%m-%d %H:%M:%S')

    totalCounter += 1
    if (krakenSprzedaz):  # pozycja kupna={}, pozycja sprzedaży={}
        krakenCounter += 1
        # print("Data kupna={}, Giełda kupno={}, Data sprzedaży={}, Giełda sprzedaż={} ilość={}, oryg ilość. partia zakupu={} cena zakupu={}, cena sprzedaży={}, zysk={}". \
        #   format(dateBuy, exchangeBuy, dateSell, exchangeSell, amount, amountBuy, priceStart, priceEnd, zysk))
        print(
            "{}. Sprzedaż={}, ilość={:f}BTC, kursS={}PLN, giełdaS={}; Kupno={}, giełdaK={}, kursK={}PLN, partia={:f}BTC; Zysk={}PLN". \
            format(krakenCounter, dateSell, amount, priceEnd, exchangeSell, dateBuy, exchangeBuy, priceStart, amountBuy,
                   zysk))
        print()
    # else :
    #     print(
    #         "{}. Sprzedaż={}, ilość={:f}BTC, kursS={}PLN, giełdaS={}; Kupno={}, giełdaK={}, kursK={}PLN, partia={:f}BTC; Zysk={}PLN". \
    #             format(krakenCounter, dateSell, amount, priceEnd, exchangeSell, dateBuy, exchangeBuy, priceStart,
    #                    amountBuy,
    #                    zysk))
    #     print()

# Uncomment if you want to see more information
# logging.basicConfig(level=logging.DEBUG)

trans_list = list()

# with open('test.csv', newline='') as csvfile:
with open('bitcoin_2020.csv', newline='') as csvfile:
# with open('bitcoin_2020_with2018_2019.csv', newline='') as csvfile:
    spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    i = 1
    for row in spamreader:
        if row["Data"] == "":
            continue
        i += 1
        trans = Trans(row["Data"], float(row["BTCInv"]), float(row["Kurs"]), row["Giełda"], i)
        trans_list.append(trans)

# Test selling more than bought - trans not indicated; There is a debug log: "Remained on list transaction" though
# trans = Trans("2022-01-01", 1, 10, 'kraken', 0)
# trans_list.append(trans)
# trans = Trans("2022-01-03", -0.5, 25, 'bitbay', 1)
# trans_list.append(trans)


balanceFifo(trans_list)

print()
print()

zyskKrakenTotal = round(zyskKrakenTotal, 2)
# zyskBitbayKrakenTotal = round(zyskBitbayKrakenTotal, 2)

print("Zysk: ", zyskTotal)
print("Kraken zysk:", zyskKrakenTotal, 'PLN')
# print("Zysk ze sprzedaży partii kupionej na Bitbay:", zyskBitbayKrakenTotal, 'PLN')
print()
# print("BTC: ", btcTotal)

btcKrakenTotal = round(btcKrakenTotal, 8)
# btcBitbayKrakenTotal = round(btcBitbayKrakenTotal, 8)

print("Suma BTC:", btcTotal, 'BTC')
print("Suma BTC sprzedaż Kraken:", btcKrakenTotal, 'BTC')
# print("Suma BTC partii kupionej na Bitbay:", btcBitbayKrakenTotal, 'BTC')

trans_list.clear()