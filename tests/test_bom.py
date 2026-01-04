"""Tests for BOM extraction functionality."""

import csv
import tempfile
from pathlib import Path

from extrusion_decoder.decoder import extract_misumi_from_bom, format_bom_output


class TestExtractMisumiFromBom:
    """Tests for extract_misumi_from_bom function."""

    def test_extract_from_comma_separated_csv(self):
        """Test extracting MISUMI parts from comma-separated CSV."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=["Category", "Description", "Qty"])
            writer.writeheader()
            writer.writerow(
                {
                    "Category": "Frame",
                    "Description": "Misumi HFSB5-2020-500-LCP-RCP-AV360",
                    "Qty": "4",
                }
            )
            writer.writerow(
                {
                    "Category": "",
                    "Description": "Some other part",
                    "Qty": "1",
                }
            )
            temp_path = f.name

        try:
            parts = extract_misumi_from_bom(temp_path)
            assert len(parts) == 1
            assert parts[0]["part_number"] == "HFSB5-2020-500-LCP-RCP-AV360"
            assert parts[0]["quantity"] == "4"
        finally:
            Path(temp_path).unlink()

    def test_extract_from_semicolon_separated_csv(self):
        """Test extracting MISUMI parts from semicolon-separated CSV."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            writer = csv.DictWriter(
                f, fieldnames=["Category", "Description", "Qty"], delimiter=";"
            )
            writer.writeheader()
            writer.writerow(
                {
                    "Category": "Frame",
                    "Description": "Misumi HFS6-3030-500",
                    "Qty": "2",
                }
            )
            temp_path = f.name

        try:
            parts = extract_misumi_from_bom(temp_path)
            assert len(parts) == 1
            assert parts[0]["part_number"] == "HFS6-3030-500"
        finally:
            Path(temp_path).unlink()

    def test_case_insensitive_misumi_match(self):
        """Test that MISUMI matching is case-insensitive."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=["Description", "Qty"])
            writer.writeheader()
            writer.writerow(
                {
                    "Description": "MISUMI HFSB5-2020-500",
                    "Qty": "1",
                }
            )
            writer.writerow(
                {
                    "Description": "misumi HFS6-3030-500",
                    "Qty": "2",
                }
            )
            temp_path = f.name

        try:
            parts = extract_misumi_from_bom(temp_path)
            assert len(parts) == 2
        finally:
            Path(temp_path).unlink()

    def test_no_misumi_parts(self):
        """Test CSV with no MISUMI parts."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=["Description", "Qty"])
            writer.writeheader()
            writer.writerow({"Description": "Some other part", "Qty": "1"})
            temp_path = f.name

        try:
            parts = extract_misumi_from_bom(temp_path)
            assert parts == []
        finally:
            Path(temp_path).unlink()

    def test_file_not_found(self):
        """Test handling of non-existent file."""
        parts = extract_misumi_from_bom("/nonexistent/file.csv")
        assert len(parts) == 1
        assert "error" in parts[0]
        assert "File not found" in parts[0]["error"]

    def test_missing_quantity_defaults_to_one(self):
        """Test that missing quantity defaults to '1'."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=["Description", "Qty"])
            writer.writeheader()
            writer.writerow({"Description": "Misumi HFSB5-2020-500", "Qty": ""})
            temp_path = f.name

        try:
            parts = extract_misumi_from_bom(temp_path)
            assert len(parts) == 1
            assert parts[0]["quantity"] == "1"
        finally:
            Path(temp_path).unlink()


class TestFormatBomOutput:
    """Tests for format_bom_output function."""

    def test_format_empty_list(self):
        """Test formatting empty parts list."""
        output = format_bom_output([])
        assert "No MISUMI parts found" in output

    def test_format_with_error(self):
        """Test formatting when there's an error."""
        parts = [{"error": "File not found: test.csv"}]
        output = format_bom_output(parts)
        assert "Error:" in output
        assert "File not found" in output

    def test_format_valid_parts(self):
        """Test formatting valid parts."""
        parts = [
            {
                "part_number": "HFSB5-2020-500-LCP",
                "quantity": "4",
                "description": "Misumi HFSB5-2020-500-LCP",
            }
        ]
        output = format_bom_output(parts)
        assert "MISUMI Parts from BOM" in output
        assert "HFSB5-2020-500-LCP" in output
        assert "Qty: 4" in output
