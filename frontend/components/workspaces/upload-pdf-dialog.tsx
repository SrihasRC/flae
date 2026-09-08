"use client";

import { useState, useRef } from "react";
import { Upload, FileUp, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { uploadDocument } from "@/lib/api";

interface UploadPdfDialogProps {
  workspaceId: string;
  onUploaded?: () => void;
}

export function UploadPdfDialog({ workspaceId, onUploaded }: UploadPdfDialogProps) {
  const [open, setOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (selected: File | null) => {
    if (!selected) return;
    if (selected.type !== "application/pdf" && !selected.name.endsWith(".pdf")) {
      setError("Only PDF files are supported");
      return;
    }
    if (selected.size > 50 * 1024 * 1024) {
      setError("File exceeds maximum allowed size of 50MB");
      return;
    }
    setError(null);
    setFile(selected);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);

    try {
      await uploadDocument(workspaceId, file);
      setOpen(false);
      setFile(null);
      if (onUploaded) {
        onUploaded();
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to upload document");
    } finally {
      setUploading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={
          <Button size="sm" className="w-full gap-1.5 text-xs font-medium">
            <Upload className="h-3.5 w-3.5" />
            <span>Upload PDF</span>
          </Button>
        }
      />
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Upload Document</DialogTitle>
          <DialogDescription>
            PDF files are ingested into the pipeline (parsed, facts extracted with context
            envelopes, and vector embedded).
          </DialogDescription>
        </DialogHeader>

        <div className="py-3 space-y-3">
          {error && (
            <div className="p-2.5 rounded-md bg-destructive/10 border border-destructive/20 text-destructive text-xs flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
              dragActive
                ? "border-primary bg-primary/5"
                : "border-border hover:border-muted-foreground/50 bg-muted/20"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,application/pdf"
              className="hidden"
              onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
            />
            <div className="flex flex-col items-center gap-2">
              <div className="h-10 w-10 rounded-full bg-secondary flex items-center justify-center">
                <FileUp className="h-5 w-5 text-muted-foreground" />
              </div>
              {file ? (
                <div>
                  <p className="text-xs font-medium text-foreground">{file.name}</p>
                  <p className="text-[11px] text-muted-foreground">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-xs font-medium text-foreground">
                    Click to browse or drag and drop
                  </p>
                  <p className="text-[11px] text-muted-foreground mt-0.5">
                    PDF up to 50MB (filings, annual reports, earnings presentations)
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="text-xs"
            onClick={() => setOpen(false)}
            disabled={uploading}
          >
            Cancel
          </Button>
          <Button
            type="button"
            size="sm"
            className="text-xs font-medium"
            disabled={!file || uploading}
            onClick={handleUpload}
          >
            {uploading ? "Ingesting..." : "Upload & Ingest"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
