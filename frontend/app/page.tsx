"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  MessageSquarePlus,
  Send,
  Trash2,
  FileText,
  Bot,
  User,
  Loader2,
  FileUp,
  SparklesIcon,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  type ChatMessage,
  type ChatSession,
  type Document,
  streamMessage,
  fetchSessions,
  fetchMessages,
  deleteSession,
  fetchDocuments,
  uploadDocument,
  deleteDocument,
} from "@/lib/api";

export default function ChatPage() {
  // ─── State ───
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | undefined>();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [docDialogOpen, setDocDialogOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ─── Effects ───
  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // ─── Session Management ───
  const loadSessions = async () => {
    try {
      const data = await fetchSessions();
      setSessions(data);
    } catch {
      console.error("Failed to load sessions");
    }
  };

  const loadMessages = useCallback(async (sessionId: string) => {
    try {
      const data = await fetchMessages(sessionId);
      setMessages(data);
      setCurrentSessionId(sessionId);
    } catch {
      console.error("Failed to load messages");
    }
  }, []);

  const handleNewChat = () => {
    setCurrentSessionId(undefined);
    setMessages([]);
    setStreamingContent("");
    setInput("");
  };

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await deleteSession(sessionId);
      if (currentSessionId === sessionId) {
        handleNewChat();
      }
      loadSessions();
    } catch {
      console.error("Failed to delete session");
    }
  };

  // ─── Chat ───
  const handleSend = async () => {
    const msg = input.trim();
    if (!msg || isLoading) return;

    setInput("");
    setIsLoading(true);
    setStreamingContent("");

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: msg,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      let content = "";
      await streamMessage(
        msg,
        currentSessionId,
        (chunk) => {
          content += chunk;
          setStreamingContent(content);
        },
        (sessionId) => {
          setCurrentSessionId(sessionId);
          const aiMsg: ChatMessage = {
            id: crypto.randomUUID(),
            role: "assistant",
            content: content,
            created_at: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, aiMsg]);
          setStreamingContent("");
          setIsLoading(false);
          loadSessions();
        },
        (error) => {
          console.error("Stream error:", error);
          const errMsg: ChatMessage = {
            id: crypto.randomUUID(),
            role: "assistant",
            content: "抱歉，系统暂时无法处理您的请求，请稍后再试。",
            created_at: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, errMsg]);
          setStreamingContent("");
          setIsLoading(false);
        }
      );
    } catch {
      setIsLoading(false);
      setStreamingContent("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // ─── Documents ───
  const loadDocuments = async () => {
    try {
      const data = await fetchDocuments();
      setDocuments(data);
    } catch {
      console.error("Failed to load documents");
    }
  };

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    try {
      for (const file of Array.from(files)) {
        await uploadDocument(file);
      }
      loadDocuments();
    } catch (err) {
      console.error("Upload failed:", err);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDoc = async (docId: string) => {
    try {
      await deleteDocument(docId);
      loadDocuments();
    } catch {
      console.error("Failed to delete document");
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleUpload(e.dataTransfer.files);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const quickQuestions = [
    "公司的年假制度是怎样的？",
    "试用期有多久？薪资怎么算？",
    "请假需要怎么申请？",
    "公司缴纳哪些保险和公积金？",
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* ─── Sidebar ─── */}
      <div
        className={`${sidebarOpen ? "w-72" : "w-0"
          } flex-shrink-0 transition-all duration-300 overflow-hidden border-r border-border`}
      >
        <div className="flex h-full w-72 flex-col bg-card/50">
          {/* Sidebar Header */}
          <div className="flex items-center justify-between p-4">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-violet-600">
                <Bot className="h-4 w-4 text-white" />
              </div>
              <span className="font-semibold text-sm">HRAgent</span>
            </div>
            <Tooltip>
              <TooltipTrigger
                render={
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={handleNewChat}
                  />
                }
              >
                <MessageSquarePlus className="h-4 w-4" />
              </TooltipTrigger>
              <TooltipContent>新建对话</TooltipContent>
            </Tooltip>
          </div>

          <Separator />

          {/* Sessions List */}
          <ScrollArea className="flex-1">
            <div className="p-2 space-y-1">
              {sessions.length === 0 ? (
                <p className="p-4 text-center text-sm text-muted-foreground">
                  暂无对话记录
                </p>
              ) : (
                sessions.map((session) => (
                  <div
                    key={session.id}
                    className={`group flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm cursor-pointer transition-colors ${currentSessionId === session.id
                        ? "bg-accent text-accent-foreground"
                        : "hover:bg-accent/50 text-muted-foreground hover:text-foreground"
                      }`}
                    onClick={() => loadMessages(session.id)}
                  >
                    <MessageSquarePlus className="h-4 w-4 flex-shrink-0 opacity-50" />
                    <span className="flex-1 truncate">{session.title}</span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                      onClick={(e) => handleDeleteSession(session.id, e)}
                    >
                      <Trash2 className="h-3 w-3 text-muted-foreground" />
                    </Button>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>

          <Separator />

          {/* Documents Button */}
          <div className="p-3">
            <Dialog
              open={docDialogOpen}
              onOpenChange={(open) => {
                setDocDialogOpen(open);
                if (open) loadDocuments();
              }}
            >
              <DialogTrigger
                render={
                  <Button
                    variant="outline"
                    className="w-full justify-start gap-2 text-sm"
                  />
                }
              >
                <FileText className="h-4 w-4" />
                知识库管理
              </DialogTrigger>
              <DialogContent className="sm:max-w-xl">
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    知识库文档管理
                  </DialogTitle>
                </DialogHeader>

                {/* Upload Area */}
                <div
                  className={`border-2 border-dashed rounded-xl p-6 text-center transition-colors ${dragOver
                      ? "border-blue-500 bg-blue-500/5"
                      : "border-border hover:border-muted-foreground/50"
                    }`}
                  onDragOver={(e) => {
                    e.preventDefault();
                    setDragOver(true);
                  }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={handleDrop}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.md,.txt"
                    multiple
                    className="hidden"
                    onChange={(e) => handleUpload(e.target.files)}
                  />
                  {uploading ? (
                    <div className="flex flex-col items-center gap-2">
                      <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                      <p className="text-sm text-muted-foreground">正在上传并处理...</p>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center gap-2">
                      <FileUp className="h-8 w-8 text-muted-foreground" />
                      <p className="text-sm text-muted-foreground">
                        拖拽文件到此处，或{" "}
                        <button
                          className="text-blue-500 hover:underline"
                          onClick={() => fileInputRef.current?.click()}
                        >
                          点击选择文件
                        </button>
                      </p>
                      <p className="text-xs text-muted-foreground/60">
                        支持 PDF、Markdown、TXT 格式
                      </p>
                    </div>
                  )}
                </div>

                {/* Document List */}
                <ScrollArea className="max-h-64">
                  <div className="space-y-2">
                    {documents.length === 0 ? (
                      <p className="py-4 text-center text-sm text-muted-foreground">
                        暂无文档，请上传 HR 相关文件
                      </p>
                    ) : (
                      documents.map((doc) => (
                        <div
                          key={doc.id}
                          className="flex items-center gap-3 rounded-lg border border-border p-3 text-sm"
                        >
                          <FileText className="h-5 w-5 flex-shrink-0 text-blue-500" />
                          <div className="flex-1 min-w-0">
                            <p className="font-medium truncate">{doc.filename}</p>
                            <div className="flex items-center gap-2 mt-0.5">
                              <span className="text-xs text-muted-foreground">
                                {formatFileSize(doc.file_size)}
                              </span>
                              <span className="text-xs text-muted-foreground">·</span>
                              <span className="text-xs text-muted-foreground">
                                {doc.chunk_count} 个片段
                              </span>
                              <Badge
                                variant={doc.status === "ready" ? "default" : "secondary"}
                                className="text-[10px] h-4"
                              >
                                {doc.status === "ready" ? "就绪" : doc.status}
                              </Badge>
                            </div>
                          </div>
                          <Tooltip>
                            <TooltipTrigger
                              render={
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-7 w-7 flex-shrink-0"
                                  onClick={() => handleDeleteDoc(doc.id)}
                                />
                              }
                            >
                              <Trash2 className="h-3.5 w-3.5 text-muted-foreground" />
                            </TooltipTrigger>
                            <TooltipContent>删除文档</TooltipContent>
                          </Tooltip>
                        </div>
                      ))
                    )}
                  </div>
                </ScrollArea>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </div>

      {/* ─── Main Chat Area ─── */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Header */}
        <header className="flex items-center gap-3 border-b border-border px-4 py-3">
          <Tooltip>
            <TooltipTrigger
              render={
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                />
              }
            >
              {sidebarOpen ? (
                <PanelLeftClose className="h-4 w-4" />
              ) : (
                <PanelLeft className="h-4 w-4" />
              )}
            </TooltipTrigger>
            <TooltipContent>{sidebarOpen ? "收起侧栏" : "展开侧栏"}</TooltipContent>
          </Tooltip>
          <div className="flex-1">
            <h1 className="text-sm font-semibold">HR 智能问答助手</h1>
            <p className="text-xs text-muted-foreground">
              基于企业知识库的专业 HR 政策解答
            </p>
          </div>
        </header>

        {/* Messages */}
        <ScrollArea className="flex-1">
          <div className="mx-auto max-w-3xl px-4 py-6 space-y-6">
            {messages.length === 0 && !streamingContent ? (
              /* Welcome Screen */
              <div className="flex flex-col items-center justify-center pt-16 pb-8 space-y-8">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-violet-600 shadow-lg shadow-blue-500/20">
                  <SparklesIcon className="h-8 w-8 text-white" />
                </div>
                <div className="text-center space-y-2">
                  <h2 className="text-2xl font-bold">HRAgent 智能问答</h2>
                  <p className="text-muted-foreground max-w-md">
                    我是您的 HR 智能助手，可以回答关于员工手册、公司政策、薪酬福利、请假制度等方面的问题
                  </p>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
                  {quickQuestions.map((q, i) => (
                    <button
                      key={i}
                      className="rounded-xl border border-border p-3.5 text-left text-sm hover:bg-accent/50 transition-colors group"
                      onClick={() => {
                        setInput(q);
                        setTimeout(() => textareaRef.current?.focus(), 0);
                      }}
                    >
                      <span className="text-muted-foreground group-hover:text-foreground transition-colors">
                        {q}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              /* Messages */
              <>
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"
                      }`}
                  >
                    {msg.role === "assistant" && (
                      <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-violet-600">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${msg.role === "user"
                          ? "bg-primary text-primary-foreground rounded-br-md"
                          : "bg-accent/60 text-foreground rounded-bl-md"
                        }`}
                    >
                      {msg.role === "assistant" ? (
                        <div className="prose prose-sm prose-invert max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {msg.content}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      )}
                    </div>
                    {msg.role === "user" && (
                      <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-muted">
                        <User className="h-4 w-4" />
                      </div>
                    )}
                  </div>
                ))}

                {/* Streaming message */}
                {streamingContent && (
                  <div className="flex gap-3 justify-start">
                    <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-violet-600">
                      <Bot className="h-4 w-4 text-white" />
                    </div>
                    <div className="max-w-[80%] rounded-2xl rounded-bl-md bg-accent/60 px-4 py-3 text-sm leading-relaxed">
                      <div className="prose prose-sm prose-invert max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {streamingContent}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </div>
                )}

                {/* Loading indicator */}
                {isLoading && !streamingContent && (
                  <div className="flex gap-3 justify-start">
                    <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-violet-600">
                      <Bot className="h-4 w-4 text-white" />
                    </div>
                    <div className="rounded-2xl rounded-bl-md bg-accent/60 px-4 py-3">
                      <div className="flex items-center gap-1.5">
                        <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-bounce [animation-delay:-0.3s]" />
                        <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-bounce [animation-delay:-0.15s]" />
                        <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-bounce" />
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="border-t border-border p-4">
          <div className="mx-auto max-w-3xl">
            <div className="flex items-end gap-2 rounded-2xl border border-border bg-card/80 p-2 focus-within:ring-1 focus-within:ring-ring">
              <Textarea
                ref={textareaRef}
                placeholder="输入您的 HR 相关问题..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                className="flex-1 resize-none border-0 bg-transparent p-2 text-sm shadow-none focus-visible:ring-0 min-h-[40px] max-h-[120px]"
              />
              <Tooltip>
                <TooltipTrigger
                  render={
                    <Button
                      size="icon"
                      className="h-9 w-9 rounded-xl bg-gradient-to-r from-blue-500 to-violet-600 hover:from-blue-600 hover:to-violet-700 transition-all flex-shrink-0"
                      disabled={!input.trim() || isLoading}
                      onClick={handleSend}
                    />
                  }
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </TooltipTrigger>
                <TooltipContent>发送消息 (Enter)</TooltipContent>
              </Tooltip>
            </div>
            <p className="mt-2 text-center text-[11px] text-muted-foreground/50">
              HRAgent 基于企业知识库生成回答，仅供参考，请以 HR 部门正式通知为准
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
