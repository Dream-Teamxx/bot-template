from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format

from tgbot.states.main_menu import MainMenu

main_menu_dialog = Dialog(
    Window(
        Format('Привет!'),
        state=MainMenu.main_menu
    )

)
