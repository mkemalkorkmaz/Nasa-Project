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

meal_1 = null
meal_2 = null
meal_3 = null

avarage_shouldve_been_protein = null
avarage_shouldve_been_vitamins = null
avarage_shouldve_been_energy = null

deficiency_protein = 0
deficiency_vitamins = 0
deficiency_energy = 0

total_protein = 0
total_vitamin = 0
total_energy = 0

#Functions
def read_and_fill():
    try:
        with open(meals_history.txt, "r") as file:
            lines = file.readlines()
            for i, start in enumerate(file, start=0):
                splitted = lines[i].split() #First means the meal's date, then meal type(breakfast, launch etc.) and then what foods it contained, how much protein, vitamin they have and finally whether they are consumed.

                total_protein += int(splitted[3]) 
                total_vitamin += int(splitted[4])
                total_energy += int(splitted[5])

                if splitted[6] == "true":
                    continue
                elif splitted[6] == "false":
                    deficiency_protein += int(splitted[3])
                    deficiency_vitamins += int(splitted[4])
                    deficiency_energy += int(splitted[5])
                elif splitted[6] == "semi":
                    deficiency_protein += round(int(splitted[3]) / 2)
                    deficiency_vitamins += round(int(splitted[4]) / 2)
                    deficiency_energy += round(int(splitted[5]) / 2)

                avarage_shouldve_been_protein = total_protein / i
                avarage_shouldve_been_vitamins = total_vitamin / i
                avarage_shouldve_been_energy = total_energy / i
    except:
        with open(meals_history.txt, "w") as file:
            file.write("")

def choose_the_most(whereis):
    biggest = 0
    second = 0

    for i in meals:
        for im in i:
            if im == whereis:
                if im > biggest:
                    biggest = i
                elif im < biggest and im > second:
                    second = i

    return biggest, second
        
def select_the_most_nutritional():
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
        return null


def select_meal():
    result = select_the_most_nutritional()
    if result != null and meal_1 == null or meal_2 == null or meal_3 == null:
        numOfnulls = 0
        if meal_1 == null: numOfnulls += 1
        elif meal_2 == null: numOfnulls += 1
        elif meal_3 == null: numOfnulls += 1
        
        for i in range(numOfnulls):
            rd = random.randint(0, 6)
            if meal_1 == null: meals[rd]
            elif meal_2 == null: meals[rd]
            elif meal_3 == null: meals[rd]

        return meal_1, meal_2, meal_3

def consumed(whichOne):
    with open("meals_history.txt", "w") as file:
        if whichOne == 0: file.write(date.today(), "breakfast", meal_1[4], meal_1[1], meal_1[2], meal_1[3], consumed)
        elif whichOne == 1: file.write(date.today(), "launch", meal_1[4], meal_1[1], meal_1[2], meal_1[3], consumed)
        elif whichOne == 2: file.write(date.today(), "dinner", meal_1[4], meal_1[1], meal_1[2], meal_1[3], consumed)
