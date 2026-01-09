"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  SEQUENCE COMPLETION TASK PROMPTS                             ║
║                                                                               ║
║  Prompts/instructions for sequence completion reasoning tasks.                ║
║  Prompts are selected based on task type and provided to video models.        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random


# ══════════════════════════════════════════════════════════════════════════════
#  DEFINE YOUR PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

PROMPTS = {
    "default": [
        "The scene shows a sequence of elements arranged horizontally from left to right. Each element is displayed as a number, shape, color, or position marker. The last position in the sequence contains a question mark (?) indicating a missing element. Observe the pattern formed by the visible elements in the sequence. Identify the mathematical relationship, repeating cycle, or logical rule that governs how each element follows from the previous ones. Determine the correct element that should replace the question mark to complete the sequence according to the established pattern.",
    ],
    
    "arithmetic": [
        "The scene shows a sequence of numbers arranged horizontally from left to right. Each number is displayed as a digit in the center of the frame. The last position contains a question mark (?) indicating the missing number. Observe the arithmetic pattern: each number differs from the previous one by a constant value (the common difference). Calculate the difference between consecutive visible numbers to identify the step size. Apply this step size to the last visible number to determine the missing value. Replace the question mark with the correct number that completes the arithmetic sequence.",
    ],
    
    "geometric": [
        "The scene shows a sequence of numbers arranged horizontally from left to right. Each number is displayed as a digit in the center of the frame. The last position contains a question mark (?) indicating the missing number. Observe the geometric pattern: each number is obtained by multiplying the previous number by a constant ratio. Calculate the ratio between consecutive visible numbers by dividing each number by its predecessor. Verify that this ratio remains constant throughout the sequence. Apply this ratio to the last visible number to determine the missing value. Replace the question mark with the correct number that completes the geometric sequence.",
    ],
    
    "power": [
        "The scene shows a sequence of numbers arranged horizontally from left to right. Each number is displayed as a digit in the center of the frame. The last position contains a question mark (?) indicating the missing number. Observe the power pattern: each number is the square of consecutive integers (1², 2², 3², etc.). Identify the base integer for each visible number by finding the square root. Determine the position of each number in the sequence to establish the pattern. Calculate the square of the next integer in the sequence. Replace the question mark with the correct number that completes the square number sequence.",
    ],
    
    "fibonacci": [
        "The scene shows a sequence of numbers arranged horizontally from left to right. Each number is displayed as a digit in the center of the frame. The last position contains a question mark (?) indicating the missing number. Observe the Fibonacci pattern: starting from the first two numbers, each subsequent number is the sum of the two immediately preceding numbers. Verify this relationship by checking that each visible number equals the sum of its two predecessors. Apply this rule to calculate the missing number by adding the last two visible numbers together. Replace the question mark with the correct number that completes the Fibonacci sequence.",
    ],
    
    "shape_cycle": [
        "The scene shows a sequence of shapes arranged horizontally from left to right. Each shape is displayed as a geometric figure (circle, square, triangle, diamond, or star) in the center of the frame. The last position contains a question mark (?) indicating the missing shape. Observe the repeating pattern: the shapes follow a cyclic order that repeats after a certain number of elements. Identify the cycle by examining the order of shapes from left to right. Determine where in the cycle the sequence currently is and which shape should come next. Replace the question mark with the correct shape that completes the shape cycle pattern.",
    ],
    
    "color_cycle": [
        "The scene shows a sequence of colored circles arranged horizontally from left to right. Each circle is displayed in a distinct color (red, blue, green, yellow, or orange) in the center of the frame. The last position contains a question mark (?) indicating the missing color. Observe the repeating pattern: the colors follow a cyclic order that repeats after a certain number of elements. Identify the color cycle by examining the order of colors from left to right. Determine where in the cycle the sequence currently is and which color should come next. Replace the question mark with the correct colored circle that completes the color cycle pattern.",
    ],
    
    "direction_cycle": [
        "The scene shows a sequence of direction markers arranged horizontally from left to right. Each marker is displayed as an arrow or indicator pointing in a specific direction (top, bottom, left, right, center, or diagonal positions) in the center of the frame. The last position contains a question mark (?) indicating the missing direction. Observe the repeating pattern: the directions follow a cyclic order that repeats after a certain number of elements. Identify the direction cycle by examining the order of directions from left to right. Determine where in the cycle the sequence currently is and which direction should come next. Replace the question mark with the correct direction marker that completes the direction cycle pattern.",
    ],
    
    "mixed": [
        "The scene shows a sequence of colored shapes arranged horizontally from left to right. Each element is displayed as a geometric shape (circle, square, triangle, diamond, or star) filled with a specific color (red, blue, green, yellow, or orange) in the center of the frame. The last position contains a question mark (?) indicating the missing element. Observe the repeating pattern: both the colors and shapes follow cyclic orders that combine to form a mixed sequence. Identify the combined cycle by examining how both color and shape change from left to right. Determine where in the cycle the sequence currently is and which colored shape combination should come next. Replace the question mark with the correct colored shape that completes the mixed sequence pattern.",
    ],
}


def get_prompt(task_type: str = "default") -> str:
    """
    Select a random prompt for the given task type.
    
    Args:
        task_type: Type of task (key in PROMPTS dict)
        
    Returns:
        Random prompt string from the specified type
    """
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)


def get_all_prompts(task_type: str = "default") -> list[str]:
    """Get all prompts for a given task type."""
    return PROMPTS.get(task_type, PROMPTS["default"])
