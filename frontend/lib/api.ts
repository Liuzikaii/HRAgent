/**
 * API client for HRAgent backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";

// ─── Chat API ───

export interface ChatMessage {
    id: string;
    role: "user" | "assistant";
    content: string;
    created_at: string;
}

export interface ChatSession {
    id: string;
    title: string;
    created_at: string;
    updated_at: string;
}

export interface ChatResponse {
    session_id: string;
    message: ChatMessage;
}

export async function sendMessage(
    message: string,
    sessionId?: string
): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, session_id: sessionId }),
    });
    if (!res.ok) throw new Error(`Chat failed: ${res.statusText}`);
    return res.json();
}

export async function streamMessage(
    message: string,
    sessionId: string | undefined,
    onChunk: (chunk: string) => void,
    onDone: (sessionId: string) => void,
    onError?: (error: string) => void
): Promise<void> {
    const res = await fetch(`${API_BASE}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, session_id: sessionId }),
    });

    if (!res.ok) {
        onError?.(`Request failed: ${res.statusText}`);
        return;
    }

    const reader = res.body?.getReader();
    if (!reader) return;

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
            if (line.startsWith("data: ")) {
                const data = line.slice(6);
                if (data.startsWith("[DONE]")) {
                    const sid = data.replace("[DONE]", "");
                    onDone(sid);
                } else if (data.startsWith("[ERROR]")) {
                    onError?.(data.replace("[ERROR] ", ""));
                } else {
                    onChunk(data);
                }
            }
        }
    }
}

export async function fetchSessions(): Promise<ChatSession[]> {
    const res = await fetch(`${API_BASE}/chat/sessions`);
    if (!res.ok) throw new Error("Failed to fetch sessions");
    const data = await res.json();
    return data.sessions;
}

export async function fetchMessages(sessionId: string): Promise<ChatMessage[]> {
    const res = await fetch(`${API_BASE}/chat/sessions/${sessionId}/messages`);
    if (!res.ok) throw new Error("Failed to fetch messages");
    const data = await res.json();
    return data.messages;
}

export async function deleteSession(sessionId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/chat/sessions/${sessionId}`, {
        method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete session");
}

// ─── Document API ───

export interface Document {
    id: string;
    filename: string;
    file_size: number;
    chunk_count: number;
    status: string;
    created_at: string;
}

export async function fetchDocuments(): Promise<Document[]> {
    const res = await fetch(`${API_BASE}/documents`);
    if (!res.ok) throw new Error("Failed to fetch documents");
    const data = await res.json();
    return data.documents;
}

export async function uploadDocument(
    file: File
): Promise<{ id: string; filename: string; chunk_count: number; message: string }> {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/documents/upload`, {
        method: "POST",
        body: formData,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "Upload failed");
    }
    return res.json();
}

export async function deleteDocument(documentId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/documents/${documentId}`, {
        method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete document");
}
