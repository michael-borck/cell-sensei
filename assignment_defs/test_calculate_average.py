import pytest
import math

# These tests will be run on the student's calculate_average function
# The function will be imported at runtime

def test_basic_calculation():
    """Test that the function correctly calculates the average of [1, 2, 3, 4, 5]"""
    assert calculate_average([1, 2, 3, 4, 5]) == 3.0

def test_empty_list():
    """Test that the function returns 0 for an empty list"""
    assert calculate_average([]) == 0

def test_negative_numbers():
    """Test that the function handles negative numbers correctly"""
    assert calculate_average([-1, -2, -3, -4, -5]) == -3.0

def test_floating_point():
    """Test that the function works with floating point numbers"""
    result = calculate_average([1.5, 2.5, 3.5])
    assert math.isclose(result, 2.5, rel_tol=1e-9)

def test_large_numbers():
    """Test handling of large numbers"""
    result = calculate_average([10**6, 2*10**6, 3*10**6])
    assert result == 2*10**6

def test_mixed_types():
    """Test with mixed numeric types"""
    result = calculate_average([1, 2.5, 3])
    assert math.isclose(result, 2.1666666667, rel_tol=1e-9)