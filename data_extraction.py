from sec_edgar_downloader import Downloader

# Download latest 10-K filing for Walmart (CIK: 0000104169)
dl = Downloader("sec_data", "krishanmohan@gmail.com")  # all data gets saved into ./sec_data
dl.get("10-K", "WMT")  # or use "0000104169" for direct CIK
