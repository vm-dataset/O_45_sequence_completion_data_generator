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
        "This is a sequence. Observe its pattern, then replace the question mark with the correct element to complete the sequence.",
    ],
    
    "arithmetic": [
        "This is a sequence. Observe its pattern, then replace the question mark with the correct number to complete the arithmetic sequence.",
    ],
    
    "geometric": [
        "This is a sequence. Observe its pattern, then replace the question mark with the correct number to complete the geometric sequence.",
    ],
    
    "power": [
        "This is a sequence. Observe its pattern, then replace the question mark with the correct number to complete the square sequence.",
    ],
    
    "fibonacci": [
        "This is a sequence. Observe its pattern, then replace the question mark with the correct number to complete the Fibonacci sequence.",
    ],
    
    "shape_cycle": [
        "This is a sequence with a repeating cycle of shapes. Observe the pattern, then replace the question mark with the correct shape to complete the shape cycle.",
    ],
    
    "color_cycle": [
        "This is a sequence with a repeating cycle of colors. Observe the pattern, then replace the question mark with the correct color to complete the color cycle.",
    ],
    
    "direction_cycle": [
        "This is a sequence with a repeating cycle of directions. Observe the pattern, then replace the question mark with the correct direction to complete the direction cycle.",
    ],
    
    "mixed": [
        "This is a sequence with a repeating cycle of mixed elements (combining color and shape). Observe the pattern, then replace the question mark with the correct element to complete the mixed sequence.",
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
