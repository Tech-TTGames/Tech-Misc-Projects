"""A script to automagically insert requested names into the code."""
import argparse
import pyperclip
import bs4
from selenium import webdriver

driver = webdriver.Firefox()


def get_chapter_body_and_comments(url: str, soup: bs4.BeautifulSoup) -> tuple[bs4.Tag, list[bs4.Tag]]:
    """Get the body of a chapter."""
    body = soup.find(id="chp_raw")
    boiling_soup = soup
    comments = boiling_soup.find_all(class_="cmt_li_chp_1")
    total_pages = int(soup.find_all(class_="page-link")[-2].text)
    for page in range(2, total_pages + 1):
        driver.get(url + f"?gb={page}")
        driver.implicitly_wait(10)
        boiling_soup = bs4.BeautifulSoup(driver.page_source, "lxml")
        comments += boiling_soup.find_all(class_="cmt_li_chp_1")
    return body, comments


def commentmagics(url: str, comment_head: str, replaced_part: str) -> str:
    """Do the Comment Magicks on the chapter."""
    driver.get(url)
    driver.implicitly_wait(10)
    soup = bs4.BeautifulSoup(driver.page_source, 'lxml')
    chapter_body, comments = get_chapter_body_and_comments(url, soup)
    placement_requests = []
    for comment in comments:
        author = comment.find("a").text
        reqs_raw = comment.find_all(attrs={'class': ['profilereportpop_quote_qt']})
        reqs = [string.find('p').text.strip() for string in reqs_raw if comment_head in string.text]
        if reqs:
            placement_requests.append((author, reqs))
    while placement_requests:
        working_placement_requests = placement_requests.copy()
        offset = 0
        for i in range(len(placement_requests)):
            elem = soup.find(string=placement_requests[i][1][0])
            if elem:
                replaced = elem.replace(replaced_part, placement_requests[i][0])
                elem.replace_with(replaced)
            working_placement_requests[i - offset][1].pop(0)
            if not working_placement_requests[i - offset][1]:
                working_placement_requests.pop(i - offset)
                offset += 1
        placement_requests = working_placement_requests
    soup.smooth()
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for p in soup.find_all("p"):
        p.replace_with(f"{p.text}\n")
    print(f"Chapter {soup.title} magicked.")
    return chapter_body.get_text()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A Comment replacement utility by Tech.',
        prog='HVGCommentMagicks.py',
    )

    parser.add_argument('-u', '--url', type=str, help='URL of the chapter.')
    parser.add_argument('-U', '--urls', action="extend", type=str, help='URLs of the chapters.', nargs="+")
    parser.add_argument('-c', '--comment_header', type=str, help="Starting part of eligible comments.", default="@[]")
    parser.add_argument('-r', '--replaced-part', type=str, help="The part of the comment being replaced.", default="[]")
    args = parser.parse_args()

    if (args.url and args.urls) or (not args.url and not args.urls):
        raise ValueError("You must provide either a URL or a list of URLs.")

    if args.url:
        pyperclip.copy(commentmagics(args.url, args.comment_header, args.replaced_part))
        print("Replaced chapter copied to clipboard.")
    else:
        for order, url in enumerate(args.urls):
            pyperclip.copy(commentmagics(args.url, args.comment_header, args.replaced_part))
            print(f"Replaced chapter copied {order+1} to clipboard.")
            input("Press Enter to continue...")
    driver.quit()
