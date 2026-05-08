# ============================================================
# FILE NAME : amazon_scraper.py
# ROLE      : Role 5 - Web Scraping Developer (Amazon)
# PROJECT   : Product Sentiment Analyzer & Review Dashboard
# TEAM      : Backend / Scraper Team
# TECH      : Selenium + BeautifulSoup + MongoDB
# ============================================================
# HOW TO RUN:
#   Step 1: pip install selenium beautifulsoup4 pymongo webdriver-manager
#   Step 2: Make sure MongoDB is running (mongod)
#   Step 3: py amazon_scraper.py
# ============================================================


# ---------- IMPORTS ----------
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
import time
import re


# ============================================================
# FUNCTION 1: Connect to MongoDB
# ============================================================
def connect_mongodb():
    try:
        # Local MongoDB connection
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.server_info()  # Test connection
        db = client["sentiment_analyzer"]
        collection = db["amazon_reviews"]
        print("[OK] MongoDB Connected Successfully!")
        return collection
    except Exception as e:
        print(f"[ERROR] MongoDB Connection Failed: {e}")
        print("[INFO] Make sure MongoDB is running: type 'mongod' in terminal")
        return None


# ============================================================
# FUNCTION 2: Setup Chrome Browser (Selenium)
# ============================================================
def setup_driver():
    options = Options()

    # Run browser without opening window
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Fake user agent so Amazon doesn't block us
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # Auto install ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    print("[OK] Chrome Browser Started!")
    return driver


# ============================================================
# FUNCTION 3: Search Amazon for a Product
# ============================================================
def search_amazon(driver, product_name):
    print(f"\n[SEARCH] Searching Amazon for: '{product_name}'")

    try:
        driver.get("https://www.amazon.in")
        time.sleep(3)

        # Find search box and type product name
        search_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
        )
        search_box.clear()
        search_box.send_keys(product_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        # Click first product in search results
        first_product = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[data-component-type='s-search-result'] h2 a")
            )
        )

        product_url   = first_product.get_attribute("href")
        product_title = first_product.text.strip()

        print(f"[FOUND] {product_title[:60]}...")
        return product_url, product_title

    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        return None, None


# ============================================================
# FUNCTION 4: Scrape Product Details (name, price, rating)
# ============================================================
def scrape_product_details(driver, product_url):
    print("\n[INFO] Scraping product details...")

    try:
        driver.get(product_url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Product Name
        try:
            name = soup.find("span", {"id": "productTitle"}).get_text(strip=True)
        except:
            name = "Unknown Product"

        # Overall Star Rating
        try:
            rating_tag = soup.find("span", {"data-hook": "rating-out-of-text"})
            if not rating_tag:
                rating_tag = soup.find("i", {"data-hook": "average-star-rating"})
            rating_text   = rating_tag.get_text(strip=True)
            overall_rating = float(re.search(r"[\d.]+", rating_text).group())
        except:
            overall_rating = 0.0

        # Total Number of Reviews
        try:
            count_tag    = soup.find("span", {"data-hook": "total-review-count"})
            count_text   = count_tag.get_text(strip=True)
            review_count = int(re.sub(r"[^0-9]", "", count_text))
        except:
            review_count = 0

        # Price
        try:
            price_tag = soup.find("span", {"class": "a-price-whole"})
            price = "Rs." + price_tag.get_text(strip=True) if price_tag else "N/A"
        except:
            price = "N/A"

        product_data = {
            "product_name"  : name,
            "overall_rating": overall_rating,
            "total_reviews" : review_count,
            "price"         : price,
            "product_url"   : product_url,
            "scraped_at"    : datetime.now()
        }

        print(f"  Name    : {name[:50]}")
        print(f"  Rating  : {overall_rating} stars")
        print(f"  Reviews : {review_count}")
        print(f"  Price   : {price}")

        return product_data

    except Exception as e:
        print(f"[ERROR] Product detail scraping failed: {e}")
        return {}


# ============================================================
# FUNCTION 5: Go to Full Reviews Page
# ============================================================
def go_to_reviews_page(driver, product_url):
    print("\n[INFO] Navigating to reviews page...")

    try:
        # Try clicking 'See all reviews' button
        see_all = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a[data-hook='see-all-reviews-link-foot']")
            )
        )
        see_all.click()
        time.sleep(3)
        print("[OK] Navigated to reviews page!")
        return True

    except:
        try:
            # Alternative: build reviews URL directly from product URL
            asin_match = re.search(r"/dp/([A-Z0-9]{10})", product_url)
            if asin_match:
                asin = asin_match.group(1)
                reviews_url = f"https://www.amazon.in/product-reviews/{asin}/?reviewerType=all_reviews"
                driver.get(reviews_url)
                time.sleep(3)
                print(f"[OK] Opened reviews URL directly: {reviews_url}")
                return True
        except Exception as e:
            print(f"[ERROR] Could not navigate to reviews page: {e}")
            return False


