import requests
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": API_KEY, "isbns": isbn}).json()
print("Average Rating:", res['books'][0]['average_rating'], "AND Ratings Count:", res['books'][0]['work_ratings_count'])

res2 = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:0446545244").json()
print(res2['items'][0]['volumeInfo']['categories'])
print(res2['items'][0]['volumeInfo']['description']) #Description
print(res2['items'][0]['volumeInfo']['previewLink']) #Direct to google books
imageLinkParts = res2['items'][0]['volumeInfo']['imageLinks']['thumbnail'].split('zoom=1')  #Image links
imageLink = imageLinkParts[0] + "zoom=0" + imageLinkParts[1]
print(imageLink)
print(res2)

# from datetime import datetime

# now = datetime.now()
# current_time = now.strftime("%H:%M:%S")
# today = datetime.now().date()
# date = today.strftime('%a %b %d %Y')
# print(current_time)
# print (date)