import os
import tempfile
from pathlib import Path

import fitz
from PIL import Image

from image_processor import encode_page, get_image_rectangles, restore_original_image_regions, smart_dark_mapping

from utils import logger, setup_logging, validate_output_pdf, validate_paths


def pdf_to_dark_mode(input_pdf_path, output_pdf_path, dpi=144, preserve_images=True, image_padding=0.5, output_format="PNG", quality=90, progress_callback=None, background=(28, 31, 38), foreground=(232, 235, 241)):
    """
    Convert a PDF to a raster-based Dark Mode PDF with safer file handling.

    Stage 4 adds:
    - Input validation.
    - Clear logging and page-specific errors.
    - Temporary output file.
    - Reopen and validate output before replacing destination.
    - Cleanup of temporary files after failures.

    The original input PDF is never modified.
    """
    setup_logging()

    if dpi < 72 or dpi > 400:
        raise ValueError("DPI must be between 72 and 400.")

    if image_padding < 0:
        raise ValueError("image_padding cannot be negative.")

    if not 40 <= quality <= 100:
        raise ValueError("quality must be between 40 and 100.")

    output_format = output_format.upper()
    if output_format == "JPG":
        output_format = "JPEG"

    if output_format not in ("PNG", "JPEG"):
        raise ValueError("output_format must be PNG or JPEG.")

    input_path, output_path = validate_paths(input_pdf_path, output_pdf_path)

    input_size = input_path.stat().st_size
    scale = dpi / 72.0
    source_doc = None
    output_doc = None
    temporary_path = None
    conversion_succeeded = False

    try:
        logger.info("Opening input PDF: %s", input_path)
        source_doc = fitz.open(str(input_path))

        if not source_doc.is_pdf:
            raise ValueError("Input file is not a valid PDF.")

        if source_doc.needs_pass:
            raise ValueError(
                "This PDF is password-protected. Unlock it before conversion."
            )

        total_pages = len(source_doc)
        if total_pages == 0:
            raise ValueError("Input PDF contains no pages.")

        logger.info("PDF opened successfully. Pages: %s", total_pages)
        logger.info(
            "Settings: %s DPI | %s | quality: %s",
            dpi,
            output_format,
            quality if output_format == "JPEG" else "lossless",
        )



        # Create a temporary file beside the output PDF.
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{output_path.stem}_",
            suffix=".tmp.pdf",
            dir=str(output_path.parent),
        )
        os.close(fd)
        os.unlink(temp_name)
        temporary_path = Path(temp_name)

        output_doc = fitz.open()

        for page_number, page in enumerate(source_doc, start=1):
            logger.info("Processing page %s/%s", page_number, total_pages)
            if progress_callback:
                progress_callback(page_number - 1, total_pages)

            try:
                image_rects = (
                    get_image_rectangles(page, padding=image_padding)
                    if preserve_images
                    else []
                )

                # Render the PDF page as an image.
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(scale, scale),
                    colorspace=fitz.csRGB,
                    alpha=False,
                    annots=True,
                )

                original_image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

                # Apply the dark color mapping.
                processed_image = smart_dark_mapping(original_image, background=background, foreground=foreground)

                # Restore original images when requested.
                if preserve_images and image_rects:
                    processed_image = restore_original_image_regions(
                        original_image=original_image,
                        processed_image=processed_image,
                        rectangles=image_rects,
                        page_rect=page.rect,
                        scale=scale,
                        pix_x=pix.x,
                        pix_y=pix.y,
                    )

                page_bytes = encode_page(
                    processed_image,
                    output_format=output_format,
                    quality=quality,
                )

                page_rect = page.rect
                new_page = output_doc.new_page(
                    width=page_rect.width,
                    height=page_rect.height,
                )
                new_page.insert_image(new_page.rect, stream=page_bytes)


                del pix, original_image, processed_image
                del page_bytes, image_rects

            except Exception as page_error:
                raise RuntimeError(
                    f"Failed while processing page {page_number}: {page_error}"
                ) from page_error

        if progress_callback:
            progress_callback(total_pages, total_pages)

        logger.info("All pages processed. Saving temporary PDF...")
        output_doc.save(str(temporary_path), garbage=4, deflate=True)

        output_doc.close()
        output_doc = None

        source_doc.close()
        source_doc = None

        logger.info("Validating generated PDF...")
        # Replace the output only after the temporary PDF passes validation.
        validate_output_pdf(temporary_path, total_pages)


        os.replace(temporary_path, output_path)
        temporary_path = None
        conversion_succeeded = True

    except Exception:
        logger.exception("Conversion failed. Existing output was not replaced.")
        raise

    finally:
        if output_doc is not None:
            output_doc.close()

        if source_doc is not None:
            source_doc.close()

        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                logger.warning(
                    "Could not remove temporary file: %s",
                    temporary_path,
                )

    if conversion_succeeded:
        output_size = output_path.stat().st_size
        size_change = output_size - input_size
        ratio = (output_size / input_size * 100) if input_size else 0
        reduction = (1 - output_size / input_size) * 100 if input_size else 0

        logger.info("Conversion completed successfully.")
        logger.info("Original size: %.2f MB", input_size / 1024 / 1024)
        logger.info("Output size: %.2f MB", output_size / 1024 / 1024)
        logger.info("Size change: %+.2f MB", size_change / 1024 / 1024)
        logger.info("Output ratio: %.1f%%", ratio)

        if reduction >= 0:
            logger.info("Size reduction: %.1f%%", reduction)
        else:
            logger.info("Size increase: %.1f%%", abs(reduction))

        logger.info("Saved to: %s", output_path)
