from langchain.text_splitter import TextSplitter
import dspy
from typing import List
from langchain.docstore.document import Document


class ExtractSentences(dspy.Signature):
    """Extract meaningful propositions (semantic chunks) from the given text."""
    text = dspy.InputField()
    sentences = dspy.OutputField(desc="List of extracted sentences")


class ExtractSentencesProgram(dspy.Program):
    def run(self, text):
        extract = dspy.Predict(ExtractSentences)
        result = extract(text=text)
        return result.sentences


class LlmSemanticChunker(TextSplitter):
    def __init__(self, llm, chunk_size: int = 1000):
        super().__init__(chunk_size=chunk_size)
        self.llm = llm
        self.chunk_size = chunk_size  # Explicitly set chunk_size as an instance attribute
        dspy.settings.configure(lm=llm)
        self.extractor = ExtractSentencesProgram()

    def get_propositions(self, text):
        sentences = self.extractor.run(text)

        if isinstance(sentences, list):
            return sentences

        # Fallback: extract sentences heuristically
        return [s.strip() for s in text.split('.') if s.strip()]

    def split_text(self, text: str) -> List[str]:
        """Extract propositions and chunk them accordingly."""
        propositions = self.get_propositions(text)
        return self._chunk_propositions(propositions)

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        split_docs = []
        for doc in documents:
            chunks = self.split_text(doc.page_content)
            for i, chunk in enumerate(chunks):
                metadata = doc.metadata.copy()
                metadata.update({"chunk_index": i})
                split_docs.append(
                    Document(page_content=chunk, metadata=metadata))
        return split_docs

    def _chunk_propositions(self, propositions: List[str]) -> List[str]:
        chunks = []
        current_chunk = []
        current_size = 0

        for prop in propositions:
            prop_size = len(prop)
            if current_size + prop_size > self.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_size = 0
            current_chunk.append(prop)
            current_size += prop_size

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks
