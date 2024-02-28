import logging
from collections import deque
import math
import csv

zyskTotal = 0
zyskBitbayTotal = 0
zyskBitbayKrakenTotal = 0

btcTotal = 0
btcBitbayTotal = 0
btcBitbayKrakenTotal = 0
class Trans:
    datetime = None
    amount = None
    price = None
    exchange = None
    row = None

    def __init__(self, datetime, amount, price, exchange, row):
        self.datetime = datetime
        self.amount = amount
        self.price = price
        self.exchange = exchange
        self.row = row

    def getInfo(self):
        return (str(self.datetime) + "; " +
                str(self.amount) + "; " +
                str(self.price)) + "; "


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
                    insertTransaction(tq.datetime, tq.exchange, t.datetime, t.exchange, math.copysign(t.amount, tq.amount), tq.price, t.price, tq.row, t.row)
                    # update the amount of the element in the queue
                    tq.amount = tq.amount + t.amount
                    # return the element back to the same place
                    qTransactions.appendleft(tq)
                    logging.debug('Removed transaction: %s', t.getInfo())
                    # the transaction has been balanced, take a new transaction
                    break

                # The element from the queue and transaction have the same amount of units
                if abs(tq.amount) == abs(t.amount):
                    insertTransaction(tq.datetime, tq.exchange, t.datetime, t.exchange, math.copysign(t.amount, tq.amount), tq.price, t.price, tq.row, t.row)

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
                    insertTransaction(tq.datetime, tq.exchange, t.datetime, t.exchange, tq.amount, tq.price, t.price, tq.row, t.row)
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

def insertTransaction(dateBuy, exchangeBuy, dateSell, exchangeSell, amount, priceStart, priceEnd, posBuy, posSell):
    global zyskTotal, zyskBitbayTotal, zyskBitbayKrakenTotal
    global btcTotal, btcBitbayTotal, btcBitbayKrakenTotal
    zysk = amount * (priceEnd - priceStart)
    zyskTotal += zysk
    btcTotal += amount

    bitbaySprzedaz = exchangeSell == 'bitbay'
    bitbayKupno = exchangeBuy == 'bitbay'

    if (bitbaySprzedaz):
        zyskBitbayTotal += zysk
        btcBitbayTotal += amount

    # if (exchangeSell == 'kraken' and exchangeBuy == 'bitbay'):
    if (bitbayKupno):
        zyskBitbayKrakenTotal += zysk
        btcBitbayKrakenTotal += amount

    if (bitbaySprzedaz or bitbayKupno):
        print("Data kupna={}, Giełda kupno={}, Data sprzedaży={}, Giełda sprzedaż={} ilość={}, cena zakupu={}, cena sprzedaży={}, zysk={}, pozycja kupna={}, pozycja sprzedaży={}". \
          format(dateBuy, exchangeBuy, dateSell, exchangeSell, amount, priceStart, priceEnd, amount * (priceEnd - priceStart), posBuy, posSell))


# Uncomment if you want to see more information
# logging.basicConfig(level=logging.DEBUG)

trans_list = list()
# with open('bitcoin_od_2018.csv', newline='') as csvfile:
with open('bitcoin_2020_bez_coinmate.csv', newline='') as csvfile:
# with open('bitcoin_2020_z_coinmate.csv', newline='') as csvfile:
    spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    i = 1
    for row in spamreader:
        if row["Data"] == "":
            continue
        i+=1
        trans = Trans(row["Data"], float(row["BTCInv"]), float(row["Kurs"]), row["Giełda"], i)
        trans_list.append(trans)


# trans = Trans("2022-01-01", 1, 10, 'kraken', 0)
# trans_list.append(trans)
# trans = Trans("2022-01-02", 1, 15, 'kraken', 1)
# trans_list.append(trans)
# trans = Trans("2022-01-03", -2, 20, 'bitbay', 2)
# trans_list.append(trans)

balanceFifo(trans_list)

print()
# print("Zysk: ", zyskTotal)
print("Bitbay sprzedaż zysk:", zyskBitbayTotal)
print("Zysk ze sprzedaży partii kupionej na Bitbay:", zyskBitbayKrakenTotal)
print()
# print("BTC: ", btcTotal)
print("Suma BTC sprzedaż Bitbay:", btcBitbayTotal)
print("Suma BTC partii kupionej na Bitbay:", btcBitbayKrakenTotal)

trans_list.clear()