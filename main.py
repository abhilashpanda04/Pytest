import ell
from dotenv import load_dotenv
import os
from openai import OpenAI
from PyPDF2 import PdfReader


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

ell.init(verbose=True)


class ParseTable:
    
    def __init__(self):
        pass

    @ell.simple(model="gpt-4o-mini",
                client=OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
                )
    def parse_table(self, extract_table: str, your_xml_format: str):
        """Convert text to XML format based on provided structure."""
        prompt = f"Given the text: \n {extract_table} \n Generate the xml in the below format." + \
            f"xml format: {your_xml_format}" + \
            "else output 'No table found'"
        return prompt

class ExtractTable:
    def __init__(self):
        pass

    @ell.tool()
    def load_pdf(path: str, page: int = 1):
        """Reads PDF and returns text based on page number."""
        with open(path, "rb") as f:
            pdf = PdfReader(f)
            return pdf.pages[page - 1].extract_text() if page else pdf.pages[0].extract_text()

    @ell.complex(model="gpt-4o-mini",
                tools=[load_pdf],
                temperature=0.1)
    def extract_table(self, pdf_text: str):
        """Extract table from PDF text in structured JSON format."""
        prompt = f"Given the context: \n {pdf_text} \n identify if there is a table and if yes, extract only latest period from the table in structured json." + \
            "json format: {table_name,field_name,field_value,year}" + \
            "else output 'No table found'"
        return prompt

    @ell.simple(model="gpt-4o-mini",
                client=OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
                )
    def verify_output(self, output_text: str):
        """Check if the output text is in JSON format."""
        prompt = f"Given the text: {output_text} \n question: Is it json formatted or not, if not formatted valid output is: No table found, your answer should be yes or no"
        return prompt

class PdfReader:
    def __init__(self, path):
        self.path = path

    @ell.tool()
    def load_pdf(self, path: str, page: int):
        """Reads PDF and returns text based on page number."""
        with open(path, "rb") as f:
            pdf = PdfReader(f)
            return pdf.pages[page - 1].extract_text() if page else pdf.pages[0].extract_text()

    @ell.complex(model="gpt-4o-mini",
                tools=[load_pdf],
                temperature=0.1)
    def get_pdf(self, path: str, page: int):
        """Read PDF from the specified path and page number."""
        prompt = f"use the tool to read pdf from the path: {path} and page number from {page}"
        return prompt

if __name__ == "__main__":
    response = get_pdf("AppTech Corp 10-K 04-01-2024.pdf", 16)
    if response.tool_calls:
        tool_results = response.call_tools_and_collect_as_message()
        text = tool_results.text
        print("Tool results:", tool_results.text)

    extractor = ExtractTable()
    greeting = extractor.extract_table(text)  # Changed 'pdf' to 'text'
    thoughts = extractor.verify_output(greeting)



