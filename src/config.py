"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              SEQUENCE COMPLETION TASK CONFIGURATION                           ║
║                                                                               ║
║  Configuration for sequence completion task data generation.                  ║
║  Inherits common settings from core.GenerationConfig                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from pydantic import Field
from core import GenerationConfig


class TaskConfig(GenerationConfig):
    """
    Sequence completion task-specific configuration.
    
    Configuration for generating sequence completion reasoning tasks with
    8 different types: arithmetic, geometric, power, Fibonacci, shape cycles,
    color cycles, direction cycles, and mixed sequences.
    
    Inherited from GenerationConfig:
        - num_samples: int          # Number of samples to generate
        - domain: str               # Task domain name ("sequence_completion")
        - difficulty: Optional[str] # Difficulty level
        - random_seed: Optional[int] # For reproducibility
        - output_dir: Path          # Where to save outputs
        - image_size: tuple[int, int] # Image dimensions (default: 1024x1024)
    """
    
    # ══════════════════════════════════════════════════════════════════════════
    #  OVERRIDE DEFAULTS
    # ══════════════════════════════════════════════════════════════════════════
    
    domain: str = Field(default="sequence_completion")
    image_size: tuple[int, int] = Field(default=(1024, 1024))
    
    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    generate_videos: bool = Field(
        default=False,
        description="Whether to generate ground truth videos"
    )
    
    video_fps: int = Field(
        default=10,
        description="Video frame rate"
    )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  TASK-SPECIFIC SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    # Task types to generate: list of task type numbers (1-8)
    # 1: Arithmetic, 2: Geometric, 3: Power, 4: Fibonacci,
    # 5: Shape Cycle, 6: Color Cycle, 7: Direction Cycle, 8: Mixed
    task_types: list[int] = Field(
        default=[1, 2, 3, 4, 5, 6, 7, 8],
        description="List of task types to generate (1-8)"
    )
    
    # Limit task generation (if None, generates all possible tasks)
    max_tasks_per_type: int = Field(
        default=None,
        description="Maximum number of tasks to generate per type (None = all)"
    )
