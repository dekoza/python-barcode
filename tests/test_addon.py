from __future__ import annotations

import pytest

from barcode import get_barcode
from barcode.ean import EAN8
from barcode.ean import EAN13
from barcode.errors import IllegalCharacterError
from barcode.errors import NumberOfDigitsError
from barcode.isxn import ISBN10
from barcode.isxn import ISBN13
from barcode.isxn import ISSN
from barcode.upc import UPCA


class TestEAN2Addon:
    """Tests for EAN-2 addon functionality."""

    def test_ean13_with_addon2(self) -> None:
        """Test EAN-13 with 2-digit addon."""
        ean = EAN13("5901234123457", addon="12")
        assert ean.ean == "5901234123457"
        assert ean.addon == "12"
        assert ean.get_fullcode() == "5901234123457 12"
        assert str(ean) == "5901234123457 12"

    def test_ean8_with_addon2(self) -> None:
        """Test EAN-8 with 2-digit addon."""
        ean = EAN8("40267708", addon="05")
        assert ean.addon == "05"
        assert ean.get_fullcode() == "40267708 05"

    def test_addon2_builds_correctly(self) -> None:
        """Test that EAN-2 addon pattern is built correctly."""
        ean = EAN13("5901234123457", addon="12")
        code = ean.build()[0]
        # Main barcode should be there
        assert code.startswith("101")  # Start guard
        # Addon should be appended
        assert "1011" in code  # Addon start guard

    def test_addon2_parity_mod4(self) -> None:
        """Test EAN-2 parity patterns based on value mod 4."""
        # Test different mod 4 values
        ean00 = EAN13("5901234123457", addon="00")  # 0 % 4 = 0 -> AA
        ean01 = EAN13("5901234123457", addon="01")  # 1 % 4 = 1 -> AB
        ean02 = EAN13("5901234123457", addon="02")  # 2 % 4 = 2 -> BA
        ean03 = EAN13("5901234123457", addon="03")  # 3 % 4 = 3 -> BB

        # Each should build without error
        for ean in [ean00, ean01, ean02, ean03]:
            code = ean.build()[0]
            assert len(code) > 95  # Main EAN-13 + addon


class TestEAN5Addon:
    """Tests for EAN-5 addon functionality."""

    def test_ean13_with_addon5(self) -> None:
        """Test EAN-13 with 5-digit addon."""
        ean = EAN13("5901234123457", addon="52495")
        assert ean.addon == "52495"
        assert ean.get_fullcode() == "5901234123457 52495"
        assert str(ean) == "5901234123457 52495"

    def test_ean8_with_addon5(self) -> None:
        """Test EAN-8 with 5-digit addon."""
        ean = EAN8("40267708", addon="12345")
        assert ean.addon == "12345"
        assert ean.get_fullcode() == "40267708 12345"

    def test_addon5_builds_correctly(self) -> None:
        """Test that EAN-5 addon pattern is built correctly."""
        ean = EAN13("5901234123457", addon="52495")
        code = ean.build()[0]
        # Main barcode should be there
        assert code.startswith("101")  # Start guard
        # Addon should be appended
        assert "1011" in code  # Addon start guard

    def test_addon5_price_encoding(self) -> None:
        """Test EAN-5 with typical price encoding (e.g., $24.95)."""
        # 52495 typically means $24.95 USD (5 = USD, 2495 = price)
        ean = EAN13("9780132354189", addon="52495")
        assert ean.get_fullcode() == "9780132354189 52495"


class TestAddonValidation:
    """Tests for addon validation."""

    def test_addon_must_be_digits(self) -> None:
        """Test that addon must contain only digits."""
        with pytest.raises(IllegalCharacterError):
            EAN13("5901234123457", addon="1A")

    def test_addon_must_be_2_or_5_digits(self) -> None:
        """Test that addon must be exactly 2 or 5 digits."""
        with pytest.raises(NumberOfDigitsError):
            EAN13("5901234123457", addon="1")
        with pytest.raises(NumberOfDigitsError):
            EAN13("5901234123457", addon="123")
        with pytest.raises(NumberOfDigitsError):
            EAN13("5901234123457", addon="1234")
        with pytest.raises(NumberOfDigitsError):
            EAN13("5901234123457", addon="123456")

    def test_addon_empty_string_ignored(self) -> None:
        """Test that empty addon string is treated as no addon."""
        ean = EAN13("5901234123457", addon="")
        assert ean.addon is None
        assert ean.get_fullcode() == "5901234123457"

    def test_addon_whitespace_stripped(self) -> None:
        """Test that whitespace is stripped from addon."""
        ean = EAN13("5901234123457", addon="  12  ")
        assert ean.addon == "12"

    def test_addon_none_is_valid(self) -> None:
        """Test that None addon is valid (no addon)."""
        ean = EAN13("5901234123457", addon=None)
        assert ean.addon is None
        assert ean.get_fullcode() == "5901234123457"


