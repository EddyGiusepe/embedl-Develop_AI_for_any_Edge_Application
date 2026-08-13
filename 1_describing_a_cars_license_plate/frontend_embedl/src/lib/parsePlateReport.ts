/**
 * Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro
 *
 * parsePlateReport.ts
 * ===================
 * Parses the structured markdown output produced by the VLM
 * (Cosmos-Reason2-2B by embedl) and returns one or more license plate records.
 *
 * FORMATO ESPERADO (definido em backend_embedl/app/core/prompts.py)
 * ----------------
 * For an image (single block):
 *
 *   **Analysis status**: No license plate detected
 *   **Reason**: No vehicle or real vehicle license plate is visible in the image.
 *   **Confidence**: High
 *
 * Or, when a plate is detected:
 *
 *   **Country**: India
 *   **License plate number**: TN87 C5106
 *   **State/City**: Chennai
 *   **Format**: Indian plate
 *   **Visual characteristics**: ...
 *   **Vehicle**: ...
 *   **Confidence**: High
 *
 * For a video (multiple blocks separated by "---"):
 *
 *   **Plate #**: 1
 *   **Country**: ...
 *   ...
 *   ---
 *   **Plate #**: 2
 *   **Country**: ...
 *
 * RESILIENCE
 * -----------
 * The VLM may drift from the format (missing fields, reordered fields, extra
 * text before/after, or markdown code fences). The parser is tolerant: missing
 * fields remain undefined, unknown lines are ignored, and the original string
 * is exposed as fallback if no known fields are recognized.
 */

export type Confidence = "Low" | "Medium" | "High";

export interface PlateInfo {
  /** Special status used when no real vehicle/license plate is detected. */
  analysisStatus?: string;
  /** Explanation for special states such as no detected license plate. */
  reason?: string;
  /** Plate index (1, 2, ...). Present in videos with multiple plates. */
  index?: string;
  /** Country of origin, if identified. */
  country?: string;
  /** Plate number/text, exactly as read by the model. */
  plateText?: string;
  /** State, city, or region visible on the plate. */
  region?: string;
  /** Identified plate format. */
  format?: string;
  /** Visual characteristics (colors, symbols, strips, flags). */
  visualFeatures?: string;
  /** Vehicle make/model/color. */
  vehicle?: string;
  /** Video context (only for video analysis). */
  videoContext?: string;
  /** Confidence level assigned by the model. */
  confidence?: Confidence | string;
}

export interface ParsedReport {
  /** Detected plates (always >= 1, even in fallback mode). */
  plates: PlateInfo[];
  /**
   * Indicates that the parser could not extract any known field.
   * In this case, plates[0] is empty and the UI should show the raw text.
   */
  isFallback: boolean;
  /** Original model output, used for fallback display. */
  raw: string;
}

/**
 * Maps normalized field labels to PlateInfo keys. English labels are the
 * current canonical format; legacy pt-BR labels remain for backward
 * compatibility with previous model outputs.
 */
const FIELD_MAP: Record<string, keyof PlateInfo> = {
  "analysisstatus": "analysisStatus",
  "status": "analysisStatus",
  "reason": "reason",
  "plate#": "index",
  "platen": "index",
  "plateno": "index",
  "plateindex": "index",
  "placan": "index",
  "placano": "index",
  "country": "country",
  "pais": "country",
  "licenseplatenumber": "plateText",
  "platenumber": "plateText",
  "plate": "plateText",
  "number": "plateText",
  "numerodaplaca": "plateText",
  "numero": "plateText",
  "state/city": "region",
  "statecity": "region",
  "state": "region",
  "city": "region",
  "estado/cidade": "region",
  "estadocidade": "region",
  "estado": "region",
  "format": "format",
  "formato": "format",
  "visualcharacteristics": "visualFeatures",
  "visualfeatures": "visualFeatures",
  "caracteristicasvisuais": "visualFeatures",
  "caracteristicas": "visualFeatures",
  "vehicle": "vehicle",
  "veiculo": "vehicle",
  "videocontext": "videoContext",
  "contextodovideo": "videoContext",
  "contexto": "videoContext",
  "confidence": "confidence",
  "confianca": "confidence",
};

/** Normalizes a field label so it can be matched against FIELD_MAP. */
function normalizeKey(key: string): string {
  return key
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[\s°*]/g, "")
    .toLowerCase();
}

/** Matches a `**key**: value` line and returns { key, value }. */
const LINE_PATTERN = /^\s*\**\s*([^*:]+?)\s*\**\s*:\s*(.+)$/;

function stripCodeFences(text: string): string {
  return text
    .replace(/^\s*```(?:markdown|md)?\s*/i, "")
    .replace(/\s*```\s*$/i, "")
    .trim();
}

function parseBlock(block: string): PlateInfo {
  const info: PlateInfo = {};

  for (const rawLine of block.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line) continue;

    const match = LINE_PATTERN.exec(line);
    if (!match) continue;

    const [, rawKey, rawValue] = match;
    const key = normalizeKey(rawKey);
    const field = FIELD_MAP[key];
    if (!field) continue;

    const value = rawValue.trim().replace(/^\*+|\*+$/g, "").trim();
    if (!value) continue;

    info[field] = value;
  }

  return info;
}

/**
 * Main parser. Receives the API `description` string and returns the
 * ParsedReport consumed by the UI.
 */
export function parsePlateReport(description: string): ParsedReport {
  const text = stripCodeFences(description?.trim() ?? "");

  if (!text) {
    return { plates: [{}], isFallback: true, raw: "" };
  }

  // The video prompt instructs the model to separate plate blocks with "---".
  const blocks = text
    .split(/^\s*-{3,}\s*$/m)
    .map((b) => b.trim())
    .filter((b) => b.length > 0);

  const plates = blocks.map(parseBlock);

  // If no block produced any known field, mark as fallback.
  const isFallback = plates.every(
    (p) => Object.keys(p).length === 0,
  );

  return {
    plates: isFallback ? [{}] : plates,
    isFallback,
    raw: text,
  };
}
