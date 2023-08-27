from back_program_classes_lib.encounter import Encounter
from back_program_classes_lib.creature_classes import Player

from functools import partial
from kivy.metrics import dp

from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.screen import Screen, MDScreen
from kivy.properties import ObjectProperty

from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.behaviors import CommonElevationBehavior

from kivymd.uix.menu import MDDropdownMenu

class EncounterManagerWindow(Screen):
    
    app_reference = ObjectProperty(None)
    creatures_md_list = ObjectProperty(None)
    round_label = ObjectProperty(None)
    spinner = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)
        
        self.encounter = None
        self.current_index = 0 #Selected creature's index.
        self.creature_count = 0
        self.list_ref = None #Creature Items List reference for easy use.
        
        self.manage_dialog = None
        self.editing_c_item = None #We assign manage dialog's creature item.

        self.add_menu = None
        self.__instantiate_add_creature_menu__()
        self.add_dialog = None
        self.add_new_c_list = None #Add New Creature Dialog's Add Screens' MDList reference. 
    
    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        
        #Because of some variables comes from kv file. We only can assign these after that kv file is read.
        
        self.list_ref = self.creatures_md_list.children 
        self.__instantiate_manage_dialog__() 
        self.__instantiate_add_dialog__()

    def on_enter(self, *args):
        """Write documenetation string.""" 
        super().on_enter(*args)

        #Top App Bar Editing
        self.app_reference.change_top_app_items(add_menu = self.add_menu)
        self.app_reference.disable_add_button()
        self.display_encounter()
        self.spinner.active = False

    def on_leave(self, *args):
        super().on_leave(*args)

        self.spinner.active = True

    def start_encounter(self):
        """Starts encounter: Rolls initiatives and sorts creatures by initiatives."""
        
        self.encounter.sort_creatures()
        self.encounter.started = True
        #Selected first creature
        
    def display_encounter(self):
        """Initiates CreatureItems and edits screen based on encounter. """

        self.creatures_md_list.clear_widgets()
        
        #Initiate CreatureListItems
        for creature in self.encounter.initiative_order:
            new_creature_item = CreatureListItem(creature = creature)
            self.creatures_md_list.add_widget(new_creature_item)
            new_creature_item.bind(on_release = partial(self.open_manage_dialog, creature_item = new_creature_item))

        try:  #We trying it because, an encounter could be be started that have no creature in it.
            self.current_index = self.encounter.current_index 
            current_item = self.list_ref[-self.current_index - 1]
            current_item.select_deselect_item(True)
        
        except IndexError:
            pass

        self.round_label.text = f"ROUND {self.encounter.round}"
        self.creature_count = len(self.encounter.initiative_order)

    def on_next_button(self, remove_and_next: bool):
        """Passes turn to next creature. 
        "remove_and_next" indicates that is current selected creature removing.
        True meaning: method is called from dialog's remove button on_release (__manage_dialog_on_remove__())
        False meaning: method is called from Next button on_relase.
        """
        
        self.list_ref[-self.current_index - 1].select_deselect_item(False)

        self.current_index += 1

        try:
            self.list_ref[-self.current_index - 1].select_deselect_item(True)
        
        except IndexError: #If that was last of the items, we turn back to head and new round is going to be started.
            self.current_index = 0   
            
            self.list_ref[-self.current_index - 1].select_deselect_item(True)
            
            self.encounter.round += 1
            self.round_label.text = f"ROUND {self.encounter.round}"
        
        self.encounter.current_index = self.current_index

    def on_prev_button(self):
        if self.current_index == 0:
            return
            
        self.list_ref[-self.current_index - 1].select_deselect_item(False)
        self.current_index -= 1
        self.encounter.current_index = self.current_index
        self.list_ref[-self.current_index - 1].select_deselect_item(True)

    def open_manage_dialog(self, *args, **kwargs):
        """CreatureListItem's "on_release" method: Opens manage dialog and passes the clicked creature item's info and itself."""

        self.editing_c_item = kwargs["creature_item"]
        creature = self.editing_c_item.creature

        #Pasiing info here...
        self.manage_dialog.title = creature.name
        self.manage_dialog.content_cls.pass_creature_info(creature)
        
        self.manage_dialog.open() 
    
    def __instantiate_manage_dialog__(self): 

        self.manage_dialog = self.__get_base_dialog__(content = ManageDialogScreenManager())
            
        self.manage_dialog.buttons[0].bind(on_release = self.__manage_dialog_on_cancel__)  #cancel_btn
        self.manage_dialog.buttons[1].bind(on_release = self.__manage_dialog_on_remove__)
        self.manage_dialog.buttons[2].bind(on_release = self.__manage_dialog_on_apply__) #Apply button
        
    def __manage_dialog_on_cancel__(self, instance):
        self.manage_dialog.dismiss()

    def __manage_dialog_on_apply__(self,instance):
        """Apply changes and dismiss the manage dialog."""
        
        self.manage_dialog.content_cls.get_screen("edit_scr").apply_changes(self.editing_c_item.creature)

        dh_amount = self.manage_dialog.content_cls.get_screen("manage_scr").get_damage_or_heal()
        self.editing_c_item.creature.hit_point += dh_amount

        self.editing_c_item.update_creature_info()
        self.manage_dialog.dismiss()

    def __manage_dialog_on_remove__(self,instance):
        """Removes current creature item and dismiss dialog."""
        
        removing_index = self.creature_count - self.list_ref.index(self.editing_c_item) - 1

        if self.list_ref[-self.current_index - 1] == self.editing_c_item:
            #If we are removing current selected, we have to pass to next before removing.
            self.on_next_button(True)
        
        self.encounter.initiative_order.remove(self.editing_c_item.creature)
        self.creatures_md_list.remove_widget(self.editing_c_item)
        self.creature_count -= 1
        self.manage_dialog.dismiss()

        #Updating index 
        if removing_index < self.current_index: self.current_index -= 1
    
    
    def __instantiate_add_creature_menu__(self):
        """Right-Up corner "Add New Creature to Encounter Button"s menu. """

        menu_items = [
            {
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": lambda x = i : self.__on_add_menu_item__(x),
            } for i in ("Player", "Monster")
        ]
        self.add_menu = MDDropdownMenu(
            items = menu_items,
            width_mult = 2,
            max_height = dp(112),
            ver_growth = "down",
            hor_growth = "left"
        )
    
    def __instantiate_add_dialog__(self):

        self.add_dialog = self.__get_base_dialog__(content = AddDialogScreenManager())
        self.add_dialog.title = "Add New Creature"
        self.add_new_c_list = self.add_dialog.content_cls.get_screen("list_scr").creatures_md_list
        
        #Removing "REMOVE" button.
        self.add_dialog.ids.button_box.remove_widget(self.add_dialog.buttons[1]) 
        del self.add_dialog.buttons[1]

        self.add_dialog.buttons[1].text = "ADD"
        self.add_dialog.buttons[0].bind(on_release = self. __add_dialog_on_cancel__) #CANCEL button
        self.add_dialog.buttons[1].bind(on_release = self.__add_dialog_on_add__) #ADD button


    def __on_add_menu_item__(self, creature):
        """Opens Add New Creature to Encounter Menu:"""
        self.add_dialog.open()
        self.add_menu.dismiss()

        if creature == "Player": self.__add_creatures_to_add_dialog__(self.app_reference.players_list)
        elif creature == "Monster": self.__add_creatures_to_add_dialog__(self.app_reference.monsters_list)

    def __add_creatures_to_add_dialog__(self, creatures):
        """Add selected creature types to Add New Creature Dialog"""
        self.add_new_c_list.clear_widgets()
        
        for c in creatures:
            self.add_new_c_list.add_widget(
                AddDialogItem(creature = c)
                )
    
    def __add_dialog_on_cancel__(self, instance):
        
        self.add_dialog.content_cls.creature = None
        self.add_dialog.content_cls.current = "list_scr"
        self.add_dialog.dismiss()

    def __add_dialog_on_add__(self, instance):

        c_to_be_added = self.add_dialog.content_cls.creature
        
        if c_to_be_added: 
            self.__insert_new_creature__(c_to_be_added)

        self.__add_dialog_on_cancel__(instance = None)

    def __insert_new_creature__(self, creature):
        """Inserts new creature to MDList and encounter's initiative_order."""

        e_creatures = self.encounter.initiative_order
        insert_index = 0

        #First we find where we are going to insert new creature.
        for i in range(len(e_creatures)):
            if e_creatures[i].initiative >= creature.initiative:
                continue
            
            e_creatures.insert(i, creature)
            insert_index = i
            break
        
        #Adding a new CreatureListItem
        self.creatures_md_list.add_widget(CreatureListItem(creature = creature))
        
        for i in range(insert_index, len(e_creatures)):
            self.list_ref[-i - 1].update_item(e_creatures[i])


    def __get_base_dialog__(self, content = None): 

        cancel_btn = MDFlatButton(
                    text = "CANCEL",
                    theme_text_color = "Custom",
                    text_color = self.app_reference.theme_cls.primary_color,
                )
        remove_btn = MDFlatButton(
                    text = "REMOVE",
                    theme_text_color = "Custom",
                    text_color = self.app_reference.theme_cls.primary_color,
                )
        apply_btn = MDFlatButton(
                    text = "APPLY",
                    theme_text_color = "Custom",
                    text_color = self.app_reference.theme_cls.primary_color,
                )

        dialog = MDDialog(
                        title = "New Encounter",
                        content_cls = content,
                        type = "custom",   
                        buttons = [cancel_btn, remove_btn, apply_btn]
                        )
        
        return dialog