class TestISXNWithAddon:
    """Tests for ISBN and ISSN with addons."""

    def test_issn_with_addon2(self) -> None:
        """Test ISSN with 2-digit addon (issue number)."""
        issn = ISSN("03178471", addon="05")
        assert issn.addon == "05"
        assert str(issn) == "03178471 05"
        assert issn.get_fullcode() == "9770317847001 05"

    def test_issn_with_addon5(self) -> None:
        """Test ISSN with 5-digit addon."""
        issn = ISSN("03178471", addon="12345")
        assert issn.addon == "12345"
        assert issn.get_fullcode() == "9770317847001 12345"

    def test_isbn13_with_addon5(self) -> None:
        """Test ISBN-13 with 5-digit addon (price)."""
        isbn = ISBN13("978-3-16-148410-0", addon="52495")
        assert isbn.addon == "52495"
        assert isbn.get_fullcode() == "9783161484100 52495"

    def test_isbn10_with_addon5(self) -> None:
        """Test ISBN-10 with 5-digit addon (price)."""
        isbn = ISBN10("3-12-517154-7", addon="52495")
        assert isbn.addon == "52495"
        assert str(isbn) == "3125171547 52495"
        assert isbn.get_fullcode() == "9783125171541 52495"


class TestGetBarcodeWithAddon:
    """Tests for get_barcode function with addon parameter."""

    def test_get_barcode_ean13_with_addon(self) -> None:
        """Test get_barcode with EAN-13 and addon."""
        ean = get_barcode("ean13", "5901234123457", options={"addon": "12"})
        assert ean.addon == "12"
        assert ean.get_fullcode() == "5901234123457 12"

    def test_get_barcode_issn_with_addon(self) -> None:
        """Test get_barcode with ISSN and addon."""
        issn = get_barcode("issn", "03178471", options={"addon": "05"})
        assert issn.addon == "05"

    def test_get_barcode_upca_with_addon(self) -> None:
        """Test get_barcode with UPC-A and addon."""
        upca = get_barcode("upca", "01234567890", options={"addon": "12"})
        assert upca.addon == "12"
        assert upca.get_fullcode() == "012345678905 12"


class TestUPCAWithAddon:
    """Tests for UPC-A with EAN-2 and EAN-5 addons."""

    def test_upca_with_addon2(self) -> None:
        """Test UPC-A with 2-digit addon."""
        upc = UPCA("01234567890", addon="12")
        assert upc.upc == "012345678905"
        assert upc.addon == "12"
        assert upc.get_fullcode() == "012345678905 12"
        assert str(upc) == "012345678905 12"

    def test_upca_with_addon5(self) -> None:
        """Test UPC-A with 5-digit addon."""
        upc = UPCA("01234567890", addon="52495")
        assert upc.addon == "52495"
        assert upc.get_fullcode() == "012345678905 52495"
        assert str(upc) == "012345678905 52495"

    def test_upca_addon2_builds_correctly(self) -> None:
        """Test that UPC-A with EAN-2 addon pattern is built correctly."""
        upc = UPCA("01234567890", addon="12")
        code = upc.build()[0]
        # Main barcode should be there
        assert code.startswith("101")  # Start guard
        # Addon should be appended
        assert "1011" in code  # Addon start guard

    def test_upca_addon5_builds_correctly(self) -> None:
        """Test that UPC-A with EAN-5 addon pattern is built correctly."""
        upc = UPCA("01234567890", addon="52495")
        code = upc.build()[0]
        # Main barcode should be there
        assert code.startswith("101")  # Start guard
        # Addon should be appended
        assert "1011" in code  # Addon start guard

    def test_upca_addon_must_be_digits(self) -> None:
        """Test that UPC-A addon must contain only digits."""
        with pytest.raises(IllegalCharacterError):
            UPCA("01234567890", addon="1A")

    def test_upca_addon_must_be_2_or_5_digits(self) -> None:
        """Test that UPC-A addon must be exactly 2 or 5 digits."""
        with pytest.raises(NumberOfDigitsError):
            UPCA("01234567890", addon="1")
        with pytest.raises(NumberOfDigitsError):
            UPCA("01234567890", addon="123")
        with pytest.raises(NumberOfDigitsError):
            UPCA("01234567890", addon="1234")
        with pytest.raises(NumberOfDigitsError):
            UPCA("01234567890", addon="123456")

    def test_upca_addon_empty_string_ignored(self) -> None:
        """Test that empty addon string is treated as no addon."""
        upc = UPCA("01234567890", addon="")
        assert upc.addon is None
        assert upc.get_fullcode() == "012345678905"

    def test_upca_addon_whitespace_stripped(self) -> None:
        """Test that whitespace is stripped from UPC-A addon."""
        upc = UPCA("01234567890", addon="  12  ")
        assert upc.addon == "12"

    def test_upca_addon_none_is_valid(self) -> None:
        """Test that None addon is valid (no addon) for UPC-A."""
        upc = UPCA("01234567890", addon=None)
        assert upc.addon is None
        assert upc.get_fullcode() == "012345678905"

    def test_upca_make_ean_with_addon(self) -> None:
        """Test UPC-A with make_ean=True and addon."""
        upc = UPCA("01234567890", make_ean=True, addon="12")
        assert upc.addon == "12"
        assert upc.get_fullcode() == "0012345678905 12"
        assert str(upc) == "0012345678905 12"

    def test_upca_addon2_parity_mod4(self) -> None:
        """Test UPC-A EAN-2 parity patterns based on value mod 4."""
        # Test different mod 4 values
        upc00 = UPCA("01234567890", addon="00")  # 0 % 4 = 0 -> AA
        upc01 = UPCA("01234567890", addon="01")  # 1 % 4 = 1 -> AB
        upc02 = UPCA("01234567890", addon="02")  # 2 % 4 = 2 -> BA
        upc03 = UPCA("01234567890", addon="03")  # 3 % 4 = 3 -> BB

        # Each should build without error
        for upc in [upc00, upc01, upc02, upc03]:
            code = upc.build()[0]
            assert len(code) > 95  # Main UPC-A + addon

