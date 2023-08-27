from back_program_classes_lib.encounter import Encounter
from back_program_classes_lib.creature_classes import Player

from kivymd.uix.screen import MDScreen
from kivymd.uix.screen import Screen
from kivymd.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel

from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineRightIconListItem, MDList
from kivymd.uix.list import IRightBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox

class EncounterMakingWindow(Screen):
    
    added_monsters_list = ObjectProperty(None)
    app_reference = ObjectProperty(None)
    
    add_dialog = None
    start_dialog = None

    def __init__(self, **kw):
        super().__init__(**kw)
        
        self.encounter = None #Encounter that showed currently on the screen.

    def on_enter(self, *args):
        super().on_enter(*args)

        self.app_reference.change_top_app_items()
        
    def load_encounter_and_addeds(self, encounter):
        """Passes encounter this window(from EncountersWindow/Screen) 
        and regenerates added monsters if there is."""
        
        self.encounter = encounter

        self.added_monsters_list.clear_widgets()

        for added in encounter.added_monsters_list:
            monster_item = MonsterItem(encounter_making_window_ref = self, monster = added[0])
            self.added_monsters_list.add_widget(monster_item)
            monster_item.amount = added[1]
            monster_item.amount_input.text = str(added[1])

    def __new_custom_dialog__(self, content):
        """Initiates a new custom dialog with an parameter content, and returns it."""
        
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
            
        dialog = MDDialog(
                    title = "New Encounter",
                    type = "custom",
                    content_cls = content,
                    buttons = [cancel_btn, add_btn],
                    )

        return dialog
    
    def on_add_button(self):
        if not self.add_dialog:
            self.add_dialog = self.__new_custom_dialog__(DialogContent())
            self.add_dialog.content_cls.creatures_list = self.app_reference.monsters_list

            self.add_dialog.buttons[0].bind(on_release = self.__add_dialog_on_cancel__)
            self.add_dialog.buttons[1].bind(on_release = self.__add_dialog_on_add__)
            self.add_dialog.buttons[1].text = "ADD"

        self.add_dialog.content_cls.update_dialog_list()
        self.add_dialog.open()

        print("test:", self.encounter.added_monsters_list)

    def __add_dialog_on_cancel__(self, instance):
        self.add_dialog.dismiss()
    
    def __add_dialog_on_add__(self, instance):
        """When pressed add dialog's "ADD" button, adds selected monsters to encounter making screen"""

        selected_monsters = self.add_dialog.content_cls.selected_creatures
        for monster_obj in selected_monsters:
            self.__add_monster_item__(monster_obj = monster_obj)
        
        self.add_dialog.dismiss()

    def __add_monster_item__(self, monster_obj):
        """Initiates a monster list item with given monster obj parameters and adds it to screens MDlist"""
        self.added_monsters_list.add_widget(MonsterItem(encounter_making_window_ref = self, monster = monster_obj))
        self.encounter.added_monsters_list.append([monster_obj, 0])
    
    def on_start_encounter(self):
        """Initiates "start_dialog" that contains players. And user can select players are going to
        join encounter from that list."""

        if not self.start_dialog:
            self.start_dialog = self.__new_custom_dialog__(StartDialogContent())
            player_selection_content = self.start_dialog.content_cls.get_screen("adding_screen")
            player_selection_content.creatures_list = self.app_reference.players_list

            self.start_dialog.buttons[0].bind(on_release = self.__start_dialog_on_cancel__)
            self.start_dialog.buttons[1].bind(on_release = self.__start_dialog_on_next__)
            self.start_dialog.buttons[1].text = "NEXT"

        self.start_dialog.content_cls.update_dialog_list()
        self.start_dialog.open()

    def __start_dialog_on_next__(self, instance):
        """This is invoked when pressed on "NEXT" button in the start dialog's first screen.(DialogContent())
        Turns dialog's content to screen that displays creatures that will join the encounter, and edits it. """

        selected_players = self.start_dialog.content_cls.current_screen.selected_creatures
        #We transfer selected_players from "adding_screen".
        creatures_list_screen = self.start_dialog.content_cls.get_screen("creatures_list_screen")

        for player in selected_players:
            creatures_list_screen.players_list.add_widget(PlayerInitiativeItem(player = player))

        for monster_n_amount in self.encounter.added_monsters_list:
            monster_label = MDLabel(
                                text = f"{monster_n_amount[1]} {monster_n_amount[0].name}",
                                adaptive_height = True
            )
            creatures_list_screen.monsters_list.add_widget(monster_label)
                                                    
        self.start_dialog.content_cls.current = "creatures_list_screen"
            
        self.start_dialog.buttons[1].text = "START"
        self.start_dialog.buttons[1].unbind(on_release = self.__start_dialog_on_next__)
        self.start_dialog.buttons[1].bind(on_release = self.__start_dialog_on_start__)

    def __start_dialog_on_start__(self, instance):
        """Start dialog "START" buttons method. Initiates monsters and players. Puts them inside encounter obj,
        turns screen to EncounterManagerWindow and transfer encounter to it."""
        
        self.start_dialog.dismiss()

        #Change screen to EncounterManagerWindow and transfer Encounter() object to it.
        self.encounter.clone_creatures(players = self.start_dialog.content_cls.get_screen("adding_screen").selected_creatures)
        #Since self.__set_default_start_dialog__() invoked current_screen is "adding_screen"
        
        e_manager_scr = self.manager.get_screen("encounter_manager_screen")
        e_manager_scr.encounter = self.encounter 
        e_manager_scr.start_encounter() 
        self.manager.current = "encounter_manager_screen"
        #Annndd.. we completed encounter making process and transfered it to encounter manager screen.
         
        self.__set_default_start_dialog__() 

    def __start_dialog_on_cancel__(self, instance):
        
        self.start_dialog.dismiss()
        self.__set_default_start_dialog__()
    
    def __set_default_start_dialog__(self):
        """Set start dialog's settings to default. This is an assistant method."""

        #If dialog screen is not changed to creatures_list_screen, no need to set settings to default because of already they are.
        if not self.start_dialog.content_cls.current == "creatures_list_screen":
            return   

        self.start_dialog.content_cls.current_screen.set_screen_to_default() #We set creature list screens to default.
        self.start_dialog.content_cls.current = "adding_screen"
        
        for player in self.start_dialog.content_cls.current_screen.selected_creatures: #Setting player initiatives to 0.
            player.initiative = 0

        self.start_dialog.buttons[1].text = "NEXT"
        self.start_dialog.buttons[1].unbind(on_release = self.__start_dialog_on_start__)
        self.start_dialog.buttons[1].bind(on_release = self.__start_dialog_on_next__)

        # print("binded methods",self.start_dialog.buttons[1].get_property_observers('on_release'))

