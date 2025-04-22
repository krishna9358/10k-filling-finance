from sec_edgar_downloader import Downloader

dl = Downloader("sec-edgar-data", "krishanmohank974@gmail.com", "sec-edgar-data")

dl.get("10-K", "AAPL")