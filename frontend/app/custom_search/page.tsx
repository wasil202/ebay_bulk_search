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
  columns?: string[];
};

type MakeSampleResponse = {
  sample_search_id: string;
  sample_indices: number[];
};

type GenerateRecommendationsResponse = {
  n_rows: number;
  rows: EbayRow[];
};

export default function SearchPage() {
  const [query, setQuery] = useState("Charizard 151 SIR");
  const [limit, setLimit] = useState<number>(400);

  const [searchId, setSearchId] = useState<string | null>(null);
  const [allRows, setAllRows] = useState<EbayRow[]>([]);
  const [nAllRows, setNAllRows] = useState<number>(0);

  const [sampleSearchId, setSampleSearchId] = useState<string | null>(null);
  const [sampleIndices, setSampleIndices] = useState<number[]>([]);
  const [selectedToDelete, setSelectedToDelete] = useState<number[]>([]);

  const [finalRows, setFinalRows] = useState<EbayRow[]>([]);
  const [nFinalRows, setNFinalRows] = useState<number>(0);

  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const [step, setStep] = useState<"search" | "sample" | "final">("search");

  const API_BASE =
    process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

  const sampleRows = useMemo(() => {
    return sampleIndices
      .map((idx) => ({ idx, row: allRows[idx] }))
      .filter((x) => x.row);
  }, [sampleIndices, allRows]);

  function toggleDeleteIndex(idx: number) {
    setSelectedToDelete((prev) =>
      prev.includes(idx) ? prev.filter((x) => x !== idx) : [...prev, idx]
    );
  }

  async function runSearch(e: React.FormEvent) {
    e.preventDefault();

    if (limit % 100 !== 0) {
      setErr("Number of results must be a multiple of 100.");
      return;
    }

    setErr(null);
    setLoading(true);

    // reset state for a fresh run
    setSearchId(null);
    setAllRows([]);
    setNAllRows(0);
    setSampleSearchId(null);
    setSampleIndices([]);
    setSelectedToDelete([]);
    setFinalRows([]);
    setNFinalRows(0);

    try {
      const res = await fetch(`${API_BASE}/search/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, limit }),
      });

      if (!res.ok) throw new Error(await res.text());

      const json = (await res.json()) as StartSearchResponse;

      setSearchId(json.search_id);
      setAllRows(json.rows ?? []);
      setNAllRows(json.n_rows ?? (json.rows?.length ?? 0));
      setStep("sample");
    } catch (e: any) {
      setErr(e?.message ?? "Something went wrong");
      setStep("search");
    } finally {
      setLoading(false);
    }
  }

  async function runMakeSample() {
    if (!searchId) return;

    setErr(null);
    setLoading(true);
    setSampleSearchId(null);
    setSampleIndices([]);
    setSelectedToDelete([]);
    setFinalRows([]);
    setNFinalRows(0);

    try {
      const res = await fetch(`${API_BASE}/make_sample_endpoint`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ search_id: searchId }),
      });

      if (!res.ok) throw new Error(await res.text());

      const json = (await res.json()) as MakeSampleResponse;

      setSampleSearchId(json.sample_search_id);
      setSampleIndices(json.sample_indices ?? []);
    } catch (e: any) {
      setErr(e?.message ?? "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  async function runGenerateRecommendations() {
    if (!searchId || !sampleSearchId) return;

    setErr(null);
    setLoading(true);
    setFinalRows([]);
    setNFinalRows(0);

    try {
      const res = await fetch(`${API_BASE}/generate_recomendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          search_id: searchId,
          sample_search_id: sampleSearchId,
          searches_sample_row_indices: sampleIndices,
          list_of_indicies_to_delete: selectedToDelete,
        }),
      });

      if (!res.ok) throw new Error(await res.text());

      const json = (await res.json()) as GenerateRecommendationsResponse;

      setFinalRows(json.rows ?? []);
      setNFinalRows(json.n_rows ?? (json.rows?.length ?? 0));
      setStep("final");
    } catch (e: any) {
      setErr(e?.message ?? "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  const theme = {
    bg: "#0b0d12",
    panel: "#0f1320",
    panel2: "#0c101a",
    border: "rgba(255,255,255,0.10)",
    border2: "rgba(255,255,255,0.14)",
    text: "rgba(255,255,255,0.92)",
    muted: "rgba(255,255,255,0.65)",
    subtle: "rgba(255,255,255,0.08)",
    dangerBg: "rgba(255, 80, 80, 0.14)",
    dangerBorder: "rgba(255, 80, 80, 0.25)",
    dangerText: "rgba(255, 170, 170, 0.95)",
    primaryBg: "rgba(100, 160, 255, 0.14)",
    primaryBorder: "rgba(100, 160, 255, 0.30)",
    primaryText: "rgba(190, 220, 255, 0.95)",
    link: "rgba(120, 190, 255, 0.95)",
    inputBg: "rgba(255,255,255,0.06)",
  };

  const buttonBase: React.CSSProperties = {
    padding: "10px 14px",
    borderRadius: 10,
    border: `1px solid ${theme.border2}`,
    background: theme.subtle,
    color: theme.text,
    fontWeight: 600,
    cursor: "pointer",
    transition: "transform 120ms ease, background 120ms ease",
  };

  const buttonPrimary: React.CSSProperties = {
    ...buttonBase,
    background: theme.primaryBg,
    border: `1px solid ${theme.primaryBorder}`,
    color: theme.primaryText,
  };

  const buttonDanger: React.CSSProperties = {
    ...buttonBase,
    background: theme.dangerBg,
    border: `1px solid ${theme.dangerBorder}`,
    color: theme.dangerText,
  };

  const inputStyle: React.CSSProperties = {
    flex: 1,
    padding: 10,
    borderRadius: 10,
    border: `1px solid ${theme.border2}`,
    background: theme.inputBg,
    color: theme.text,
    outline: "none",
  };

  const numberStyle: React.CSSProperties = {
    width: 140,
    padding: 10,
    borderRadius: 10,
    border: `1px solid ${theme.border2}`,
    background: theme.inputBg,
    color: theme.text,
    outline: "none",
  };

  function ItemCard({
    row,
    selected,
    onClick,
    showSelectState,
  }: {
    row: EbayRow;
    selected?: boolean;
    onClick?: () => void;
    showSelectState?: boolean;
  }) {
    return (
      <div
        onClick={onClick}
        style={{
          border: `1px solid ${selected ? theme.dangerBorder : theme.border}`,
          background: selected ? theme.dangerBg : theme.panel,
          borderRadius: 12,
          padding: 12,
          display: "flex",
          flexDirection: "column",
          gap: 8,
          cursor: onClick ? "pointer" : "default",
          boxShadow: "0 8px 28px rgba(0,0,0,0.35)",
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
              borderRadius: 10,
              background: theme.panel2,
              border: `1px solid ${theme.border}`,
            }}
          />
        )}

        {row.thumbnailImages && row.thumbnailImages.length > 0 && (
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {row.thumbnailImages.slice(0, 6).map((img, i) => (
              <img
                key={i}
                src={img.imageUrl}
                alt="thumbnail"
                style={{
                  width: 48,
                  height: 48,
                  objectFit: "cover",
                  borderRadius: 8,
                  border: `1px solid ${theme.border}`,
                  background: theme.panel2,
                }}
              />
            ))}
          </div>
        )}

        <div style={{ fontWeight: 700, lineHeight: 1.25, color: theme.text }}>
          {row.title ?? "(no title)"}
        </div>

        {row.price && (
          <div style={{ fontWeight: 600, color: theme.text }}>
            {row.price.value} {row.price.currency}
          </div>
        )}

        {showSelectState && (
          <div style={{ fontSize: 12, color: selected ? theme.dangerText : theme.muted }}>
            {selected ? "Marked for removal" : "Click to mark for removal"}
          </div>
        )}

        {row.itemWebUrl && (
          <a
            href={row.itemWebUrl}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: theme.link, marginTop: "auto", fontWeight: 600 }}
            onClick={(e) => e.stopPropagation()}
          >
            View on eBay →
          </a>
        )}
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: `radial-gradient(1200px 800px at 20% -10%, rgba(100,160,255,0.20), transparent 60%),
                     radial-gradient(900px 600px at 100% 0%, rgba(255,120,180,0.12), transparent 55%),
                     ${theme.bg}`,
        color: theme.text,
      }}
    >
      <div style={{ padding: 24, maxWidth: 1200, margin: "0 auto" }}>
        <div
          style={{
            border: `1px solid ${theme.border}`,
            borderRadius: 16,
            padding: 18,
            background: "rgba(15,19,32,0.78)",
            backdropFilter: "blur(10px)",
            boxShadow: "0 10px 34px rgba(0,0,0,0.45)",
          }}
        >
          <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 12 }}>
            <h1 style={{ fontSize: 24, fontWeight: 800, margin: 0 }}>eBay Search</h1>
            <div style={{ fontSize: 12, color: theme.muted }}>
              {step === "search" && "Step 1/3"}
              {step === "sample" && "Step 2/3"}
              {step === "final" && "Step 3/3"}
            </div>
          </div>

          <p style={{ fontSize: 14, color: theme.muted, marginTop: 6, marginBottom: 0 }}>
            Please request results in multiples of <strong>100</strong>. This is required to gather enough data for good recommendations.
          </p>

          <form
            onSubmit={runSearch}
            style={{
              display: "flex",
              gap: 10,
              margin: "16px 0 0",
              flexWrap: "wrap",
            }}
          >
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search query"
              style={inputStyle}
            />
            <input
              type="number"
              value={limit}
              min={100}
              step={100}
              max={2000}
              onChange={(e) => setLimit(Number(e.target.value))}
              style={numberStyle}
            />
            <button style={buttonPrimary} disabled={loading} type="submit">
              {loading ? "Searching…" : "Search"}
            </button>

            {step !== "search" && (
              <button
                type="button"
                style={buttonBase}
                disabled={loading}
                onClick={() => {
                  setStep("search");
                  setSearchId(null);
                  setAllRows([]);
                  setNAllRows(0);
                  setSampleSearchId(null);
                  setSampleIndices([]);
                  setSelectedToDelete([]);
                  setFinalRows([]);
                  setNFinalRows(0);
                  setErr(null);
                }}
              >
                Reset
              </button>
            )}
          </form>

          {err && (
            <div
              style={{
                marginTop: 12,
                padding: 10,
                borderRadius: 12,
                border: `1px solid ${theme.dangerBorder}`,
                background: theme.dangerBg,
                color: theme.dangerText,
                fontWeight: 600,
              }}
            >
              {err}
            </div>
          )}

          {step === "sample" && searchId && (
            <div style={{ marginTop: 14, display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
              <div style={{ color: theme.muted, fontSize: 13 }}>
                <strong style={{ color: theme.text }}>{nAllRows}</strong> raw results loaded
              </div>
              <button style={buttonPrimary} disabled={loading} type="button" onClick={runMakeSample}>
                {loading ? "Creating sample…" : "Create sample"}
              </button>
              {sampleIndices.length > 0 && (
                <div style={{ color: theme.muted, fontSize: 13 }}>
                  Sample size: <strong style={{ color: theme.text }}>{sampleIndices.length}</strong>
                </div>
              )}
            </div>
          )}

          {step === "final" && (
            <div style={{ marginTop: 14, color: theme.muted, fontSize: 13 }}>
              Recommended results: <strong style={{ color: theme.text }}>{nFinalRows}</strong>
            </div>
          )}
        </div>

        {step === "search" && (
          <div style={{ marginTop: 16, color: theme.muted, fontSize: 13 }}>
            Run a search to begin.
          </div>
        )}

        {step === "sample" && sampleIndices.length > 0 && (
          <>
            <div
              style={{
                marginTop: 18,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 12,
                flexWrap: "wrap",
              }}
            >
              <div>
                <h2 style={{ fontSize: 18, margin: 0, fontWeight: 800 }}>
                  Select items to remove
                </h2>
                <div style={{ fontSize: 13, color: theme.muted, marginTop: 4 }}>
                  Click cards to toggle removal. You can select nothing if you want to keep everything.
                </div>
              </div>

              <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
                <div style={{ fontSize: 13, color: theme.muted }}>
                  Marked for removal:{" "}
                  <strong style={{ color: theme.text }}>{selectedToDelete.length}</strong>
                </div>
                <button
                  type="button"
                  style={selectedToDelete.length ? buttonDanger : buttonBase}
                  disabled={loading}
                  onClick={() => setSelectedToDelete([])}
                >
                  Clear selection
                </button>
                <button
                  type="button"
                  style={buttonPrimary}
                  disabled={loading || !searchId || !sampleSearchId}
                  onClick={runGenerateRecommendations}
                >
                  {loading ? "Generating…" : "Confirm & Generate"}
                </button>
              </div>
            </div>

            <div
              style={{
                marginTop: 14,
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
                gap: 16,
              }}
            >
              {sampleRows.map(({ idx, row }) => (
                <div key={idx} style={{ position: "relative" }}>
                  <div
                    style={{
                      position: "absolute",
                      top: 10,
                      left: 10,
                      zIndex: 2,
                      fontSize: 12,
                      padding: "4px 8px",
                      borderRadius: 999,
                      background: "rgba(0,0,0,0.55)",
                      border: `1px solid ${theme.border}`,
                      color: "rgba(255,255,255,0.85)",
                      backdropFilter: "blur(6px)",
                    }}
                  >
                    Index {idx}
                  </div>

                  <ItemCard
                    row={row}
                    selected={selectedToDelete.includes(idx)}
                    onClick={() => toggleDeleteIndex(idx)}
                    showSelectState
                  />
                </div>
              ))}
            </div>
          </>
        )}

        {step === "final" && (
          <>
            <div style={{ marginTop: 18 }}>
              <h2 style={{ fontSize: 18, margin: 0, fontWeight: 800 }}>
                Recommended searches
              </h2>
              <div style={{ fontSize: 13, color: theme.muted, marginTop: 4 }}>
                These are the filtered results returned by <code style={{ color: theme.primaryText }}>POST /generate_recomendations</code>.
              </div>
            </div>

            <div
              style={{
                marginTop: 14,
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
                gap: 16,
              }}
            >
              {finalRows.map((row, idx) => (
                <ItemCard key={idx} row={row} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}