import re

MSC_BASE_LINK = 'https://www.myscore.ru'
MSC_MAIN_TABLE = 'table-main'
MSC_SOCCER_TABLE = 'soccer'
MSC_LEAGUE_TABLE = 'league'
MSC_EVENT_TABLE = 'event_game'
MSC_SCORE_REGEX = re.compile(r'([\d]).?-.?([\d])')
MSC_TIMER_REGEX = re.compile(r'[\d]+')
MSC_MATCH_LINK = 'match'
MSC_MATCH_SUMMARY_LINK = '#match-summary'

MSC_LIVE_ODDS_TABLE = 'default-live-odds'
MSC_PRE_ODDS_TABLE = 'default-odds'
MSC_FLASH_FACTS_TABLE = 'flash-facts'
MSC_MATCH_SUMMARY_CLASS = 'detail-header-wrapper'
MSC_ODDS = 'odds'

MSC_TIMER_NEW_EVENT = 10

WORK_TIME_HOUR = 18