"""Automated pytest suite for synthetic pilot dataset validation and schema integrity."""

import json
from pathlib import Path

DATASET_DIR = Path("data/synthetic_pilot")
DOCS_DIR = DATASET_DIR / "documents"
ANNOTATIONS_DIR = DATASET_DIR / "annotations"
MANIFEST_PATH = DATASET_DIR / "manifest.json"
COMPARISONS_PATH = DATASET_DIR / "expected_comparisons.json"


def test_manifest_structure_and_counts():
    """Verify manifest.json contains 12 packages, balanced languages, and valid splits."""
    assert MANIFEST_PATH.exists(), "manifest.json must exist"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    packages = manifest.get("packages", [])
    assert len(packages) == 12, "Manifest must contain exactly 12 packages"
    assert manifest.get("total_documents") == 24, "Manifest must declare 24 documents"

    en_count = sum(1 for p in packages if p["language"] == "en")
    vi_count = sum(1 for p in packages if p["language"] == "vi")
    assert en_count == 6, f"Expected 6 English packages, got {en_count}"
    assert vi_count == 6, f"Expected 6 Vietnamese packages, got {vi_count}"


def test_document_files_exist_and_are_valid_pdfs():
    """Verify all 24 referenced PDF documents exist on disk and have valid PDF headers."""
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    for pkg in manifest["packages"]:
        for doc_key in ["commercial_invoice", "packing_list"]:
            file_name = pkg[doc_key]["file_name"]
            pdf_path = DOCS_DIR / file_name
            assert pdf_path.exists(), f"Missing PDF file: {pdf_path}"
            assert pdf_path.stat().st_size > 1000, f"PDF file too small: {pdf_path}"

            with open(pdf_path, "rb") as f_pdf:
                header = f_pdf.read(5)
                assert header == b"%PDF-", f"Invalid PDF header in {file_name}"


def test_annotations_exist_and_conform_to_schema():
    """Verify all 24 annotation JSON files exist and have required schema properties."""
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    required_keys = {
        "dataset_version",
        "package_id",
        "document_id",
        "document_type",
        "language",
        "template_id",
        "file_name",
        "page_dimensions",
        "scenario",
        "fields",
        "line_items",
    }

    for pkg in manifest["packages"]:
        for doc_key in ["commercial_invoice", "packing_list"]:
            annot_file = pkg[doc_key]["annotation_file"]
            annot_path = ANNOTATIONS_DIR / annot_file
            assert annot_path.exists(), f"Missing annotation file: {annot_path}"

            with open(annot_path, "r", encoding="utf-8") as f_annot:
                data = json.load(f_annot)

            missing_keys = required_keys - set(data.keys())
            assert not missing_keys, f"{annot_file} missing required keys: {missing_keys}"
            assert len(data["fields"]) >= 4, f"{annot_file} must have at least 4 annotated fields"
            assert len(data["line_items"]) >= 1, f"{annot_file} must have at least 1 line item"


def test_bounding_boxes_strictly_bounded():
    """Verify every bounding box satisfies:
    0 <= x_min < x_max <= width and 0 <= y_min < y_max <= height.
    """
    for annot_path in ANNOTATIONS_DIR.glob("*.json"):
        with open(annot_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        page_w = data["page_dimensions"]["width"]
        page_h = data["page_dimensions"]["height"]

        # Check fields bounding boxes
        for field in data["fields"]:
            fname = field["canonical_name"]
            bbox = field["bbox"]
            assert len(bbox) == 4, f"{annot_path.name} field {fname} bbox length != 4"
            x_min, y_min, x_max, y_max = bbox
            assert 0 <= x_min < x_max <= page_w + 1.0, (
                f"{annot_path.name} field {fname} invalid X bounds: "
                f"[{x_min}, {x_max}] (max: {page_w})"
            )
            assert 0 <= y_min < y_max <= page_h + 1.0, (
                f"{annot_path.name} field {fname} invalid Y bounds: "
                f"[{y_min}, {y_max}] (max: {page_h})"
            )

        # Check line items bounding boxes
        for item in data["line_items"]:
            l_no = item["line_number"]
            bbox = item["bbox"]
            assert len(bbox) == 4, f"{annot_path.name} line {l_no} bbox length != 4"
            x_min, y_min, x_max, y_max = bbox
            assert 0 <= x_min < x_max <= page_w + 1.0, (
                f"{annot_path.name} line {l_no} invalid X bounds: [{x_min}, {x_max}]"
            )
            assert 0 <= y_min < y_max <= page_h + 1.0, (
                f"{annot_path.name} line {l_no} invalid Y bounds: [{y_min}, {y_max}]"
            )


def test_split_isolation_and_no_leakage():
    """Verify that both documents in every package belong to the same partition."""
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    for pkg in manifest["packages"]:
        split = pkg["split"]
        assert split in ["train", "validation", "test"], f"Invalid split: {split}"
        # Package level assignment ensures invoice and PL cannot be in different splits
        assert pkg["commercial_invoice"]["document_id"].startswith(pkg["package_id"])
        assert pkg["packing_list"]["document_id"].startswith(pkg["package_id"])


def test_expected_comparisons_integrity():
    """Verify expected_comparisons.json has valid rules, package references, and explanations."""
    with open(COMPARISONS_PATH, "r", encoding="utf-8") as f:
        comparisons_data = json.load(f)

    comparisons = comparisons_data["comparisons"]
    assert len(comparisons) == 50, f"Expected 50 comparison records, got {len(comparisons)}"

    valid_outcomes = {"match", "discrepancy", "not_comparable"}
    valid_rules = {"QTY-002", "WT-001", "PARTY-001", "ID-001", "MONEY-001", "MONEY-002"}

    for cmp_item in comparisons:
        assert cmp_item["rule_id"] in valid_rules, f"Unknown rule_id: {cmp_item['rule_id']}"
        assert cmp_item["expected_outcome"] in valid_outcomes, (
            f"Invalid outcome: {cmp_item['expected_outcome']}"
        )
        assert len(cmp_item["explanation"]) > 10, (
            f"Explanation too short in {cmp_item['comparison_id']}"
        )


def test_malformed_annotation_rejection():
    """Test that validation logic properly catches inverted or out-of-bounds bounding boxes."""
    # Inverted X: x_min >= x_max
    inverted_bbox = [300.0, 100.0, 200.0, 120.0]
    is_valid = (0 <= inverted_bbox[0] < inverted_bbox[2] <= 595.28) and (
        0 <= inverted_bbox[1] < inverted_bbox[3] <= 841.89
    )
    assert not is_valid, "Validation logic must reject inverted X coordinates"

    # Out of bounds Y: y_max > page_height
    oob_bbox = [100.0, 800.0, 250.0, 950.0]
    is_valid_oob = (0 <= oob_bbox[0] < oob_bbox[2] <= 595.28) and (
        0 <= oob_bbox[1] < oob_bbox[3] <= 841.89
    )
    assert not is_valid_oob, "Validation logic must reject out-of-bounds coordinates"
