import random
import configparser

# class for input colors


class Color:
    def __init__(self, rValue, gValue, bValue, color_name):
        self.red_value = rValue
        self.blue_value = bValue
        self.green_value = gValue
        self.color_name = color_name

# class for perceptrons


class Perceptron:
    def __init__(self, weight_red, weight_green, weight_blue, weight_bias, target):
        self.weight_red = weight_red
        self.weight_green = weight_green
        self.weight_blue = weight_blue
        self.weight_bias = weight_bias
        self.threshold = 0.5
        self.target = target
        self.fired_correctly = 0
        self.false_positive_counter = 0
        self.false_negative_counter = 0

# performs net sum and activation of perceptron for given input


def net_sum_activation(color_input, perceptron):
    net_sum = color_input.red_value * perceptron.weight_red + color_input.green_value * \
        perceptron.weight_green + color_input.blue_value * \
        perceptron.weight_blue + perceptron.weight_bias
    if net_sum >= perceptron.threshold:
        return 1
    return 0

# function for training - adjusts weights


def training(color_input, perceptron, guess, learning_rate, correct):
    perceptron.weight_bias = perceptron.weight_bias + \
        learning_rate * (correct - guess)
    perceptron.weight_red = perceptron.weight_red + \
        learning_rate * (correct - guess) * color_input.red_value
    perceptron.weight_green = perceptron.weight_green + \
        learning_rate * (correct - guess) * color_input.green_value
    perceptron.weight_blue = perceptron.weight_blue + \
        learning_rate * (correct - guess) * color_input.blue_value


# intialization of variables for program
correct_counter = 0
incorrect_counter = 0
false_positive_counter = 0
false_negative_counter = 0
perfect_counter = 0
perceptron_fired_counter = 0
total = 0
multiple_fire_counter = 0
zero_neuron_fired_counter = 0
input_total = 0
line = 'a'
color_list = []
perceptron_list = []
list_of_possible_colors = ['Red', 'Blue', 'Yellow',
                           'Green', 'Purple', 'Orange', 'Brown', 'Pink', 'Gray']

# instantiate configuration file parser
config = configparser.ConfigParser()
config.read('config.ini')  # select config file to use
# import config values into program
learning_rate = float(config['DEFAULT']['initialLearningRate'])
num_epochs = int(config['DEFAULT']['numEpochs'])
file_name = str(config['DEFAULT']['fileName'])
input_method = int(config['DEFAULT']['inputMethod'])
weight_input_file = str(config['DEFAULT']['weightInputFile'])
weight_output_file = str(config['DEFAULT']['weightOutputFile'])
turn_off_training = int(config['DEFAULT']['turnOffTraining'])

# read color ipnut from file
with open(file_name) as f:
    while line:
        line = f.readline()
        if line:
            info = line.split()
            color_list.append(
                Color(int(info[0])/255, int(info[1])/255, int(info[2])/255, info[3]))

# determine whether weights should be inputted randomly or from file
if input_method == 0:
    for color in list_of_possible_colors:
        temp_red = random.uniform(0, 1)
        temp_green = random.uniform(0, 1)
        temp_blue = random.uniform(0, 1)
        temp_bias = random.uniform(0, 1)
        perceptron_list.append(Perceptron(
            temp_red, temp_green, temp_blue, temp_bias, color))
else:
    with open(weight_input_file, 'r') as f:
        while line:
            for color in list_of_possible_colors:
                line = f.readline().split()
                print(line)
                perceptron_list.append(Perceptron(
                    line[4], line[3], line[2], line[1], color))
# main loop
print('Working...\n\n')
for _ in range(num_epochs):
    for color in color_list:
        perceptron_fired_counter_round = 0
        list_correct = []
        list_incorrect = []
        for perceptron in perceptron_list:
            guess = net_sum_activation(color, perceptron)
            # determine whether guess is correct, update counters for stats
            if (guess == 1 and color.color_name == perceptron.target):
                correct = 1
                perceptron_fired_counter += 1
                perceptron_fired_counter_round += 1
                perceptron.fired_correctly += 1
                correct_counter += 1
                list_correct.append(perceptron)
            elif (guess == 0 and color.color_name != perceptron.target):
                correct = 0
                perceptron.fired_correctly += 1
                correct_counter += 1
                list_correct.append(perceptron)
            elif (color.color_name == perceptron.target and guess == 0):
                correct = 1
                perceptron.false_negative_counter += 1
                incorrect_counter += 1
                list_incorrect.append(perceptron)
            elif (color.color_name != perceptron.target and guess == 1):
                correct = 0
                perceptron_fired_counter += 1
                perceptron_fired_counter_round += 1
                perceptron.false_positive_counter += 1
                incorrect_counter += 1
                list_incorrect.append(perceptron)
            if not turn_off_training:
                training(color, perceptron, guess, learning_rate, correct)
            total += 1
        # adjust NN statistic counters
        if len(list_correct) == len(list_of_possible_colors) and perceptron_fired_counter_round == 1:
            perfect_counter += 1
        if perceptron_fired_counter > 1:
            multiple_fire_counter += 1
        if perceptron_fired_counter_round == 0:
            zero_neuron_fired_counter += 1
        input_total += 1
# output final weights to txt file
with open(weight_output_file, 'w+') as f:
    for p in perceptron_list:
        string = p.target + ' ' + str(p.weight_bias) + ' ' + str(
            p.weight_blue) + ' ' + str(p.weight_green) + ' ' + str(p.weight_red)
        f.write(string)
        f.write('\n')

# calculate NN stats
percent_zero_neurons_fired = zero_neuron_fired_counter/total
percent_multiple_neurons_fired = multiple_fire_counter/total
percent_perfect = perfect_counter/input_total

# program output
print('Percent 0 neurons fired:', percent_zero_neurons_fired)
print('Percent multiple neurons fired:', percent_multiple_neurons_fired)
print('Percent perfectly executed:', percent_perfect)
print('\nColor    % Correct   % False Pos   % False Neg')

# calculate and output indivdual neuron stats
for p in perceptron_list:
    print(p.target, '   ', round(p.fired_correctly/input_total, 5), '  ', round(p.false_positive_counter /
          input_total, 5), '      ', round(p.false_negative_counter/input_total, 5))
