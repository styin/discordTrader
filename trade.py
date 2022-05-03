from sql import session
from StockS import *
from Ept import *

#helpermethod
def getcommissionrate(quantity):
    if quantity <=20:
        return 2
    else:
        return quantity * 0.1
    
def savetransaction(member_id,server_id,stock,buy):
    crecordlist = session.query(Record).filter(Record.member_id==member_id, Record.server_id==server_id).order_by(Record.transactionRealTime).all()
    if len(crecordlist) > 100:
        session.delete(crecordlist[0])
    newrecord = Record(member_id,server_id,stock.ticker,stock.quantity,stock.price,stock.quote["currentTime"],buy)
    session.add(newrecord)
    session.commit()

initialbalance= 100000

def start(member_id, server_id):
    cuserlist = session.query(User).filter(User.member_id==member_id, User.server_id==server_id).all()
    if cuserlist == []:
        cuser = User(member_id,server_id,initialbalance)
        session.add(cuser)
        session.commit()
        return True
    else:
        return False

def getquote(ticker):
    cstock = Stock(1,1,ticker,1)
    return cstock.quote

def getbalance(member_id,server_id):
    cuserlist = session.query(User).filter(User.member_id==member_id, User.server_id==server_id).all()
    if cuserlist == []:
        raise MemberNotExistException("Member not exist")
    else:
        return cuserlist[0].balance

def buy(member_id,server_id,ticker,quantity):
    commissionrate = getcommissionrate(quantity)
    cuserlist = session.query(User).filter(User.member_id==member_id, User.server_id==server_id).all()
    if cuserlist == []:
        raise MemberNotExistException("Member not exist")
    else:
        cuser = cuserlist[0]
    cstock = Stock(member_id,server_id,ticker,quantity)
    if cuser.balance < cstock.price * cstock.quantity+commissionrate:
        raise InsufficientBalanceException("Insufficient balance")
    cstocklist = session.query(Stock).filter(Stock.member_id==member_id,Stock.server_id==server_id, Stock.ticker==ticker).all()
    if cstocklist == []:
        session.add(cstock)
        session.commit()
    else:
        holdstock = cstocklist[0]
        holdstock = holdstock + cstock
        session.query(Stock).filter(Stock.member_id==member_id,Stock.server_id==server_id, Stock.ticker==ticker).\
            update({"price":holdstock.price,"quantity":holdstock.quantity}, synchronize_session="fetch")
        session.commit()
    session.query(User).filter(User.member_id==member_id, User.server_id==server_id).\
        update({"balance":cuser.balance-cstock.price * cstock.quantity-commissionrate}, synchronize_session="fetch")
    session.commit()
    savetransaction(member_id,server_id,cstock,True)
    return cstock.quote

def sell(member_id,server_id,ticker,quantity):
    commissionrate = getcommissionrate(quantity)
    cuserlist = session.query(User).filter(User.member_id==member_id, User.server_id==server_id).all()
    if cuserlist == []:
        raise MemberNotExistException("Member not exist")
    else:
        cuser = cuserlist[0]
    cstock = Stock(member_id,server_id,ticker,quantity)
    cstocklist = session.query(Stock).filter(Stock.member_id==member_id,Stock.server_id==server_id, Stock.ticker==ticker).all()
    if cstocklist == []:
        raise InsufficientHoldingsException("Insufficient holdings")
    else:
        holdstock = cstocklist[0]
        holdstock = holdstock - cstock
        if holdstock.quantity < 0:
            raise InsufficientHoldingsException("Insufficient holdings")
        elif holdstock.quantity == 0:
            session.query(Stock).filter(Stock.member_id==member_id,Stock.server_id==server_id, Stock.ticker==ticker).\
                 delete(synchronize_session="fetch")
        else:
            session.query(Stock).filter(Stock.member_id==member_id,Stock.server_id==server_id, Stock.ticker==ticker).\
                update({"quantity":holdstock.quantity}, synchronize_session="fetch")
        session.commit()
    session.query(User).filter(User.member_id==member_id, User.server_id==server_id).\
        update({"balance":cuser.balance+cstock.price * cstock.quantity-commissionrate}, synchronize_session="fetch")
    session.commit()
    savetransaction(member_id,server_id,cstock,False)
    return cstock.quote

def holdings(member_id,server_id):
    cuserlist = session.query(User).filter(User.member_id==member_id, User.server_id==server_id).all()
    if cuserlist == []:
        raise MemberNotExistException("Member not exist")
    cstocklist = session.query(Stock).filter(Stock.member_id==member_id,Stock.server_id==server_id).all()
    if cstocklist == []:
        raise InsufficientHoldingsException("Insufficient holdings")
    else:
        quotelist=[]
        for s in cstocklist:
            cprice = Stock(member_id,server_id,s.ticker,s.quantity).price
            quotelist.append([s.ticker,s.quantity,s.price,cprice,(cprice-s.price)*s.quantity,(cprice-s.price)/s.price])
        return quotelist
   
def addmoney(member_id,server_id):
    
    cuserlist = session.query(User).filter(User.member_id==member_id, User.server_id==server_id).all()
    
    if cuserlist == []:
        raise MemberNotExistException("Member not exist")
    else:
        cuser = cuserlist[0]
    
    if getESTrealtimestamp() - cuser.lasttimeaddbalance > 72000:
        
        quotelist = holdings(member_id,server_id)
        
        holdingvalue = 0
        for q in quotelist:
            holdingvalue = q[1]*q[3] +holdingvalue
        
        value = cuser.balance + holdingvalue
        cuser.balance = cuser.balance + 1.00003**(-1*value)*10000
        cuser.lasttimeaddbalance = getESTrealtimestamp()
        session.commit()
        
        return {"Success":True,"Balance":cuser.balance,"amountAdded":1.00003**(-1*value)*10000}
    else:
        return {"Success":False,"timeLeft":72000-getESTrealtimestamp() + cuser.lasttimeaddbalance}

def getrecord(member_id,server_id):
    cuserlist = session.query(User).filter(User.member_id==member_id, User.server_id==server_id).all()
    if cuserlist == []:
        raise MemberNotExistException("Member not exist")
    crecordlist = session.query(Record).filter(Record.member_id==member_id, Record.server_id==server_id).order_by(Record.transactionRealTime).all()
    history = []
    for r in crecordlist():
        history.append(r.getinfo())
    return history

if __name__=="__main__":
    print("debug")

