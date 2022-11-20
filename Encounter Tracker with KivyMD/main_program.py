import time
import threading

from back_program_classes_lib.encounter import Encounter
from back_program_classes_lib.creature_classes import Player, Monster
from save_load import SaveLoad

from ui_classes_lib.encounters_screen import EncountersWindow
from ui_classes_lib.players_screen import PlayersWindow
from ui_classes_lib.monsters_screen import MonstersWindow
from ui_classes_lib.encounter_making_screen import EncounterMakingWindow
from ui_classes_lib.encounter_manager_screen import EncounterManagerWindow
from ui_classes_lib.loading_screen import LoadingWindow

from ui_classes_lib.custom_widgets import AddButton

from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock

from kivymd.uix.toolbar import MDTopAppBar

class MainScreen(MDScreen):
    pass

Builder.load_file("kv_lib/loading_screen.kv") 
Builder.load_file("kv_lib/encounters_screen.kv") 
Builder.load_file("kv_lib/players_screen.kv") 
Builder.load_file("kv_lib/monsters_screen.kv")
Builder.load_file("kv_lib/encounter_making_screen.kv")
Builder.load_file("kv_lib/encounter_manager_screen.kv") 


class EncounterTrackerApp(MDApp):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        #ACTUAL CREATURE LISTS: We use this to save and load processings and for accessing when instantiating a new encounter. 
        self.players_list = [] 
        self.monsters_list = []
        self.encounters_list = []

        self.top_app_bar = None
        self.add_button = None

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.primary_hue = "A700"

        self.secondary_color = "#311B92"

    def build(self):

        return Builder.load_file("kv_lib/root.kv") 

    def on_start(self):
        self.top_app_bar = self.root.ids["top_bar"] 
        self.scr_manager = self.root.ids["screen_manager"] 
        self.nav_drawer = self.root.ids["nav_drawer"] 
        self.nav_drawer.disabled = True
        
        Clock.schedule_once(self.load_app, 2)
        print("APP ON START")       

    def on_stop(self):
        
        SaveLoad.save_app_data(app = self)
        print("APP TERMINATED")

    def load_app(self, dt):
        """Loads and starts the app when on enter loading screen."""

        #Load Data
        SaveLoad.load_app_data(app = self)

        #Change Screen
        self.scr_manager.current = "encounters_screen"

        #Edit UI
        self.top_app_bar.title = "Encounters"
        self.top_app_bar.left_action_items = [['menu', lambda x: self.nav_drawer.set_state("open")]]
        self.enable_add_button()
        self.nav_drawer.disabled = False
        

    def update_top_app_bar_title(self, title):
        self.top_app_bar.title = title
    
    def change_top_app_items(self, add_menu = None):
        """Turns top bar's items to proper ones by screen.
        Encounter Making Screen: Left Arrow
        Encounter Manager Screen: Left Arrow, Add New Creature Button(right)"""

        self.top_app_bar.left_action_items = [["arrow-left", lambda x: self.__on_top_bar_back_butt__()]]
        
        if add_menu:
            self.top_app_bar.right_action_items = [["plus", lambda x: add_menu.open()]]
            add_menu.caller = self.top_app_bar.ids.right_actions

    def __on_top_bar_back_butt__(self):
        """Top bar's left Back(left arrow) button method. Turn screen to Encounters."""

        self.top_app_bar.left_action_items = [['menu', lambda x: self.nav_drawer.set_state("open")]]
        self.top_app_bar.right_action_items = []
        
        self.scr_manager.current = "encounters_screen"
        self.update_top_app_bar_title("Encounters")
        self.enable_add_button()
        
    def enable_add_button(self):
        """Adds "Add Button" """
        
        if self.add_button: return #We put this line so as not to be instantiated "ADD" button more than one.
        
        add_button = AddButton()
        self.root.add_widget(add_button)
        self.add_button = add_button

    def disable_add_button(self):
        """Removes "Add Button" """
        
        self.root.remove_widget(self.add_button)
        self.add_button = None 


if __name__ == "__main__":
    encounter_tracker_app = EncounterTrackerApp()
    encounter_tracker_app.run()

            # left_action_items:
            #     [['menu', lambda x: nav_drawer.set_state("open")]]

