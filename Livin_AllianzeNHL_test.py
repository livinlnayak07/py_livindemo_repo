import pytest
from io import BytesIO
from AllianzeNHL_Demo import parse_team_stats, create_excel_file, save_html_zip, TeamStat

# Sample HTML for testing
sample_html = """
<table class="stats-table">
    <tr class="team">
        <td class="year">1995</td>
        <td class="name">Team A</td>
        <td class="wins">10</td>
        <td class="losses">20</td>
    </tr>
    <tr class="team">
        <td class="year">1995</td>
        <td class="name">Team B</td>
        <td class="wins">15</td>
        <td class="losses">25</td>
    </tr>
</table>
"""

def test_parse_team_stats():
    stats = parse_team_stats(sample_html)
    assert len(stats) == 2
    assert stats[0].team == "Team A"
    assert stats[1].wins == 15

def test_save_html_zip():
    html_pages = ["<html><body>Page 1</body></html>", "<html><body>Page 2</body></html>"]
    zip_buffer = save_html_zip(html_pages)
    with zipfile.ZipFile(zip_buffer) as z:
        assert len(z.namelist()) == 2
        assert z.read("1.html") == b"<html><body>Page 1</body></html>"

def test_create_excel_file():
    stats = [TeamStat(1995, "Team A", 10, 20), TeamStat(1995, "Team B", 15, 25)]
    excel_buffer = create_excel_file(stats)
    assert isinstance(excel_buffer, BytesIO)