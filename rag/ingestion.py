from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rag.chunking import chunk_text
from rag.embeddings import Embedder
from rag.extraction import clean_text, extract_document
from rag.vector_store import VectorStore


SUPPORTED = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}


class KnowledgeBase:
    """
    Incremental local knowledge base.

    Documents are hashed so unchanged documents are not re-chunked
    or re-embedded.

    FAISS stores vectors while all citation metadata is retained
    alongside each vector.
    """

    def __init__(self, settings):
        self.settings = settings

        self.doc_dir = settings.data_dir / "documents"
        self.chunk_dir = settings.data_dir / "chunks"
        self.faiss_dir = settings.data_dir / "faiss"

        self.manifest_path = settings.data_dir / "manifest.json"
        self.chunks_path = settings.data_dir / "all_chunks.json"
        self.metadata_path = settings.data_dir / "metadata.json"

        self.doc_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.chunk_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.faiss_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.manifest = self._load_json(
            self.manifest_path,
            {},
        )

        self.all_chunks = self._load_json(
            self.chunks_path,
            [],
        )

        if not isinstance(self.manifest, dict):
            self.manifest = {}

        if not isinstance(self.all_chunks, list):
            self.all_chunks = []

        self.embedder = None
        self.store = VectorStore(
            self.faiss_dir
        )

    # ---------------------------------------------------------
    # LOAD / SAVE
    # ---------------------------------------------------------

    @staticmethod
    def _load_json(path: Path, default):
        if not path.exists():
            return default

        try:
            return json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )
        except Exception:
            return default

    @staticmethod
    def _write_json(
        path: Path,
        value,
    ) -> None:
        path.write_text(
            json.dumps(
                value,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    # ---------------------------------------------------------
    # HASHING
    # ---------------------------------------------------------

    @staticmethod
    def sha256(path: Path) -> str:
        digest = hashlib.sha256()

        with path.open("rb") as file:
            for block in iter(
                lambda: file.read(1024 * 1024),
                b"",
            ):
                digest.update(block)

        return digest.hexdigest()

    # ---------------------------------------------------------
    # SOURCE FILES
    # ---------------------------------------------------------

    def _all_source_files(self) -> list[Path]:
        return sorted(
            (
                path
                for path in self.doc_dir.rglob("*")
                if path.is_file()
                and path.suffix.lower() in SUPPORTED
            ),
            key=lambda path: str(path).lower(),
        )

    # ---------------------------------------------------------
    # CHUNKING
    # ---------------------------------------------------------

    def _chunks_for_file(
        self,
        path: Path,
        digest: str,
    ) -> list[dict]:

        doc_id = digest[:16]
        chunks: list[dict] = []

        pages = extract_document(path)

        for page in pages:
            raw_text = page.get(
                "text",
                "",
            )

            cleaned = clean_text(
                raw_text
            )

            if not cleaned:
                continue

            page_number = page.get(
                "page",
                1,
            )

            section = page.get(
                "section",
                "",
            )

            page_chunks = chunk_text(
                cleaned,
                self.settings.chunk_size,
                self.settings.chunk_overlap,
            )

            for number, chunk in enumerate(
                page_chunks
            ):
                chunk = chunk.strip()

                if not chunk:
                    continue

                chunks.append(
                    {
                        "document_id": doc_id,
                        "filename": path.name,
                        "file_type": path.suffix.lower(),
                        "source_type": "knowledge_base",
                        "page": page_number,
                        "section": section,
                        "chunk_id": (
                            f"{doc_id}-{number:04d}"
                        ),
                        "text": chunk,
                    }
                )

        return chunks

    # ---------------------------------------------------------
    # METADATA
    # ---------------------------------------------------------

    def _write_metadata(
        self,
        embedding_dimension: int | None = None,
    ) -> None:

        metadata = []

        for index, chunk in enumerate(
            self.all_chunks
        ):
            metadata.append(
                {
                    "faiss_index": index,
                    "document_id": chunk.get(
                        "document_id"
                    ),
                    "filename": chunk.get(
                        "filename"
                    ),
                    "file_type": chunk.get(
                        "file_type"
                    ),
                    "source_type": chunk.get(
                        "source_type"
                    ),
                    "page": chunk.get(
                        "page"
                    ),
                    "section": chunk.get(
                        "section",
                        "",
                    ),
                    "chunk_id": chunk.get(
                        "chunk_id"
                    ),
                    "embedding_model": (
                        self.settings.embedding_model
                    ),
                    "embedding_dimension": (
                        embedding_dimension
                    ),
                }
            )

        payload = {
            "version": 2,
            "embedding_model": (
                self.settings.embedding_model
            ),
            "embedding_dimension": (
                embedding_dimension
            ),
            "total_documents": len(
                self.manifest
            ),
            "total_chunks": len(
                self.all_chunks
            ),
            "vector_index": "FAISS IndexFlatIP",
            "chunks": metadata,
        }

        self._write_json(
            self.metadata_path,
            payload,
        )

    # ---------------------------------------------------------
    # BUILD / INCREMENTAL UPDATE
    # ---------------------------------------------------------

    def build(self) -> dict:
        files = self._all_source_files()

        current: dict = {}
        changed: list = []
        removed_ids: set[str] = set()

        # ---------------------------------------------
        # Detect current files and changed documents
        # ---------------------------------------------

        for path in files:
            relative_path = str(
                path.relative_to(
                    self.doc_dir
                )
            )

            digest = self.sha256(path)
            doc_id = digest[:16]

            current[relative_path] = {
                "sha256": digest,
                "document_id": doc_id,
                "filename": path.name,
            }

            old = self.manifest.get(
                relative_path
            )

            if (
                not old
                or old.get("sha256") != digest
            ):
                changed.append(
                    (
                        relative_path,
                        path,
                        digest,
                        doc_id,
                    )
                )

        # ---------------------------------------------
        # Detect removed files
        # ---------------------------------------------

        for relative_path, old in (
            self.manifest.items()
        ):
            if relative_path not in current:
                old_id = old.get(
                    "document_id"
                )

                if old_id:
                    removed_ids.add(
                        old_id
                    )

        # ---------------------------------------------
        # Remove old chunks for changed/removed docs
        # ---------------------------------------------

        old_changed_ids = {
            self.manifest[relative_path][
                "document_id"
            ]
            for relative_path, _, _, _ in changed
            if relative_path in self.manifest
            and self.manifest[
                relative_path
            ].get("document_id")
        }

        drop_ids = (
            removed_ids
            | old_changed_ids
        )

        if drop_ids:
            self.all_chunks = [
                chunk
                for chunk in self.all_chunks
                if chunk.get(
                    "document_id"
                ) not in drop_ids
            ]

        # ---------------------------------------------
        # Create chunks for changed docs
        # ---------------------------------------------

        added_chunks: list[dict] = []

        for _, path, digest, _ in changed:
            added_chunks.extend(
                self._chunks_for_file(
                    path,
                    digest,
                )
            )

        self.all_chunks.extend(
            added_chunks
        )

        # ---------------------------------------------
        # Rebuild vector index when required
        # ---------------------------------------------

        must_rebuild = bool(
            changed
            or removed_ids
            or (
                self.all_chunks
                and self.store.count == 0
            )
        )

        embedding_dimension = None

        if must_rebuild:
            texts = [
                chunk.get("text", "")
                for chunk in self.all_chunks
            ]

            texts = [
                text
                for text in texts
                if text.strip()
            ]

            if texts:
                if self.embedder is None:
                    self.embedder = Embedder(
                        self.settings.embedding_model
                    )

                vectors = self.embedder.encode(
                    texts
                )

                embedding_dimension = int(
                    vectors.shape[1]
                )

                self.store.replace(
                    vectors,
                    self.all_chunks,
                )

            else:
                self._clear_vector_store()

        elif self.store.count:
            try:
                embedding_dimension = int(
                    self.store.index.d
                )
            except Exception:
                embedding_dimension = None

        # ---------------------------------------------
        # Persist current state
        # ---------------------------------------------

        self.manifest = current

        self._write_json(
            self.manifest_path,
            self.manifest,
        )

        self._write_json(
            self.chunks_path,
            self.all_chunks,
        )

        self._write_metadata(
            embedding_dimension
        )

        return {
            "documents": len(files),
            "chunks": len(
                self.all_chunks
            ),
            "vectors": len(
                self.all_chunks
            ),
            "changed_documents": len(
                changed
            ),
            "removed_documents": len(
                removed_ids
            ),
            "reembedded": must_rebuild,
            "metadata_file": str(
                self.metadata_path
            ),
        }

    # ---------------------------------------------------------
    # UPLOADS
    # ---------------------------------------------------------

    def add_upload(
        self,
        source_path: str | Path,
    ) -> Path:

        source_path = Path(
            source_path
        )

        if not source_path.exists():
            raise FileNotFoundError(
                f"Upload does not exist: "
                f"{source_path}"
            )

        if not source_path.is_file():
            raise ValueError(
                "Upload path is not a file."
            )

        suffix = (
            source_path.suffix.lower()
        )

        if suffix not in SUPPORTED:
            raise ValueError(
                f"Unsupported knowledge-base "
                f"file type: {suffix}"
            )

        target = (
            self.doc_dir
            / source_path.name
        )

        # Avoid accidental overwrite when a different
        # uploaded file has the same name.
        if target.exists():
            old_hash = self.sha256(
                target
            )
            new_hash = self.sha256(
                source_path
            )

            if old_hash != new_hash:
                stem = target.stem
                suffix = target.suffix

                counter = 2

                while target.exists():
                    target = (
                        self.doc_dir
                        / f"{stem}-{counter}{suffix}"
                    )
                    counter += 1

        target.write_bytes(
            source_path.read_bytes()
        )

        return target

    # ---------------------------------------------------------
    # VECTOR STORE RESET
    # ---------------------------------------------------------

    def _clear_vector_store(self) -> None:
        self.store.index = None
        self.store.metadata = []

        if self.store.index_path.exists():
            self.store.index_path.unlink()

        self.store.meta_path.write_text(
            "[]",
            encoding="utf-8",
        )
