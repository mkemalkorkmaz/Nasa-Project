#Instances
meals = (
   ("Meal 1", 50, 50),
   ("Meal 2", 100, 100),
   ("Meal 3", 25, 50),
   ("Meal 4", 100, 15),
   ("Meal 5", 20, 75),
   ("Meal 6", 10, 50)
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
            for i, start in enumerate(start=0):
                splitted = lines[i].split() #First means the meal's date, then meal type(breakfast, launch etc.) and then what foods it contained, how much protein, vitamin they have and whether they are consumed.

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

def select_meals():
    read_and_fill()


with open("meals_history.txt", "w") as file:
    file.write()
