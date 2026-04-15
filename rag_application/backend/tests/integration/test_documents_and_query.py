"""End-to-end tests for the /documents and /query routes."""

from __future__ import annotations

import fitz
from fastapi.testclient import TestClient


def _build_pdf(pages: list[str]) -> bytes:
    doc = fitz.open()
    for body in pages:
        page = doc.new_page()
        page.insert_text((72, 72), body, fontsize=11)
    data = doc.tobytes()
    doc.close()
    return data


def _register_and_login(client: TestClient, email: str = "eve@test.com") -> str:
    client.post("/auth/register", json={"email": email, "password": "supersecret1"})
    login = client.post("/auth/login", json={"email": email, "password": "supersecret1"})
    return login.json()["access_token"]


def test_upload_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("x.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert response.status_code == 401


def test_upload_rejects_non_pdf(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_upload_list_and_delete_cycle(client: TestClient) -> None:
    token = _register_and_login(client)
    pdf = _build_pdf(
        [
            "This contract defines a probation period of ninety days for new employees.",
            "Vacation entitlement is twenty-one working days per calendar year.",
        ]
    )

    upload = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("contract.pdf", pdf, "application/pdf")},
    )
    assert upload.status_code == 201
    body = upload.json()
    assert body["filename"] == "contract.pdf"
    assert body["num_pages"] == 2
    assert body["num_chunks"] >= 2
    document_id = body["id"]

    listing = client.get(
        "/documents",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert listing.status_code == 200
    docs = listing.json()
    assert len(docs) == 1
    assert docs[0]["id"] == document_id
    assert docs[0]["filename"] == "contract.pdf"

    delete_response = client.delete(
        f"/documents/{document_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_response.status_code == 204

    after_delete = client.get(
        "/documents",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert after_delete.json() == []


def test_query_requires_authentication(client: TestClient) -> None:
    response = client.post("/query", json={"question": "what is the probation period?"})
    assert response.status_code == 401


def test_query_returns_answer_and_sources_after_upload(client: TestClient) -> None:
    token = _register_and_login(client, email="query@test.com")
    pdf = _build_pdf(
        [
            "The probation period is ninety calendar days. It may be extended once.",
        ]
    )
    upload = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("contract.pdf", pdf, "application/pdf")},
    )
    assert upload.status_code == 201

    query = client.post(
        "/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "What is the probation period?"},
    )
    assert query.status_code == 200
    body = query.json()
    assert body["answer"]
    assert isinstance(body["sources"], list)
    assert len(body["sources"]) >= 1
    assert body["sources"][0]["filename"] == "contract.pdf"
    assert body["sources"][0]["page"] >= 1


def test_query_with_empty_corpus_returns_fallback(client: TestClient) -> None:
    token = _register_and_login(client, email="lonely@test.com")
    query = client.post(
        "/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "anything at all"},
    )
    assert query.status_code == 200
    body = query.json()
    assert "not in the provided documents" in body["answer"].lower()
    assert body["sources"] == []


def test_documents_isolated_between_users(client: TestClient) -> None:
    token_a = _register_and_login(client, email="a@test.com")
    token_b = _register_and_login(client, email="b@test.com")
    pdf = _build_pdf(["User A private data about project alpha."])

    upload = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"file": ("alpha.pdf", pdf, "application/pdf")},
    )
    assert upload.status_code == 201

    # User A sees their document.
    listing_a = client.get("/documents", headers={"Authorization": f"Bearer {token_a}"})
    assert len(listing_a.json()) == 1

    # User B sees nothing.
    listing_b = client.get("/documents", headers={"Authorization": f"Bearer {token_b}"})
    assert listing_b.json() == []

    # And a query from user B falls back because there is nothing to retrieve.
    query_b = client.post(
        "/query",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"question": "What does user A know?"},
    )
    assert query_b.status_code == 200
    assert query_b.json()["sources"] == []
