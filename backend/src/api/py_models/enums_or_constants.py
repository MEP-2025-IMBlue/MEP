from enum import Enum

class ImageModality(str, Enum):
    CT = "CT"
    MRT = "MRT"
    CR = "CR"
    NONE = "Keins davon"

class InputFormat(str, Enum):
    DICOM = "dicom"
    NIFTI = "nifti"
    NONE = "Keins davon"

class OutputFormat(str, Enum):
    PNG = "png"
    JPEG = "jpeg"
    NPY = "npy"
    NONE = "Keins davon"

class ImageBodypart(str, Enum):
    HEAD = "head"
    CHEST = "chest"
    NONE = "Keins davon"

class ImagePurpose(str, Enum):
    SEGMENTATION = "segmentation"
    NONE = "Keins davon"

FORBIDDEN_COMMANDS = ["rm", "shutdown", "reboot"]



