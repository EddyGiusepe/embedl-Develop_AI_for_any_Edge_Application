/**
 * Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro
 *
 * ResultCard.tsx
 * ==============
 * Final result card shown after a successful analysis job.
 * Displays file metadata and delegates the VLM report rendering to
 * PlateReport.
 */

import { CheckCircle2, Clock, FileText } from "lucide-react";

import { PlateReport } from "@/components/PlateReport";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { AnalysisResult } from "@/lib/types";

interface ResultCardProps {
  result: AnalysisResult;
}

export function ResultCard({ result }: ResultCardProps) {
  return (
    <Card className="border-primary/20 bg-card">
      <CardHeader>
        <div className="flex items-center gap-2">
          <CheckCircle2 className="size-5 text-primary" />
          <CardTitle>License Plate Report</CardTitle>
        </div>
        <CardDescription className="flex flex-wrap items-center gap-2 pt-1">
          <Badge variant="secondary" className="gap-1">
            <FileText className="size-3" />
            {result.filename}
          </Badge>
          <Badge variant="outline">{result.media_type}</Badge>
          <Badge variant="outline" className="gap-1">
            <Clock className="size-3" />
            {result.processing_time_seconds.toFixed(2)}s
          </Badge>
        </CardDescription>
      </CardHeader>
      <CardContent>
        <PlateReport description={result.description} />
      </CardContent>
    </Card>
  );
}
