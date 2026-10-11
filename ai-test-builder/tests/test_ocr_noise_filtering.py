from __future__ import annotations

from src.ingestion.normalizer import normalize_extraction


def test_normalize_extraction_filters_obvious_ocr_answer_noise_for_scanned_sources():
    extraction = {
        "file_name": "scan.pdf",
        "source_kind": "scanned_pdf",
        "segments": [
            {
                "page_number": 1,
                "text": "\n".join(
                    [
                        "Name: | lol? A KAY",
                        "SCH3U Unit 2 Chemical Reactions Test",
                        "Application Questions (18 Marks)",
                        "1. Silver is a highly valuable metal used in batteries and medicine.",
                        "Ug coull USC a More fractive prey 1/\\C",
                        "Gaaum Jo Aiciece dhe Silver a",
                        "2. Many antacid tablets contain calcium carbonate, CaCO3(aq).",
                        "Blase AS Sou _JunSd H/ POSEN) it p Ye fs",
                        "Yoo Coll Ppove ane Gore-nOn Sein",
                    ]
                ),
            }
        ],
        "metadata": {"extraction_method": "ocr"},
    }

    normalized = normalize_extraction(extraction)
    text = normalized["text"]

    assert "SCH3U Unit 2 Chemical Reactions Test" in text
    assert "Application Questions (18 Marks)" in text
    assert "1. Silver is a highly valuable metal used in batteries and medicine." in text
    assert "2. Many antacid tablets contain calcium carbonate, CaCO3(aq)." in text
    assert "Ug coull USC a More fractive prey 1/\\C" not in text
    assert "Blase AS Sou _JunSd H/ POSEN) it p Ye fs" not in text
    assert "Yoo Coll Ppove ane Gore-nOn Sein" not in text
    assert normalized["metadata"]["ocr_noise_lines_removed"] >= 3


def test_normalize_extraction_does_not_filter_non_ocr_sources():
    extraction = {
        "file_name": "source.docx",
        "source_kind": "docx",
        "segments": [
            {
                "index": 1,
                "text": "Name: Student Copy\nSection A - Multiple Choice\n1. Explain the concept clearly.",
            }
        ],
        "metadata": {"extraction_method": "python-docx"},
    }

    normalized = normalize_extraction(extraction)

    assert "Name: Student Copy" in normalized["text"]
    assert "ocr_noise_lines_removed" not in normalized["metadata"]
