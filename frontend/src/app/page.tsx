"use client";

import { useEffect, useState } from "react";

/**
 * Home page — temporarily used to verify backend connectivity.
 */
export default function Home() {
  const [status, setStatus] = useState<string>("checking...");

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    fetch(`${apiUrl}/health`)
      .then((res) => res.json())
      .then((data) => setStatus(`Backend says: ${data.status} — ${data.message}`))
      .catch((err) => setStatus(`Connection failed: ${err.message}`));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="text-2xl font-bold mb-4">Local RAG System — Frontend</h1>
      <p className="text-lg">{status}</p>
    </main>
  );
}