from back_program_classes_lib.creature_classes import Monster

from kivymd.uix.screen import Screen
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField

class MonstersWindow(Screen):

    monster_md_list = ObjectProperty(None)
    app_reference = ObjectProperty(None)
    monsters_list = None #Monster() objects' list. Actual list in the App Instance
    
    def on_kv_post(self, base_widget):
        self.monsters_list = self.app_reference.monsters_list 
        #NOTE TO MYSELF: Biz  bu listeyi niye burda referanslıyoruz: Çünkü eğer direk atamaya çalışırsak hata alıyoruz.
        # NEDEN: Çünkü app_reference kv fileda atanıyor. Ve önce bu obje pythonda initialize ediliyor,
        # sonra kv file kısmını okumaya başlıyor. Ee sonuç olarak app_reference boş bir ObjectProperty oluyor 
        # o sırada ve app i referanslamadığından hala monster_list diye bir attribute u bulunmuyor.
        # Dolayısıyla kv file yüklenmesi bittikten sonra yapılmalı

    def load_items(self):
        """Used for loading monsters at programs start."""

        for m in self.monsters_list:
            m_item = MonsterListItem(self)
            self.monster_md_list.add_widget(m_item)
            m_item.monster = m
            m_item.pass_monsters_info_to_item()

    def on_add_button(self):
        self.monster_md_list.add_widget(MonsterListItem(self))


class MonsterListItem(MDBoxLayout):
    """New MonsterListItem. It is added when the "Add" button is pressed.
    Add Buttons content direction: "kv_lib\root.kv\" and "ui_classes_lib\custom_widgets.py\" """
    
    monster = None
    
    def __init__(self, monsters_window_reference, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.monsters_window_reference = monsters_window_reference
        self.text_fields_list = list(filter(lambda widget: isinstance(widget, MDTextField), self.children))  #We filtered TextFields list

    def on_remove_button(self):
        """Removes this MonsterListItem from MDlist and this items refence Monster() from monster's list"""
        
        # s.remove('') if '' in s else None # Does nothing if '' not in s
        monsters_list = self.monsters_window_reference.monsters_list
        monsters_list.remove(self.monster) if self.monster in monsters_list else None #Removing from Screens list
        self.parent.remove_widget(self) #Removing from MDList 
        
    def on_focus_text_field(self, text_field, numeric_filter):
        """Text Fields on_focus() method."""

        if text_field.focus: #Makes when focus in the text_field.
            print('focus-in', text_field.hint_text) 
            return 

        #Makes from here onwards if user focus out the text field.
        
        if numeric_filter and not self.__is_input_numeric__(text_field.text):
        #If Text field have numeric filter, it have to check is input numerical: If input is not numerical
            text_field.text = ""

            #!WARNING! Alttan kart çıkarttırarak aşağıdaki print mesajını uyarı olarak ver. Bunu ekle sonra bi ara
            print("WARNING: This field can take just numerical input!") 
            
            #If program enters this if statement consequently any Player isn't going to be instantiated. 
            # So we can return method from this point.
            
            if not self.monster: #If hasn't added a monster before 
                return

            #Else: it is added before now we have to remove from the actual Monster list and self.monster
            monsters_list = self.monsters_window_reference.monsters_list
            monsters_list.remove(self.monster) 
            self.monster = None
            return    

        if self.__check_inputs_validation__():
            name = self.ids["name_input_id"].text
            hp = int(self.ids["hp_input_id"].text)
            ac = int(self.ids["ac_input_id"].text)
            pp = int(self.ids["pp_input_id"].text)
            init_modifier = int(self.ids["init_modifier_input_id"].text)

            #If this item have already monster, which means user not initiating "New" monster,
            # but modifying the already exist. So we should update that.
            if self.monster: 
                self.monster.name = name 
                self.monster.hit_point = hp
                self.monster.armor_class = ac 
                self.monster.passive_perception = pp 
                self.monster.initiative_modifier = init_modifier
                print("Monster modified.")

            else:
                self.monster = Monster(
                                    name = name, 
                                    hit_point = hp,
                                    armor_class = ac, 
                                    passive_perception = pp, 
                                    initiative_modifier = init_modifier
                                    )
                self.monsters_window_reference.monsters_list.append(self.monster)

                print("Monster instantiated.")

        else:
            print("Please fill all fields to instantiate a new Monster")

            if not self.monster: #If Hasn't added a monster 
                return

            #Else: it is added before now we have to remove from the actual Monster list and self.monster
            monsters_list = self.monsters_window_reference.monsters_list
            monsters_list.remove(self.monster) 
            self.monster = None

    def __check_inputs_validation__(self) -> bool:
        """Checks if text inputs are filled for instantiation of a Player() object."""
        
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

    def pass_monsters_info_to_item(self):
        """Types self.monster's info to associated text fields"""
        
        self.ids.name_input_id.text = self.monster.name
        self.ids.hp_input_id.text = str(self.monster.hit_point)
        self.ids.ac_input_id.text = str(self.monster.armor_class)
        self.ids.pp_input_id.text = str(self.monster.passive_perception)
        self.ids.init_modifier_input_id.text = str(self.monster.initiative_modifier)