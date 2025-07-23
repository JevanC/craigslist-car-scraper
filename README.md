🚗 Craigslist Car Scraper Bot
A fully automated Python workflow that scans used car listings on Craigslist to identify underpriced Japanese vehicles with strong resale value. It uses an LLM to estimate market worth, calculates potential profit, and stores high-opportunity listings in a PostgreSQL database and a synced Google Sheet — all running in the background twice a day via GitHub Actions.

🧠 Key Features
🎯 Targeted Filtering
Scrapes the most recent 100 Craigslist listings and filters for Japanese cars under $7,000 and under 200,000 miles.

🤖 AI-Powered Valuation
Uses a large language model to predict the fair market value of each vehicle based on its description and metadata.

💵 Profit-Based Filtering
Applies SQL queries to retain only cars expected to yield at least $1,000 in resale profit.

🔁 Deduplication System
Tracks all previously seen URLs using a links_checked table to prevent redundant processing.

📶 Listing Verification
Regularly checks whether listings in the active_cars table are still live, keeping the database fresh and actionable.

📄 Google Sheets Integration
Automatically syncs filtered high-value listings to a connected Google Sheet using Coefficient for easy monitoring and access.

🗃️ Serverless Storage
All data is stored in a PostgreSQL database hosted on Neon, with two tables:

active_cars: high-value listings currently live

links_checked: all URLs already processed

⚙️ Scheduled Automation
The bot runs twice per day automatically using GitHub Actions with a cron schedule, requiring zero manual input.

🛠 Tech Stack
Language: Python

Scraping: Requests + BeautifulSoup + randomized headers/proxies

AI Model: LLM (used for price estimation)

Database: PostgreSQL (Neon serverless)

Automation: GitHub Actions + cron

Filtering: SQL (profit filters, duplication check)

Integration: Coefficient + Google Sheets

🔁 Automated Workflow
This project is fully backgrounded — no prompts or user interaction. It runs twice daily using GitHub Actions and follows this workflow:

Scrape the latest 100 Craigslist car listings

Filter for Japanese vehicles under $7,000 and under 200,000 miles

Predict each vehicle's true market value using an LLM

Score listings by estimated resale profit

Store qualifying cars (≥ $1,000 margin) in active_cars

Log all visited URLs in links_checked

Verify status of listings in active_cars to remove expired posts

Sync valid, profitable listings to a Google Sheet via Coefficient

📌 Notes
Built for zero-interaction, recurring analysis

Designed for flip-friendly car scouting and resale arbitrage

Easily extensible to other regions, price ranges, or vehicle makes

Smart deduplication ensures API efficiency and clean data

Cron schedule (e.g., 0 */12 * * *) runs the scraper twice daily via GitHub Actions

