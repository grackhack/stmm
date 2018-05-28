import telegram
class BotKeyboard:
    keyboard={}
    def SetKb(*args,resize_keyboard=True,one_time_keyboard=False,selective=False):
        row=[]
        keyboard=[]
        for item in args:
            if item=='|':
                if row!=[]: keyboard.append(row)
                row=[]
            else:
                row.append(telegram.KeyboardButton(item)) #build keyboard row
        if row!=[]: keyboard.append(row)

        keyboard=telegram.ReplyKeyboardMarkup(keyboard,resize_keyboard,one_time_keyboard,selective)

        if __name__ == '__main__': #debug
            print(args,keyboard,sep='===')
        return keyboard







if __name__=='__main__':
    assert BotKeyboard.SetKb('')
    assert BotKeyboard.SetKb('|','|','|','|','s','|','|','d','|','|')
    assert BotKeyboard.SetKb('|', 's',  'd', '|', '|')