# ============================================================
# FUNCTION 6: Scrape All Reviews on Current Page
# ============================================================
def scrape_reviews_from_page(driver, product_name):
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find all review blocks on the page
    review_blocks = soup.find_all("div", {"data-hook": "review"})
    reviews = []

    for block in review_blocks:
        try:
            # Reviewer Name
            try:
                reviewer = block.find("span", {"class": "a-profile-name"}).get_text(strip=True)
            except:
                reviewer = "Anonymous"

            # Star Rating (e.g. 4.0 out of 5)
            try:
                star_tag  = block.find("i", {"data-hook": "review-star-rating"})
                if not star_tag:
                    star_tag = block.find("i", {"data-hook": "cmps-review-star-rating"})
                star_text = star_tag.get_text(strip=True)
                stars     = float(re.search(r"[\d.]+", star_text).group())
            except:
                stars = 0.0

            # Review Title
            try:
                title_tag = block.find("a", {"data-hook": "review-title"})
                if not title_tag:
                    title_tag = block.find("span", {"data-hook": "review-title"})
                title = title_tag.get_text(strip=True)
                # Remove "X out of 5 stars" prefix if present
                title = re.sub(r"^\d+(\.\d+)?\s*out of \d+\s*stars\s*", "", title).strip()
            except:
                title = "No Title"

            # Review Body Text
            try:
                body = block.find("span", {"data-hook": "review-body"}).get_text(strip=True)
            except:
                body = ""

            # Review Date
            try:
                date_text = block.find("span", {"data-hook": "review-date"}).get_text(strip=True)
            except:
                date_text = "Unknown Date"

            # Verified Purchase badge
            try:
                verified_tag = block.find("span", {"data-hook": "avp-badge"})
                verified     = True if verified_tag else False
            except:
                verified = False

            # Helpful Votes
            try:
                helpful_tag  = block.find("span", {"data-hook": "helpful-vote-statement"})
                helpful_text = helpful_tag.get_text(strip=True) if helpful_tag else "0"
                helpful_num  = re.search(r"\d+", helpful_text)
                helpful      = int(helpful_num.group()) if helpful_num else 0
            except:
                helpful = 0

            # Build review dictionary
            review = {
                "product_name"     : product_name,
                "reviewer_name"    : reviewer,
                "star_rating"      : stars,
                "review_title"     : title,
                "review_body"      : body,
                "review_date"      : date_text,
                "verified_purchase": verified,
                "helpful_votes"    : helpful,
                "sentiment"        : None,       # NLP team fills this later
                "source"           : "Amazon",
                "scraped_at"       : datetime.now()
            }

            reviews.append(review)

        except Exception as e:
            # Skip broken review blocks
            continue

    print(f"  [PAGE] Found {len(reviews)} reviews")
    return reviews


# ============================================================
# FUNCTION 7: Click Next Page Button
# ============================================================
def go_to_next_page(driver):
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, "li.a-last a")
        next_btn.click()
        time.sleep(3)
        print("  [NEXT] Moving to next page...")
        return True
    except:
        print("  [DONE] No more pages found.")
        return False


