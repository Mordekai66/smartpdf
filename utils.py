import logging
from pathlib import Path

import fitz


logger = logging.getLogger("SmartPDFDarkMode")


def setup_logging():
    """Configure clear console logging without creating extra log files."""
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    logger.propagate = False


def validate_paths(input_pdf_path, output_pdf_path):
    """Validate input/output paths before starting conversion."""
    input_path = Path(input_pdf_path).expanduser()
    output_path = Path(output_pdf_path).expanduser()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not input_path.is_file():
        raise ValueError("Input path is not a file.")

    if input_path.suffix.lower() != ".pdf":
        raise ValueError("Input file must have a .pdf extension.")

    if output_path.suffix.lower() != ".pdf":
        raise ValueError("Output file must have a .pdf extension.")

    if not output_path.parent.exists():
        raise FileNotFoundError(
            f"Output folder does not exist: {output_path.parent}"
        )

    if input_path.resolve() == output_path.resolve():
        raise ValueError("Input and output paths must be different.")

    return input_path, output_path


def validate_output_pdf(path, expected_pages):
    """Reopen the temporary output and verify that it is a valid PDF."""
    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError("Output PDF was not created or is empty.")

    check_doc = None
    try:
        check_doc = fitz.open(str(path))

        if not check_doc.is_pdf:
            raise RuntimeError("Generated file is not a valid PDF.")

        if check_doc.needs_pass:
            raise RuntimeError("Generated PDF unexpectedly requires a password.")

        if len(check_doc) != expected_pages:
            raise RuntimeError(
                f"Page count mismatch: expected {expected_pages}, "
                f"found {len(check_doc)}."
            )


        for page_index in range(len(check_doc)):
            _ = check_doc[page_index].rect

    except Exception as error:
        raise RuntimeError(f"Output validation failed: {error}") from error

    finally:
        if check_doc is not None:
            check_doc.close()
