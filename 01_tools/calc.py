#!/usr/bin/env python3
"""Simple BMI calculator."""

from __future__ import annotations


def bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100.0
    if height_m <= 0:
        raise ValueError("Height must be positive")
    return weight_kg / (height_m ** 2)


def category(value: float) -> str:
    if value < 18.5:
        return "Underweight"
    if value < 25:
        return "Normal"
    if value < 30:
        return "Overweight"
    return "Obese"


def main() -> None:
    try:
        weight = float(input("Weight (kg): ").strip())
        height = float(input("Height (cm): ").strip())
    except ValueError:
        print("Please enter valid numbers.")
        return

    if weight <= 0 or height <= 0:
        print("Weight and height must be positive.")
        return

    value = bmi(weight, height)
    print(f"\nBMI: {value:.1f}")
    print(f"Category: {category(value)}")


if __name__ == "__main__":
    main()
