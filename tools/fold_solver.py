"""
NouGenDesign Fold-Aware Solver and Visual Intelligence Density (VID) Engine.

Implements the deterministic fold formulas specified in relay 20261004T051626Z:
- Viewport and Inset Solver: Fy = H - I_top - I_bottom
- Above-Fold Ratio: AF_i = max(0, min(y_i + h_i, Fy) - max(y_i, 0)) / h_i
- Fold Density and Information Cost: Cost_i = Area_i / (W * Fy)
- Placement Priority Solver: P_i = (Goal * Urgency * Action * Context) / (1 + Complexity + Distraction)
- Fold Continuation: 0.08H <= Peek_next <= 0.18H
- Hero Solver: H_hero = H_identity + H_state + H_primaryAction + S_required <= Fy
- Visual Intelligence Density: VID = (Clarity * Value * Actionability * Hierarchy) / (Cost + Load + Noise + Interaction)
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


@dataclass
class Viewport:
    width: float
    height: float
    inset_top: float = 64.0     # Navigation / top chrome
    inset_bottom: float = 0.0   # Bottom bar / safe area

    @property
    def fy(self) -> float:
        """Effective fold height after subtracting fixed insets."""
        return max(0.0, self.height - self.inset_top - self.inset_bottom)

    @property
    def area_above_fold(self) -> float:
        """Total usable area above the fold."""
        return self.width * self.fy


@dataclass
class UIElement:
    name: str
    y: float
    height: float
    width: float
    # Placement scoring terms [0.0 - 1.0]
    goal_relevance: float = 1.0
    urgency: float = 1.0
    actionability: float = 1.0
    context_fit: float = 1.0
    complexity: float = 0.1
    distraction: float = 0.0
    confidence: float = 1.0

    def compute_af(self, viewport: Viewport) -> float:
        """Above-Fold Factor AF_i: 1 = fully above, 0 = below, (0,1) = crosses fold."""
        if self.height <= 0:
            return 0.0
        y_top = self.y
        y_bottom = self.y + self.height
        visible_top = max(y_top, 0.0)
        visible_bottom = min(y_bottom, viewport.fy)
        overlap = max(0.0, visible_bottom - visible_top)
        return min(1.0, overlap / self.height)

    def area_cost(self, viewport: Viewport) -> float:
        """Fraction of above-fold area consumed by this element."""
        if viewport.area_above_fold <= 0:
            return 0.0
        return (self.width * self.height) / viewport.area_above_fold

    def priority_score(self) -> float:
        """
        P_i = (Goal * Urgency * Action * Context) / (1 + Complexity + Distraction)
        """
        numerator = self.goal_relevance * self.urgency * self.actionability * self.context_fit
        denominator = 1.0 + self.complexity + self.distraction
        return numerator / denominator

    def information_value(self) -> float:
        """Value_i = Relevance * TaskImportance * Actionability * Confidence."""
        return self.goal_relevance * self.urgency * self.actionability * self.confidence


class FoldSolver:
    def __init__(self, viewport: Viewport, tau_high: float = 0.65, tau_low: float = 0.35):
        self.viewport = viewport
        self.tau_high = tau_high
        self.tau_low = tau_low

    def classify_placement(self, element: UIElement) -> str:
        """
        ABOVE_FOLD if P_i >= tau_H
        FOLD_EDGE  if tau_L < P_i < tau_H
        BELOW_FOLD if P_i <= tau_L
        """
        p = element.priority_score()
        if p >= self.tau_high:
            return "ABOVE_FOLD"
        elif p > self.tau_low:
            return "FOLD_EDGE"
        else:
            return "BELOW_FOLD"

    def verify_continuation_peek(self, peek_height: float) -> Tuple[bool, float, float]:
        """
        0.08H <= Peek_next <= 0.18H
        Returns (is_valid, min_allowed, max_allowed)
        """
        min_peek = 0.08 * self.viewport.height
        max_peek = 0.18 * self.viewport.height
        is_valid = min_peek <= peek_height <= max_peek
        return is_valid, min_peek, max_peek

    def compute_fold_density(self, elements: List[UIElement]) -> float:
        """FoldDensity = sum(Value_i) / sum(Cost_i) for above-fold elements."""
        total_val = 0.0
        total_cost = 0.0
        for elem in elements:
            af = elem.compute_af(self.viewport)
            if af > 0:
                total_val += elem.information_value() * af
                total_cost += elem.area_cost(self.viewport) * af
        return total_val / max(0.0001, total_cost)

    def compute_vid(
        self,
        task_clarity: float,
        info_value: float,
        actionability: float,
        hierarchy: float,
        pixel_cost: float,
        cognitive_load: float,
        visual_noise: float,
        interaction_cost: float,
    ) -> float:
        """
        VID = (TaskClarity * InformationValue * Actionability * Hierarchy) /
              (PixelCost + CognitiveLoad + VisualNoise + InteractionCost)
        """
        num = task_clarity * info_value * actionability * hierarchy
        den = pixel_cost + cognitive_load + visual_noise + interaction_cost
        return num / max(0.0001, den)
