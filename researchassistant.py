import time
from metaphor_python import Metaphor
from bs4 import BeautifulSoup
import requests
import openai
from flask import Flask, render_template, request
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up OpenAI API key
openai.api_key = "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"

# Set up Metaphor API key
metaphor_key = "fd616880-e3ac-4c24-9e24-78f3cd541b36"
metaphor = Metaphor(metaphor_key)

app = Flask(__name__)

# Function to search Metaphor for relevant sources
def search_metaphor(question):
    search_results = metaphor.search(question, use_autoprompt=True)
    return search_results

# Function to scrape and summarize web content
def scrape_and_summarize(search_results):
    scraped_content = []
    for i in range(5):  # Reducing number of sources to 5
        response = requests.get(search_results.results[i].url, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            contents = soup.find_all('body')
            for content in contents:
                scraped_content.append(content.text.replace("\t", "").replace("\r", "").replace("\n", ""))
        else:
            scraped_content.append("Failed to fetch data from " + search_results.results[i].url)

    summaries = []
    combined_content = " ".join(scraped_content)
    if len(combined_content) < 10000:
        summaries.append(summarize(combined_content[:10000]))
    return summaries

# Function to summarize text
def summarize(text):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt="Summarize the following text:\n" + text,
        max_tokens=50  # Adjust the max_tokens to control the length of the summary
    )
    return response.choices[0].text

# Function to answer user's question
def answer_question(question, summaries):
    summary = summarize(question + "," + str(summaries))
    return summary

# Flask route for both input form and results
@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    if request.method == 'POST':
        question = request.form['question']
        search_results = search_metaphor(question)
        summaries = scrape_and_summarize(search_results)
        summary = answer_question(question, summaries)
    return render_template('index.html', summary=summary)


if __name__ == '__main__':
    app.run(debug=True)
