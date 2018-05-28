from telegram.ext import BaseFilter

class StatFilter(BaseFilter):
    def filter(self, message):
        return 'статистика' in message.text.lower()
stat_filter=StatFilter()

class ResFilter(BaseFilter):
    def filter(self, message):
        return 'результаты' in message.text.lower()

class HomeFilter(BaseFilter):
    def filter(self, message):
        return 'домой' in message.text.lower()
class ChempFilter(BaseFilter):
    def filter(self, message):
        return 'чемпионат' in message.text.lower()

stat_filter=StatFilter()
res_filter =ResFilter()
home_filter=HomeFilter()
chemp_filter=ChempFilter()