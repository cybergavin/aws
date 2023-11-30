import requests
import sys
import time
from bs4 import BeautifulSoup
from pathlib import Path, PurePath

# Set year for posts
if len(sys.argv) == 2:
    if (sys.argv[1]).isdigit() and int(sys.argv[1]) > 2012 and int(sys.argv[1]) <= int(time.strftime("%Y")):
        requested_year = sys.argv[1]
    else:
       print("\nInvalid argument! Argument must be a year (YYYY) between 2012 and the current year."
            " For the current year, no input argument is required."
            " If more than one argument is used, all arguments will be ignored and the current year will be used.\n")
       sys.exit()
else:
    requested_year = time.strftime("%Y")

# Set variables
output_file = f"{PurePath(sys.argv[0]).stem}_{requested_year}.html"
arl_page_num=0
arl_blog_posts = []
stop_crawl = False

# Crawl AWS re:Invent launch blog post pages and write requested blog posts to a file
with open(output_file, "w") as f:
    f.write(f"<h2>Amazon re:Invent launch blog posts for {requested_year}</h2>")
    while True:
        if arl_page_num == 0:
            url = "https://aws.amazon.com/blogs/aws/category/events/reinvent/"
            arl_page_num += 2
        elif arl_page_num >= 2:
            url = f"https://aws.amazon.com/blogs/aws/category/events/reinvent/page/{arl_page_num}/"
            arl_page_num += 1
        page = requests.get(url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "html.parser")
            page_blog_posts = soup.find_all("article", class_="blog-post")
            for post in page_blog_posts:
                post_title = post.find("span", {'property' : 'name headline'}).text
                post_year = post.find("time", {'property' : 'datePublished'})["datetime"][:4]
                post_url = post.find("li", class_="blog-share-dialog-url").input["value"]
                if post_year == requested_year:
                    arl_blog_posts.append(f"<a href='{post_url}' target='blank'>{post_title}</a>")
                elif post_year < requested_year:
                    stop_crawl = True
                    break
        else:
            stop_crawl = True
        if stop_crawl:
            break  
    arl_blog_posts = list(set(arl_blog_posts))
    if len(arl_blog_posts) > 0:
        for i,p in enumerate(arl_blog_posts):
            f.write(f"{i+1}.&nbsp;&nbsp;&nbsp;{p}<br>")
    else:
        f.write(f"<br>No re:Invent launch posts have been published so far for {requested_year}")