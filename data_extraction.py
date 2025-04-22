from sec_edgar_downloader import Downloader

dl = Downloader("sec-edgar-data", "krishanmohank974@gmail.com")

dl.get("10-K", "AAPL")