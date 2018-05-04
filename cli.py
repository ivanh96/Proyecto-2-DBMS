import sys
from antlr4 import *
from sqlLexer import sqlLexer
from sqlParser import sqlParser
from sqlListener import sqlListener
from antlr4.error.ErrorListener import ErrorListener
import simplejson as json

class ParserException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ParserExceptionErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise ParserException("line " + str(line) + ":" + str(column) + " " + msg)

def db_select(current_db, db_list,text):    
    for i in db_list:
        if text == i:
            return text
        else:
            print("Seleccione una base de datos existente")

def parse(text):
    lexer = sqlLexer(InputStream(text))
    lexer.removeErrorListeners()
    lexer.addErrorListener(ParserExceptionErrorListener())

    stream = CommonTokenStream(lexer)

    parser = sqlParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(ParserExceptionErrorListener())

    # Este es el nombre de la produccion inicial de la gramatica definida en sql.g4
    tree = parser.parse()

    listener = sqlListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)




'''
Uso: python cli.py

Las construcciones validas para esta gramatica son todas aquellas
'''

def main(argv):
    current_db = ""
    while True:
        db_list = []
        metaData = json.load(open('meta-data.json'))
        databases = metaData["databases"]
        for db in databases:
            db_list.append(db["name"])

        if current_db == "" and len(db_list) == 0:
            text = input("> Aun no existen bases de datos. Por favor, ingrese el nombre de una nueva: ")
            try:
                parse("CREATE DATABASE " + text)
                current_db = text
            except:
                print("¡Ingrese un nombre valido!")

        elif current_db == "" and len(db_list) > 0:
            print("Por favor, seleccione una de las siguientes bases de datos:")
            for i in db_list:
                print(i)
            text = input("> ")
            current_db = db_select(current_db,db_list,text)


        else:
            try:
                text = input("> ")

                if (text == 'exit'):
                    sys.exit()

                elif text[0:12] == "USE DATABASE " and ' ' in text[12:] == False:
                    current_db = db_select(current_db, db_list,text[12:])

                else:
                    parse(text);


                    print("Valid")

            except ParserException as e:
                print("Got a parser exception:", e.value)

            except EOFError as e:
                print("Bye")
                sys.exit()

            except Exception as e:
                print("Got exception: ", e)

if __name__ == '__main__':
    main(sys.argv)
