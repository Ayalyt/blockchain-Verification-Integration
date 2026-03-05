# enum for vulnerable type

from enum import Enum


class VulnerabilityEnum(Enum):
    none = 'none'
    confidentiality = 'confidentiality'
    integrity = 'integrity'
