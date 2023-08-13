import os
from zipfile import ZipFile
import uuid
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

class ImageDownloader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('URL Image Downloader')

        # Create UI elements
        tk.Label(self.root, text="Enter URL:").pack(pady=10)
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack(pady=10)
        tk.Button(self.root, text="Download Images", command=self.download_images).pack(pady=20)
        self.root.mainloop()

    def download_images(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a URL!")
            return

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Referrer": url
        }

        # Fetch web page
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Parse the page using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            img_tags = soup.find_all('img')
            if not img_tags:
                messagebox.showinfo("Info", "No images found on the provided URL!")
                return

            # Ask user for output directory
            output_folder = filedialog.askdirectory(title="Select Output Folder")
            if not output_folder:
                return

            zip_filename = os.path.join(output_folder, f"images_{uuid.uuid4().hex[:8]}.zip")

            with ZipFile(zip_filename, 'w') as zipf:
                for img_tag in img_tags:
                    img_url = img_tag.get('src')
                    if img_url:
                        # Resolve relative URLs
                        img_url = urljoin(url, img_url)

                        try:
                            img_response = requests.get(img_url, headers=headers, stream=True)
                            img_response.raise_for_status()

                            temp_file = os.path.join(output_folder, "temp_img")
                            with open(temp_file, 'wb') as img_file:
                                for chunk in img_response.iter_content(chunk_size=8192):
                                    img_file.write(chunk)
                            zipf.write(temp_file, os.path.basename(img_url))
                            os.remove(temp_file)

                        except requests.RequestException:
                            print(f"Failed to download {img_url}")

            messagebox.showinfo("Info", f"Downloaded images saved to {zip_filename}")

        except requests.RequestException:
            messagebox.showerror("Error", "Failed to fetch the provided URL!")

if __name__ == "__main__":
    app = ImageDownloader()
