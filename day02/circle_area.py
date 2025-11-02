import math

def circle_area(radius):
    return math.pi * (radius ** 2)

if __name__ == "__main__":
    try:
        radius = float(input("Enter circle radius: ").strip())
        area = circle_area(radius)
        print(f"Circle with radius {radius} has area: {area}")

    except ValueError:
        print("Please enter valid numbers for the radius.")