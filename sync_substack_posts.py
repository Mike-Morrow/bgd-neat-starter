import feedparser
import pandas as pd
import markdownify
import re
from datetime import datetime
import os

# URL of the Substack RSS feed
feed_url = "https://bettergutdigest.substack.com/feed"

# Parse the RSS feed
feed = feedparser.parse(feed_url)

# Function to convert HTML content to Markdown using markdownify
def html_to_markdown(html):
    # Convert HTML to markdown
    markdown_content = markdownify.markdownify(html, heading_style="ATX")
    
    # Remove any unnecessary backslashes before hyphens
    markdown_content = markdown_content.replace("\\-", "-")
    
    # Find any inline footnotes using regex in the form [number](link)
    footnote_pattern = re.compile(r"\[(\d+)\]\((http.*?)\)")
    footnotes = footnote_pattern.findall(markdown_content)
    
    # Replace inline footnotes with Markdown-style footnotes (e.g., [^1])
    for number, url in footnotes:
        markdown_content = markdown_content.replace(f"[{number}]({url})", f"[^{number}]")
        # Append the footnote definition at the end of the content
        markdown_content += f"\n\n[^{number}]: {url}"
    
    # Remove "Read more" link and related section
    read_more_pattern = re.compile(r"\[Read more\]\(.*?\)")
    markdown_content = re.sub(read_more_pattern, "", markdown_content).strip()  # Remove "Read more" and strip any trailing spaces
    
    return markdown_content

# Function to format the date into the ISO format required in the front matter
def format_date(published_date):
    dt = datetime.strptime(published_date, '%a, %d %b %Y %H:%M:%S %Z')  # Parse the RSS date format
    return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')  # Convert to ISO format

# Function to sanitize file names (removing special characters)
def sanitize_filename(title):
    return re.sub(r'[^A-Za-z0-9\- ]+', '', title).replace(' ', '-').lower()

# Directory to save markdown files
output_dir = "/Users/mike/Documents/BGD_Website/bgd-neat-starter/src/posts"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Extract relevant information from the feed entries
data = {
    "Title": [],
    "Link": [],
    "Published": [],
    "Summary": [],
    "Content": [],
    "Markdown Output": []
}

for entry in feed.entries:
    # Raw data
    title = entry.title
    link = entry.link
    published = entry.published
    summary = entry.summary if 'summary' in entry else "No description available."  # Use summary for description
    content = entry.content[0].value if 'content' in entry else ""

    # Convert HTML content to Markdown, and fix footnotes
    markdown_content = html_to_markdown(content)
    
    # Extract the first header to use as the title
    header_match = re.search(r'## (.*)', markdown_content)
    if header_match:
        title = header_match.group(1).strip()

    # Format the published date for YAML
    formatted_date = format_date(published)
    
    # Sanitize the summary to escape any double quotes
    sanitized_summary = summary.replace('"', '\\"')

    # Create YAML front matter using the summary as the description
    front_matter = (
        f"---\n"
        f"title: \"{title}\"\n"
        f"description: \"{sanitized_summary}\"\n"
        f"author: Mike Morrow\n"
        f"date: {formatted_date}\n"
        f"tags:\n"
        f"  - left\n"
        f"  - center\n"
        f"  - right\n"
        f"---\n\n"
    )

    # Combine front matter with markdown content
    markdown_entry = f"{front_matter}{markdown_content}\n\n---\n"
    
    # Append to data dictionary
    data["Title"].append(title)
    data["Link"].append(link)
    data["Published"].append(published)
    data["Summary"].append(summary)
    data["Content"].append(content)
    data["Markdown Output"].append(markdown_entry)
    
    # Create markdown file name
    sanitized_title = sanitize_filename(title)
    file_name = f"{sanitized_title}.md"
    
    # Write the markdown content to a file
    file_path = os.path.join(output_dir, file_name)
    with open(file_path, 'w', encoding='utf-8') as md_file:
        md_file.write(markdown_entry)

# Convert the data into a pandas DataFrame
substack_rss_df = pd.DataFrame(data)

# Display the DataFrame (optional)
# print(substack_rss_df)
