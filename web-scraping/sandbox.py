import bs4

html = "<body>toto</body>"
soup = bs4.BeautifulSoup(html, 'lxml')

print(soup)