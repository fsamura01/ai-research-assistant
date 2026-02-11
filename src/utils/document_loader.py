"""Document loading utilities for multiple formats"""
from typing import List, Dict, Optional
from pathlib import Path
import pypdf
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
import re
import zipfile
import io
import frontmatter
import os

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
    def load_pdf(file_path_or_obj) -> List[Document]:
        """Load and parse PDF file (accepts path string or file-like object)"""
        documents = []
        
        # Determine source name for metadata
        if isinstance(file_path_or_obj, (str, Path)):
            path = Path(file_path_or_obj)
            source_name = str(path)
            file_context = open(path, 'rb')
        else:
            # Assume file-like object (e.g. Streamlit UploadedFile)
            source_name = getattr(file_path_or_obj, 'name', 'uploaded_file.pdf')
            file_context = file_path_or_obj

        try:
            pdf_reader = pypdf.PdfReader(file_context)
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                
                if text.strip():  # Only add non-empty pages
                    doc = Document(
                        content=text,
                        metadata={
                            "source_type": "pdf",
                            "source_path": source_name,
                            "page_number": page_num + 1,
                            "total_pages": len(pdf_reader.pages),
                            "source_authority": 7
                        }
                    )
                    documents.append(doc)
        finally:
            # Only close if we opened it ourselves
            if isinstance(file_path_or_obj, (str, Path)):
                file_context.close()
        
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
                    "title": title,
                    "source_authority": 5
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
                    "video_id": video_id,
                    "source_authority": 4
                }
            )
        except Exception as e:
            raise ValueError(f"Failed to load YouTube transcript: {str(e)}")
    
    @staticmethod
    def parse_github_url(url: str) -> Optional[Dict[str, str]]:
        """Extract owner and repo name from a GitHub URL."""
        # Handle variations like https://github.com/owner/repo or github.com/owner/repo
        pattern = r"github\.com/([^/]+)/([^/]+)"
        match = re.search(pattern, url)
        if match:
            return {
                "owner": match.group(1),
                "repo": match.group(2).replace(".git", "")
            }
        return None

    @staticmethod
    def load_github_repo(repo_owner: str, repo_name: str, branch: str = 'main') -> List[Document]:
        """
        Download and parse markdown files from a GitHub repository.
        """
        prefix = 'https://codeload.github.com' 
        url = f'{prefix}/{repo_owner}/{repo_name}/zip/refs/heads/{branch}'
        
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            
            repo_docs = []
            zf = zipfile.ZipFile(io.BytesIO(response.content))
            
            for file_info in zf.infolist():
                filename = file_info.filename
                filename_lower = filename.lower()
                
                # Only process markdown files
                if not (filename_lower.endswith('.md') or filename_lower.endswith('.mdx')):
                    continue
                
                try:
                    with zf.open(file_info) as f_in:
                        content = f_in.read().decode('utf-8', errors='ignore')
                        
                        # Parse frontmatter if present
                        post = frontmatter.loads(content)
                        text_content = post.content
                        metadata = post.to_dict()
                        
                        # Remove content from metadata to avoid duplication
                        if 'content' in metadata:
                            del metadata['content']
                            
                        # Add standard metadata
                        metadata.update({
                            "source_type": "github",
                            "repo": f"{repo_owner}/{repo_name}",
                            "filename": filename,
                            "source_url": f"https://github.com/{repo_owner}/{repo_name}/blob/{branch}/{filename.split('/', 1)[-1]}",
                            "source_authority": 9
                        })
                        
                        if text_content.strip():
                            repo_docs.append(Document(content=text_content, metadata=metadata))
                            
                except Exception as e:
                    print(f"      [WARNING] Skipping {filename}: {e}")
                    continue
            
            zf.close()
            print(f"   ✅ Loaded {len(repo_docs)} markdown files from GitHub: {repo_owner}/{repo_name}")
            return repo_docs
            
        except Exception as e:
            raise ValueError(f"Failed to download GitHub repository {repo_owner}/{repo_name}: {str(e)}")


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