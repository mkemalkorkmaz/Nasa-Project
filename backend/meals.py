#Importances
import random
import os
from datetime import date
 
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meals_history.txt")
 
#Instances
meals = (
    ("Meal 1", 28.0, 3.2, 380, "Beef Stew with Tortilla"),
    ("Meal 2", 18.0, 4.1, 350, "Red Beans and Rice"),
    ("Meal 3", 25.0, 8.5, 280, "Chicken Salad"),
    ("Meal 4", 22.0, 5.8, 250, "Shrimp Cocktail with Tortilla"),
    ("Meal 5", 30.0, 2.7, 300, "Smoked Turkey with Wheat Flatbread"),
    ("Meal 6", 28.0, 3.4, 390, "Tuna Casserole"),
    ("Meal 7", 19.0, 4.8, 340, "Split Pea Soup with Tortilla"),
    ("Meal 8", 10.0, 2.5, 420, "Granola with Nuts and Dried Fruit"),
    ("Meal 9", 32.0, 7.6, 400, "Beef Fajitas with Tortilla")
)
 
meal_1 = None
meal_2 = None
meal_3 = None
 
avarage_shouldve_been_protein = None
avarage_shouldve_been_vitamins = None
avarage_shouldve_been_energy = None
 
deficiency_protein = 0
deficiency_vitamins = 0
deficiency_energy = 0
 
total_protein = 0
total_vitamin = 0
total_energy = 0
 
#Functions
def read_and_fill():
    global total_protein, total_vitamin, total_energy
    global deficiency_protein, deficiency_vitamins, deficiency_energy
    global avarage_shouldve_been_protein, avarage_shouldve_been_vitamins, avarage_shouldve_been_energy
 
    # Reset everything so repeated calls (e.g. from a running server) don't double count
    total_protein = total_vitamin = total_energy = 0
    deficiency_protein = deficiency_vitamins = deficiency_energy = 0
    avarage_shouldve_been_protein = avarage_shouldve_been_vitamins = avarage_shouldve_been_energy = None
 
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            file.write("")
        return
 
    counted = 0
    for line in lines:
        # Fields are tab separated: date, slot, meal name, protein, vitamins, energy, status
        splitted = line.rstrip("\n").split("\t")
        if len(splitted) < 7:
            continue  # empty or old-format line
        try:
            protein = float(splitted[3])
            vitamins = float(splitted[4])
            energy = float(splitted[5])
        except ValueError:
            continue
        status = splitted[6]
        counted += 1
 
        total_protein += protein
        total_vitamin += vitamins
        total_energy += energy
 
        if status == "false":
            deficiency_protein += protein
            deficiency_vitamins += vitamins
            deficiency_energy += energy
        elif status == "semi":
            deficiency_protein += protein / 2
            deficiency_vitamins += vitamins / 2
            deficiency_energy += energy / 2
 
    if counted:
        avarage_shouldve_been_protein = total_protein / counted
        avarage_shouldve_been_vitamins = total_vitamin / counted
        avarage_shouldve_been_energy = total_energy / counted
 
def choose_the_most(whereis):
    biggest = None
    second = None
 
    for i in meals:
        if biggest is None or i[whereis] > biggest[whereis]:
            second = biggest
            biggest = i
        elif second is None or i[whereis] > second[whereis]:
            second = i
 
    return biggest, second
 
def select_the_most_nutritional():
    global meal_1, meal_2, meal_3
    read_and_fill()
    if deficiency_protein >= 20: 
        biggest, second = choose_the_most(1)
        rd = random.randint(0, 1)
        if rd == 0:
            meal_1 = biggest
        else:
            meal_1 = second
        return 0
    elif deficiency_vitamins >= 25:
        biggest, second = choose_the_most(2)
        rd = random.randint(0, 1)
        if rd == 0:
            meal_2 = biggest
        else:
            meal_2 = second
        return 0
    elif deficiency_energy >= 300:
        biggest, second = choose_the_most(3)
        rd = random.randint(0, 1)
        if rd == 0:
            meal_3 = biggest
        else:
            meal_3 = second
        return 0
    else:
        return None
 
def select_meal():
    global meal_1, meal_2, meal_3
    meal_1 = meal_2 = meal_3 = None
    select_the_most_nutritional()
 
    numOfnulls = 0
    if meal_1 is None: numOfnulls += 1
    if meal_2 is None: numOfnulls += 1
    if meal_3 is None: numOfnulls += 1
 
    for i in range(numOfnulls):
        rd = random.randint(0, len(meals) - 1)
        if meal_1 is None:
            meal_1 = meals[rd]
        elif meal_2 is None:
            meal_2 = meals[rd]
        elif meal_3 is None:
            meal_3 = meals[rd]
 
    return meal_1, meal_2, meal_3
 
def consumed(whichOne, status="false"):
    if status not in ("true", "false", "semi"):
        raise ValueError("status must be true, false or semi")
    if whichOne == 0:
        meal, slot = meal_1, "breakfast"
    elif whichOne == 1:
        meal, slot = meal_2, "lunch"
    elif whichOne == 2:
        meal, slot = meal_3, "dinner"
<<<<<<< HEAD
    else:
        raise ValueError("slot must be 0, 1 or 2")
    if meal is None:
        raise ValueError("no meal selected yet")
 
    with open(HISTORY_FILE, "a", encoding="utf-8") as file:
        file.write(f"{date.today()}\t{slot}\t{meal[4]}\t{meal[1]}\t{meal[2]}\t{meal[3]}\t{status}\n")
 
=======

    with open("meals_history.txt", "a") as file:
        file.write(f"{date.today()} {slot} {meal[4]} {meal[1]} {meal[2]} {meal[3]} {status}\n")



>>>>>>> 009521840f591c03f2561151c82337b2f4513d9f
