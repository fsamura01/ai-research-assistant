import sys
import os
import unittest

# Adds the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.document_loader import Document, DocumentLoader

class TestDocumentLoader(unittest.TestCase):
    def setUp(self):
        self.loader = DocumentLoader()

    def test_document_creation(self):
        doc = Document(content="test", metadata={"key": "value"})
        self.assertEqual(doc.content, "test")
        self.assertEqual(doc.metadata["key"], "value")

    def test_document_repr(self):
        doc = Document(content="hello world", metadata={"source_type": "test"})
        self.assertIn("source=test", repr(doc))
        self.assertIn("length=11", repr(doc))

if __name__ == "__main__":
    unittest.main()
