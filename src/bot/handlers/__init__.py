from aiogram import Dispatcher

from .trial_week_handlers.zero_day_handlers import register_handlers_zero_day
from .trial_week_handlers.first_day_handlers import register_handlers_first_day
from .trial_week_handlers.second_day_handlers import register_handlers_second_day
from .trial_week_handlers.third_day_handlers import register_handlers_third_day
from .trial_week_handlers.fourth_day_handlers import register_handlers_fourth_day
from .trial_week_handlers.fifth_day_handlers import register_handlers_fifth_day

from .main_menu_handlers.my_habbits_handlers import register_my_habbits_handlers

def setup_dispatcher_handlers(dp: Dispatcher):
    register_handlers_zero_day(dp)
    register_handlers_first_day(dp)
    register_handlers_second_day(dp)
    register_handlers_third_day(dp)
    register_handlers_fourth_day(dp)
    register_handlers_fifth_day(dp)

    register_my_habbits_handlers(dp)
