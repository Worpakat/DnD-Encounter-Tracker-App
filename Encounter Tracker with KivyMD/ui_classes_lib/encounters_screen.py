from back_program_classes_lib.encounter import Encounter
from back_program_classes_lib.creature_classes import Player, Monster

from kivymd.uix.screen import Screen
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty

from kivy.uix.boxlayout import BoxLayout

from kivymd.uix.list import OneLineRightIconListItem, MDList
from kivymd.uix.list import IconRightWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

class EncountersWindow(Screen):
    app_reference = ObjectProperty(None)
    encounter_md_list = ObjectProperty(None)
    encounters_list = None

    dialog = None
    
    def on_kv_post(self, base_widget):
        self.encounters_list = self.app_reference.encounters_list

    def load_encounters(self):
        for e in self.encounters_list:
            self.__initiate_encounter_item__(encounter = e)

    def on_add_button(self):
        """This is called when on_press Add button. Adds a new associated list item."""
        
        if not self.dialog:
            cancel_btn = MDFlatButton(
                        text = "CANCEL",
                        theme_text_color = "Custom",
                        text_color = self.app_reference.theme_cls.primary_color,
                    )  
            add_btn = MDFlatButton(
                        text = "ADD",
                        theme_text_color = "Custom",
                        text_color = self.app_reference.theme_cls.primary_color,
                    )
            # Note: We initiate buttons because of, if we initiate them at the same time with iniating MDDialog
            # it gives an error because of button methods contains self.dialog and that time that field is None
            # Soo, it gives an error like: There is no property dismiss() of None Type object.(Buttons' methods contains dismiss())
             
            self.dialog = MDDialog(
                            title = "New Encounter",
                            content_cls = NewEncounterDialogContent(),
                            type = "custom",   #!!__WARNING__!!: If you want to content_cls work, make sure you do type = "custom"
                            buttons = [cancel_btn, add_btn])
            
            cancel_btn.bind(on_release = self.__add_dialog_on_cancel__)
            add_btn.bind(on_release = self.__add_dialog_on_add__)

        self.dialog.open()

    def __add_dialog_on_cancel__(self, instance):
        self.dialog.dismiss()
    
    def __add_dialog_on_add__(self, instance):
        """When pressed dialogs "ADD" button, initiates a new Encounter and EncounterListItem and adds
        them to app's list """
        encounter_name = self.dialog.content_cls.name_input.text
        new_encounter = Encounter(name = encounter_name)
        self.encounters_list.append(new_encounter)

        self.__initiate_encounter_item__(encounter = new_encounter)
        
        self.dialog.content_cls.name_input.text = "" #We make sure that is cleared.
        self.dialog.dismiss()

    def __initiate_encounter_item__(self, encounter):
        """Initiates a new encounter list item and adds it to MDList."""
        list_item = EncounterListItem(encounter = encounter, encounters_window_reference = self)
        self.encounter_md_list.add_widget(list_item)
        

class NewEncounterDialogContent(BoxLayout):

    name_input = ObjectProperty(None)

class EncounterListItem(OneLineRightIconListItem):
    
    def __init__(self, encounter, encounters_window_reference, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.encounter = encounter
        self.text = self.encounter.name
        self.encounters_window_reference = encounters_window_reference
        self.scr_manager_reference = self.encounters_window_reference.manager

        remove_button = IconRightWidget(icon = "trash-can-outline")
        self.add_widget(remove_button)
        remove_button.bind(on_release = self.on_remove_button)
    
    def on_remove_button(self, instance):
        self.encounters_window_reference.encounters_list.remove(self.encounter)
        self.parent.remove_widget(self)
    
    def on_press(self):
        """Passes encounter to EncounterMakingWindow() and opens it."""
        
        if self.encounter.started:
            encounter_manager_scr = self.scr_manager_reference.get_screen("encounter_manager_screen")
            encounter_manager_scr.encounter = self.encounter
            self.encounters_window_reference.app_reference.update_top_app_bar_title(self.encounter.name)
            self.scr_manager_reference.current = "encounter_manager_screen"
            # encounter_manager_scr.display_encounter()

        else:
            self.scr_manager_reference.current = "encounter_making_screen"
            self.scr_manager_reference.current_screen.load_encounter_and_addeds(encounter = self.encounter)
            self.encounters_window_reference.app_reference.update_top_app_bar_title(self.encounter.name)