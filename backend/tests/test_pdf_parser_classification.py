from app.services.pdf_parser import _is_footnote_block


def test_bold_kpi_content_is_not_a_footnote() -> None:
    assert not _is_footnote_block(
        "**2 Express Parcel: 18%+ Service EBITDA profitability**",
        chunk_idx=4,
        total_chunks=8,
    )


def test_explicit_source_note_is_a_footnote() -> None:
    assert _is_footnote_block(
        "**Source: Delhivery FY24 earnings presentation**",
        chunk_idx=7,
        total_chunks=8,
    )


def test_bold_decimal_stat_is_not_a_footnote() -> None:
    assert not _is_footnote_block("**1.4 Mn Tons**", chunk_idx=4, total_chunks=8)
