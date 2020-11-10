import sys
from PySide2 import QtCore, QtScxml


app = QtCore.QCoreApplication()
el = QtCore.QEventLoop()

sm = QtScxml.QScxmlStateMachine.fromFile('states.scxml')

sm.start()
el.processEvents()

print('SYS> こんにちは天気情報システムです')

uttdic ={'ask_place':'地名を言ってください',
        'ask_date':'日付を言ってください',
        'ask_type':"情報種別は"}


current_state = sm.activeStateNames()[0]
print("currnt_state=", current_state)

sysutt = uttdic[current_state]
print('SYS>', sysutt)

while True:
    text = input('> ')
    sm.submitEvent(text)
    el.processEvents()

    current_state = sm.activeStateNames()[0]
    print("currnt_state=", current_state)

    if current_state == 'tell_info':
        print('お天気をお伝えします')
        break
    else:
        sysutt = uttdic[current_state]
        print('SYS>', sysutt)
print('THank you')