#Importances
import random
from datetime import date

#Instances
meals = (
   ("Meal 1", 50, 50, 5, "one_two_three"),
   ("Meal 2", 100, 100, 3, "one_two_three"),
   ("Meal 3", 25, 50, 2, "one_two_three"),
   ("Meal 4", 100, 15, 8, "one_two_three"),
   ("Meal 5", 20, 75, 4, "one_two_three"),
   ("Meal 6", 10, 50, 8, "one_two_three")
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
    try:
        with open("meals_history.txt", "r") as file:
            lines = file.readlines()
        for line in lines:
            splitted = line.split() #First means the meal's date, then meal type(breakfast, launch etc.) and then what foods it contained, how much protein, vitamin they have and finally whether they are consumed.
            if not splitted: 
                continue

            total_protein += int(splitted[3])
            total_vitamin += int(splitted[4])
            total_energy += int(splitted[5])

            if splitted[6] == "false":
                deficiency_protein += int(splitted[3])
                deficiency_vitamins += int(splitted[4])
                deficiency_energy += int(splitted[5])
            elif splitted[6] == "semi":
                deficiency_protein += round(int(splitted[3]) / 2)
                deficiency_vitamins += round(int(splitted[4]) / 2)
                deficiency_energy += round(int(splitted[5]) / 2)

        if lines:
            avarage_shouldve_been_protein = total_protein / len(lines)
            avarage_shouldve_been_vitamins = total_vitamin / len(lines)
            avarage_shouldve_been_energy = total_energy / len(lines)
    except FileNotFoundError:
        with open("meals_history.txt", "w") as file:
            file.write("")

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
    if deficiency_protein >= 100: #to be changed
        biggest, second = choose_the_most(1)
        rd = random.randint(0, 1)
        if rd == 0:
            meal_1 = biggest
        else:
            meal_1 = second
        return 0
    elif deficiency_vitamins >= 100:
        biggest, second = choose_the_most(2)
        rd = random.randint(0, 1)
        if rd == 0:
            meal_2 = biggest
        else:
            meal_2 = second
        return 0
    elif deficiency_energy >= 100:
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
    if whichOne == 0:
        meal, slot = meal_1, "breakfast"
    elif whichOne == 1:
        meal, slot = meal_2, "lunch"
    else:
        meal, slot = meal_3, "dinner"

    with open("meals_history.txt", "a") as file:
        file.write(f"{date.today()} {slot} {meal[4]} {meal[1]} {meal[2]} {meal[3]} {status}\n")

