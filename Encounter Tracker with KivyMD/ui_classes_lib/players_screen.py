# import sys
 
# setting path
# sys.path.append('D:/YAZILIM/Esas Şimdi Başlıyoruz/DnD Encounter Manager/Encounter Tracker with KivyMD') 
##!!DİKKAT KENDİME ÖNEMLİ NOT: Bunu "os" ile yapman gerekecek muhtemelen. Çünkü şuanki durumda
# o directory çalışır ama başka cihazda durum farklı olacak. Dolayısıyla "os" yi kullanman lazım
# SONRA BAK DZÜEL BU DURUMU!!! 

from back_program_classes_lib.creature_classes import Player

from kivymd.uix.screen import Screen
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField

class PlayersWindow(Screen):
    
    player_md_list = ObjectProperty(None)
    app_reference = ObjectProperty(None)
    
    def __init__(self, **kw):
        super().__init__(**kw)
        
        self.players_list = None #Player() objects' list. Actual list in the App Instance

    def on_kv_post(self, base_widget):
        self.players_list = self.app_reference.players_list

    def load_items(self):
        """Used for loading players at programs start."""

        for p in self.players_list:
            p_item = PlayerListItem(self)
            self.player_md_list.add_widget(p_item)
            p_item.player = p
            p_item.pass_players_info_to_item()

    def __load_item__(self, player):
        """Assistant method: Add's a PlayerItem to MDList"""

        p_item = PlayerListItem(self)
        self.player_md_list.add_widget(p_item)
        p_item.player = player
        p_item.pass_players_info_to_item()

    def on_add_button(self):
        self.player_md_list.add_widget(PlayerListItem(self))


class PlayerListItem(MDBoxLayout):
    """New Player List Item. It is added when the "Add" button is pressed.
    Content direction: "kv_lib\root.kv\" """

    player = None
    
    def __init__(self, player_window_reference, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.players_window_reference = player_window_reference
        self.text_fields_list = list(filter(lambda widget: isinstance(widget, MDTextField), self.children))  #We filtered TextFields list

    def on_remove_button(self):
        """Removes this PlayerListItem from MDlist and this items refence Player() from player's list"""
        
        # s.remove('') if '' in s else None # Does nothing if '' not in s
        players_list = self.players_window_reference.players_list
        players_list.remove(self.player) if self.player in players_list else None #Removing from Screens list
        self.parent.remove_widget(self) #Removing from MDList 

    def on_focus_text_field(self, text_field, numeric_filter : bool):
        """Text Fields on_focus() method."""

        if text_field.focus: #Makes when focus in the text_field.
            print('focus-in', text_field.hint_text)
            return  

        #Makes from here onwards if focus out the text field.
        
        if numeric_filter and not self.__is_input_numeric__(text_field.text):
        #If Text field have numeric filter, it have to check is input numerical: If input is not numerical
            text_field.text = ""

            #!WARNING! Alttan kart çıkarttırarak aşağıdaki print mesajını uyarı olarak ver. Bunu ekle sonra bi ara
            print("WARNING: This field can take just numerical input!") 
            #If program enters this if statement consequently any Player is'nt going to be instantiated. 
            # So we can return method from this point.

            if not self.player: #If Hasn't already added a player before
                return

            #Else: it is added before now we have to remove from the actual Player list and self.player
            players_list = self.players_window_reference.players_list
            players_list.remove(self.player) 
            self.player = None
            return    
            
        if self.__check_inputs_validation__():
            name = self.ids["name_input_id"].text
            hp = int(self.ids["hp_input_id"].text)
            ac = int(self.ids["ac_input_id"].text)
            pp = int(self.ids["pp_input_id"].text)

            #If this item have already player, which means user not initiating "New" player,
            # but modifying the already exist. So we should update that.
            if self.player: 
                self.player.name = name 
                self.player.hit_point = hp
                self.player.armor_class = ac 
                self.player.passive_perception = pp 
                print("Player modified.")
            
            else:  #Initiating a new player
                self.player = Player(name = name, hit_point = hp, armor_class = ac, passive_perception = pp)
                self.players_window_reference.players_list.append(self.player)
                
                print("Player instantiated.")

        else:
            print("Please fill all fields to instantiate a new Player")

            if not self.player: #If Hasn't already added a player
                return

            #Else: it is added before now we have to remove from the actual Player list and self.player
            players_list = self.players_window_reference.players_list
            players_list.remove(self.player) 
            self.player = None

    def __check_inputs_validation__(self) -> bool:
        """Checks if text inputs are valid for instantiation of a Player() object."""
        
        for input_field in self.text_fields_list:
            if input_field.text.strip() == "":
                return False
        
        return True
    
    def __is_input_numeric__(self,text_input : str) -> bool:
        """Returns True if input is valid in terms of be a numerical input."""

        try:
            int(text_input)
            return True

        except ValueError:
            return False

    def pass_players_info_to_item(self):
        """Types self.player's info to associated text fields"""
        
        self.ids.name_input_id.text = self.player.name
        self.ids.hp_input_id.text = str(self.player.hit_point)
        self.ids.ac_input_id.text = str(self.player.armor_class)
        self.ids.pp_input_id.text = str(self.player.passive_perception)
