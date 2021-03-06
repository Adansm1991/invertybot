from settings import BOT_TOKEN
import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
import pandas as pd
import matplotlib.pyplot as plt
from yahoo_finance import YahooFinance
import os

yf = YahooFinance()

updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hola! Mandame el excel \"Portfolio.xslx\" y generaré una imagen de tu cartera (de momento nada más)")

def generate_picture(df):
    df.index = df.Producto
    img = df.plot.pie(y='Valor en EUR')
    return img.figure

def generate_circle_plot(df, path):
    # create data
    names = df['Ticker']
    size = df['Valor en EUR']

    # Create a circle for the center of the plot
    my_circle = plt.Circle((0, 0), 0.7, color='white')

    plt.pie(size, labels=names)
    p = plt.gcf()
    p.gca().add_artist(my_circle)
    # plt.show()
    p.savefig(path)
    return p


def get_file(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Archivo recibido, generando imagen...")
    excel_file = update.message.document.get_file().download()
    df = pd.read_excel(excel_file)
    df['Ticker'] = df['Symbol/ISIN'].apply(yf.get_ticker)

    generate_circle_plot(df, './figure.png')

    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('./figure.png', 'rb'))

    os.remove(excel_file)
    os.remove('./figure.png')


from telegram.ext import MessageHandler, Filters
excel_handler = MessageHandler(Filters.document, get_file)

dispatcher.add_handler(excel_handler)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()

