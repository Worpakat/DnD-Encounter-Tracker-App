from abc import ABC, abstractmethod, abstractproperty, abstractstaticmethod
import random

class Creature(ABC): #We don't need creature base class object.

    def __init__(self, name, hit_point, armor_class, passive_perception) -> None:
        
        self.name = name
        self.hit_point = hit_point
        self.armor_class = armor_class
        self.passive_perception = passive_perception
        self.initiative = 0
       
    def __str__(self) -> str:
        return f"{self.name} HP:{self.hit_point} AC:{self.armor_class} PP:{self.passive_perception} Initiative:{self.initiative}"
    
    def get_dict_form(self):
        """Returns a dictionary that creature's data saved in."""
        
        dict_form = self.__dict__.copy()
        dict_form["type"] = type(self).__name__
        return dict_form

    @classmethod
    def get_object_form(cls, dict_form):
        """Takes a creature's dict. form and returns obj. form."""
        
        if dict_form["type"] == "Player":
            player = Player(
                    name = dict_form["name"],
                    hit_point = dict_form["hit_point"],
                    armor_class = dict_form["armor_class"],
                    passive_perception = dict_form["passive_perception"]
            )
            player.initiative = dict_form["initiative"]
            return player

        elif dict_form["type"] == "Monster":
            monster = Monster(
                    name = dict_form["name"],
                    hit_point = dict_form["hit_point"],
                    armor_class = dict_form["armor_class"],
                    passive_perception = dict_form["passive_perception"],
                    initiative_modifier = dict_form["initiative_modifier"]
            )
            monster.initiative = dict_form["initiative"]
            return monster


class Player(Creature):
    pass

class Monster(Creature):

    def __init__(self, name, hit_point, armor_class, passive_perception, initiative_modifier) -> None:
        
        super().__init__(name, hit_point, armor_class, passive_perception) 

        self.initiative_modifier = initiative_modifier 
    
    def roll_initiative(self):
        """Rolls and assign initiative for this monster instance."""
        
        initiative = random.randint(1,20) + self.initiative_modifier
        self.initiative = initiative

