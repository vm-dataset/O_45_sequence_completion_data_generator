"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SEQUENCE COMPLETION TASK GENERATOR                         ║
║                                                                               ║
║  Generates sequence completion reasoning tasks with 8 different types:        ║
║  1. Arithmetic sequences, 2. Geometric sequences, 3. Power sequences          ║
║  4. Fibonacci sequences, 5. Shape cycles, 6. Color cycles                     ║
║  7. Direction cycles, 8. Mixed sequences (color+shape)                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import tempfile
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from itertools import permutations
from PIL import Image

from core import BaseGenerator, TaskPair
from core.video_utils import VideoGenerator
from core.sequence_renderer import SequenceRenderer, SHAPE_MAP, COLORS, POSITIONS
from .config import TaskConfig
from .prompts import get_prompt


# Task type mappings
TASK_TYPE_NAMES = {
    1: "arithmetic",
    2: "geometric",
    3: "power",
    4: "fibonacci",
    5: "shape_cycle",
    6: "color_cycle",
    7: "direction_cycle",
    8: "mixed"
}


class TaskGenerator(BaseGenerator):
    """
    Sequence Completion Task Generator.
    
    Generates sequence completion tasks with 8 different types:
    1. Arithmetic sequences
    2. Geometric sequences
    3. Power sequences (squares)
    4. Fibonacci sequences
    5. Shape cycles
    6. Color cycles
    7. Direction cycles
    8. Mixed sequences (color+shape)
    """
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.sequence_renderer = SequenceRenderer(output_size=config.image_size)
        
        # Initialize video generator if enabled
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")
        
        # Pre-generate all task definitions
        self.all_tasks = self._generate_all_task_definitions()
        
        # Filter by task types if specified
        if config.task_types:
            self.all_tasks = [t for t in self.all_tasks if t[1] in config.task_types]
        
        # Limit tasks per type if specified
        if config.max_tasks_per_type:
            task_by_type = {}
            for task in self.all_tasks:
                task_type = task[1]
                if task_type not in task_by_type:
                    task_by_type[task_type] = []
                task_by_type[task_type].append(task)
            
            limited_tasks = []
            for task_type, tasks in task_by_type.items():
                limited_tasks.extend(tasks[:config.max_tasks_per_type])
            self.all_tasks = limited_tasks
        
        # Shuffle for random sampling
        random.shuffle(self.all_tasks)
        
        print(f"📊 Loaded {len(self.all_tasks)} sequence completion task definitions")
    
    def generate_task_pair(self, task_id: str, task_index: int = None) -> TaskPair:
        """Generate one task pair."""
        # Use provided task_index or default to 0
        if task_index is None:
            task_index = getattr(self, '_current_task_index', 0)
        
        # Ensure we don't exceed available tasks
        if task_index >= len(self.all_tasks):
            task_index = task_index % len(self.all_tasks)
        
        _, task_type, task_params = self.all_tasks[task_index]
        
        # Generate sequence and answer
        sequence, answer = self._generate_sequence(task_type, task_params)
        
        # Render images
        first_image = self._render_sequence_with_blank(sequence)
        final_image = self._render_complete_sequence(sequence, answer)
        
        # Generate video (optional)
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(first_image, final_image, task_id)
        
        # Get prompt based on task type
        task_type_name = TASK_TYPE_NAMES.get(task_type, "default")
        prompt = get_prompt(task_type_name)
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    def generate_dataset(self) -> List[TaskPair]:
        """Generate complete dataset."""
        pairs = []
        num_samples = min(self.config.num_samples, len(self.all_tasks))
        
        for i in range(num_samples):
            task_id = f"{self.config.domain}_{i:04d}"
            pair = self.generate_task_pair(task_id, task_index=i)
            pairs.append(pair)
            task_type = self.all_tasks[i][1]
            print(f"  Generated: {task_id} (Type {task_type}: {TASK_TYPE_NAMES.get(task_type, 'unknown')})")
        
        return pairs
    
    # ══════════════════════════════════════════════════════════════════════════
    #  SEQUENCE GENERATION METHODS
    # ══════════════════════════════════════════════════════════════════════════
    
    def _generate_sequence(self, task_type: int, task_params: Dict[str, Any]) -> Tuple[List[Any], Any]:
        """Generate sequence and answer based on task type."""
        if task_type == 1:  # Arithmetic
            return self._generate_arithmetic_sequence(
                task_params['start'], task_params['step'], task_params['length'])
        elif task_type == 2:  # Geometric
            return self._generate_geometric_sequence(
                task_params['start'], task_params['ratio'], task_params['length'])
        elif task_type == 3:  # Power
            return self._generate_power_sequence(
                task_params['base'], task_params['power'], task_params['length'])
        elif task_type == 4:  # Fibonacci
            return self._generate_fibonacci_sequence(
                task_params['first'], task_params['second'], task_params['length'])
        elif task_type in [5, 6, 7, 8]:  # Cycles
            return self._generate_cycle_sequence(
                task_params['cycle'], task_params['length'])
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    def _generate_arithmetic_sequence(self, start: int, step: int, length: int) -> Tuple[List[int], int]:
        """Generate arithmetic sequence and answer."""
        sequence = [start + i * step for i in range(length - 1)]
        answer = start + (length - 1) * step
        return sequence, answer
    
    def _generate_geometric_sequence(self, start: int, ratio: int, length: int) -> Tuple[List[int], int]:
        """Generate geometric sequence and answer."""
        sequence = [start * (ratio ** i) for i in range(length - 1)]
        answer = start * (ratio ** (length - 1))
        return sequence, answer
    
    def _generate_power_sequence(self, base: int, power: int, length: int) -> Tuple[List[int], int]:
        """Generate power sequence (squares) and answer."""
        sequence = [(base + i) ** power for i in range(length - 1)]
        answer = (base + length - 1) ** power
        return sequence, answer
    
    def _generate_fibonacci_sequence(self, first: int, second: int, length: int) -> Tuple[List[int], int]:
        """Generate Fibonacci sequence and answer."""
        sequence = [first, second]
        for i in range(2, length - 1):
            sequence.append(sequence[i-1] + sequence[i-2])
        answer = sequence[-1] + sequence[-2]
        return sequence, answer
    
    def _generate_cycle_sequence(self, cycle: List[Any], length: int) -> Tuple[List[Any], Any]:
        """Generate cycle sequence and answer."""
        sequence = []
        for i in range(length - 1):
            sequence.append(cycle[i % len(cycle)])
        answer = cycle[(length - 1) % len(cycle)]
        return sequence, answer
    
    # ══════════════════════════════════════════════════════════════════════════
    #  RENDERING METHODS
    # ══════════════════════════════════════════════════════════════════════════
    
    def _render_sequence_with_blank(self, sequence: List[Any]) -> Image.Image:
        """Render sequence with blank (question mark) at the end."""
        sequence_with_blank = sequence + [None]
        return self.sequence_renderer.render_sequence(sequence_with_blank, show_blank=True)
    
    def _render_complete_sequence(self, sequence: List[Any], answer: Any) -> Image.Image:
        """Render complete sequence with answer."""
        complete_sequence = sequence + [answer]
        return self.sequence_renderer.render_sequence(complete_sequence, show_blank=False)
    
    def _generate_video(self, first_image: Image.Image, final_image: Image.Image, task_id: str) -> Optional[str]:
        """Generate ground truth video."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        # Use crossfade video for smooth transition
        result = self.video_generator.create_crossfade_video(
            first_image, final_image, video_path,
            hold_frames=5, transition_frames=15
        )
        
        return str(result) if result else None
    
    # ══════════════════════════════════════════════════════════════════════════
    #  TASK DEFINITION GENERATION
    # ══════════════════════════════════════════════════════════════════════════
    
    def _generate_all_task_definitions(self) -> List[Tuple[str, int, Dict[str, Any]]]:
        """Generate all possible task definitions."""
        all_tasks = []
        
        # Type 1: Arithmetic Sequence
        for start in range(1, 16):
            for step in [-5, -2, -1, 1, 2, 5]:
                for length in [5, 6, 7]:
                    test_seq, test_ans = self._generate_arithmetic_sequence(start, step, length)
                    if min(test_seq + [test_ans]) >= 0 or all(x >= 0 for x in test_seq):
                        task_params = {'start': start, 'step': step, 'length': length}
                        all_tasks.append(('arithmetic', 1, task_params))
        
        # Type 2: Geometric Sequence
        for start in range(1, 31):
            for ratio in [2, 3, 4]:
                for length in [5, 6, 7]:
                    test_seq, test_ans = self._generate_geometric_sequence(start, ratio, length)
                    if test_ans <= 1000:
                        task_params = {'start': start, 'ratio': ratio, 'length': length}
                        all_tasks.append(('geometric', 2, task_params))
        
        # Type 3: Power Sequence
        for base in range(1, 11):
            for length in [5, 6]:
                test_seq, test_ans = self._generate_power_sequence(base, 2, length)
                if test_ans <= 100:
                    task_params = {'base': base, 'power': 2, 'length': length}
                    all_tasks.append(('power', 3, task_params))
        
        # Type 4: Fibonacci Sequence
        for first in range(1, 10):
            for second in range(1, 10):
                for length in [6, 7]:
                    task_params = {'first': first, 'second': second, 'length': length}
                    all_tasks.append(('fibonacci', 4, task_params))
        
        # Type 5: Shape Cycle
        shapes = list(SHAPE_MAP.keys())
        for cycle_len in [3, 4, 5]:
            if cycle_len == 3:
                for combo in permutations(shapes, 3):
                    cycle = list(combo)
                    for length in [5, 6, 7]:
                        task_params = {'cycle': cycle, 'length': length}
                        all_tasks.append(('shape_cycle', 5, task_params))
            elif cycle_len == 4:
                for combo in permutations(shapes, 4):
                    cycle = list(combo)
                    for length in [6, 7, 8]:
                        task_params = {'cycle': cycle, 'length': length}
                        all_tasks.append(('shape_cycle', 5, task_params))
            elif cycle_len == 5:
                for combo in permutations(shapes, 5):
                    cycle = list(combo)
                    for length in [7, 8]:
                        task_params = {'cycle': cycle, 'length': length}
                        all_tasks.append(('shape_cycle', 5, task_params))
        
        # Type 6: Color Cycle
        for combo in permutations(COLORS, 3):
            cycle = list(combo)
            for length in [5, 6, 7, 8]:
                task_params = {'cycle': cycle, 'length': length}
                all_tasks.append(('color_cycle', 6, task_params))
        for combo in permutations(COLORS, 4):
            cycle = list(combo)
            for length in [6, 7, 8]:
                task_params = {'cycle': cycle, 'length': length}
                all_tasks.append(('color_cycle', 6, task_params))
        
        # Type 7: Direction Cycle
        position_sets_3 = [
            ['top', 'bottom', 'left'], ['left', 'right', 'top'], ['top', 'bottom', 'right'],
            ['top-left', 'bottom-right', 'top-right'], ['top-right', 'bottom-left', 'top-left'],
            ['left', 'right', 'bottom'], ['top-left', 'bottom-left', 'top-right']
        ]
        position_sets_4 = [
            ['top', 'bottom', 'left', 'right'], ['top-left', 'top-right', 'bottom-left', 'bottom-right'],
            ['top', 'bottom', 'left', 'right'], ['left', 'right', 'top', 'bottom'],
            ['top', 'left', 'bottom', 'right']
        ]
        position_sets_5 = [
            ['top', 'bottom', 'left', 'right', 'top-left'],
            ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'top'],
            ['top', 'bottom', 'left', 'right', 'center']
        ]
        
        for cycle in position_sets_3:
            for length in [5, 6, 7, 8]:
                task_params = {'cycle': cycle, 'length': length}
                all_tasks.append(('direction_cycle', 7, task_params))
        
        for cycle in position_sets_4:
            for length in [6, 7, 8]:
                task_params = {'cycle': cycle, 'length': length}
                all_tasks.append(('direction_cycle', 7, task_params))
        
        for cycle in position_sets_5:
            for length in [7, 8]:
                task_params = {'cycle': cycle, 'length': length}
                all_tasks.append(('direction_cycle', 7, task_params))
        
        # Type 8: Mixed Sequence (Color + Shape)
        color_shape_cycles = []
        limit_reached = False
        for color_combo in permutations(COLORS, 3):
            if limit_reached:
                break
            for shape_combo in permutations(SHAPE_MAP.keys(), 3):
                cycle = [f"{color}{shape}" for color, shape in zip(color_combo, shape_combo)]
                color_shape_cycles.append(cycle)
                if len(color_shape_cycles) >= 48:
                    limit_reached = True
                    break
        
        for cycle in color_shape_cycles:
            for length in [6, 7, 8]:
                task_params = {'cycle': cycle, 'length': length, 'mixed_type': 'color_shape'}
                all_tasks.append(('mixed', 8, task_params))
        
        return all_tasks
