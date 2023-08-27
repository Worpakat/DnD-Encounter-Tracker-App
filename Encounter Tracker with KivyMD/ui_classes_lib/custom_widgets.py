from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import ObjectProperty
    
class AddButton(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 

    def on_press_button(self):
        
        screen_manager_reference = self.parent.ids["screen_manager"]
        current_scr = screen_manager_reference.current_screen
        current_scr.on_add_button()