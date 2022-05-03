import mysql.connector
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

def selectuser(member_id):
    mydb = mysql.connector.connect(
    host = "150.230.26.251",
    user = "test",
    password = "DTtestpw1!",
    database="DiscordTrader"
    )
    myc = mydb.cursor()
    sql = "select * from user where member_id = "+str(member_id)
    myc.execute(sql)
    return myc.fetchall()
    
def insertuser(member_id,balance):
    mydb = mysql.connector.connect(
    host = "150.230.26.251",
    user = "test",
    password = "DTtestpw1!",
    database="DiscordTrader"
    )
    myc = mydb.cursor()
    sql = "insert into user (member_id, balance) values (%s, %s)"
    val = (member_id,balance)
    myc.execute(sql,val)
    mydb.commit()
    return "Done!"

def updateuser(member_id,balance):
    mydb = mysql.connector.connect(
    host = "150.230.26.251",
    user = "test",
    password = "DTtestpw1!",
    database="DiscordTrader"
    )
    myc = mydb.cursor()
    sql = "UPDATE user SET balance = "+ str(balance) + "Where member_id =" + str(member_id);
    myc.execute(sql)
    mydb.commit()
    return "Done!"

def selectholdings(member_id,ticker):
    mydb = mysql.connector.connect(
    host = "150.230.26.251",
    user = "test",
    password = "DTtestpw1!",
    database="DiscordTrader"
    )
    myc = mydb.cursor()
    sql = "select * from holdings where member_id = "+str(member_id)+" and ticker =\'" + ticker +"\'"
    myc.execute(sql)
    return myc.fetchall()

def insertholdings(member_id,ticker,quantity,cost):
    mydb = mysql.connector.connect(
    host = "150.230.26.251",
    user = "test",
    password = "DTtestpw1!",
    database="DiscordTrader"
    )
    myc = mydb.cursor()
    sql = "insert into holdings (member_id, ticker, quantity, cost) values (%s, %s, %s, %s)"
    val = (member_id,ticker,quantity,cost)
    myc.execute(sql,val)
    mydb.commit()
    return "Done!"

def updateholdings(member_id,ticker,quantity,cost):
    mydb = mysql.connector.connect(
    host = "150.230.26.251",
    user = "test",
    password = "DTtestpw1!",
    database="DiscordTrader"
    )
    myc = mydb.cursor()
    sql = "UPDATE holdings SET quantity = %s , cost = %s where member_id = %s and ticker=\'%s\'"
    val = (quantity,cost,member_id,ticker)
    print(sql%val)
    myc.execute(sql%val)
    mydb.commit()
    return "Done!"

engine = create_engine('mysql+mysqlconnector://test:DTtestpw1!@150.230.26.251/DiscordTrader')
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = session.query_property()

if __name__=="__main__":
    mid = 156156158
    bal = 500.36
    ticker="AMZN"
    #insertuser(mid,bal)
    #updateuser(mid,260.35)
    #x=selectuser(156156158)
    #insertholdings(mid,ticker,50,100)
    #updateholdings(mid,ticker,80,102)
    #x=selectholdings(mid,ticker)
    
    print(engine)
    print(session)