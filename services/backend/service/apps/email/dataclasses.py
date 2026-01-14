from dataclasses import dataclass


@dataclass
class EmailAttachmentProperty:
    filename: str
    mimetype: str
    content: bytes
