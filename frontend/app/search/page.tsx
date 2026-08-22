"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  SearchResult,
  searchDocuments,
} from "@/lib/api";

export default function SearchPage() {
  const router = useRouter();

  const [query, setQuery] =
    useState("");

  const [topK, setTopK] =
    useState(5);

  const [results, setResults] =
    useState<SearchResult[]>([]);

  const [searchedQuery, setSearchedQuery] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  useEffect(() => {
    const token =
      localStorage.getItem(
        "access_token"
      );

    if (!token) {
      router.replace("/login");
    }
  }, [router]);

  async function handleSearch(
    event: FormEvent
  ) {
    event.preventDefault();

    const token =
      localStorage.getItem(
        "access_token"
      );

    if (!token) {
      router.replace("/login");
      return;
    }

    if (!query.trim()) {
      setError(
        "Enter something to search."
      );
      return;
    }

    try {
      setLoading(true);
      setError("");
      setResults([]);

      const data =
        await searchDocuments(
          token,
          query.trim(),
          topK
        );

      setSearchedQuery(
        data.query
      );

      setResults(
        data.results
      );
    } catch (err: any) {
      setError(
        err.message ||
          "Search failed."
      );
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    localStorage.removeItem(
      "access_token"
    );

    router.replace("/login");
  }

  return (
    <main className="app-page">
      <nav className="navbar">
        <div className="nav-brand">
          Personal KB
        </div>

        <div className="nav-links">
          <Link href="/dashboard">
            Dashboard
          </Link>

          <Link href="/documents">
            Documents
          </Link>

          <Link
            href="/search"
            className="active-link"
          >
            Search
          </Link>

          <button
            onClick={logout}
            className="logout-button"
          >
            Logout
          </button>
        </div>
      </nav>

      <section className="content">
        <div className="page-header">
          <div>
            <h1>
              Search Knowledge Base
            </h1>

            <p className="muted">
              Search your own uploaded
              documents using semantic
              search.
            </p>
          </div>
        </div>

        <div className="section-card">
          <form
            onSubmit={handleSearch}
            className="search-form"
          >
            <input
              type="text"
              value={query}
              onChange={(e) =>
                setQuery(e.target.value)
              }
              placeholder="Ask something about your documents..."
            />

            {/* Results dropdown: 1 to 5 */}
            <select
              value={topK}
              onChange={(e) =>
                setTopK(
                  Number(e.target.value)
                )
              }
            >
              <option value={1}>
                1 result
              </option>

              <option value={2}>
                2 results
              </option>

              <option value={3}>
                3 results
              </option>

              <option value={4}>
                4 results
              </option>

              <option value={5}>
                5 results
              </option>
            </select>

            <button
              type="submit"
              disabled={loading}
              className="primary-button"
            >
              {loading
                ? "Searching..."
                : "Search"}
            </button>
          </form>

          {error && (
            <div className="error">
              {error}
            </div>
          )}
        </div>

        {searchedQuery && (
          <div className="results-header">
            <h2>
              Results for "
              {searchedQuery}"
            </h2>

            <span>
              {results.length} result
              {results.length !== 1
                ? "s"
                : ""}
            </span>
          </div>
        )}

        {!loading &&
          searchedQuery &&
          results.length === 0 && (
            <div className="section-card empty-state">
              <h3>
                No relevant results
              </h3>

              <p className="muted">
                No document chunks passed
                the configured similarity
                threshold.
              </p>
            </div>
          )}

        <div className="results-list">
          {results.map(
            (result, index) => (
              <article
                className="result-card"
                key={`${result.document_id}-${result.chunk_index}-${index}`}
              >
                <div className="result-top">
                  <div>
                    <h3>
                      {result.document_name}
                    </h3>

                    <p className="result-source">
                      Source:{" "}
                      {result.source}
                    </p>
                  </div>

                  <div className="score">
                    <span>
                      Similarity
                    </span>

                    <strong>
                      {(
                        result.score *
                        100
                      ).toFixed(1)}
                      %
                    </strong>
                  </div>
                </div>

                <div className="result-meta">
                  <span>
                    Result #{index + 1}
                  </span>

                  <span>
                    Page:{" "}
                    {result.page_number ??
                      "N/A"}
                  </span>

                  <span>
                    Chunk:{" "}
                    {result.chunk_index}
                  </span>
                </div>

                <div className="result-text">
                  {result.text}
                </div>
              </article>
            )
          )}
        </div>
      </section>
    </main>
  );
}