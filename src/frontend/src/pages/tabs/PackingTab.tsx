import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useOutletContext, useParams } from "react-router";
import {
  Check,
  CircleAlert,
  LoaderCircle,
  Plus,
  Sparkles,
  Trash2,
  User,
} from "lucide-react";

import {
  packingApi,
  type PackingItem,
  collaborationApi,
  type WorkspaceMember,
  type Workspace,
} from "@/lib/api";

export function PackingTab() {
  const { workspace } = useOutletContext<{ workspace: Workspace }>();
  const { workspaceId = "" } = useParams();

  const [items, setItems] = useState<PackingItem[]>([]);
  const [members, setMembers] = useState<WorkspaceMember[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState("");

  const [newItemName, setNewItemName] = useState("");
  const [isAdding, setIsAdding] = useState(false);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError("");
    try {
      const [fetchedItems, fetchedMembers] = await Promise.all([
        packingApi.listItems(workspaceId),
        collaborationApi.listMembers(workspaceId),
      ]);
      setItems(fetchedItems);
      setMembers(fetchedMembers);
    } catch (e) {
      setError("Could not load packing list.");
    } finally {
      setIsLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  async function generateAI() {
    setIsGenerating(true);
    setError("");
    try {
      await packingApi.generateSuggestions(workspaceId);
      await loadData();
    } catch (e) {
      setError("Could not generate packing list.");
    } finally {
      setIsGenerating(false);
    }
  }

  async function toggleItem(item: PackingItem) {
    try {
      const updated = await packingApi.updateItem(item.id, {
        is_checked: !item.is_checked,
      });
      setItems(items.map((i) => (i.id === updated.id ? updated : i)));
    } catch (e) {
      // Ignore
    }
  }

  async function deleteItem(itemId: string) {
    try {
      await packingApi.deleteItem(itemId);
      setItems(items.filter((i) => i.id !== itemId));
    } catch (e) {
      // Ignore
    }
  }

  async function assignItem(itemId: string, userId: string | null) {
    try {
      const updated = await packingApi.assignItem(itemId, {
        assigned_to: userId,
      });
      setItems(items.map((i) => (i.id === updated.id ? updated : i)));
    } catch (e) {
      // Ignore
    }
  }

  async function addItem(e: FormEvent) {
    e.preventDefault();
    if (!newItemName.trim()) return;
    setIsAdding(true);
    try {
      const added = await packingApi.addItem(workspaceId, {
        name: newItemName.trim(),
      });
      setItems([...items, added]);
      setNewItemName("");
    } catch (e) {
      setError("Could not add item.");
    } finally {
      setIsAdding(false);
    }
  }

  if (isLoading)
    return (
      <section className="workspace-loading">
        <LoaderCircle className="spin" aria-hidden="true" />
        <p>Loading packing list…</p>
      </section>
    );

  return (
    <div className="workspace-view">
      <header className="workspace-view-header">
        <div>
          <h2>Group Packing List</h2>
          <p>Shared items and personal responsibilities</p>
        </div>
        <button
          data-testid="generate-packing-checklist-button"
          className="button button-primary"
          type="button"
          onClick={() => void generateAI()}
          disabled={isGenerating}
        >
          {isGenerating ? (
            <>
              <LoaderCircle className="spin" aria-hidden="true" /> Generating…
            </>
          ) : (
            <>
              <Sparkles aria-hidden="true" /> Generate AI Checklist
            </>
          )}
        </button>
      </header>

      {error && (
        <div className="inline-error" role="alert">
          <CircleAlert aria-hidden="true" />
          <span>{error}</span>
        </div>
      )}

      <div className="packing-list-container" style={{ marginTop: "2rem" }}>
        <form
          onSubmit={addItem}
          style={{ display: "flex", gap: "1rem", marginBottom: "2rem" }}
        >
          <input
            data-testid="custom-luggage-name-input"
            value={newItemName}
            onChange={(e) => setNewItemName(e.target.value)}
            placeholder="Add a custom item..."
            style={{
              flex: 1,
              padding: "0.75rem",
              borderRadius: "0.5rem",
              border: "1px solid var(--color-border)",
            }}
            disabled={isAdding}
          />
          <button
            data-testid="custom-luggage-save-button"
            className="button button-secondary"
            type="submit"
            disabled={isAdding || !newItemName.trim()}
          >
            {isAdding ? (
              <LoaderCircle className="spin" aria-hidden="true" />
            ) : (
              <Plus aria-hidden="true" />
            )}{" "}
            Add
          </button>
        </form>

        {items.length === 0 ? (
          <div
            className="packing-list-empty"
            style={{
              textAlign: "center",
              padding: "3rem",
              background: "var(--color-surface-dim)",
              borderRadius: "0.5rem",
            }}
          >
            <p style={{ color: "var(--color-text-dim)", marginBottom: "1rem" }}>
              No items in the packing list yet.
            </p>
            <button
              className="recovery-link"
              type="button"
              onClick={() => void generateAI()}
            >
              Generate AI Checklist
            </button>
          </div>
        ) : (
          <ul
            style={{
              listStyle: "none",
              padding: 0,
              display: "flex",
              flexDirection: "column",
              gap: "0.5rem",
            }}
          >
            {items.map((item) => (
              <li
                data-testid="packing-item-row"
                key={item.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "1rem",
                  padding: "0.75rem 1rem",
                  background: "var(--color-surface-dim)",
                  borderRadius: "0.5rem",
                }}
              >
                <button
                  data-testid="luggage-item-checkbox"
                  type="button"
                  onClick={() => void toggleItem(item)}
                  style={{
                    width: "24px",
                    height: "24px",
                    borderRadius: "50%",
                    border: `2px solid ${item.is_checked ? "var(--color-brand)" : "var(--color-border)"}`,
                    background: item.is_checked
                      ? "var(--color-brand)"
                      : "transparent",
                    color: "white",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    cursor: "pointer",
                  }}
                >
                  {item.is_checked && <Check size={14} />}
                </button>
                <span
                  style={{
                    flex: 1,
                    textDecoration: item.is_checked ? "line-through" : "none",
                    color: item.is_checked
                      ? "var(--color-text-dim)"
                      : "inherit",
                  }}
                >
                  {item.name}{" "}
                  {item.category && (
                    <span
                      style={{
                        fontSize: "0.8rem",
                        color: "var(--color-text-dim)",
                        marginLeft: "0.5rem",
                      }}
                    >
                      ({item.category})
                    </span>
                  )}
                </span>

                <select
                  data-testid="luggage-item-assignee-select"
                  value={item.assigned_to || ""}
                  onChange={(e) =>
                    void assignItem(item.id, e.target.value || null)
                  }
                  style={{
                    padding: "0.25rem",
                    borderRadius: "4px",
                    border: "1px solid var(--color-border)",
                    fontSize: "0.85rem",
                  }}
                >
                  <option value="">Unassigned</option>
                  {members.map((m) => (
                    <option key={m.user_id} value={m.user_id}>
                      {m.user?.full_name || m.user?.email}
                    </option>
                  ))}
                </select>

                <button
                  type="button"
                  onClick={() => void deleteItem(item.id)}
                  style={{
                    background: "transparent",
                    border: "none",
                    color: "var(--color-text-dim)",
                    cursor: "pointer",
                  }}
                >
                  <Trash2 size={18} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
