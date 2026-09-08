"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Plus } from "lucide-react";
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
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { createWorkspace } from "@/lib/api";

interface CreateWorkspaceDialogProps {
  onCreated?: () => void;
}

export function CreateWorkspaceDialog({ onCreated }: CreateWorkspaceDialogProps) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const created = await createWorkspace({
        name: name.trim().toLowerCase().replace(/\s+/g, "-"),
        description: description.trim() || undefined,
      });

      setOpen(false);
      setName("");
      setDescription("");
      if (onCreated) {
        onCreated();
      }
      router.push(`/workspaces/${created.id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create workspace");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={
          <Button size="sm" className="w-full gap-1.5 text-xs font-medium rounded-sm">
            <Plus className="h-3.5 w-3.5" />
            <span>New Workspace</span>
          </Button>
        }
      />
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Create Workspace</DialogTitle>
            <DialogDescription>
              Workspaces isolate fact ledgers, uploaded PDF documents, and arbitration graphs.
            </DialogDescription>
          </DialogHeader>

          <div className="py-4 space-y-3">
            {error && (
              <div className="p-2.5 rounded-md bg-destructive/10 border border-destructive/20 text-destructive text-xs">
                {error}
              </div>
            )}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-foreground">
                Workspace Name <span className="text-destructive">*</span>
              </label>
              <Input
                placeholder="e.g. tata-motors-fy24"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="h-8 text-xs font-mono"
              />
              <p className="text-[11px] text-muted-foreground">
                Lowercase letters, numbers, and hyphens recommended.
              </p>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-foreground">Description</label>
              <Textarea
                placeholder="e.g. Annual reports and financial notes for Tata Motors FY24"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                className="text-xs resize-none"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="text-xs"
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              size="sm"
              className="text-xs font-medium"
              disabled={loading || !name.trim()}
            >
              {loading ? "Creating..." : "Create Workspace"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
