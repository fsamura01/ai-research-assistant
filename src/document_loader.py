"""Document loading utilities for multiple formats"""
from typing import List, Dict, Optional
from pathlib import Path
import pypdf
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
import re

class Document:
    """Represents a document with content and metadata"""
    
    def __init__(self, content: str, metadata: Dict):
        self.content = content
        self.metadata = metadata
    
    def __repr__(self):
        return f"Document(source={self.metadata.get('source_type')}, length={len(self.content)})"


class DocumentLoader:
    """Load documents from various sources"""
    
    @staticmethod
    def load_pdf(file_path: str) -> List[Document]:
        """Load and parse PDF file"""
        documents = []
        path = Path(file_path)
        
        with open(path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                
                if text.strip():  # Only add non-empty pages
                    doc = Document(
                        content=text,
                        metadata={
                            "source_type": "pdf",
                            "source_path": str(path),
                            "page_number": page_num + 1,
                            "total_pages": len(pdf_reader.pages)
                        }
                    )
                    documents.append(doc)
        
        return documents
    
    @staticmethod
    def load_web_page(url: str) -> Document:
        """Load and parse web page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Get title
            title = soup.title.string if soup.title else url
            
            return Document(
                content=text,
                metadata={
                    "source_type": "web",
                    "source_url": url,
                    "title": title
                }
            )
        except Exception as e:
            raise ValueError(f"Failed to load web page {url}: {str(e)}")
    
    @staticmethod
    def load_youtube_transcript(url: str) -> Document:
        """Load YouTube video transcript"""
        # Extract video ID from URL
        video_id_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]+)', url)
        if not video_id_match:
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        video_id = video_id_match.group(1)
        
        try:
            # Get transcript
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id)
            
            # Combine transcript text
            content = " ".join([item.text for item in transcript_list])
            
            return Document(
                content=content,
                metadata={
                    "source_type": "youtube",
                    "source_url": url,
                    "video_id": video_id
                }
            )
        except Exception as e:
            raise ValueError(f"Failed to load YouTube transcript: {str(e)}")


# Example usage
if __name__ == "__main__":
    loader = DocumentLoader()
    
    # Test PDF loading
    docs = loader.load_pdf("data/neuronetworksbook.pdf")
    print(f"Loaded {len(docs)} pages from PDF")
    
    # Test web page loading
    doc = loader.load_web_page("https://en.wikipedia.org/wiki/Python_(programming_language)")
    print(f"Loaded web page: {doc.metadata['title']}")
    
    # Test YouTube transcript
    doc = loader.load_youtube_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print(f"Loaded YouTube transcript: {len(doc.content)} characters")
    
    print("DocumentLoader ready to use!")