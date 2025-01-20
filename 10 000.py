from itertools import product
import csv


number_of_dice = 5
prob_cut_off = 5e-15

# each throw will have three possibilities
# 1. possible points * proba * recursion with 5 dice
# 2. possible points * proba * recursion with n-1 dice
# 3. -acumalted points * proba 



def calculate_points_combinations(n) -> list[bool,float,int]:
    # bool: 1 if next throw would give a 5 die throw
    # float: proba of getting that score depending if the next is a 5 or not
    # int: amount of possible points gained by throw

    rv = []
    possible_scores = set()

    dice_combinatios = list(product(range(1,7), repeat=n))
    
    for combination in dice_combinatios:
        combination = list(combination)
        point_sum = 0

        while any(combination.count(die) >= 3 for die in set(combination)):
            # Check if there is a number repeated 3 times and identify it
            repeated_three = [die for die in set(combination) if combination.count(die) >= 3]

            if repeated_three:
                repeated_three = repeated_three[0]

                if repeated_three != 1:
                    point_sum += repeated_three *100
                else:
                    point_sum += 1000

                # Remove exactly 3 occurrences of the identified number
                count = 0
                i = 0
                while count < 3 and i < len(combination):
                    if combination[i] == repeated_three:
                        combination.pop(i)
                        count += 1
                    else:
                        i += 1

        # Remove all occurrences of 1 and 5 and update the counter
        i = 0
        while i < len(combination):
            if combination[i] == 1:
                point_sum += 100
                combination.pop(i)
            elif combination[i] == 5:
                point_sum += 50
                combination.pop(i)
            else:
                i += 1


        next_is_5:bool = 0

        if len(combination) == 0:
            next_is_5 = 1
        
        if (next_is_5, point_sum) not in possible_scores:
            possible_scores.add((next_is_5, point_sum))
            rv.append([next_is_5, 1, point_sum])
        else:
            i = 0
            for ls in rv:
                if ls[2] == point_sum and ls[0] == next_is_5:
                    rv[i][1] += 1
                i += 1

    i = 0
    for _ in rv:
        rv[i][1] = rv[i][1]/ len(dice_combinatios)
        i += 1
    return rv



def make_csv(n):
    try:
        # Check if file exists 
        with open(f'Probability with {n} dice.csv', mode='r', newline='') as file:
            return
    except FileNotFoundError:
        
        first = n
        while n > 0:
            # File name
            csv_file = f"Probability with {first} dice.csv"
            Head = calculate_points_combinations(first)
            # Prepare data for the current row
            headers = sorted(set(row[2] for row in Head))  # Unique values from the third column, sorted descending
            row_values = {header: 0.0 for header in headers}  # Initialize all headers with 0.0 for summation

            data = calculate_points_combinations(n)
            # Populate the row values with sums for matching keys
            for _, value, key in data:
                if key in row_values:
                    row_values[key] += value

            if n == first:
                append_mode = False
            else:
                append_mode = True

            # Write or append the CSV
            with open(csv_file, mode='a' if append_mode else 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["Dice left"] + headers)

                if not append_mode:
                    # Write headers if the file is being created
                    writer.writeheader()

                # Write the new row
                row = {"Dice left": n}
                row.update(row_values)
                writer.writerow(row)
            n -= 1

        print(f"Data written to {csv_file}.")

def Exp_Value_n_memo(n, actual_points, point_combinations, prob_cut_off, current_prob, memo=None):
    if memo is None:
        memo = {}  # Initialize the memoization dictionary

    # Check if the result is already in the memo table
    if (n, current_prob) in memo:
        return memo[(n, current_prob)]

    # Get the corresponding point combination
    point_combination = point_combinations[n-1]
    Exp = 0

    # Base case: If the current probability is below the cutoff, return 0
    if current_prob < prob_cut_off:
        return Exp

    # Iterate through point combinations
    for next_5, proba, points in point_combination:
        # If next_5 is True, recurse with a higher n value
        if next_5:
            Exp += proba * (points + Exp_Value_n_memo(5, actual_points, point_combinations, prob_cut_off, current_prob * proba, memo))
        else:
            # If points is 0, subtract actual points weighted by probability
            if points == 0:
                Exp -= proba * actual_points
            else:
                # Otherwise, recurse with the same n (but adjust the probability)
                Exp += proba * (points + Exp_Value_n_memo(n-1, actual_points, point_combinations, prob_cut_off, current_prob * proba, memo))

    # Store the result in the memoization dictionary before returning
    memo[(n, current_prob)] = Exp
    return Exp



def make_ExpV_csv(n, prob_cut_off):
    try:
        # Check if file exists 
        with open(f"Exp Value {prob_cut_off} with {n} dice.csv", mode='r', newline='') as file:
            return  # File exists, no need to create a new one
    except FileNotFoundError:
        first = n  # To keep track of the first row
        while n > 0:
            # File name
            csv_file = f"Exp Value {prob_cut_off} with {first} dice.csv"

            # Prepare data for the current row
            headers = ['Expected Value']  # Include other headers if needed

            # Calculate combinations for the number of dice
            c = []
            for num in range(1, number_of_dice + 1):
                c.append(calculate_points_combinations(num)) 
            
            actual_points = 0
            value = Exp_Value_n_memo(n, actual_points, c, prob_cut_off, 1, None)  # Calculate the expected value
            # print(f'Expected value for {n} dice with {actual_points} actual points with {prob_cut_off} probability cut off is {value:.0f} points')

            # Populate the row values with the calculated expected value
            row_values = {'Expected Value': value}  # Mapping the header to its value

            if n == first:
                append_mode = False  # Write headers if it's the first row
            else:
                append_mode = True  # Append to the file for subsequent rows

            # Write or append the CSV
            with open(csv_file, mode='a' if append_mode else 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=[f"Dice left with max porbability of {prob_cut_off}"] + headers)

                if not append_mode:
                    # Write headers if the file is being created
                    writer.writeheader()

                # Write the new row
                row = {f"Dice left with max porbability of {prob_cut_off}": n}
                row.update(row_values)  # Add the calculated expected value
                writer.writerow(row)

            n -= 1

        print(f"Data written to {csv_file}.")



make_csv(number_of_dice)
make_ExpV_csv(number_of_dice, prob_cut_off)

