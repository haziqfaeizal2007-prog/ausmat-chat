import random
animals = ['pig','pigeon','bull','owl','bear','chicken']
adjectives = ['sneaky','dangerous','killing','spooky','menacing','swift']
print ("What is your name?")
name = input()
print("Haziq,your codename is,")
print((random.choice(adjectives))+(" ")+ (random.choice(animals)))
print("Your code number is:")
print(random.randint(0,100))