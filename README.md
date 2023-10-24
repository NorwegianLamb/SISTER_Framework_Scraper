# Automated SISTER FrameWork Scraper
This code lets you automate the "note" research of the SISTER Framework, in the [portale banche dati](https://portalebanchedaticdl.visura.it/homepageAreeTematicheAction.do) website.

It gathers the PDF files for property successions and parses them

## How to run the code:
```
./src/main.py [-h] -u USERNAME -p PASSWORD -n NUMSTART -N NUMEND
```
This will automatically create the output.csv file that can be viewed with tools such as [Google Sheets](https://www.google.com/sheets/about/)
