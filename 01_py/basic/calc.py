def bmi(weight, height):
    height = height / 100
    return weight / height**2

weight = float(input('weight (kg)'))
height = float(input('height (cm)'))

bmindex = bmi(weight,height)

print(f"BMI output: {bmindex:.1f}")

if bmindex>25:
    print("you a fat ass nigga")
elif bmindex<18.5:
    print('eat longman')
else:
    print('normal')