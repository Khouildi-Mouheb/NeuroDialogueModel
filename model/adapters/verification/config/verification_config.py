"""
Verification configuration - Thresholds and settings for verification system.
"""
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class VerificationConfig:
    """Configuration for verification system"""
    
    # Thresholds
    safety_threshold: float = 0.8
    empathy_threshold: float = 0.6
    appropriateness_threshold: float = 0.7
    
    # Model paths
    safety_model_path: str = "unitary/toxic-bert"
    empathy_model_path: str = "microsoft/deberta-v3-base"
    
    # Behavior
    enable_fallback: bool = True
    enable_revision: bool = True
    strict_mode: bool = False  # If True, reject on any issue
    
    # Weights for score aggregation
    score_weights: Dict[str, float] = field(default_factory=lambda: {
        'safety': 0.4,
        'empathy': 0.3,
        'appropriateness': 0.3
    })
    
    # Logging
    log_all_verifications: bool = True
    log_failed_only: bool = False
    
    def __post_init__(self):
        """Validate configuration"""
        # Ensure thresholds are valid
        for threshold in [self.safety_threshold, self.empathy_threshold, self.appropriateness_threshold]:
            if not 0.0 <= threshold <= 1.0:
                raise ValueError(f"Thresholds must be between 0 and 1")
        
        # Ensure weights sum to reasonable value
        total_weight = sum(self.score_weights.values())
        if not 0.9 <= total_weight <= 1.1:
            raise ValueError(f"Score weights should sum to ~1.0, got {total_weight}")
