"""File parser — reads CSV and Excel files into Pandas DataFrames."""

import io
import pandas as pd
import chardet
from app.utils.logger import get_logger

logger = get_logger(__name__)


def detect_encoding(file_bytes: bytes) -> str:
    """Detect file encoding using chardet."""
    result = chardet.detect(file_bytes[:10000])
    encoding = result.get("encoding", "utf-8")
    confidence = result.get("confidence", 0)
    logger.info(f"Detected encoding: {encoding} (confidence: {confidence:.2f})")
    return encoding or "utf-8"


def parse_csv(file_bytes: bytes, file_name: str = "") -> pd.DataFrame:
    """Parse a CSV file into a DataFrame with encoding detection."""
    encoding = detect_encoding(file_bytes)

    try:
        df = pd.read_csv(
            io.BytesIO(file_bytes),
            encoding=encoding,
            low_memory=False,
            on_bad_lines="warn",
        )
    except UnicodeDecodeError:
        logger.warning(f"Failed with {encoding}, falling back to latin-1")
        df = pd.read_csv(
            io.BytesIO(file_bytes),
            encoding="latin-1",
            low_memory=False,
            on_bad_lines="warn",
        )

    logger.info(f"Parsed CSV '{file_name}': {df.shape[0]} rows × {df.shape[1]} columns")
    return df


def parse_excel(file_bytes: bytes, file_name: str = "") -> pd.DataFrame:
    """Parse an Excel file into a DataFrame (first sheet)."""
    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=0, engine="openpyxl")
    logger.info(f"Parsed Excel '{file_name}': {df.shape[0]} rows × {df.shape[1]} columns")
    return df


def parse_file(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    """Parse a file based on its extension."""
    ext = file_name.lower().rsplit(".", 1)[-1] if "." in file_name else ""

    if ext == "csv":
        return parse_csv(file_bytes, file_name)
    elif ext in ("xlsx", "xls"):
        return parse_excel(file_bytes, file_name)
    else:
        raise ValueError(f"Unsupported file type: .{ext}. Use .csv, .xlsx, or .xls")


def extract_column_metadata(df: pd.DataFrame) -> dict:
    """
    Extract metadata for each column: dtype, null count, unique count,
    numeric stats, and sample values.
    """
    metadata = {}

    for col in df.columns:
        series = df[col]
        info = {
            "dtype": str(series.dtype),
            "null_count": int(series.isnull().sum()),
            "null_percentage": round(float(series.isnull().mean()) * 100, 2),
            "unique_count": int(series.nunique()),
            "sample_values": [
                _safe_value(v) for v in series.dropna().head(5).tolist()
            ],
        }

        # Numeric stats
        if pd.api.types.is_numeric_dtype(series):
            desc = series.describe()
            info.update({
                "mean": _safe_float(desc.get("mean")),
                "std": _safe_float(desc.get("std")),
                "min": _safe_float(desc.get("min")),
                "max": _safe_float(desc.get("max")),
                "median": _safe_float(series.median()),
                "q25": _safe_float(desc.get("25%")),
                "q75": _safe_float(desc.get("75%")),
            })

        metadata[col] = info

    return metadata


def _safe_float(val) -> float | None:
    """Convert to float safely, handling NaN."""
    if val is None or pd.isna(val):
        return None
    return round(float(val), 6)


def _safe_value(val):
    """Make a value JSON-serializable."""
    if pd.isna(val):
        return None
    if isinstance(val, (pd.Timestamp,)):
        return val.isoformat()
    if hasattr(val, "item"):  # numpy scalar
        return val.item()
    return val
