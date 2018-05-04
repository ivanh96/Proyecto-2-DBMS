import os
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
            text = input("> There is no databases yet. Please, enter the name of a new database: ")
            try:
                parse("CREATE DATABASE " + text)
                current_db = text
            except:
                print("Enter a valid name!")

        elif current_db == "" and len(db_list) > 0:
            print("Please, select one of these databases:")
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


                elif text[0:13] == "CREATE TABLE " or text[0:11] == "DROP TABLE " or text == "SHOW TABLES" or text[0:12] == "ALTER TABLE ":
                    try:
                        os.chdir(current_db)
                        parse(text);
                        tableNumber = len(os.listdir())
                        os.chdir("..")
                        metaData = json.load(open('meta-data.json'))
                        databases = metaData["databases"]
                        for i in databases:
                            if i["name"] == current_db:
                                i["numberOfTables"] = tableNumber
                        with open("meta-data.json", 'w') as f:
                            json.dump(metaData,f)


                    except ParserException as e:
                        print("Got a parser exception:", e.value)
                        os.chdir("..")


                else:
                    parse(text);


                    print("Valid, but the function is not supported")

            except ParserException as e:
                print("Got a parser exception:", e.value)

            except EOFError as e:
                print("Bye")
                sys.exit()

            except Exception as e:
                print("Got exception: ", e)

if __name__ == '__main__':
    main(sys.argv)
