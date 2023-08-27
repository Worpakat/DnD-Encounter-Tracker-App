import json
import copy
import time
from threading import Thread


from back_program_classes_lib.creature_classes import Creature, Player, Monster
from back_program_classes_lib.encounter import Encounter


SAVE_FILE = "app_save_file.json"

class SaveLoad:
    """This class contains methods to saving and loading process
    of application's data. Should not be instantiated any instance of this class.
    Should be used with class name."""

    @classmethod
    def save_app_data(cls, app):
        """Saves all data(encounters, players, monsters) to a JSON file."""
        
        save_thread = Thread(target = cls.__save_data__, args = (app, ))
        save_thread.start()        

    @classmethod
    def __save_data__(cls, app):
        """Method of thread that saving app's data."""
        current_time = time.time()

        players_list = app.players_list
        monsters_list = app.monsters_list
        players_dicts = cls.__get_creatures_list_dicts__(players_list)
        monsters_dicts = cls.__get_creatures_list_dicts__(monsters_list)
        
        encounters_list = app.encounters_list
        encounters_dicts = cls.__get_encounters_list_dicts__(encounters_list) 

        save_dict = {"players": players_dicts, "monsters": monsters_dicts, "encounters": encounters_dicts}

        with open(SAVE_FILE, "w") as save_file:
            json.dump(save_dict, save_file, indent = 4)

        print("DATA SAVED IN:",time.time() - current_time,"\nSAVE COMPLETED, TIME:", time.time())

    @classmethod
    def __get_creatures_list_dicts__(cls, creature_list):
        """Returns a list contains creatures dict. form"""      
        
        c_dict_list = []
        for c in creature_list:
            c_dict_list.append(c.get_dict_form())
        
        return c_dict_list

    #______________________________________________
    #ENCOUNTER CONVERTER METHODS TO DICT FORM
    # Creature's converter method to dict at own class.
    # We put encounter's methods here because need to use "cls.__get_creatures_list_dicts__(cls, creature_list)"
    # We could access this method from there too, but I think this is more proper. 
    # Because I want this class to be isolated as possible.
    @classmethod
    def __get_encounters_list_dicts__(cls, encounters_list):
        """Returns a list contains encounters' dict. forms"""

        e_dicts_list = []

        for e in encounters_list:
            e_dicts_list.append(cls.__get_encounters_dict_form__(encounter = e))
            
        return e_dicts_list
    @classmethod  
    def __get_encounters_dict_form__(cls, encounter):
        """Returns an encounter's dict form."""
        
        dict_form = {"name": encounter.name, "started": encounter.started}
        
        if encounter.started:
            dict_form["current_index"] = encounter.current_index
            dict_form["round"] = encounter.round 
            
            players_dicts = cls. __get_creatures_list_dicts__(encounter.players)
            monsters_dicts = cls. __get_creatures_list_dicts__(encounter.monsters)
            dict_form["players"] = players_dicts
            dict_form["monsters"] = monsters_dicts
        
        else:
            added_dict_forms = copy.copy(encounter.added_monsters_list)

            for added in added_dict_forms:
                added[0] = added[0].get_dict_form()
            
            dict_form["added_monsters_list"] = added_dict_forms

        return dict_form
    #______________________________________________

    @classmethod
    def load_app_data(cls, app):
        current_time = time.time()
        
        with open(SAVE_FILE, "r") as save_file:
            save_dict = json.load(save_file)
        

        #LOADING PLAYERS
        players_dicts = save_dict["players"]
        players_list = app.players_list
        players_scr = app.scr_manager.get_screen("players_screen")
        cls.__load_creature_items__(creatures_dicts = players_dicts, creatures_list = players_list, screen = players_scr)
        

        #LOADING MONSTERS
        monsters_dicts = save_dict["monsters"]
        monsters_list = app.monsters_list
        monsters_scr = app.scr_manager.get_screen("monsters_screen")
        cls.__load_creature_items__(creatures_dicts = monsters_dicts, creatures_list = monsters_list, screen = monsters_scr)

        #LOADING ENCOUNTERS
        encounters_dicts = save_dict["encounters"]
        encounters_list = app.encounters_list
        encounters_scr = app.scr_manager.get_screen("encounters_screen")
        cls.__load_encounters__(encounters_dicts = encounters_dicts, encounters_list = encounters_list, screen = encounters_scr)
        
        print("ALL DATA LOADED IN:",time.time() - current_time)

    @classmethod
    def __load_creature_items__(cls, creatures_list,  creatures_dicts, screen):

        cls.__convert_creatures__to_obj__(creatures_list = creatures_list, creatures_dicts = creatures_dicts)
        
        screen.load_items()

    @classmethod
    def __convert_creatures__to_obj__(cls, creatures_list,  creatures_dicts):
        """Assistant method: Converts creatures dict to obj form and appends "creatures_list".
        ATTENTION: This is a spesific list. In this case one of app object's creatures lists.
        (players_list || monsters_list)"""
        
        for dict_form in creatures_dicts:
            creature = Creature.get_object_form(dict_form = dict_form)
            creatures_list.append(creature)

    @classmethod
    def __load_encounters__(cls, encounters_list,  encounters_dicts, screen):
        
        for e_dict_form in encounters_dicts:
            encounter = cls.__get_encounters_obj_form__(e_dict_form)
            encounters_list.append(encounter)

        screen.load_encounters()
    
    @classmethod
    def __get_encounters_obj_form__(cls, dict_form):
        
        encounter = Encounter(name = dict_form["name"])
        encounter.started = dict_form["started"]

        if encounter.started:
            encounter.current_index = dict_form["current_index"]
            encounter.round = dict_form["round"] 
                
            players_dicts = dict_form["players"] 
            monsters_dicts = dict_form["monsters"]
            cls.__convert_creatures__to_obj__(creatures_list = encounter.players, creatures_dicts = players_dicts)
            cls.__convert_creatures__to_obj__(creatures_list = encounter.monsters, creatures_dicts = monsters_dicts)

            encounter.initiative_order.extend(encounter.players)
            encounter.initiative_order.extend(encounter.monsters)
            encounter.initiative_order.sort(reverse = True, key = lambda creature: creature.initiative)


        else:
            encounter.added_monsters_list = dict_form["added_monsters_list"]      

            for added in encounter.added_monsters_list:
                added[0] = Creature.get_object_form(dict_form = added[0])
            
        return encounter
