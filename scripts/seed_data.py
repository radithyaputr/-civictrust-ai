import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.rag.ingestion import DocumentIngestion
from app.database.connection import database


async def seed_documents():
    print("=" * 60)
    print("CivicTrust AI - Document Seeder")
    print("=" * 60)

    documents_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "documents", "sample_documents.json"
    )

    if not os.path.exists(documents_path):
        print(f"Error: File dokumen tidak ditemukan di {documents_path}")
        print("Jalankan script dari root direktori proyek.")
        sys.exit(1)

    with open(documents_path, "r", encoding="utf-8") as f:
        documents = json.load(f)

    print(f"\nMenemukan {len(documents)} dokumen untuk di-seed...\n")

    await database.connect()
    print("Database terhubung.\n")

    ingestion = DocumentIngestion()
    success_count = 0
    error_count = 0

    for doc in documents:
        try:
            print(f"  Mengingest: {doc['document_id']} ({doc['source_type']})...", end=" ")
            await ingestion.ingest(
                document_id=doc["document_id"],
                content=doc["content"],
                source=doc["source"],
                source_type=doc["source_type"],
                language="id",
                metadata={"title": doc.get("title", doc["document_id"])},
            )
            print("OK")
            success_count += 1
        except Exception as e:
            print(f"ERROR: {e}")
            error_count += 1

    await database.disconnect()

    print(f"\n{'=' * 60}")
    print(f"Seeding selesai!")
    print(f"  Berhasil: {success_count}")
    print(f"  Gagal: {error_count}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(seed_documents())
