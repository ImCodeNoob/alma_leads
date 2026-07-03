"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { API_BASE_URL, ApiError, apiRequest } from "@/lib/api";
import { authHeaders, clearToken } from "@/lib/auth";
import { Lead } from "@/lib/types";
import { useRequireAuth } from "@/lib/useRequireAuth";

export default function LeadsPage() {
  const ready = useRequireAuth();
  const router = useRouter();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  useEffect(() => {
    if (!ready) return;

    let cancelled = false;

    (async () => {
      try {
        const data = await apiRequest<Lead[]>("/api/leads", { headers: authHeaders() });
        if (!cancelled) setLeads(data);
      } catch (error) {
        if (cancelled) return;
        if (error instanceof ApiError && error.status === 401) {
          clearToken();
          router.replace("/login");
          return;
        }
        setErrorMessage("Failed to load leads.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [ready, router]);

  async function markReachedOut(leadId: string) {
    setUpdatingId(leadId);
    try {
      const updated = await apiRequest<Lead>(`/api/leads/${leadId}/status`, {
        method: "PATCH",
        headers: { ...authHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify({ status: "REACHED_OUT" }),
      });
      setLeads((prev) => prev.map((lead) => (lead.id === leadId ? updated : lead)));
    } catch {
      setErrorMessage("Failed to update lead status.");
    } finally {
      setUpdatingId(null);
    }
  }

  async function downloadResume(lead: Lead) {
    const response = await fetch(`${API_BASE_URL}/api/leads/${lead.id}/resume`, {
      headers: authHeaders(),
    });
    if (!response.ok) {
      setErrorMessage("Failed to download resume.");
      return;
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = lead.resume_filename;
    link.click();
    URL.revokeObjectURL(url);
  }

  function handleLogout() {
    clearToken();
    router.replace("/login");
  }

  if (!ready) return null;

  return (
    <div className="flex-1 bg-zinc-50 px-6 py-10 dark:bg-black">
      <div className="mx-auto max-w-5xl">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Leads</h1>
          <button
            onClick={handleLogout}
            className="rounded-full border border-zinc-300 px-4 py-1.5 text-sm text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
          >
            Log out
          </button>
        </div>

        {errorMessage && (
          <p className="mt-4 text-sm text-red-600 dark:text-red-400">{errorMessage}</p>
        )}

        <div className="mt-6 overflow-x-auto rounded-xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-zinc-200 text-zinc-500 dark:border-zinc-800 dark:text-zinc-400">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Email</th>
                <th className="px-4 py-3 font-medium">Resume</th>
                <th className="px-4 py-3 font-medium">Submitted</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td className="px-4 py-6 text-zinc-500" colSpan={6}>
                    Loading...
                  </td>
                </tr>
              )}
              {!loading && leads.length === 0 && (
                <tr>
                  <td className="px-4 py-6 text-zinc-500" colSpan={6}>
                    No leads yet.
                  </td>
                </tr>
              )}
              {leads.map((lead) => (
                <tr
                  key={lead.id}
                  className="border-b border-zinc-100 last:border-0 dark:border-zinc-800"
                >
                  <td className="px-4 py-3 text-zinc-900 dark:text-zinc-100">
                    {lead.first_name} {lead.last_name}
                  </td>
                  <td className="px-4 py-3 text-zinc-700 dark:text-zinc-300">{lead.email}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => downloadResume(lead)}
                      className="text-zinc-900 underline hover:text-zinc-600 dark:text-zinc-100 dark:hover:text-zinc-300"
                    >
                      {lead.resume_filename}
                    </button>
                  </td>
                  <td className="px-4 py-3 text-zinc-500">
                    {new Date(lead.created_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                        lead.status === "PENDING"
                          ? "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300"
                          : "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300"
                      }`}
                    >
                      {lead.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {lead.status === "PENDING" && (
                      <button
                        onClick={() => markReachedOut(lead.id)}
                        disabled={updatingId === lead.id}
                        className="rounded-full bg-zinc-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-zinc-700 disabled:opacity-50 dark:bg-white dark:text-black dark:hover:bg-zinc-200"
                      >
                        {updatingId === lead.id ? "Updating..." : "Mark reached out"}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
