"""
Sequence Renderer for Sequence Completion Tasks

Renders sequences of elements (numbers, shapes, colors, positions, mixed) for visualization.
"""

import numpy as np
from typing import List, Any, Optional, Tuple
from PIL import Image
import io
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, RegularPolygon, Polygon, FancyArrowPatch
from pathlib import Path

# Shape mappings
SHAPE_MAP = {
    '○': 'circle',
    '□': 'square',
    '△': 'triangle',
    '◇': 'diamond',
    'star': 'star'
}

# Color list
COLORS = ['red', 'blue', 'green', 'yellow', 'orange']

# Position list (2D only)
POSITIONS = ['top', 'bottom', 'left', 'right', 'center', 'top-left', 'top-right', 
             'bottom-left', 'bottom-right']


class SequenceRenderer:
    """Renderer for different types of sequence elements."""
    
    def __init__(self, figsize=(10, 10), dpi=150, output_size=(1024, 1024)):
        """
        Initialize sequence renderer.
        
        Args:
            figsize: Figure size in inches
            dpi: Dots per inch
            output_size: Target output image size in pixels (width, height)
        """
        self.figsize = figsize
        self.dpi = dpi
        self.output_size = output_size
        self.canvas_size = 10  # Coordinate system: 0 to 10
        self.blank_cell_width = 1.2
        self.blank_cell_height = 1.2
        self.shape_size = 0.55
        self.color_circle_size = 0.55
        self.number_fontsize = 50
        self.text_fontsize = 32
    
    def render_sequence(self, sequence: List[Any], show_blank: bool = False,
                       output_path: Optional[str] = None) -> Image.Image:
        """
        Render a sequence of elements. Returns PIL Image.
        
        Args:
            sequence: List of sequence elements (numbers, shapes, colors, positions, or mixed)
            show_blank: If True, show question mark for the last element (for first_frame)
            output_path: Optional path to save the image
        
        Returns:
            PIL Image of the rendered sequence
        """
        num_elements = len(sequence)
        
        # Calculate spacing and positioning
        safe_margin = 0.8
        target_spacing = 1.5
        available_width = self.canvas_size - 2 * safe_margin
        max_element_radius_base = max(self.shape_size, self.color_circle_size, self.blank_cell_width / 2)
        
        # Calculate element spacing and scale
        element_size_scale = 1.0
        element_spacing = target_spacing
        
        total_width_needed = (num_elements - 1) * element_spacing + max_element_radius_base * 2
        
        if total_width_needed > available_width:
            max_radius_available = (available_width - (num_elements - 1) * target_spacing) / 2
            if max_radius_available > 0:
                element_size_scale = max(0.3, min(1.0, max_radius_available / max_element_radius_base))
                element_spacing = target_spacing
            else:
                min_spacing = 1.0
                max_radius_available = (available_width - (num_elements - 1) * min_spacing) / 2
                if max_radius_available > 0:
                    element_size_scale = max(0.3, min(1.0, max_radius_available / max_element_radius_base))
                    element_spacing = min_spacing
                else:
                    min_spacing = 0.8
                    max_radius_available = (available_width - (num_elements - 1) * min_spacing) / 2
                    element_size_scale = max(0.25, max_radius_available / max_element_radius_base) if max_radius_available > 0 else 0.25
                    element_size_scale = max(0.25, min(1.0, element_size_scale))
                    element_spacing = min_spacing
        
        max_element_radius = max_element_radius_base * element_size_scale
        self._current_scale = element_size_scale
        
        # Check if sequence contains numbers
        has_numbers = any(isinstance(elem, (int, float)) for elem in sequence if elem is not None)
        
        if has_numbers:
            # Edge-based spacing for numbers
            scale = element_size_scale
            fontsize = int(self.number_fontsize * scale)
            
            # Measure text widths
            temp_fig, temp_ax = plt.subplots(figsize=(1, 1))
            temp_ax.axis('off')
            
            number_widths = []
            for element in sequence:
                if element is None:
                    text_obj = temp_ax.text(0, 0, '?', fontsize=fontsize, ha='center', va='center',
                                           fontweight='bold')
                    bbox = text_obj.get_window_extent(renderer=temp_fig.canvas.get_renderer())
                    width = bbox.width / temp_fig.dpi * (self.canvas_size / self.figsize[0])
                    number_widths.append(width)
                    text_obj.remove()
                else:
                    text_obj = temp_ax.text(0, 0, str(element), fontsize=fontsize, ha='center', va='center',
                                           fontweight='bold')
                    bbox = text_obj.get_window_extent(renderer=temp_fig.canvas.get_renderer())
                    width = bbox.width / temp_fig.dpi * (self.canvas_size / self.figsize[0])
                    number_widths.append(width)
                    text_obj.remove()
            
            plt.close(temp_fig)
            
            gap_between_numbers = element_spacing * 0.5
            
            x_positions = []
            current_x = safe_margin
            
            for i in range(len(number_widths)):
                x_positions.append(current_x + number_widths[i] / 2)
                if i < len(number_widths) - 1:
                    current_x += number_widths[i] / 2 + gap_between_numbers + number_widths[i + 1] / 2
            
            # Center the sequence
            first_number_left_edge = x_positions[0] - number_widths[0] / 2
            last_number_right_edge = x_positions[-1] + number_widths[-1] / 2
            actual_total_width = last_number_right_edge - first_number_left_edge
            actual_sequence_center = first_number_left_edge + actual_total_width / 2
            canvas_center = self.canvas_size / 2
            offset = canvas_center - actual_sequence_center
            x_positions = [x + offset for x in x_positions]
        else:
            # Center-based spacing for non-numbers
            total_width = (num_elements - 1) * element_spacing + max_element_radius * 2
            temp_start_x = max_element_radius
            first_element_left = temp_start_x - max_element_radius
            last_element_right = temp_start_x + (num_elements - 1) * element_spacing + max_element_radius
            actual_total_width = last_element_right - first_element_left
            actual_sequence_center = first_element_left + actual_total_width / 2
            canvas_center = self.canvas_size / 2
            center_offset = canvas_center - actual_sequence_center
            start_x = temp_start_x + center_offset
            x_positions = [start_x + i * element_spacing for i in range(num_elements)]
            
            # Ensure margins
            first_pos_left = x_positions[0] - max_element_radius
            last_pos_right = x_positions[-1] + max_element_radius
            if first_pos_left < safe_margin:
                shift = safe_margin - first_pos_left
                x_positions = [x + shift for x in x_positions]
            elif last_pos_right > self.canvas_size - safe_margin:
                shift = (self.canvas_size - safe_margin) - last_pos_right
                x_positions = [x + shift for x in x_positions]
        
        center_y = self.canvas_size / 2
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        ax.set_xlim(0, self.canvas_size)
        ax.set_ylim(0, self.canvas_size)
        ax.axis('off')
        
        # Render elements
        for i, element in enumerate(sequence):
            x = x_positions[i]
            y = center_y
            
            if i == len(sequence) - 1 and show_blank:
                # Show question mark
                scale = getattr(self, '_current_scale', 1.0)
                question_fontsize = int(self.number_fontsize * scale)
                ax.text(x, y, '?', fontsize=question_fontsize, ha='center', va='center',
                       fontweight='bold', color='black')
            else:
                # Render the element
                self._render_element(ax, element, x, y)
        
        plt.tight_layout(pad=0)
        
        # Convert to PIL Image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=self.dpi, pad_inches=0)
        buf.seek(0)
        img = Image.open(buf).convert('RGB')
        plt.close()
        
        # Resize to exact output size if specified
        if self.output_size:
            img = img.resize(self.output_size, Image.Resampling.LANCZOS)
        
        # Save if path provided
        if output_path:
            img.save(output_path)
        
        return img
    
    def _render_element(self, ax, element: Any, x: float, y: float) -> None:
        """Render a single element based on its type."""
        if element is None:
            return
        
        if isinstance(element, (int, float)):
            # Number
            scale = getattr(self, '_current_scale', 1.0)
            ax.text(x, y, str(element), fontsize=int(self.number_fontsize * scale),
                   ha='center', va='center', fontweight='bold', color='black')
        
        elif isinstance(element, str):
            if element in SHAPE_MAP:
                self._render_shape(ax, element, x, y)
            elif element in COLORS:
                self._render_color(ax, element, x, y)
            elif element in POSITIONS:
                self._render_position(ax, element, x, y)
            elif '+' in element or any(shape in element for shape in SHAPE_MAP.keys()):
                self._render_mixed(ax, element, x, y)
            elif '-' in element and any(color in element for color in COLORS):
                self._render_mixed(ax, element, x, y)
            else:
                scale = getattr(self, '_current_scale', 1.0)
                ax.text(x, y, element, fontsize=int(self.text_fontsize * scale),
                       ha='center', va='center', fontweight='bold', color='black')
        
        elif isinstance(element, (list, tuple)):
            if len(element) == 2:
                self._render_mixed(ax, f"{element[0]}{element[1]}", x, y)
            else:
                scale = getattr(self, '_current_scale', 1.0)
                ax.text(x, y, str(element), fontsize=int(self.text_fontsize * scale),
                       ha='center', va='center', fontweight='bold', color='black')
    
    def _render_shape(self, ax, shape: str, x: float, y: float) -> None:
        """Render a shape."""
        shape_type = SHAPE_MAP[shape]
        scale = getattr(self, '_current_scale', 1.0)
        bbox_size = self.shape_size * 2 * scale
        
        if shape_type == 'circle':
            circle = Circle((x, y), bbox_size / 2, facecolor='lightblue', edgecolor='black', linewidth=2)
            ax.add_patch(circle)
        elif shape_type == 'square':
            square_size = bbox_size * 0.85
            square = Rectangle((x - square_size / 2, y - square_size / 2), square_size, square_size,
                             facecolor='lightblue', edgecolor='black', linewidth=2)
            ax.add_patch(square)
        elif shape_type == 'triangle':
            triangle_radius = bbox_size / np.sqrt(3)
            triangle = RegularPolygon((x, y), 3, radius=triangle_radius,
                                    facecolor='lightblue', edgecolor='black', linewidth=2)
            ax.add_patch(triangle)
        elif shape_type == 'diamond':
            half_size = bbox_size / 2
            diamond_points = [
                (x, y - half_size),
                (x + half_size, y),
                (x, y + half_size),
                (x - half_size, y),
            ]
            diamond = Polygon(diamond_points, closed=True, facecolor='lightblue',
                            edgecolor='black', linewidth=2)
            ax.add_patch(diamond)
        elif shape_type == 'star':
            star_radius = bbox_size / 2.2
            star = RegularPolygon((x, y), 5, radius=star_radius,
                               facecolor='lightblue', edgecolor='black', linewidth=2)
            ax.add_patch(star)
    
    def _render_color(self, ax, color: str, x: float, y: float) -> None:
        """Render a color as a colored circle."""
        scale = getattr(self, '_current_scale', 1.0)
        circle = Circle((x, y), self.color_circle_size * scale, facecolor=color,
                       edgecolor='black', linewidth=2)
        ax.add_patch(circle)
    
    def _render_position(self, ax, position: str, x: float, y: float) -> None:
        """Render a position as an arrow."""
        scale = getattr(self, '_current_scale', 1.0)
        arrow_size = self.shape_size * scale * 2.2
        arrow_lw = 5 * scale
        center_arrow_lw = 4 * scale
        arrow_head_scale = 30 * scale
        center_arrow_head_scale = 25 * scale
        
        if 'top' in position and 'left' in position:
            arrow = FancyArrowPatch((x + arrow_size * 0.35, y + arrow_size * 0.35),
                                   (x - arrow_size * 0.35, y - arrow_size * 0.35),
                                   arrowstyle='->', mutation_scale=arrow_head_scale, lw=arrow_lw, color='black')
            ax.add_patch(arrow)
        elif 'top' in position and 'right' in position:
            arrow = FancyArrowPatch((x - arrow_size * 0.35, y + arrow_size * 0.35),
                                   (x + arrow_size * 0.35, y - arrow_size * 0.35),
                                   arrowstyle='->', mutation_scale=arrow_head_scale, lw=arrow_lw, color='black')
            ax.add_patch(arrow)
        elif 'bottom' in position and 'left' in position:
            arrow = FancyArrowPatch((x + arrow_size * 0.35, y - arrow_size * 0.35),
                                   (x - arrow_size * 0.35, y + arrow_size * 0.35),
                                   arrowstyle='->', mutation_scale=arrow_head_scale, lw=arrow_lw, color='black')
            ax.add_patch(arrow)
        elif 'bottom' in position and 'right' in position:
            arrow = FancyArrowPatch((x - arrow_size * 0.35, y - arrow_size * 0.35),
                                   (x + arrow_size * 0.35, y + arrow_size * 0.35),
                                   arrowstyle='->', mutation_scale=arrow_head_scale, lw=arrow_lw, color='black')
            ax.add_patch(arrow)
        elif 'top' in position:
            arrow = FancyArrowPatch((x, y + arrow_size * 0.5), (x, y - arrow_size * 0.5),
                                   arrowstyle='->', mutation_scale=arrow_head_scale, lw=arrow_lw, color='black')
            ax.add_patch(arrow)
        elif 'bottom' in position:
            arrow = FancyArrowPatch((x, y - arrow_size * 0.5), (x, y + arrow_size * 0.5),
                                   arrowstyle='->', mutation_scale=arrow_head_scale, lw=arrow_lw, color='black')
            ax.add_patch(arrow)
        elif 'left' in position:
            arrow = FancyArrowPatch((x + arrow_size * 0.5, y), (x - arrow_size * 0.5, y),
                                   arrowstyle='->', mutation_scale=arrow_head_scale, lw=arrow_lw, color='black')
            ax.add_patch(arrow)
        elif 'right' in position:
            arrow = FancyArrowPatch((x - arrow_size * 0.5, y), (x + arrow_size * 0.5, y),
                                   arrowstyle='->', mutation_scale=arrow_head_scale, lw=arrow_lw, color='black')
            ax.add_patch(arrow)
        elif 'center' in position:
            small_arrow = arrow_size * 0.4
            for (dx, dy) in [(0, small_arrow * 0.5), (0, -small_arrow * 0.5),
                            (small_arrow * 0.5, 0), (-small_arrow * 0.5, 0)]:
                arrow = FancyArrowPatch((x + dx, y + dy), (x - dx, y - dy),
                                       arrowstyle='->', mutation_scale=center_arrow_head_scale,
                                       lw=center_arrow_lw, color='black')
                ax.add_patch(arrow)
    
    def _render_mixed(self, ax, mixed: str, x: float, y: float) -> None:
        """Render a mixed element (color+shape, color+position, shape+position)."""
        scale = getattr(self, '_current_scale', 1.0)
        shape_chars = ['○', '□', '△', '◇', 'star']
        
        # Check if it starts with a color
        color_part = None
        remaining = None
        
        for color in COLORS:
            if mixed.startswith(color):
                color_part = color
                remaining = mixed[len(color):]
                if remaining.startswith('-'):
                    remaining = remaining[1:]
                break
        
        if color_part:
            color_en = color_part
            
            if remaining and remaining in SHAPE_MAP:
                # Color + Shape
                shape_type = SHAPE_MAP[remaining]
                bbox_size = self.shape_size * 2 * scale
                
                if shape_type == 'circle':
                    circle = Circle((x, y), bbox_size / 2, facecolor=color_en, edgecolor='black', linewidth=2)
                    ax.add_patch(circle)
                elif shape_type == 'square':
                    square_size = bbox_size * 0.85
                    square = Rectangle((x - square_size / 2, y - square_size / 2), square_size, square_size,
                                     facecolor=color_en, edgecolor='black', linewidth=2)
                    ax.add_patch(square)
                elif shape_type == 'triangle':
                    triangle_radius = bbox_size / np.sqrt(3)
                    triangle = RegularPolygon((x, y), 3, radius=triangle_radius,
                                            facecolor=color_en, edgecolor='black', linewidth=2)
                    ax.add_patch(triangle)
                elif shape_type == 'diamond':
                    half_size = bbox_size / 2
                    diamond_points = [
                        (x, y - half_size),
                        (x + half_size, y),
                        (x, y + half_size),
                        (x - half_size, y),
                    ]
                    diamond = Polygon(diamond_points, closed=True, facecolor=color_en,
                                    edgecolor='black', linewidth=2)
                    ax.add_patch(diamond)
                elif shape_type == 'star':
                    star_radius = bbox_size / 2.2
                    star = RegularPolygon((x, y), 5, radius=star_radius,
                                       facecolor=color_en, edgecolor='black', linewidth=2)
                    ax.add_patch(star)
                return
            
            elif remaining and (remaining in POSITIONS or any(p in remaining for p in POSITIONS)):
                # Color + Position
                circle = Circle((x, y), self.color_circle_size * scale, facecolor=color_en,
                               edgecolor='black', linewidth=2)
                ax.add_patch(circle)
                self._render_position(ax, remaining, x, y)
                return
        
        # Check if it's shape+position
        for shape_char in shape_chars:
            if mixed.startswith(shape_char):
                position_part = mixed[len(shape_char):]
                if position_part in POSITIONS or any(p in position_part for p in POSITIONS):
                    self._render_shape(ax, shape_char, x, y)
                    self._render_position(ax, position_part, x, y)
                    return
        
        # Fallback: render as text
        ax.text(x, y, mixed, fontsize=int(self.text_fontsize * scale),
               ha='center', va='center', fontweight='bold', color='black')

