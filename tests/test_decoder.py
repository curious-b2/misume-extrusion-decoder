"""Tests for the MISUMI decoder core functionality."""

from extrusion_decoder.decoder import (
    decode_misumi_name,
    format_description,
    parse_alteration_code,
    parse_length,
    parse_size,
)


class TestParseSize:
    """Tests for parse_size function."""

    def test_square_cross_section(self):
        """Test parsing square cross-section sizes."""
        assert parse_size("2020") == "20mm × 20mm"
        assert parse_size("3030") == "30mm × 30mm"
        assert parse_size("1515") == "15mm × 15mm"

    def test_rectangular_cross_section(self):
        """Test parsing rectangular cross-section sizes."""
        assert parse_size("404020") == "40mm × 40mm × 20mm"

    def test_custom_size(self):
        """Test parsing custom/unusual sizes."""
        result = parse_size("12345")
        assert "custom size" in result


class TestParseLength:
    """Tests for parse_length function."""

    def test_valid_length(self):
        """Test parsing valid length strings."""
        assert parse_length("500") == "500mm"
        assert parse_length("1000") == "1000mm"
        assert parse_length("250") == "250mm"

    def test_invalid_length(self):
        """Test parsing invalid length strings."""
        result = parse_length("abc")
        assert result == "abc"  # Returns as-is on ValueError


class TestParseAlterationCode:
    """Tests for parse_alteration_code function."""

    def test_exact_match_codes(self):
        """Test codes that match exactly."""
        desc, value = parse_alteration_code("Z6")
        assert "Counterbore" in desc
        assert value is None

        desc, value = parse_alteration_code("X5")
        assert "Wrench Hole Diameter" in desc
        assert value is None

        desc, value = parse_alteration_code("LCP")
        assert "Left Wrench Access Hole" in desc
        assert value is None

    def test_codes_with_underscores(self):
        """Test codes with underscores."""
        desc, value = parse_alteration_code("L_T45")
        assert "45-Degree Cut" in desc
        assert value is None

    def test_codes_with_numeric_suffixes(self):
        """Test codes with numeric suffixes."""
        desc, value = parse_alteration_code("AV360")
        assert "Wrench Hole" in desc
        assert value == "360mm from left end"

        desc, value = parse_alteration_code("XA200")
        assert "Counterbore" in desc
        assert value == "200mm from left end"

        desc, value = parse_alteration_code("JLP1100")
        assert "L Hole" in desc
        assert value == "Hole pitch: 1100mm"

    def test_labeling_codes(self):
        """Test labeling codes with numeric suffixes."""
        desc, value = parse_alteration_code("ZZZ123")
        assert "Serial Number" in desc
        assert value == "Serial: 123"

        desc, value = parse_alteration_code("LL42")
        assert "Unit Number" in desc
        assert value == "Unit: 42"

    def test_unknown_codes(self):
        """Test handling of unknown codes."""
        desc, value = parse_alteration_code("UNKNOWN")
        assert "Unknown alteration code" in desc
        assert value is None

        desc, value = parse_alteration_code("XYZ123")
        assert "Unknown alteration code" in desc
        assert value == "123"


class TestDecodeMisumiName:
    """Tests for decode_misumi_name function."""

    def test_basic_part_number(self):
        """Test decoding a basic part number."""
        result = decode_misumi_name("HFSB5-2020-500")
        assert result["series"] == "HFSB5"
        assert result["size"] == "20mm × 20mm"
        assert result["length"] == "500mm"
        assert result["alterations"] == []

    def test_part_number_with_alterations(self):
        """Test decoding a part number with alterations."""
        result = decode_misumi_name("HFSB5-2020-500-LCP-RCP-AV360")
        assert result["series"] == "HFSB5"
        assert result["size"] == "20mm × 20mm"
        assert result["length"] == "500mm"
        assert len(result["alterations"]) == 3
        assert "LCP" in result["alterations"]
        assert "RCP" in result["alterations"]
        assert "AV360" in result["alterations"]

    def test_complex_part_number(self):
        """Test decoding a complex part number with multiple alterations."""
        result = decode_misumi_name("HFS6-3030-500-Z6-XA200-XB256")
        assert result["series"] == "HFS6"
        assert result["size"] == "30mm × 30mm"
        assert result["length"] == "500mm"
        assert "Z6" in result["alterations"]
        assert "XA200" in result["alterations"]
        assert "XB256" in result["alterations"]

    def test_part_number_with_x5_x8(self):
        """Test decoding part numbers with X5/X8 diameter specifications."""
        result = decode_misumi_name("HFS6-3030-300-X8-AH30-BH280")
        assert result["series"] == "HFS6"
        assert "X8" in result["alterations"]
        assert "AH30" in result["alterations"]
        assert "BH280" in result["alterations"]

    def test_invalid_format(self):
        """Test handling of invalid part number formats."""
        result = decode_misumi_name("INVALID")
        assert "error" in result
        assert "Invalid part number format" in result["error"]

        result = decode_misumi_name("HFSB5-2020")
        assert "error" in result

    def test_rectangular_size(self):
        """Test decoding part numbers with rectangular sizes."""
        result = decode_misumi_name("HFSB5-404020-500")
        assert "40mm × 40mm × 20mm" in result["size"]


class TestFormatDescription:
    """Tests for format_description function."""

    def test_basic_formatting(self):
        """Test formatting a basic decoded part."""
        decoded = decode_misumi_name("HFSB5-2020-500")
        output = format_description(decoded)
        assert "HFSB5-2020-500" in output
        assert "Series: HFSB5" in output
        assert "Size: 20mm × 20mm" in output
        assert "Length: 500mm" in output
        assert "Alterations: None" in output

    def test_formatting_with_alterations(self):
        """Test formatting with alterations."""
        decoded = decode_misumi_name("HFSB5-2020-500-LCP-RCP")
        output = format_description(decoded)
        assert "Alterations:" in output
        assert "LCP" in output or "Left Wrench Access Hole" in output

    def test_formatting_error(self):
        """Test formatting when there's an error."""
        decoded = {"error": "Invalid format"}
        output = format_description(decoded)
        assert "Error:" in output
        assert "Invalid format" in output
