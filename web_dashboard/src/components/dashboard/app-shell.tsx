import { Toaster } from "sonner";
import { useStudioStore } from "@/lib/studio-store";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";
import { OverviewView } from "./overview";
import { ComposeView } from "./compose";
import { GalleryView } from "./gallery";
import { QueueView } from "./queue";
import { ProjectsView } from "./projects";
import { ProductionView } from "./production";
import { DnaView } from "./dna";
import { SequencesView } from "./sequences";
import { QuotaView } from "./quota";
import { ToolsView } from "./tools";

export function AppShell() {
  const view = useStudioStore((s) => s.view);

  return (
    <div className="flex min-h-dvh bg-bg text-fg">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar />
        <main className="flex-1 px-4 py-5 sm:px-6 sm:py-6">
          <div className="mx-auto max-w-7xl">
            {view === "overview" && <OverviewView />}
            {view === "production" && <ProductionView />}
            {view === "dna" && <DnaView />}
            {view === "sequences" && <SequencesView />}
            {view === "compose" && <ComposeView />}
            {view === "gallery" && <GalleryView />}
            {view === "queue" && <QueueView />}
            {view === "quota" && <QuotaView />}
            {view === "projects" && <ProjectsView />}
            {view === "tools" && <ToolsView />}
          </div>
        </main>
      </div>
      <Toaster
        theme="dark"
        position="bottom-right"
        toastOptions={{
          className:
            "!bg-bg-elevated !text-fg !border !border-border !shadow-lg",
        }}
      />
    </div>
  );
}
