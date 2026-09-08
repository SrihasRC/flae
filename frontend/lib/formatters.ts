/**
 * Text and Data Formatting Utilities for FLAE Ledger
 * Cleans extracted corporate filings data from raw OCR, Markdown tables,
 * and HTML artefacts (<br>, **, |, etc.) into polished enterprise typography.
 */

/**
 * Decode HTML entities like &amp;, &lt;, &gt;, &quot;, &#39;
 */
export function decodeHtmlEntities(str: string): string {
  if (!str) return "";
  return str
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, " ");
}

/**
 * Strips raw HTML tags, Markdown bold/italic symbols, table pipes,
 * and normalizes whitespace into clean, readable text.
 */
export function cleanText(text: string | null | undefined): string {
  if (!text) return "";
  let s = decodeHtmlEntities(text);

  // Replace <br>, <br/>, <br /> with clean space or separator
  s = s.replace(/<br\s*\/?>/gi, " ");

  // Strip all other HTML tags
  s = s.replace(/<\/?[^>]+(>|$)/g, " ");

  // Remove Markdown bold/italic: **text** -> text, *text* -> text, __text__ -> text
  s = s.replace(/\*{1,3}([^*]+)\*{1,3}/g, "$1");
  s = s.replace(/_{1,3}([^_]+)_{1,3}/g, "$1");

  // Remove stray markdown syntax characters: *, _, ~, `, #
  s = s.replace(/[*_~`#]/g, "");

  // Remove table pipes |
  s = s.replace(/\|+/g, " ");

  // Normalize multiple spaces and hyphens
  s = s.replace(/\s+/g, " ").trim();

  // Remove leading/trailing stray dashes, colons or pipes
  s = s.replace(/^[-—:|,\s]+|[-—:|,\s]+$/g, "").trim();

  return s;
}

/**
 * Specifically cleans an attribute string for concise table and card display.
 * Strips OCR noise and table artifacts while preserving readable financial metric names.
 */
export function formatAttribute(attribute: string | null | undefined): string {
  if (!attribute) return "General Assertion";
  const cleaned = cleanText(attribute);
  if (!cleaned) return "General Assertion";
  return cleaned;
}

export interface FormattedValue {
  primary: string;
  secondary?: string;
  breakdown?: string[];
  isNumeric: boolean;
}

/**
 * Cleans and formats raw and numeric values.
 * Parses multi-row OCR chunks (e.g. "105.19%<br>96,195.00<br>104.28%") into
 * a prominent primary headline value and clean secondary tags.
 */
export function formatValue(
  valueRaw: string | null | undefined,
  valueNumeric?: number | null,
  unit?: string | null
): FormattedValue {
  // If normalized numeric value is available
  if (valueNumeric !== null && valueNumeric !== undefined && !isNaN(valueNumeric)) {
    const cleanUnit = cleanText(unit);
    const formattedNum = valueNumeric.toLocaleString("en-IN", {
      maximumFractionDigits: 4,
    });
    const primary = cleanUnit ? `${formattedNum} ${cleanUnit}` : formattedNum;

    // Check if raw value has additional sub-values or years
    if (valueRaw && (valueRaw.includes("<br") || valueRaw.includes("\n"))) {
      const rawParts = valueRaw
        .split(/<br\s*\/?>|\n/gi)
        .map((p) => cleanText(p))
        .filter(Boolean);

      if (rawParts.length > 1) {
        return {
          primary,
          secondary: rawParts.filter((p) => p !== cleanText(valueRaw)).slice(0, 3).join(" • "),
          breakdown: rawParts,
          isNumeric: true,
        };
      }
    }

    return { primary, isNumeric: true };
  }

  // If no numeric value, clean valueRaw
  if (!valueRaw) {
    return { primary: "—", isNumeric: false };
  }

  const rawParts = valueRaw
    .split(/<br\s*\/?>|\n/gi)
    .map((p) => cleanText(p))
    .filter(Boolean);

  if (rawParts.length === 0) {
    return { primary: "—", isNumeric: false };
  }

  return {
    primary: rawParts[0],
    secondary: rawParts.length > 1 ? rawParts.slice(1, 4).join(" • ") : undefined,
    breakdown: rawParts.length > 1 ? rawParts : undefined,
    isNumeric: false,
  };
}

/**
 * Formats verbatim quote into clean readable text without raw table pipes, <br>, or **.
 */
export function formatEvidenceQuote(quote: string | null | undefined): string {
  if (!quote) return "No verbatim citation recorded.";
  let q = decodeHtmlEntities(quote);

  // Replace <br> with space
  q = q.replace(/<br\s*\/?>/gi, " ");

  // Remove markdown bold/italic
  q = q.replace(/\*{1,3}([^*]+)\*{1,3}/g, "$1");
  q = q.replace(/_{1,3}([^_]+)_{1,3}/g, "$1");

  // Remove table border pipes
  q = q.replace(/\|+/g, " ");

  // Remove stray markdown symbols
  q = q.replace(/[*_~`#]/g, "");

  // Normalize whitespace
  q = q.replace(/\s+/g, " ").trim();

  // Strip leading/trailing quotation marks to prevent double quotes
  q = q.replace(/^["'“”‘’\s]+|["'“”‘’\s]+$/g, "").trim();

  return q || "No verbatim citation recorded.";
}

export interface FactCategoryInfo {
  label: string;
  badgeVariant: "teal" | "coral" | "amber" | "outline";
  isHeadline: boolean;
  definition: string;
}

/**
 * Classifies extracted fact into standard business domain categories with salience tagging.
 */
export function getFactCategory(
  attribute: string,
  subject: string,
  unit?: string | null
): FactCategoryInfo {
  const text = `${attribute} ${subject} ${unit || ""}`.toLowerCase();
  const isHeadline = /revenue|ebitda|margin|volume|centers?|net profit|pat\b|pbt\b/.test(text);

  if (/revenue|ebitda|profit|loss|margin|expense|income|cash|debt|ind-as|turnover|pat\b|pbt\b|capex|dividend/.test(text)) {
    return {
      label: "Financials",
      badgeVariant: "teal",
      isHeadline,
      definition: "Financial Statement disclosure & statutory earnings metrics.",
    };
  }
  if (/volume|parcel|express|pincode|pin-code|center|hub|facility|fleet|freight|ton|tonnes|sq\s*ft|network|client|customer|shipment/.test(text)) {
    return {
      label: "Operations",
      badgeVariant: "coral",
      isHeadline,
      definition: "Operational logistics footprint, processing hubs & commercial network scale.",
    };
  }
  if (/director|esop|option|personnel|officer|managerial|remuneration|salary|board|governance|auditor|committee/.test(text)) {
    return {
      label: "Governance",
      badgeVariant: "amber",
      isHeadline,
      definition: "Corporate governance, executive appointments & equity incentive schemes.",
    };
  }
  return {
    label: "Statutory Disclosures",
    badgeVariant: "outline",
    isHeadline,
    definition: "Regulatory filings, statutory compliance statements & audit annotations.",
  };
}