class CreatureListItem(TwoLineAvatarIconListItem, CommonElevationBehavior):
    
    def __init__(self, creature, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.creature = creature
        self.text = self.creature.name
        self.update_creature_info()

        self._default_height_ = self.height
        self.bg_color = (1, 1, 1, 0)
        self._default_bg_color = self.bg_color

    def update_creature_info(self):
        """Types creature's current info to second line"""
        
        self.secondary_text = f"Initiative:{self.creature.initiative}    HP:{self.creature.hit_point}    AC:{self.creature.armor_class}    PP:{self.creature.passive_perception}"
    
    def update_item(self, creature):
        """Updates this items every info include creature it self."""
       
        self.creature = creature
        self.text = creature.name
        self.update_creature_info()

    def select_deselect_item(self, selected):
        """Selects or deselects this item according to "selected" parameter.
        True: Select | False: Deselect"""

        if selected:
            self.elevation = 4 
            self.font_style = "H6"
            self.height = self.height * 1.2
            self.bg_color = (255/255, 160/255, 0/255, 1.0) 
        else:
            self.elevation =  0
            self.font_style = "Subtitle1"
            self.height = self._default_height_
            self.bg_color = self._default_bg_color


class ManageDialogScreenManager(ScreenManager):
    
    def pass_creature_info(self, creature):
        """Passes creature's info to dialog's screens."""

        self.get_screen("edit_scr").pass_info_to_fields(creature)
 
class DialogManageScreen(MDScreen):
    
    amount_input = ObjectProperty(None)
    damage_check = ObjectProperty(None)
    heal_check = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.amount  = 0
        self.heal_or_damage = False #We use this bool for check which check_box is selected. False = Damage True = Heal

    def get_damage_or_heal(self):
        """Returns damage or heal. Positive is heal, negative is damage."""
        
        if self.damage_check.active == True and self.heal_check.active == False: #Damage
            return -self.amount

        elif self.damage_check.active == False and self.heal_check.active == True: #Heal
            return self.amount

        return 0

    def on_focus_amount_input(self):
        """Text Fields on_focus() method."""

        if self.amount_input.focus: #Makes when focus in the text_field.
            print('focus-in', self.amount_input.hint_text)
            return  

        #Makes from here onwards if focus out the text field.
        
        if not self.__is_input_numeric__(self.amount_input.text):
            #If Text field have numeric filter, it have to check is input numerical: If input is not numerical
            self.amount_input.text = ""

            #!WARNING! Alttan kart çıkarttırarak aşağıdaki print mesajını uyarı olarak ver. Bunu ekle sonra bi ara
            print("WARNING: This field can take just numerical input!") 
            #If program enters this if statement consequently any Player is'nt going to be instantiated. 
            # So we can return method from this point.
            return    
        
        self.amount = int(self.amount_input.text)

    def __is_input_numeric__(self,text_input : str) -> bool:
        """Returns True if input is valid in terms of be a numerical input."""

        try:
            int(text_input)
            return True

        except ValueError:
            return False

class DialogEditScreen(MDScreen):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.creature_attrs_dict = {"hp":0, "ac":0, "pp":0}

    def pass_info_to_fields(self, creature):
        """Passes creature's attr.s to associated fields."""
        
        self.ids["hp_input_id"].text = str(creature.hit_point)
        self.ids["ac_input_id"].text = str(creature.armor_class)
        self.ids["pp_input_id"].text = str(creature.passive_perception)

        self.creature_attrs_dict["hp"] = creature.hit_point
        self.creature_attrs_dict["ac"] = creature.armor_class
        self.creature_attrs_dict["pp"] = creature.passive_perception
 
    def on_focus_text_input(self, text_field, key):
        """Text Fields on_focus() method."""

        if text_field.focus: #Makes when focus in the text_field.
            print('focus-in', text_field.hint_text)
            return  

        #Makes from here onwards if focus out the text field.
        
        if not self.__is_input_numeric__(text_field.text):
            text_field.text = str(self.creature_attrs_dict[key])
            print("WARNING: This field can take just numerical input!") 
            return    

        self.creature_attrs_dict[key] = int(text_field.text)

    def apply_changes(self, creature):
        """Applies changes that made on creature's stats at dialog's edit screen."""
        
        creature.hit_point = self.creature_attrs_dict["hp"]
        creature.armor_class = self.creature_attrs_dict["ac"]
        creature.passive_perception = self.creature_attrs_dict["pp"]

    def __is_input_numeric__(self,text_input : str) -> bool:
        """Returns True if input is valid in terms of be a numerical input."""

        try:
            int(text_input)
            return True

        except ValueError:
            return False

   
class AddDialogScreenManager(ScreenManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.creature = None

class AddDialogListScreen(MDScreen):
    
    creatures_md_list = ObjectProperty(None)

class AddDialogInitScreen(MDScreen):
    
    init_input = ObjectProperty(None)    

    def on_focus_init_input(self):
        """Text Fields on_focus() method."""

        if self.init_input.focus: #Makes when focus in the text_field.
            print('focus-in', self.init_input.hint_text)
            return  

        #Makes from here onwards if focus out the text field.
        
        if not self.__is_input_numeric__(self.init_input.text):
            self.init_input.text = ""
            print("WARNING: This field can take just numerical input!") 
            return    

        self.manager.creature.initiative = int(self.init_input.text)
    
    def __is_input_numeric__(self,text_input : str) -> bool:
        """Returns True if input is valid in terms of be a numerical input."""

        try:
            int(text_input)
            return True

        except ValueError:
            return False

class AddDialogItem(TwoLineAvatarIconListItem):
    def __init__(self, creature, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.creature = creature

        self.text = creature.name
        self.secondary_text = f"HP:{creature.hit_point} AC:{creature.armor_class} PP:{creature.passive_perception}" 
        
        self.list_scr_ref = None  

    def on_release(self):
        super().on_release()

        self.list_scr_ref = self.parent.list_scr_ref
        self.list_scr_ref.manager.current = "init_scr"
        self.list_scr_ref.manager.creature = self.creature