class MonsterItem(MDBoxLayout):
    
    monster_name: ObjectProperty(None) #label
    amount_input: ObjectProperty(None)

    def __init__(self, encounter_making_window_ref, monster, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.encounter_making_window_ref = encounter_making_window_ref
        self.monster = monster
        self.monster_name.text = self.monster.name
        self.amount = 0
        self.encounter_added_monsters = self.encounter_making_window_ref.encounter.added_monsters_list

    def on_focus_amount_field(self):
        if self.amount_input.focus: #Makes when focus in the text_field.
            print('focus-in amount text field') 
            return

        if not self.__is_input_numeric__(self.amount_input.text): #if amount input is not numerical return.
            self.amount_input.text = ""
            self.amount = 0
            self.__get_items_encounter_data__()[1] = self.amount
            #!WARNING! Alttan kart çıkarttırarak aşağıdaki print mesajını uyarı olarak ver. Bunu ekle sonra bi ara
            print("WARNING: This field can take just numerical input!") 
            
            return

        #If code can pass here, it means input is valid.
        self.amount = int(self.amount_input.text)
        self.__get_items_encounter_data__()[1] = self.amount 

    def on_remove_button(self):
        item_index = self.parent.children.index(self)
        del self.encounter_added_monsters[-item_index - 1]
        self.parent.remove_widget(self)

    def __get_items_encounter_data__(self):
        """Returns item's data form in shape of "[Monster(), amount: int]" from encounter. This is an assisstant method."""
        item_index = self.parent.children.index(self)
        #We take from reverse because widget children list is reverse. "add_widget()" adds widgets to children list's head.
        return self.encounter_added_monsters[-item_index - 1] 

    def __is_input_numeric__(self,text_input : str) -> bool:
        """Returns True if input is valid in terms of be a numerical input."""

        try:
            int(text_input)
            return True

        except ValueError:
            return False

#____Common_Dialog_Classes_________

class DialogContent(MDScreen):  
    """add_dialog's content_cls, start_dialog's adding_screen """

    app_reference = ObjectProperty(None)
    dialog_list = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.creatures_list = None
        self.selected_creatures = []  #This list is showed at encounter making screen.
    
    def __clear_lists__(self):
        """Removes all dialog items and clears selected_monsters list"""
        self.dialog_list.clear_widgets()
        self.selected_creatures.clear()

    def update_dialog_list(self):
        """Updates encounter making screens monster adding dialog list."""
        
        #!!!KENDİME NOT DİKKAT: Bu updateleme olayının algoritmik ve verimlilik olarak daha iyi yolunu bulmaya çalış.
        #Big(O) ya göre değerlendir bulduğun yöntemleri ve en verimli olanı kullan BUNA BAK SONRA AYARLA !!!

        #First we need to clear dialog items and monsters_list.
        self.__clear_lists__()
        
        #add monsters from app's monsters_list
        for creature in self.creatures_list:
            dialog_item = DialogItem(
                                text = creature.name,
                                secondary_text = f"HP:{creature.hit_point} AC:{creature.armor_class} PP:{creature.passive_perception}" 
                                )
            dialog_item.creature = creature
            self.dialog_list.add_widget(dialog_item)
            dialog_item.dialog_content_ref = self #This reference provide access to this content.

            if isinstance(creature, Player):
                continue
            #if creature is also a Monster, it's init. modifier is be typed to DialogItem
            dialog_item.secondary_text += f" Init:{creature.initiative_modifier}"

class DialogItem(TwoLineRightIconListItem):
    
    check_box = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.creature = None
        self.dialog_content_ref = None

    def on_release(self):
        """If item pressed it will pretend check box activated. For usage simplicity."""
        self.check_box.active = not self.check_box.active

class RightCheckbox(IRightBodyTouch, MDCheckbox):
    '''Custom right container.'''
    
    def on_active(self, *args) -> None:
        super().on_active(*args)
        
        if self.active: #if it's selected, adds monster to contents selected_monsters
            self.root_reference.dialog_content_ref.selected_creatures.append(self.root_reference.creature)
        else:
            self.root_reference.dialog_content_ref.selected_creatures.remove(self.root_reference.creature)


#____________________________________________________#
#______Start Encounter Dialog Classes_______________#

class StartDialogContent(ScreenManager):
    
    def update_dialog_list(self):
        """Updates players selection screen/content"""
        self.get_screen("adding_screen").update_dialog_list()
    
class CreaturesListScreen(MDScreen):
    monsters_list = ObjectProperty(None)
    players_list = ObjectProperty(None)

    def set_screen_to_default(self):
        """Set screens to default which means clears list."""
        self.players_list.clear_widgets()
        self.monsters_list.clear_widgets()

class PlayerInitiativeItem(MDBoxLayout):
    
    player_name = ObjectProperty(None)
    initiative_input = ObjectProperty(None)

    def __init__(self, player, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.player = player
        self.player_name.text = self.player.name

    def on_focus_initiative_input(self):
        if self.initiative_input.focus: #Makes when focus in the text_field.
            print('focus-in initiative text field') 
            return

        if not self.__is_input_numeric__(self.initiative_input.text): #if amount input is not numerical return.
            self.initiative_input.text = ""
            self.player.initiative = 0
            #!WARNING! Alttan kart çıkarttırarak aşağıdaki print mesajını uyarı olarak ver. Bunu ekle sonra bi ara
            print("WARNING: This field can take just numerical input!") 
            return

        #If code can pass here, it means input is valid.
        self.player.initiative = int(self.initiative_input.text)

    def __is_input_numeric__(self,text_input : str) -> bool:
        """Returns True if input is valid in terms of be a numerical input."""

        try:
            int(text_input)
            return True

        except ValueError:
            return False
