import { useState } from "react";
import { useOutletContext, useParams } from "react-router";
import {
  CircleAlert,
  Download,
  Link2,
  LoaderCircle,
  Share2,
} from "lucide-react";

import { shareApi, type Workspace } from "@/lib/api";
import { API_BASE_URL } from "@/lib/api";

export function ShareTab() {
  const { workspace } = useOutletContext<{ workspace: Workspace }>();
  const { workspaceId = "" } = useParams();

  const [shareLink, setShareLink] = useState("");
  const [isGeneratingLink, setIsGeneratingLink] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState("");

  async function generateLink() {
    setIsGeneratingLink(true);
    setError("");
    setShareLink("");
    try {
      const res = await shareApi.createShareLink(workspaceId, {
        access_level: "viewer",
      });
      const fullLink = `${window.location.origin}/share/${res.token}`;
      setShareLink(fullLink);
    } catch (e) {
      setError("Could not generate share link.");
    } finally {
      setIsGeneratingLink(false);
    }
  }

  async function exportTrip() {
    setIsExporting(true);
    setError("");
    try {
      const res = await shareApi.exportTrip(workspaceId, "json");

      // Usually, we would trigger a download if it's a URL, or the API returns JSON data directly
      // For this implementation, let's just open the download_url if it exists, or show an alert.
      if (res.download_url) {
        window.open(
          res.download_url.startsWith("http")
            ? res.download_url
            : `${API_BASE_URL}${res.download_url}`,
          "_blank",
        );
      } else {
        alert("Export successful, but no download URL provided.");
      }
    } catch (e) {
      setError("Could not export trip.");
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <div className="workspace-view">
      <header className="workspace-view-header">
        <div>
          <h2>Share & Export</h2>
          <p>Share your itinerary with others or save it for offline use</p>
        </div>
      </header>

      {error && (
        <div
          data-testid="export-error-alert"
          className="inline-error"
          role="alert"
        >
          <CircleAlert aria-hidden="true" />
          <span>{error}</span>
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "2rem",
          marginTop: "2rem",
        }}
      >
        <section
          style={{
            padding: "2rem",
            background: "var(--color-surface-dim)",
            borderRadius: "0.5rem",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.75rem",
              marginBottom: "1rem",
            }}
          >
            <div
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "50%",
                background: "var(--color-brand)",
                color: "white",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Link2 size={20} />
            </div>
            <h3 style={{ margin: 0 }}>Public Share Link</h3>
          </div>
          <p
            style={{
              color: "var(--color-text-dim)",
              marginBottom: "1.5rem",
              fontSize: "0.9rem",
            }}
          >
            Generate a read-only link that anyone can use to view this itinerary
            without an account.
          </p>

          {shareLink ? (
            <div
              data-testid="share-link-display"
              style={{ display: "flex", gap: "0.5rem" }}
            >
              <input
                type="text"
                readOnly
                value={shareLink}
                style={{
                  flex: 1,
                  padding: "0.5rem",
                  borderRadius: "4px",
                  border: "1px solid var(--color-border)",
                  background: "var(--color-background)",
                  color: "var(--color-text)",
                }}
              />
              <button
                className="button button-secondary"
                type="button"
                onClick={() => navigator.clipboard.writeText(shareLink)}
              >
                Copy
              </button>
            </div>
          ) : (
            <button
              data-testid="generate-share-link-button"
              className="button button-primary"
              type="button"
              onClick={() => void generateLink()}
              disabled={isGeneratingLink}
            >
              {isGeneratingLink ? (
                <LoaderCircle className="spin" aria-hidden="true" />
              ) : (
                <Share2 aria-hidden="true" />
              )}{" "}
              Generate Link
            </button>
          )}
        </section>

        <section
          style={{
            padding: "2rem",
            background: "var(--color-surface-dim)",
            borderRadius: "0.5rem",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.75rem",
              marginBottom: "1rem",
            }}
          >
            <div
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "50%",
                background: "var(--color-brand)",
                color: "white",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Download size={20} />
            </div>
            <h3 style={{ margin: 0 }}>Export Data</h3>
          </div>
          <p
            style={{
              color: "var(--color-text-dim)",
              marginBottom: "1.5rem",
              fontSize: "0.9rem",
            }}
          >
            Download a copy of your trip data for offline access or backup
            purposes.
          </p>
          <button
            data-testid="export-pdf-button"
            className="button button-secondary"
            type="button"
            onClick={() => void exportTrip()}
            disabled={isExporting}
          >
            {isExporting ? (
              <LoaderCircle className="spin" aria-hidden="true" />
            ) : (
              <Download aria-hidden="true" />
            )}{" "}
            Export as JSON
          </button>
        </section>
      </div>
    </div>
  );
}
