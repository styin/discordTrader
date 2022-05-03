from yahoo_fin import stock_info as si
from sqlalchemy import *
from sqlalchemy.ext.declarative import *
from sql import Base
from sql import engine
from Ept import *
from datetime import datetime
import pytz

def getESTrealtimestamp():
    tz = pytz.timezone("EST")
    nowEST = datetime.now(tz)
    return int(datetime.timestamp(nowEST))

class Stock(Base):
    __tablename__ = 'holdings'
    member_id= Column('member_id', BIGINT, primary_key = True)
    server_id= Column('server_id', BIGINT, primary_key = True)
    ticker= Column('ticker', String, primary_key = True)
    quantity= Column('quantity', Integer)
    price = Column('price',Float)

    def __init__(self,member_id,server_id, ticker,quantity):
        quote = self.selectdata(ticker)
        self.member_id = member_id
        self.server_id = server_id
        self.ticker=quote["symbol"]
        self.quantity=quantity
        self.quote = quote
        self.price = self.quote["currentPrice"]

    
    def selectdata(self,ticker):
        quote =  self.checkticker(ticker)
        if quote.get("quoteType")!="EQUITY":
            raise TickerNotSupportedException('Ticker is not Supported')
        subkey = ["marketState","shortName","marketCap","postMarketChangePercent","postMarketTime","postMarketPrice"
                ,"postMarketChange","preMarketChangePercent","preMarketTime","preMarketPrice"
                ,"preMarketChange","regularMarketChange","regularMarketChangePercent","regularMarketTime"
                ,"regularMarketPrice","regularMarketDayHigh","regularMarketDayLow","regularMarketVolume"
                ,"regularMarketPreviousClose","regularMarketOpen","fiftyTwoWeekLow","fiftyTwoWeekHigh","displayName","symbol"]
        subquote = dict([(key, quote.get(key)) for key in subkey])
        if subquote["marketState"]=="PRE":
            subquote["currentPrice"]=subquote["preMarketPrice"]
            subquote["currentTime"]=subquote["preMarketTime"] 
            subquote["priceFrom"] = "pre"
        elif subquote["marketState"]=="REGULAR":
            subquote["currentPrice"]=subquote["regularMarketPrice"]
            subquote["currentTime"]=subquote["regularMarketTime"]
            subquote["priceFrom"] = "reg"
        else:
            subquote["currentPrice"]=subquote["postMarketPrice"]
            subquote["currentTime"]=subquote["postMarketTime"] 
            subquote["priceFrom"] = "post"
        if subquote["currentPrice"] == None:
            subquote["currentPrice"]=subquote["regularMarketPrice"]
            subquote["currentTime"]=subquote["regularMarketTime"] 
            subquote["priceFrom"] = "reg"
        return subquote

    def checkticker(self,ticker):
        try:
            quote = si.get_quote_data(ticker)
            return quote;
        except IndexError as e:
            raise TickerNotExistException('Ticker do not exist')
        except:
            raise ConnectionException('Connection failed')

    def __add__(self,o):
        self.price = (self.quantity*self.price+o.quantity*o.price)/(self.quantity+o.quantity)
        self.quantity = self.quantity+o.quantity
        return self

    def __sub__(self,o):
        self.quantity = self.quantity-o.quantity
        return self

    def __str__(self):
        return str(self.member_id)+self.ticker

    def __repr__(self):
        return str(self.member_id)+self.ticker

class User(Base):
    __tablename__ = 'user'
    member_id= Column('member_id', BIGINT, primary_key = True)
    server_id= Column('server_id', BIGINT, primary_key = True)
    balance= Column('balance', Float)
    membership = Column('membership', Integer)
    lasttimeaddbalance = Column('lasttimeaddbalance', Integer)

    def __init__(self,member_id,server_id,balance):
        self.member_id= member_id
        self.server_id=server_id
        self.balance= balance
        self.membership=1
        self.lasttimeaddbalance=getESTrealtimestamp()

    def __str__(self):
        return str(self.member_id)

    def __repr__(self):
        return str(self.member_id)

class Record(Base):
    __tablename__ = 'record'
    member_id= Column('member_id', BIGINT, primary_key = True)
    server_id= Column('server_id', BIGINT, primary_key = True)
    ticker= Column('ticker', String, primary_key = True)
    quantity= Column('quantity', Integer, primary_key = True)
    price = Column('price',Float)
    transactionCurrentTime = Column('transactionCurrentTime',Integer, primary_key = True)
    transactionRealTime = Column('transactionRealTime',Integer, primary_key = True)
    buy = Column('buy',Boolean, primary_key = True)

    def __init__(self,member_id,server_id,ticker,quantity,price,transactionCurrentTime,buy):
        self.member_id= member_id
        self.server_id=server_id
        self.ticker= ticker
        self.quantity= quantity
        self.price= price
        self.transactionCurrentTime= transactionCurrentTime
        self.transactionRealTime= getESTrealtimestamp()
        self.buy = buy

    def getinfo(self):
        return [self.ticker,self.quantity,self.price,self.quantity*self.price,self.transactionRealTime]
        