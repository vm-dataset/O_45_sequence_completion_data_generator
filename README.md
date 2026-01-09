# Sequence Completion Task Data Generator 🎲

A data generator for creating sequence completion reasoning tasks. Generates synthetic sequences with patterns (arithmetic, geometric, Fibonacci, shape cycles, color cycles, direction cycles, and mixed sequences) for video model evaluation.

This task generator follows the [template-data-generator](https://github.com/vm-dataset/template-data-generator.git) format and is compatible with [VMEvalKit](https://github.com/Video-Reason/VMEvalKit.git).

Repository: [O_45_sequence_completion_data_generator](https://github.com/vm-dataset/O_45_sequence_completion_data_generator)

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/vm-dataset/O_45_sequence_completion_data_generator.git
cd O_45_sequence_completion_data_generator

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 4. Generate tasks
python3 examples/generate.py --num-samples 50
```

---

## 📁 Structure

```
sequence-completion-task-data-generator/
├── core/                           # ✅ Standard utilities
│   ├── base_generator.py          # Abstract base class
│   ├── schemas.py                 # Pydantic models
│   ├── image_utils.py             # Image helpers
│   ├── sequence_renderer.py       # Sequence rendering utilities
│   ├── video_utils.py             # Video generation
│   └── output_writer.py           # File output
├── src/                            # ⚠️ Task-specific logic
│   ├── generator.py               # Sequence completion generator
│   ├── prompts.py                 # Prompt templates
│   └── config.py                  # Configuration
├── examples/
│   └── generate.py                # Entry point
└── data/questions/                # Generated output
```

---

## 📦 Output Format

Every generator produces:

```
data/questions/sequence_completion_task/{task_id}/
├── first_frame.png          # Initial sequence with "?" (REQUIRED)
├── final_frame.png          # Complete sequence with answer (REQUIRED)
├── prompt.txt               # Instructions (REQUIRED)
└── ground_truth.mp4         # Solution video (OPTIONAL)
```

---

## 🎯 Task Types

The generator creates 8 different types of sequence completion tasks:

1. **Arithmetic Sequences** - Linear number sequences with constant difference
2. **Geometric Sequences** - Exponential sequences with constant ratio
3. **Power Sequences** - Square number sequences
4. **Fibonacci Sequences** - Additive sequences where each element is the sum of previous two
5. **Shape Cycles** - Repeating patterns of shapes (○, □, △, ◇, star)
6. **Color Cycles** - Repeating patterns of colors (red, blue, green, yellow, orange)
7. **Direction Cycles** - Repeating patterns of directions (top, bottom, left, right, etc.)
8. **Mixed Sequences** - Combinations of color and shape in cycles

Total: **2037+ possible task combinations**

---

## 📋 Configuration

### Task Configuration (`src/config.py`)

```python
class TaskConfig(GenerationConfig):
    domain: str = "sequence_completion"
    image_size: tuple[int, int] = (1024, 1024)
    generate_videos: bool = True  # Generate ground truth videos
    video_fps: int = 10
    task_types: list[int] = [1, 2, 3, 4, 5, 6, 7, 8]  # Which types to generate
    max_tasks_per_type: int = None  # Limit per type (None = all)
```

### Command Line Usage

```bash
# Generate tasks (default: includes videos)
python3 examples/generate.py --num-samples 100 --output data/questions

# Generate without videos
python3 examples/generate.py --num-samples 100 --output data/questions --no-videos

# Generate with specific seed for reproducibility
python3 examples/generate.py --num-samples 100 --output data/questions --seed 42
```

---

## 🎨 Customization

The task generator is implemented in three main files:

### 1. `src/generator.py`
- `TaskGenerator` class: Implements sequence generation logic
- Generates 8 types of sequences with various patterns
- Renders sequences using `SequenceRenderer`

### 2. `src/prompts.py`
- Prompt templates for each task type
- Instructions for video models to complete sequences

### 3. `src/config.py`
- Task-specific configuration parameters
- Video generation settings
- Task type selection

---

## 🔧 Dependencies

- `numpy` - Numerical operations
- `Pillow` - Image processing
- `pydantic` - Data validation
- `matplotlib` - Sequence rendering
- `opencv-python` - Video generation

---

## 📊 Example Output

Each generated task includes:
- **First Frame**: Sequence with missing element (shown as "?")
- **Final Frame**: Complete sequence with correct answer
- **Prompt**: Natural language instruction
- **Video**: Smooth transition from first to final frame (optional)

The sequences test pattern recognition, mathematical reasoning, and logical extrapolation capabilities in video models.

---

## 📝 License

See LICENSE file for details.
