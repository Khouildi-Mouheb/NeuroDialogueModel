from dataclasses import dataclass


@dataclass
class AppConfig:
    """Top-level app configuration for behavior / feature flags."""
    free_mode: bool = False
    enable_telemetry: bool = False
    default_max_retries: int = 1

    def to_dict(self):
        return self.__dict__.copy()