# ============================================================
# FUNCTION 8: Save Reviews to MongoDB (No Duplicates)
# ============================================================
def save_to_mongodb(collection, reviews):
    if collection is None:
        print("[SKIP] No MongoDB connection. Skipping save.")
        return 0

    saved   = 0
    skipped = 0

    for review in reviews:
        # Check duplicate by reviewer name + review title + product
        exists = collection.find_one({
            "reviewer_name": review["reviewer_name"],
            "review_title" : review["review_title"],
            "product_name" : review["product_name"]
        })

        if not exists:
            collection.insert_one(review)
            saved += 1
        else:
            skipped += 1

    print(f"  [SAVE] Saved: {saved}  |  Skipped (duplicates): {skipped}")
    return saved


# ============================================================
# MAIN FUNCTION - Runs the full scraper
# ============================================================
def scrape_amazon_product(product_name, max_pages=3):
    print("\n" + "=" * 55)
    print("   AMAZON SCRAPER - Product Sentiment Analyzer")
    print("   Role 5: Web Scraping Developer")
    print("=" * 55)

    all_reviews  = []
    total_saved  = 0

    # Step 1: Connect MongoDB
    collection = connect_mongodb()

    # Step 2: Start browser
    driver = setup_driver()

    try:
        # Step 3: Search Amazon
        product_url, product_title = search_amazon(driver, product_name)
        if not product_url:
            print("[ERROR] Could not find product. Exiting.")
            return []

        # Step 4: Get product details
        product_data = scrape_product_details(driver, product_url)

        # Step 5: Go to reviews page
        go_to_reviews_page(driver, product_url)

        # Step 6: Scrape reviews page by page
        print(f"\n[START] Scraping reviews - Max {max_pages} pages...")

        for page_num in range(1, max_pages + 1):
            print(f"\n--- Page {page_num} of {max_pages} ---")

            page_reviews = scrape_reviews_from_page(driver, product_title)
            all_reviews.extend(page_reviews)

            # Save after each page
            if page_reviews:
                saved = save_to_mongodb(collection, page_reviews)
                total_saved += saved

            # Go to next page
            if page_num < max_pages:
                has_next = go_to_next_page(driver)
                if not has_next:
                    break

        # Step 7: Final Summary
        print("\n" + "=" * 55)
        print("   SCRAPING COMPLETE!")
        print(f"   Product  : {product_title[:45]}")
        print(f"   Rating   : {product_data.get('overall_rating', 'N/A')} stars")
        print(f"   Price    : {product_data.get('price', 'N/A')}")
        print(f"   Scraped  : {len(all_reviews)} reviews")
        print(f"   Saved DB : {total_saved} reviews")
        print(f"   Database : sentiment_analyzer > amazon_reviews")
        print("=" * 55)

        return all_reviews

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return []

    finally:
        driver.quit()
        print("[CLOSED] Browser closed.")


# ============================================================
# RUN HERE - Change product name as needed
# ============================================================
if __name__ == "__main__":

    # ✏️ Change this to any product you want to scrape
    PRODUCT_NAME = "Samsung Galaxy S24"

    # ✏️ Change number of review pages (1 page = ~10 reviews)
    MAX_PAGES = 3

    # Run the scraper
    reviews = scrape_amazon_product(
        product_name=PRODUCT_NAME,
        max_pages=MAX_PAGES
    )

    # Show sample output
    if reviews:
        print(f"\nTotal Reviews Collected: {len(reviews)}")
        print("\nSample Review Preview:")
        r = reviews[0]
        print(f"  Reviewer : {r['reviewer_name']}")
        print(f"  Stars    : {r['star_rating']}")
        print(f"  Title    : {r['review_title']}")
        print(f"  Body     : {r['review_body'][:80]}...")
        print(f"  Verified : {r['verified_purchase']}")
        print(f"  Date     : {r['review_date']}")
    else:
        print("No reviews collected.")