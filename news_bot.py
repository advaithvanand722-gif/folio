import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# The target news sources (using their stable XML feeds)
NEWS_SOURCES = {
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml"
}

def scrape_news(source_name, url):
    """Scrape the top 5 headlines, links, and times from a news source."""
    try:
        # We use a custom User-Agent so websites don't block our bot
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the XML data
        soup = BeautifulSoup(response.content, features="xml")
        
        # Standard RSS feeds use <item>, Atom feeds use <entry>
        articles = soup.find_all(['item', 'entry'], limit=5)
        
        news_data = []
        for article in articles:
            # Extract title
            title_tag = article.find('title')
            title = title_tag.text.strip() if title_tag else "No Title"
            
            # Extract link
            link_tag = article.find('link')
            if link_tag and link_tag.text:
                link = link_tag.text.strip()
            elif link_tag and link_tag.get('href'):
                link = link_tag.get('href')
            else:
                link = "#"
                
            # Extract publication time (pubDate or published)
            time_tag = article.find('pubDate') or article.find('published')
            pub_time = time_tag.text.strip() if time_tag else "Time unknown"
            
            news_data.append({"title": title, "link": link, "time": pub_time})
            
        return news_data
    except Exception as e:
        print(f"Error scraping {source_name}: {e}")
        return []

def generate_html_email(all_news):
    """Compile the scraped data into a styled HTML email."""
    today = datetime.now().strftime("%A, %B %d, %Y")
    
    # Start the HTML structure with some basic inline CSS
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
          📰 Your Morning Briefing - {today}
        </h2>
    """
    
    # Loop through each news source and inject the articles
    for source, articles in all_news.items():
        if not articles:
            continue
            
        html += f"<h3 style='color: #e74c3c; margin-top: 20px;'>{source}</h3>"
        html += "<ul style='padding-left: 20px;'>"
        
        for article in articles:
            html += f"""
            <li style='margin-bottom: 15px;'>
                <a href='{article["link"]}' style='font-size: 16px; font-weight: bold; color: #2980b9; text-decoration: none;'>
                    {article["title"]}
                </a>
                <br>
                <span style='font-size: 12px; color: #7f8c8d;'>🕒 {article["time"]}</span>
            </li>
            """
        html += "</ul>"
        
    html += """
        <p style="font-size: 12px; color: #95a5a6; border-top: 1px solid #eee; padding-top: 10px; margin-top: 30px;">
          Generated automatically via Python & GitHub Actions.
        </p>
      </body>
    </html>
    """
    return html

def send_email(html_content):
    """Send the HTML email using Gmail SMTP."""
    sender_email = os.getenv("ALERT_EMAIL")
    sender_password = os.getenv("ALERT_EMAIL_PASSWORD") 
    receiver_email = os.getenv("RECEIVER_EMAIL")
    
    if not all([sender_email, sender_password, receiver_email]):
        print("Missing email credentials in environment variables.")
        return

    msg = MIMEMultipart("alternative")
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "📰 Your Morning News Briefing"
    
    # Attach the HTML content
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("Morning briefing delivered successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def run():
    print("Initiating news scrape...")
    all_news = {}
    
    for source, url in NEWS_SOURCES.items():
        print(f"Scraping {source}...")
        all_news[source] = scrape_news(source, url)
        
    print("Compiling HTML email...")
    html_content = generate_html_email(all_news)
    
    print("Dispatching email...")
    send_email(html_content)

if __name__ == "__main__":
    run()