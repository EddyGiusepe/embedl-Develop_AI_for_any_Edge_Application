/**
 * Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro
 *
 * App.tsx
 * =======
 * Root frontend component for the license plate analysis UI.
 *
 * Orchestrates media selection, upload, job polling, progress display,
 * result rendering, and error feedback using the useAnalysisJob hook.
 *
 * RUN
 * ---
 * npm run build
 * npm run dev   (development server at http://localhost:5173)
 * npm run preview   (preview build at http://localhost:4173)
 */

import { useState } from "react";
import { AlertCircle, ImagePlus, RotateCcw, VideoIcon } from "lucide-react";

import { AnalyzeButton } from "@/components/AnalyzeButton";
import { Header } from "@/components/Header";
import { JobProgress } from "@/components/JobProgress";
import { MediaPreview } from "@/components/MediaPreview";
import { ResultCard } from "@/components/ResultCard";
import { UploadZone } from "@/components/UploadZone";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAnalysisJob } from "@/hooks/useAnalysisJob";
import type { MediaType } from "@/lib/types";

function App() {
  const [mediaType, setMediaType] = useState<MediaType>("image");
  const [file, setFile] = useState<File | null>(null);

  const {
    analyze,
    reset,
    job,
    jobId,
    isUploading,
    isProcessing,
    isComplete,
    isFailed,
  } = useAnalysisJob();

  const busy = isUploading || isProcessing;

  function handleTabChange(value: string) {
    setMediaType(value as MediaType);
    setFile(null);
    reset();
  }

  function handleNewAnalysis() {
    setFile(null);
    reset();
  }

  function handleAnalyze() {
    if (!file) return;
    analyze(file);
  }

  return (
    <div className="min-h-dvh bg-background">
      <Header />

      <main className="mx-auto max-w-4xl px-4 py-8">
        <div className="space-y-6">
          <section>
            <h2 className="text-2xl font-bold tracking-tight">
              Send an Image or Video
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              The embedl/Cosmos-Reason2-2B-W4A16 model will describe the license plate in English.
            </p>
          </section>

          <Tabs value={mediaType} onValueChange={handleTabChange}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="image" disabled={busy}>
                <ImagePlus className="size-4" />
                Image
              </TabsTrigger>
              <TabsTrigger value="video" disabled={busy}>
                <VideoIcon className="size-4" />
                Video
              </TabsTrigger>
            </TabsList>

            <TabsContent value="image" className="mt-4 space-y-4">
              {!file ? (
                <UploadZone
                  mediaType="image"
                  onFileSelected={setFile}
                  disabled={busy}
                />
              ) : (
                <MediaPreview
                  file={file}
                  mediaType="image"
                  onClear={() => setFile(null)}
                  disabled={busy}
                />
              )}
            </TabsContent>

            <TabsContent value="video" className="mt-4 space-y-4">
              {!file ? (
                <UploadZone
                  mediaType="video"
                  onFileSelected={setFile}
                  disabled={busy}
                />
              ) : (
                <MediaPreview
                  file={file}
                  mediaType="video"
                  onClear={() => setFile(null)}
                  disabled={busy}
                />
              )}
            </TabsContent>
          </Tabs>

          {file && !isComplete && !isFailed && (
            <AnalyzeButton
              onClick={handleAnalyze}
              isUploading={isUploading}
              isProcessing={isProcessing}
              disabled={!file}
            />
          )}

          {job && jobId && !isComplete && (
            <JobProgress status={job.status} jobId={jobId} />
          )}

          {isComplete && job?.result && <ResultCard result={job.result} />}

          {isFailed && (
            <Alert variant="destructive">
              <AlertCircle className="size-4" />
              <AlertTitle>Analise falhou</AlertTitle>
              <AlertDescription>
                {job?.error ?? "Unknown error processing the media."}
              </AlertDescription>
            </Alert>
          )}

          {(isComplete || isFailed) && (
            <Button
              variant="outline"
              onClick={handleNewAnalysis}
              className="w-full"
            >
              <RotateCcw className="size-4" />
              New analysis
            </Button>
          )}
        </div>
      </main>

      <footer className="border-t py-6 text-center text-xs text-muted-foreground">
      <div>Developed with ❤️</div>

      embedl/Cosmos-Reason2-2B-W4A16 - Edge AI - by Senior Data Scientist:. Dr. Eddy Giusepe Chirinos Isidro
      </footer>
    </div>
  );
}

export default App;
