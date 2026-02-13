"use client";

import React, { useMemo, useState } from "react";

type EbayImage = {
  imageUrl: string;
};

type EbayPrice = {
  value: string;
  currency: string;
};

type EbayRow = {
  title?: string;
  image?: EbayImage;
  thumbnailImages?: EbayImage[];
  price?: EbayPrice;
  itemWebUrl?: string;
  [key: string]: any;
};

type StartSearchResponse = {
  search_id: string;
  rows: EbayRow[];
  n_rows: number;
};

export default function SearchPage() {
  const [query, setQuery] = useState("Charizard 151 SIR");
  const [limit, setLimit] = useState<number>(1000);
  const [data, setData] = useState<StartSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const API_BASE =
    process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

  async function runSearch(e: React.FormEvent) {
    e.preventDefault();

    // enforce multiples of 100
    if (limit % 100 !== 0) {
      setErr("Number of results must be a multiple of 100.");
      return;
    }

    setErr(null);
    setLoading(true);
    setData(null);

    try {
      const res = await fetch(`${API_BASE}/search/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, limit }),
      });

      if (!res.ok) {
        throw new Error(await res.text());
      }

      const json = (await res.json()) as StartSearchResponse;
      setData(json);
    } catch (e: any) {
      setErr(e?.message ?? "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: "0 auto" }}>
      <h1 style={{ fontSize: 24, fontWeight: 700 }}>eBay Search</h1>

      <p style={{ fontSize: 14, color: "#555", marginTop: 4 }}>
        Please request results in multiples of <strong>100</strong>.  
        This is required to gather enough data for good recommendations.
      </p>

      <form
        onSubmit={runSearch}
        style={{ display: "flex", gap: 10, margin: "16px 0" }}
      >
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search query"
          style={{ flex: 1, padding: 10 }}
        />
        <input
          type="number"
          value={limit}
          min={100}
          step={100}
          max={1000}
          onChange={(e) => setLimit(Number(e.target.value))}
          style={{ width: 120, padding: 10 }}
        />
        <button disabled={loading}>
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {err && <div style={{ color: "red" }}>{err}</div>}

      {data && (
        <div style={{ marginBottom: 12 }}>
          <strong>{data.n_rows}</strong> results
        </div>
      )}

      {data && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
            gap: 16,
          }}
        >
          {data.rows.map((row, idx) => (
            <div
              key={idx}
              style={{
                border: "1px solid #ddd",
                borderRadius: 10,
                padding: 12,
                display: "flex",
                flexDirection: "column",
                gap: 8,
              }}
            >
              {row.image?.imageUrl && (
                <img
                  src={row.image.imageUrl}
                  alt={row.title}
                  style={{
                    width: "100%",
                    height: 200,
                    objectFit: "contain",
                    borderRadius: 6,
                  }}
                />
              )}

              {row.thumbnailImages && row.thumbnailImages.length > 0 && (
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {row.thumbnailImages.map((img, i) => (
                    <img
                      key={i}
                      src={img.imageUrl}
                      alt="thumbnail"
                      style={{
                        width: 48,
                        height: 48,
                        objectFit: "cover",
                        borderRadius: 4,
                        border: "1px solid #ccc",
                      }}
                    />
                  ))}
                </div>
              )}

              <div style={{ fontWeight: 600 }}>{row.title}</div>

              {row.price && (
                <div style={{ fontWeight: 500 }}>
                  {row.price.value} {row.price.currency}
                </div>
              )}

              {row.itemWebUrl && (
                <a
                  href={row.itemWebUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: "#0066cc", marginTop: "auto" }}
                >
                  View on eBay →
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}