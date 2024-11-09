import aiohttp
import asyncio
import zipfile
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from openpyxl import Workbook
from typing import List
from urllib.parse import urljoin

BASE_URL = 'https://www.scrapethissite.com/pages/forms/?page_num=1'

# table Structure
class TeamStat:
    def __init__(self, year: int, team: str, wins: int, losses: int, otlosses: str, winpercentage : float, goalfor:int, goalagainst:int,points :int):
        self.year = year
        self.team = team
        self.wins = wins
        self.losses = losses
        self.otlosses = otlosses
        self.winpercentage = winpercentage
        self.goalfor = goalfor
        self.goalagainst = goalagainst
        self.points = points

# Select the HTML content of a page
async def fetch_page(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text() if response.status == 200 else ""

# Pull team stats from a single page
def parse_team_stats(html: str) -> List[TeamStat]:
    soup = BeautifulSoup(html, 'html.parser')
    stats = []
    for row in soup.select('.team'):
        year = int(row.select_one('.year').text.strip())
        team = row.select_one('.name').text.strip()
        wins = int(row.select_one('.wins').text.strip())
        losses = int(row.select_one('.losses').text.strip())
        otlosses = str(row.select_one('.ot-losses').text.strip())
        winpercentage_value = row.select_one('.pct.text-success') or row.select_one('.pct.text-danger')
        winpercentage = float(winpercentage_value.text.strip())
        goalfor = int(row.select_one('.gf').text.strip())
        goalagainst = int(row.select_one('.ga').text.strip())
        points_value = row.select_one('.diff.text-success') or row.select_one('.diff.text-danger')
        points = int(points_value.text.strip())
        stats.append(TeamStat(year, team, wins, losses,otlosses,winpercentage,goalfor,goalagainst,points))
    return stats

# Save HTML files into a zip archive
def save_html_zip(html_pages: List[str]) -> BytesIO:
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for i, html in enumerate(html_pages, start=1):
            zip_file.writestr(f"{i}.html", html)
    zip_buffer.seek(0)
    return zip_buffer

# Create Excel file
def create_excel_file(stats: List[TeamStat]) -> BytesIO:
    workbook = Workbook()

    # Sheet 1
    sheet1 = workbook.active
    sheet1.title = "NHL Stats 1990-2011"
    sheet1.append(["Year", "Team", "Wins", "Losses", "OT Losses", "Win %","Goal For (GF)", "Goal Against (GA)", "+/-"])
    for stat in stats:
        sheet1.append([stat.year, stat.team, stat.wins, stat.losses, stat.otlosses ,stat.winpercentage,stat.goalfor,stat.goalagainst,stat.points])

    # Sheet 2
    sheet2 = workbook.create_sheet("Winner and Loser per Year")
    sheet2.append(["Year", "Winner", "Winner Num. of Wins", "Loser", "Loser Num. of Wins"])

    yearly_stats = {}
    for stat in stats:
        if stat.year not in yearly_stats:
            yearly_stats[stat.year] = []
        yearly_stats[stat.year].append(stat)

    for year, teams in yearly_stats.items():
        winner = max(teams, key=lambda x: x.wins)
        loser = min(teams, key=lambda x: x.wins)
        sheet2.append([year, winner.team, winner.wins, loser.team, loser.wins])

    excel_buffer = BytesIO()
    workbook.save(excel_buffer)
    excel_buffer.seek(0)
    return excel_buffer

# Main 
async def main():
    async with aiohttp.ClientSession() as session:
        current_url = BASE_URL
        page_number = 1
        html_pages = []
        all_stats = []

        # Scraping each page
        while current_url:
            html = await fetch_page(session, current_url)            
            if not html:
                break

            # Save HTML and parse stats
            html_pages.append(html)
            all_stats.extend(parse_team_stats(html))

            # Find the next page link
            soup = BeautifulSoup(html, 'html.parser')
            next_link = soup.find('a',{"aria-label": "Next"})
            current_url = urljoin(current_url, next_link['href']) if next_link else None
            page_number += 1
            

        # Save HTML files into a zip archive
        html_zip = save_html_zip(html_pages)

        # Create Excel file with data
        excel_file = create_excel_file(all_stats)

        # Save files locally
        with open("hockey_stats.zip", "wb") as f:
            f.write(html_zip.read())
        with open("hockey_stats.xlsx", "wb") as f:
            f.write(excel_file.read())

# Run Query
asyncio.run(main())
