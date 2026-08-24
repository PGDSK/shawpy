#!/usr/bin/env python3


from __future__ import annotations

import numpy as np

def make_grid(x_range, y_range, resolution=50):
    X = np.linspace(x_range[0], x_range[1], resolution)
    Y = np.linspace(y_range[0], y_range[1], resolution)
    X, Y = np.meshgrid(X, Y)

    return X, Y

def evaluate(func, X, Y):
    return func(X, Y)

def paraboloid(X, Y):
    return X**2 + Y**2

def main():
    X, Y = make_grid(x_range=(-5,5), y_range=(-5,5), resolution =5)
    Z = evaluate(paraboloid, X, Y)

    print ("X:\n", X)
    print("Y:\n", Y)
    print("Z = x^2 + y^2:\n", Z)

if __name__ == "__main__":
    main()

