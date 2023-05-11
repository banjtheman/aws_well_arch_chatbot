import os
import requests
from langchain.document_loaders import SeleniumURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Setup Chrome Driver, may need to change based on system
service = Service("/usr/bin/chromedriver")
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=service, options=options)

def extract_urls_from_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    if response.status_code != 200:
        print(f"Failed to fetch sitemap: {response.status_code}")
        return []

    sitemap_content = response.content
    root = ET.fromstring(sitemap_content)

    # Extract the URLs from the sitemap
    urls = [
        elem.text
        for elem in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    ]

    return urls


def load_html_text(sitemap_urls):
    loader = SeleniumURLLoader(urls=sitemap_urls)
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
    texts = text_splitter.split_documents(data)

    return texts


def embed_text(texts, save_loc):
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
    docsearch = FAISS.from_documents(texts, embeddings)

    docsearch.save_local(save_loc)


def main() -> None:
    """
    Purpose:
        Ingest data into a a local db
    Args:
        N/A
    Returns:
        N/A
    """
    # Site maps for the AWS Well-Architected Framework
    sitemap_url_list = [
        "https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/sitemap.xml",
        "https://docs.aws.amazon.com/wellarchitected/latest/framework/sitemap.xml",
        "https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/sitemap.xml",
        "https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/sitemap.xml",
        "https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/sitemap.xml",
        "https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/sitemap.xml",
        "https://docs.aws.amazon.com/wellarchitected/latest/sustainability-pillar/sitemap.xml",
    ]

    # Get all links from the sitemaps
    full_sitemap_list = []
    for sitemap in sitemap_url_list:
        full_sitemap_list.extend(extract_urls_from_sitemap(sitemap))

    print(full_sitemap_list)
    # get the raw html text
    texts = load_html_text(full_sitemap_list)
    # print(texts)
    # Save embeddings to local_index
    embed_text(texts, "local_index")


if __name__ == "__main__":
    main()
